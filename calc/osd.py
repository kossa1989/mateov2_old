import numpy as np
import pandas as pd

from calc.base_calc import UtilTools
from calc.plwm import Calc
from nothing_important.helper import ShapesDoesntMatch
# from pytar_calc.shared.db import engine as engine_daneb # TODO do zmiany ten silnik(config)
from database.db import DbEngine
engine_daneb = DbEngine.create_engine('pytar')

class FkSzcz(UtilTools):
    """Main class for handling FK file."""
    # TODO zmienic tak, zeby wszystki slowniki byly w jednej klasie slownikowej a nie w dedykowanych
    def __init__(self, query_sm=None, **kwargs):
        super(FkSzcz, self).__init__()
        self.table_type = 'fk'
        self.query_sm = query_sm
        self.fk_szcz = self.get_latest_dict('fk_szczegolowy')
        self.kwargs = kwargs
        self.kolumny_liczbowe = ['wyn_h_lekarz', 'wyn_h_pieleg', 'wyn_h_perf',
                                 'wyn_h_psych', 'wyn_h_diet', 'wyn_h_logop', 'wyn_h_rehab', 'wyn_h_fiz_med',
                                 'wyn_h_technik',
                                 'wyn_h_terap_zaj',
                                 'wyn_h_pozost_med', 'wyn_h_pozost_nmed', 'wyn_h_rezydent', 'infrast_odt_h_bloku',
                                 'nowy_osobodzien_koszt']

        self.fk_szcz = self.prepare_fk_szcz()
        if 'kod_sw' in self.kwargs['case_group']:
            self.fk = self.fk_szcz
        else:
            self.fk = self.fk_without_kod_sw()
        self.slo_opk = self.prepare_slo_opk()
        self.slo_oit = self.prepare_slo_oit()

    def prepare_fk_szcz(self):
        """Prepares raw FK file ie change columns names, filter to query_sm etc."""
        fk = self.fk_szcz.copy()
        fk = fk.rename(columns={'kod_nfz': 'kod_sw', 'opk_nr': 'nr_opk', 'x-do wyrzucenia powtórka': 'x-powt'})
        if self.query_sm:
            # filters FK dict to query_sm swds only
            swds = self.query_sm.query_sm[['kod_sw']].drop_duplicates()
            fk = fk.merge(swds)
        fk = fk[fk['rok'].str.len() == 4]  # filter only entire years (reject VI, I etc.)
        fk['rok'] = fk['rok'].str.extract('(\d{4})')
        fk = fk[(fk['rok'].fillna(0).astype(int).astype(str).str.strip() == self.kwargs['rok']) & (
                fk['x-powt'].astype(str) == '1')]
        # change old swd codes to new ones, preserve old as copy
        kod_sw_change_map = {'121/211925': '121211925',
                             '121/100089': '100089', }
        # store old values in list
        old_values = []
        for k, v in kod_sw_change_map.items():
            old_values.append(fk[fk['kod_sw'] == k])
            fk['kod_sw'] = fk['kod_sw'].mask((fk['kod_sw'] == k), v)
        # concat new values with old values for compatibility
        fk = pd.concat(old_values + [fk])

        fk_pers = fk[
            ['kod_sw', 'nr_opk', 'kat_med',
             'kat_opk', 'infrast_odt_h_bloku', 'opk', 'nowy_osobodzien_koszt', 'wyn_h_lekarz', 'wyn_h_pieleg',
             'wyn_h_perf',
             'wyn_h_psych', 'wyn_h_diet', 'wyn_h_logop', 'wyn_h_rehab', 'wyn_h_fiz_med', 'wyn_h_technik',
             'wyn_h_terap_zaj',
             'wyn_h_pozost_med', 'wyn_h_pozost_nmed', 'wyn_h_rezydent', 'kod_resort']]
        # convert to numerical if havent converted yet
        for i in self.kolumny_liczbowe:
            fk_pers = fk_pers.assign(**{i: lambda x: x[i].astype(np.float32)})
        fk_pers['kod_sw'] = fk_pers['kod_sw'].str.strip()
        fk_pers['nr_opk'] = fk_pers['nr_opk'].str.strip()
        fk_pers = fk_pers.rename(columns={'opk': 'opk_nazwa'})
        return fk_pers

    def fk_without_kod_sw(self):
        fk_pers = self.fk_szcz
        fk_agr = None
        for klucz in self.kolumny_liczbowe:
            # join all tables
            temp_fk = UtilTools.del_outliers_boxplot_calc_mean(fk_pers, klucz, ['kat_med', 'kat_opk'], False)
            if fk_agr is None:
                fk_agr = temp_fk
            else:
                fk_agr = fk_agr.merge(temp_fk, on=['kat_med', 'kat_opk'])

        return fk_agr

    def prepare_slo_oit(self):
        """Define OIT dictionary."""
        oit = self.fk_szcz[self.fk_szcz['kat_med'].astype(str) == '18']
        oit_slo = oit[['kat_med', 'kat_opk', 'nr_opk', 'kod_sw']].drop_duplicates()
        return oit_slo

    def prepare_slo_opk(self):
        fk = self.fk_szcz
        fk.columns = fk.columns.str.lower()
        slo_opk = fk[['kod_sw', 'kod_resort', 'nr_opk', 'opk_nazwa', 'kat_med', 'kat_opk']].rename(
            columns={'kod_resort': 'kod_resort_list'}).drop_duplicates()
        return slo_opk


class SmCalc(Calc):
    """Class used to calculated osd (osobodzien) and total osd. """
    def get_opk_list(self):
        """Usefull in proceedings which has opk table (eg 42 onk)"""
        opk_list = pd.read_sql('select * from daneb.opk', engine_daneb)
        opk_list = self.ensure_dtypes(opk_list)
        opk_list.columns = opk_list.columns.str.lower()
        opk_list = opk_list.rename(columns={'nr_opk': 'nr_opk_list', 'kod_resortowy': 'kod_resort_list'})
        opk_list = opk_list[['kod_ow', 'kod_sw', 'kod_resort_list', 'nr_opk_list', 'nazwa_opk']]
        return opk_list

    def create_tar(self):
        self.opk_list = self.fk_class.slo_opk
        self.query_sm_join = self.create_join(self.patient_id)
        self.query_sm_cols = ','.join(
            ['t2.' + i for i in self.query_sm.columns if i not in self.patient_id + ['kod_prod']])
        if self.query_sm_cols:
            self.query_sm_cols+=','
        self.schema_dot_table_type = f'{self.kwargs["schema"]}.%s' % self.table_type
        self.create_index(engine_daneb, self.schema_dot_table_type, self.patient_id)
        self.create_index(engine_daneb, self.query_sm_table_name, self.patient_id)
        query_sql = """
                create table {table_name} as
                select {query_sm_cols} t1.*
                from {schema_dot_table_type} t1 inner join {query_sm_table_name} t2 on {query_sm_join}
        """.format(**self.__dict__)

        self.execute_query(engine_daneb, query_sql, DEBUG=True)
        self.tar = pd.read_sql('select * from %s' % self.table_name, engine_daneb)
        self.tar = self.ensure_dtypes(self.tar)
        self.tar.columns = self.tar.columns.str.lower()

    def calc_osd_nr_opk(self):
        """Calculates osd cost according to old method, without intra hospital migrations."""
        self.create_tar()
        a = self.tar
        self.kp_rozl = a[a['kod_prod'].str.match('^5\.51\..*$')]
        if not self.kp_rozl[self.kp_rozl[self.patient_id].duplicated()].empty:
            print('Pojawily sie duplikaty po wziecu kp rozliczeniowcyh! Mozliwy blad.')
        kp_join = self.kp_rozl[self.patient_id + ['kod_prod', 'nr_opk_sm']]
        self.check_dups(kp_join, ['kod_sw', 'nr_ks'])
        osd = self.og.merge(kp_join, on=self.patient_id)
        osd = osd.rename(columns={'kod_prod_x': 'kod_prod'})
        self.check_dups(osd, ['kod_sw', 'nr_ks'])
        osd = osd.merge(self.fk, left_on=['kod_sw', 'nr_opk_sm'], right_on=['kod_sw', 'nr_opk']
                        , how='left')
        self.dups = self.check_dups(osd, ['kod_sw', 'nr_ks'])
        osd['koszt_osd'] = osd['czas_hosp'].astype(np.float32) * osd['osd_koszt_dzien'].astype(np.float32)
        self.osd = osd

    def prepare_table_to_calc_osd(self):
        """Selects columns and cleans df to calc osd. Defines fake_data behaviour."""
        # there could be duplicates in SM because of possibility to assign multiple products (1c, 1a etc.)
        sm_osd = self.tar[self.patient_id + ['nr_opk_sm', 'data_rozp_prod', 'data_zak_prod', 'kod_prod']] \
            .drop_duplicates().sort_values('nr_ks')

        sm_osd_filter_nulls = sm_osd[sm_osd['kod_prod'].notnull()] # deletes missing if exists (could)
        # in spite of higher lvl of aggregation osd is still calculating based on patients
        sm_slo_opk = sm_osd_filter_nulls.merge(self.fk_class.fk_szcz, left_on=['kod_sw', 'nr_opk_sm'], right_on=['kod_sw', 'nr_opk'],
                                               how='inner') # do tar doklada dane z FK

        # check if cost is provided for all opks, test for fake data option to allow analysis
        try:
            self.rownumeq(sm_slo_opk, sm_osd_filter_nulls)
        except ShapesDoesntMatch as e:
            if self.permissive:
                sm_slo_opk = sm_osd_filter_nulls.merge(self.fk, left_on=['kod_sw', 'nr_opk_sm'],
                                                       right_on=['kod_sw', 'nr_opk'],
                                                       how='left')
                sm_no_fk = sm_slo_opk[sm_slo_opk['nowy_osobodzien_koszt'].isnull()][
                    ['kod_sw', 'nr_opk_sm']].drop_duplicates().to_dict(orient='index')
                self.messages['warnings'].append('Następujące OPK nie występują w pliku FK: %s' % sm_no_fk)
            else:
                # FK file is not complete and permissive is off
                raise e
        self.raw_sm_fk = sm_slo_opk
        self.sm_slo_opk = sm_slo_opk

    def filter_opks(self):
        """Filters opks for kod_res startswith 4 and cost gt 0. """
        self.prepare_table_to_calc_osd()
        sm_slo_opk = self.sm_slo_opk.merge(self.opk_list, left_on=['kod_sw', 'nr_opk_sm'],
                                           right_on=['kod_sw', 'nr_opk'], how='left', indicator=True)
        self.rownumeq(self.sm_slo_opk, sm_slo_opk, msg="Dodanie listy OPK nie odbyło się prawidłowo, lista OPK może być niepełna")
        # checks if non of opks is not covered by opk list
        if not sm_slo_opk[sm_slo_opk['_merge'] != 'both'].empty:
            error_msg = "Istnieją OPKi, które nie mają wpisu w bazie FK. OPKI: %s" %sm_slo_opk[
                sm_slo_opk['_merge'] != 'both'][['kod_sw','nr_opk_sm']].drop_duplicates().to_dict(orient='index')
            self.messages['errors'].append(error_msg)
            if not self.permissive:
                raise Exception(error_msg)

        sm_slo_opk = sm_slo_opk.drop(columns=['_merge'])

        important_opks = sm_slo_opk[
            (sm_slo_opk['kod_resort'].astype(str).str[0] == '4') & (sm_slo_opk['nowy_osobodzien_koszt'] > 0)]

        # check for not merged rows
        self.rownumeq(important_opks, sm_slo_opk, key=self.kwargs['patient_id'])

        filtered_out = self.rownumeq(important_opks, sm_slo_opk, key=self.kwargs['patient_id'])
        self.filtered_out = filtered_out.rename(columns={'nr_opk_sm_y':'nr_opk_sm'})  # rows rejected with above filter, later on assert rownums with that
        if not filtered_out.empty:
            patients_not_inlcuded = self.filtered_out[self.kwargs['patient_id'] + ['nr_opk_sm']].drop_duplicates()
            self.messages['errors'].append(
                'Pacjenci zostali wyłączeni z analizy ze względu na nieprawidłowy koszt osd (nr_ks, kod_sw):.\
                 Błąd powstaje, ponieważ pacjenci zostali odfiltrowani - kod_res nie zaczyna się od 4 lub kolumna\
                 nowy_osobodzien_koszt z pliku FK przyjmuje dla tego OPK wartość 0. '
                +'Lista pacjentów dotkniętych błedem: %s' %
                [(i.nr_ks, i.kod_sw, i.nr_opk_sm) for i in patients_not_inlcuded.itertuples()])

        self.important_opks = important_opks

    def osd_with_intra_hosp_migrations(self):
        """Calculates osd using patients migrations in hospital."""
        self.filter_opks()
        # important_opks is hook for ABC
        important_opks = self.important_opks
        patient_grouping = list(set(self.kwargs['case_group'] + self.kwargs['patient_id']))
        if 'kod_prod' in patient_grouping:
            patient_grouping.remove('kod_prod')
        min_date = important_opks.groupby(patient_grouping)['data_rozp_prod'].min().reset_index().rename(
            columns={'data_rozp_prod': 'min_data'}) # min date for every hosp
        max_date = important_opks.groupby(patient_grouping)['data_zak_prod'].max().reset_index().rename(
            columns={'data_zak_prod': 'max_data'}) # max date for every hosp
        drop_vars = [i for i in important_opks.columns if 'wyn_h' in i]
        important_opks1 = important_opks.drop(columns=drop_vars) # remove unused cols

        dates = []
        for i in important_opks1.drop_duplicates().itertuples():
            # create one row for every day, iterate over every row
            date_range = pd.date_range(i.data_rozp_prod, i.data_zak_prod) #create dt index based on date span
            record = important_opks1.loc[i.Index, :] # points to this index
            hosp_time_span = pd.DataFrame(data=[record for i in date_range], index=date_range)
            dates.append(hosp_time_span) #appends date span for this row in sm

        daily_hospitalisation_table = pd.concat(dates).reset_index() #creates one table from all stay spans
        # combine all stays with min and max tables, its required to combine last and first of stay as one day
        daily_hosp_min_max = daily_hospitalisation_table.merge(min_date, on=patient_grouping).merge(max_date,
                                on=patient_grouping)
        # convert to the same dt fmt to properly join
        daily_hosp_min_max['min_data'] = pd.to_datetime(daily_hosp_min_max['min_data'])
        daily_hosp_min_max['max_data'] = pd.to_datetime(daily_hosp_min_max['max_data'])

        # set first and last day of stay the same value
        # uses index as it was generated with date_range so represents datetime
        # saves array in variable to assign it later to df
        dates_series_to_calc_mean = np.where(
            (daily_hosp_min_max['index'] == daily_hosp_min_max['min_data'])
            | (daily_hosp_min_max['index'] == daily_hosp_min_max['max_data']),
            daily_hosp_min_max['min_data'],
            daily_hosp_min_max['index']
        )

        # final calculations
        # asign array of dt to original df
        daily_hosp_min_max['day_to_groupby'] = pd.to_datetime(dates_series_to_calc_mean)
        self.daily_hosp_min_max = daily_hosp_min_max
        daily_cost = daily_hosp_min_max.groupby(patient_grouping + ['day_to_groupby'])[
            'nowy_osobodzien_koszt'].mean() # calc mean stay cost for every day
        # saves table in self to compare with old SAS tar
        self.daily_cost = daily_cost
        # sum all daily costs
        sum_osd = daily_cost.groupby(patient_grouping).sum().reset_index().rename(columns={
            'nowy_osobodzien_koszt': 'koszt_osd'
        })
        if self.query_sm.shape[0] == (sum_osd.shape[0] + self.filtered_out.shape[0]):
            error_msg = "W Bazie FK brakuje wpisów dotyczących NR_OPK potrzebnych do wyliczenia kosztu osobodnia"
            self.messages['errors'].append(error_msg)
            if not self.permissive:
                raise Exception(error_msg )
        self.osd = sum_osd.merge(self.query_sm)

    def calc_new_osd(self):
        self.filter_opks()
        self.osd_with_intra_hosp_migrations()

    def calc_tariff(self):
        self.tariff = self.osd.groupby(self.kwargs['case_group'])['koszt_osd'].mean().reset_index()
        # if analysis includes nr_ks, one can add refundation to patients
        if 'nr_ks' in self.kwargs['case_group']:
            nfz_1a = self.create_nfz_refund('1a')
            nfz_1c = self.create_nfz_refund('1c')
            self.tariff = self.tariff.merge(nfz_1a, how='left')
            if not nfz_1c.empty:
                self.tariff = self.tariff.merge(nfz_1c, how='left')

    def create_nfz_refund(self, nfz_table):
        self.create_index(engine_daneb, self.schema_dot_table_type, self.patient_id)
        self.create_index(engine_daneb, self.query_sm_table_name, self.patient_id)
        nfz_query_data = {
            'table_name':'%s.nfz_%s_%s' % ('tmp',nfz_table, self.uid),
            'nfz_table':'%s.nfz_%s'%(self.kwargs['schema'],nfz_table),
            'og_table':'tmp.tar_%s_%s' % ('og', self.uid),
            'og_join':self.create_join(['ksiega_rok','ksiega_nr','ksiega_poz','ksiega_nr_dziecka','id_swd'],
                                       ['ksiega_rok','ksiega_nr','ksiega_poz','ksiega_nr_dziecka','kod_sw']),
            'og_cols':','.join(self.patient_id),
        }

        query_sql = """
                create table {table_name} as
                select {og_cols}, t1.*
                from {nfz_table} t1 inner join {og_table} t2
                on {og_join}
        """.format(**nfz_query_data)
        self.execute_query(engine_daneb, query_sql, DEBUG=True)
        nfz_refund = pd.read_sql('select * from %s' % nfz_query_data['table_name'], engine_daneb)
        nfz_refund['do_obliczen']= np.where(nfz_refund['cena']==0,nfz_refund['lb_jedn'],nfz_refund['lb_jedn']*nfz_refund['cena'])
        nfz_ref_total = nfz_refund.groupby(self.patient_id)['do_obliczen'].sum().reset_index()
        nfz_ref_total = nfz_ref_total.rename(columns={'do_obliczen':'refundacja_nfz_%s' % nfz_table})
        return nfz_ref_total
