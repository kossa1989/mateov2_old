import pathlib
import re # w.regularne

import numpy as np
import pandas as pd
import sqlalchemy as sa
from django.contrib.gis.measure import D
from sqlalchemy.orm import sessionmaker
from models.externals import Dicts  #''' Do poprawy ? nie powinno być chyba oddzielnie, tylko dodać to do innego istniejącego modelu?'''
from nothing_important.helper import ShapesDoesntMatch, Freezer
from database.db import DbEngine , DbSession
from sqlalchemy.orm import sessionmaker


class UtilTools():
    """Defines some utility tools for all tables. Its parent of all calculating classes in pytar_calc."""

    def __init__(self):
        self.messages = {'warnings': [], 'errors': [], 'info': []}

    def calc_time(self, x):
        """Converts time to decimal format from semicolon separeted format (1:30 --> 1.5)."""
        try:
            y = x.split(':')
            return float(y[0]) + float(y[1]) / 60
        except ValueError:
            return 0
        except AttributeError:
            "Czas personelu wpisany jako brak."
            return 0
        except IndexError:
            "Czas personelu wpisany jako jedna liczba bez ':'."
            return 0

    @staticmethod
    def ensure_dtypes(df):
        """Converts DataFrame ensuring dtypes specified in UtilTools state (one common dict for all dtypes needs
        to fit specific table)"""
        import_dtypes = {'icd_9': str, 'kod_sw': str, 'nr_ks': str, 'kod_prod': str}
        cols = df.columns
        matching_dtypes = {}
        for i in import_dtypes:
            if i in cols:
                matching_dtypes[i]=import_dtypes[i]
        return df.astype(matching_dtypes)


    @staticmethod
    def weighted_quantile(values, quantiles, sample_weight=None, old_style=False):
        """ Very close to numpy.percentile, but supports weights.
        NOTE: quantiles should be in [0, 1]!
        :param values: numpy.array with data
        :param quantiles: array-like with many quantiles needed
        :param sample_weight: array-like of the same length as `array`
        :param old_style: if True, will correct output to be consistent
            with numpy.percentile.
        :return: numpy.array with computed quantiles.
        """
        values = np.array(values)
        quantiles = np.array(quantiles)
        if sample_weight is None:
            sample_weight = np.ones(len(values))
        sample_weight = np.array(sample_weight)
        assert np.all(quantiles >= 0) and np.all(quantiles <= 1), \
            'quantiles should be in [0, 1]'

        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]

        weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
        if old_style:
            # To be convenient with numpy.percentile
            weighted_quantiles -= weighted_quantiles[0]
            weighted_quantiles /= weighted_quantiles[-1]
        else:
            weighted_quantiles /= np.sum(sample_weight)
        interp = np.interp(quantiles, weighted_quantiles, values)
        interp_all = [values[np.argmin(np.abs(values - i))] for i in interp]
        return interp_all

    @staticmethod
    def wquantiles(group, col_name, weight_name, quantile):
        """Helper function for aggregating groups with pandas apply."""
        quantile = \
            UtilTools.weighted_quantile(group[col_name].values, [quantile], sample_weight=group[weight_name].values)[0]
        return quantile

    @staticmethod
    def del_outliers_with_boxplot(dsin, var, groups, weights=False):
        """Deletes outlier observations with boxplot method. If weights provided uses weights to
        remove outliers and calculate mean.

        Returns: df without outliers.(wartości odstające -PK)"""
        if not weights:
            x1 = dsin.groupby(groups).quantile(0.25).reset_index()
            x2 = dsin.groupby(groups).quantile(0.75).reset_index()
            x3 = dsin.groupby(groups).mean().reset_index()
        else:
            x1 = dsin.groupby(groups).apply(UtilTools.wquantiles, var, weights, quantile=0.25).reset_index().rename(
                columns={0: var})
            x2 = dsin.groupby(groups).apply(UtilTools.wquantiles, var, weights, quantile=0.75).reset_index().rename(
                columns={0: var})
            x3 = dsin.groupby(groups).apply(UtilTools.wavg, var, weights).reset_index().rename(
                columns={0: var})
            # if weights cols are provided
        y = x1.merge(x2, on=groups, suffixes=('_25', '_75'))
        y = y.merge(x3, on=groups)
        y.rename(columns={var: var + "_mean"}, inplace=True)
        y['IQR'] = y[var + '_75'] - y[var + '_25']
        y1 = dsin.merge(y, on=groups)
        # +/- 0.00001 jest po to, aby unknac usuwania obserwacji z racji matematyki zmiennoprzecinkowej na komputerach
        y2 = y1.query('{0} <= {1} + 1.5*IQR and {0} >= {1} - 1.5*IQR'.format(var, var + '_mean'))
        return y2

    @staticmethod
    def del_outliers_boxplot_calc_mean(dsin, var, groups, weights=False):
        """Deletes outlier observations with boxplot method. If weights provided uses weights to
        remove outliers and calculate mean."""
        y2 = UtilTools.del_outliers_with_boxplot(dsin, var, groups, weights=weights)
        column_select = groups[:]
        column_select.append(var)
        if not weights:
            y3 = y2[column_select].groupby(groups).mean().reset_index()
        else:
            y3 = y2.groupby(groups).apply(UtilTools.wavg, var, weights).reset_index().rename(columns={0: var})
            y3 = y3[column_select]
        return y3

    @staticmethod
    def wavg(group, avg_name, weight_name):
        """ http://stackoverflow.com/questions/10951341/pandas-dataframe-aggregate-function-using-multiple-columns
        In rare instance, we may not have weights, so just return the mean. Customize this if your business case
        should return otherwise.
        """
        d = group[avg_name]
        w = group[weight_name]
        try:
            return (d * w).sum() / w.sum()
        except ZeroDivisionError:
            return d.mean()

    def create_index(self, engine, tbl, cols):
        """Rendres query string to create index on table."""
        if len(cols) > 10:
            raise Exception('Name of index on table %s may be too long.' % tbl)
        cols_list = ','.join(cols)
        shorten_cols = [i[:5] for i in cols]
        idx_name = '_'.join(shorten_cols)
        query_sql = """
        create index %s on %s (%s);
        """ % (idx_name, tbl, cols_list)
        self.execute_query(engine, query_sql)
        return query_sql

    # TODO trzeba tutaj df zmienić na pd.read_sql i reszta pozostaje bez zmian
    def get_latest_dict(self, type='slo_abc'):
        # engine = DbEngine.create_engine('slowniki')
        # df = pd.read_sql_table(type, engine)
        """Retrieves latest dictionary from database. Dict is described by type."""
        engine = DbEngine.create_engine('pytar')
        session = DbSession.get_session(engine)
        dict_metadata = session.query(Dicts).filter_by(type=type).order_by(Dicts.creation_date.desc()).first()
        df = pd.read_pickle(dict_metadata.path_output + '.pkl')

        return df


    def check_dups(self, df, cols):
        """Checks if dataframe has any duplicates."""
        new = df[df.duplicated(cols)]
        if not new.empty:
            print('Zbiór posiada duplikaty względem kolumn %s' % cols)
            return new
        return None

    def get_dups(self, df, cols):
        return df[df[cols].duplicated(keep=False)]

    def rownumeq(self, df1, df2, msg='', key=None, permissive=False):
        """Checks if number of rows is equal in two dfs.
        If key provided returns df with rows which didnt join.
        """
        if key:
            if not isinstance(key, list):
                raise Exception('Key to check on should be a list.')
            outer_join = df1.merge(df2, on=key, indicator=True, how='outer')
            return outer_join[outer_join['_merge'] != 'both']
        if df1.shape[0] != df2.shape[0]:
            self.messages['errors'].append('Zbiory nie są równe. %s' % msg)
            if not permissive:
                raise ShapesDoesntMatch(f'Liczba rekordów w tabelach jest różna ({df1.shape[0]} vs {df2.shape[0]})! {msg}')

        return None

    def execute_query(self, engine, query, DEBUG=False, raise_excpetions=False):
        """Executes query in database."""
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            tbl_name = re.findall('create table(.*)as', query)[0].strip()
        except IndexError:
            pass
        try:
            session.execute(query)
        except sa.exc.OperationalError as e:
            if DEBUG:
                print(e)
            if raise_excpetions:
                raise e
        except sa.exc.ProgrammingError as e:
            if DEBUG:
                print(e)
            if raise_excpetions:
                raise e
        except sa.exc.InternalError as e:
            if DEBUG:
                print(e)
            if raise_excpetions:
                raise e
        session.close()



class ColumnChecker:
    """Checks if columns have any misleading names like "_x" or "_y"."""

    def __setattr__(self, key, value):
        if key == 'tar_sr_il':
            for i in ['_x', '_y', 'Unnamed']:
                for j in value.columns:
                    if i in j:
                        raise Exception('Temporary names in production table %s tar_sr_il' % self.table_type)
            if value.index.duplicated().any():
                raise Exception('Duplicated index entires in %s tar_sr_il' % self.table_type)

        super(ColumnChecker, self).__setattr__(key, value)


class Calc(UtilTools, ColumnChecker):
    """Base class for PL, WM and PR analysis."""

    def __init__(self, table_type, query_sm, uid, fk=None, og=None, **kwargs):
        super(Calc, self).__init__()
        pd.set_option('display.max_columns', 500)
        engine = DbEngine.create_engine('pytar')
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.query_sm = query_sm.query_sm
        self.query_sm_cols = query_sm.columns
        self.uid = uid
        self.table_type = table_type.lower()
        self.table_name = 'tmp.tar_%s_%s' % (self.table_type, self.uid)
        self.patient_id = kwargs['patient_id']
        self.path = pathlib.Path(kwargs['path'])
        self.query_sm_table_name = 'tmp.query_sm_%s' % self.uid
        self.og = og
        self.kwargs = kwargs
        self.session = Session()
        self.fk_class = fk
        self.fk = getattr(fk, 'fk', None)
        self.permissive = kwargs.get('permissive', False)

        if self.table_type.lower() == 'pl':
            self.unit_id = self.kwargs['pl_id']
            self.quantity_col = self.kwargs['pl_quantity'] # <-- Dowiedz się co to za kolumna xD
        elif self.table_type.lower() == 'wm':
            self.unit_id = self.kwargs['wm_id']
            self.quantity_col = self.kwargs['wm_quantity'] # <-- Dowiedz się co to za kolumna xD
        elif self.table_type.lower() == 'pr':
            self.unit_id = self.kwargs['pr_id']
            self.quantity_col = self.kwargs['pr_quantity'] # <-- Dowiedz się co to za kolumna xD

    def create_join(self, left_column_list, right_column_list=None, t1='t1', t2='t2'):

        """Creates join string for sql queries."""
        if not right_column_list:
            join = ''.join(['{t1}.{0}={t2}.{0} and '.format(i, t1=t1, t2=t2) for i in left_column_list])[:-4]
        else:
            join = ''.join(['{t1}.{0}={t2}.{1} and '.format(i, j, t1=t1, t2=t2) for i, j in
                            zip(left_column_list, right_column_list)])[:-4]
        return join

    def create_tar(self):

        engine = DbEngine.create_engine('pytar')
        self.query_sm_join = self.create_join(self.patient_id)
        self.query_sm_cols = ','.join(['t2.' + i for i in self.query_sm.columns if i not in self.patient_id])
        self.schema_dot_table_type = f'{self.kwargs["schema"]}.%s' % self.table_type
        self.create_index(engine, self.schema_dot_table_type, self.patient_id)
        self.create_index(engine, self.query_sm_table_name, self.patient_id)
        query_sql = """
                create table {table_name} as
                select {query_sm_cols}, t1.*
                from {schema_dot_table_type} t1 inner join {query_sm_table_name} t2 on {query_sm_join}
        """.format(**self.__dict__)

        self.execute_query(engine, query_sql)

        self.tar = pd.read_sql('select * from %s' % self.table_name, engine)
        self.tar = self.ensure_dtypes(self.tar)
        self.tar.columns = self.tar.columns.str.lower()

    def add_opk_name(self, tbl):
        """Adds opk name to column which contains "nr_opk" in col name."""
        shape_in = tbl.shape
        case_cols = list(tbl.columns)
        nr_opk_col = list(filter(lambda x: 'nr_opk' in x, case_cols))
        if nr_opk_col and 'kod_sw' in tbl.columns: #adds opk name only if there is enough info in tbl
            case_summary_fk = tbl.merge(self.fk_class.slo_opk, left_on=['kod_sw', nr_opk_col[0]],
                                        right_on=['kod_sw', 'nr_opk'], validate='m:1', how="left", suffixes=('','_to_drop'))
            case_summary = case_summary_fk[case_cols + ['opk_nazwa']]
            tbl_out = case_summary
        else:
            tbl_out = tbl
        shape_out = tbl_out.shape
        if not shape_in[0] == shape_out[0]:
            raise ShapesDoesntMatch('Po dodaniu nazw opk, zmieniła się liczba rekordów!')
        return tbl_out


    # Jedna z głowniejszych metod - tworzy tabele srednia ilosc wyst. w przypadku - PK
    def create_tar_sr_il(self):
        """Aggregates values in tables for given case_group."""
        self.create_tar()
        # takes column names for further analysis
        case_group = self.kwargs['case_group']
        patient_id = self.kwargs['patient_id']
        groups_pl = case_group + self.unit_id
        # aggregates and counts frequency of events in grouping
        b1 = self.tar.groupby(groups_pl)
        c_freq = b1[self.quantity_col].sum()
        c_freq = c_freq.reset_index()
        c_freq.rename(columns={self.quantity_col: 'ilosc_wyst_w_przyp'}, inplace=True)
        # groups and counts number of cases in case
        b2 = self.tar.loc[:, set(case_group + patient_id)].drop_duplicates()
        b2.loc[:, 'dummy'] = 1
        b3 = b2.groupby(case_group)
        case_N = b3.count()
        case_N = case_N[['dummy']].reset_index()
        case_N.rename(columns={'dummy': 'ilosc_przyp'}, inplace=True)
        # summaries above tables and counts average number of occurences in case
        case_summary = c_freq.merge(case_N, on=case_group)
        self.rownumeq(c_freq, case_summary, msg="Błąd przy łączeniu ilości przypadków z ilością wystąpień.")
        case_summary['sr_wyst_w_przyp'] = case_summary['ilosc_wyst_w_przyp'] / case_summary['ilosc_przyp']
        # set empty columns for later pamars
        case_summary.loc[:, 'wsp'] = np.NaN
        case_summary.loc[:, 'wsp_dni'] = np.NaN
        case_summary.loc[:, 'gr_wsp'] = np.NaN
        case_summary.loc[:, 'gr_wsp_dni'] = np.NaN
        case_summary.loc[:, 'grupa'] = np.NaN
        og_small = self.og[case_group + ['wiek', 'czas_hosp']]
        case_summary_og = case_summary.merge(og_small, on=case_group)
        self.rownumeq(case_summary, case_summary_og, msg="Błąd przy dodawaniu informacji z OG przy tworzeniu tar_sr_il.")
        case_summary_og = self.add_opk_name(case_summary_og)
        self.tar_sr_il = case_summary_og

    # Podaje cene jednostkową z pliku OM - (cena_jedn).
    # Podaje cene jednostkowa z pliku WM - (koszt_jedn). - PK
    def summarize_event_costs(self):
        """Aggregates case_grop event costs for total case_group cost."""
        try:
            self.tar_sr_il = self.tar_sr_il.drop(columns=['sum_koszt_gr'])
        except KeyError:
            "Podsumowanie jest pierwszy raz (pierwsze włączenie taryfikatora), kolumna "
            "sum_koszt_gr nie znaduje się jeszcze w tar sr il"
        a = self.tar_sr_il.groupby(self.kwargs['case_group'])['koszt_zdarzenia'].sum().reset_index()
        a = a.rename(columns={'koszt_zdarzenia': 'sum_koszt_gr'})
        tar_sr_il_sums = self.tar_sr_il.merge(a, on=self.kwargs['case_group'])
        self.tar_sr_il = tar_sr_il_sums

    def freeze(self, attrs):
        """In development, finally should save previous ABC runs in database."""
        freezer = Freezer(self, attrs, self.table_type)
        freezer.freeze()