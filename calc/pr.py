from collections import OrderedDict

import numpy as np
import pandas as pd

from calc.plwm import PlWmPrCalc
#from pytar_calc.shared.db import engine as engine_daneb
from nothing_important.helper import ShapesDoesntMatch
from database.db import DbEngine
engine_daneb = DbEngine.create_engine('pytar')


class PrCalc(PlWmPrCalc):
    def __init__(self, *args, **kwargs):
        super(PlWmPrCalc, self).__init__(*args, **kwargs)
        self.prepare_dicts()

        if self.table_type.lower() == 'pr':
            self.file_prices = self.kwargs['pr_prices']
            self.pricelist_table = f'{self.kwargs["schema"]}.cp'
            self.pricelist_col_names = self.kwargs['cp_prices']
            self.join_cols_pr_hr = self.kwargs['join_cols_pr_hr']


    # TODO zrobić z tych słowników nie pliki CSV/excel a zrobić to na DB
    def prepare_dicts(self):
        self.abc_1 = self.get_latest_dict('slo_abc').drop(columns=['nazwa_pr'])
        self.abc_2 = self.get_latest_dict('slo_abc_2').drop(columns=['nazwa_pr'])
        self.slo_hr = self.get_latest_dict('hr')

    def create_tar_sr_il_abc(self):
        """Creates tar_sr_il as normally should and adds ABC categories to procedures."""
        self.create_tar_sr_il()
        # create list to store dfs for later concatenation
        fragments_to_concat = []
        not_matched = self.tar_sr_il
        # assign ABC categories to procedures, ABC_2 dict has higher priority
        for i in [self.abc_2, self.abc_1]:
            entire_table = not_matched.merge(i, left_on=['icd_9'],
                                             right_on=['icd_9'], how='left', validate="m:1")
            fragments_to_concat.append(entire_table[entire_table['abc'].notnull()])
            not_matched = entire_table[entire_table['abc'].isnull()] # usuwa wartości puste - PK
            not_matched = not_matched.drop(columns=['abc'])

        self.tar_sr_il_abc = pd.concat(fragments_to_concat + [not_matched], sort=True).reset_index(drop=True)

        assert self.tar_sr_il_abc.shape[0] == self.tar_sr_il.shape[0]
        self.tar_sr_il_abc['abc'] = self.tar_sr_il_abc['abc'].fillna('X')
        # overwrites tar_sr_il with additional abc col
        self.tar_sr_il = self.tar_sr_il_abc

    # TODO przerobić query_sql tak by, dodac tutaj HASH do tabeli, plus
    def create_tar_pr_hr(self):
        """Creates tar_pr_hr (base table/DataFrame) for all hr calculations. Creates and executes sql statement.

        self.tar_pr_hr is later used to generate ABC dfs and calculate values.
        """
        self.query_sm_join = self.create_join(self.patient_id, t1='t2', t2='t3')
        # defines procedur entity
        self.single_pr = self.kwargs['patient_id'] + self.join_cols_pr_hr
        self.pr_hr_join = self.create_join(self.single_pr)
        self.query_sm_cols = ','.join(['t3.' + i for i in self.query_sm.columns if i not in self.patient_id])
        self.table_name_pr_hr = 'tmp.tar_pr_hr_%s' % self.uid
        self.table_pr = 'tmp.tar_pr_%s' % self.uid
        self.table_pr_hr = f'{self.kwargs["schema"]}.pr_hr'
        self.create_index(engine_daneb, self.table_pr, self.single_pr)
        self.create_index(engine_daneb, self.table_pr_hr, self.single_pr)
        query_sql = """
                create table {table_name_pr_hr} as
                select {query_sm_cols} ,t2.*, t1.nr_opk_pr, t1.czas_pr
                from {table_pr} t1 inner join {table_pr_hr} t2 on {pr_hr_join}
                 inner join {query_sm_table_name} t3 on {query_sm_join}
        """.format(**self.__dict__)
        self.execute_query(engine_daneb, query_sql)
        self.tar_pr_hr = pd.read_sql('select * from %s' % self.table_name_pr_hr, engine_daneb)
        self.tar_pr_hr = self.ensure_dtypes(self.tar_pr_hr)
        self.tar_pr_hr.columns = [i.lower() for i in self.tar_pr_hr]

    def prepare_pr_hr(self):
        """Prepares raw pr_hr df from database for further proceedings. Unifies units and adds related FK
        data (kat_med, kat_opk).
        """
        # mapping are needed to change dictionary names (eg WYN_H_LEK) for human verbose name (LEKARZ).
        # Dictionary names are specified in HR dict by FK team

        # Mapowanie potrzebne do pobierania odp. pól z slow HR

        mappings = {'WYN_H_DIET': 'DIETETYK',
                    'WYN_H_LEKARZ': 'LEKARZ',
                    'WYN_H_LEKARZ_ANESTEZJOLOG': 'LEKARZ_ANESTEZJOLOG',
                    'WYN_H_LOGOP': 'LOGOPEDA',
                    'WYN_H_PERF': 'PERFUZJONISTA',
                    'WYN_H_PIELEG': 'PIELEGNIARKA',
                    'WYN_H_PIELEG_ANESTEZJOLOG': 'PIELEGNIARKA_ANESTEZJOLOGICZNA',
                    'WYN_H_PIELEG_BLOK': 'INSTRUMENTARIUSZKA',
                    'WYN_H_POZOST_MED': 'POZOSTALY_MEDYCZNY',
                    'WYN_H_POZOST_NMED': 'POZOSTALY_NIEMEDYCZNY',
                    'WYN_H_REZYDENT': 'REZYDENT',
                    'WYN_H_PSYCH': 'PSYCHOLOG',
                    'WYN_H_REHAB': 'REHABILITANT',
                    'WYN_H_TECHNIK': 'TECHNIK',
                    }
        # prepares table
        df = self.tar_pr_hr
        # converts time into decimal

        # TODO sprawdzić czy te 2 metody będize można w przyszłości zamienić na widok w DB
        # przykla: SELECT czas_jednego_hr, HOUR (czas_jednego_hr) *60 , MINUTE (czas_jednego_hr) FROM tmp.tar_pr_hr_59cf77a008f07d9ee687ab951122015c

        df['czas_jednego_hr_int'] = df['czas_jednego_hr'].apply(self.calc_time)
        # calculates total time spent by this hr on procedure
        # if there are more than one hr listed, total time increased appropriately
        df['czas_hr'] = df['czas_jednego_hr_int'] * df['ilosc_hr']
        # adds mapping of column WYN_H to personnel name
        slo_wyn_h_to_name = pd.DataFrame([mappings.keys(), mappings.values()]).T
        slo_hr_names = self.slo_hr.merge(slo_wyn_h_to_name, left_on='słownik_fk', right_on=0, how='left')
        # checks if not matched rows are only those with question marks
        slo_hr_names_not_matched = slo_hr_names[slo_hr_names[0].isnull()]
        # handles questing marks in hr dict
        if slo_hr_names_not_matched['słownik_fk'].str.contains(r'\?').any():
            names_from_analysis = df[['kod_sw', 'nazwa_hr', 'nr_opk_hr']].drop_duplicates()
            names_to_dump = \
            names_from_analysis.merge(slo_hr_names_not_matched, left_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr'],
                                      right_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw'])[
                ['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw',
                 'słownik_fk']].drop_duplicates()

            self.messages['errors'].append("Słownik hr jest niepełny, brakujące kategorie personelu znajduja się w " +
                                           "zakresie funkcji w zmiennej) slo_hr_names_not_matched. Personel bez przypisania:\n%s"
                                           % names_to_dump.to_dict(orient='index'))

        # check rownumeq to find if rows are not multiplied by key
        self.rownumeq(self.slo_hr, slo_hr_names, msg='Pr_hr*slo_hr names multiplied by key')
        # maps hr dict to raw hr data
        df_slo = df.merge(slo_hr_names, left_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr'],
                          right_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw'], validate='m:1', how='inner')
        # cleans df with proper hr names
        df_slo = df_slo.drop(columns=['nazwa_hr_x', 'nazwa_hr_y', 'kat_med', 'kat_opk', 'kat_med_swd']) \
            .rename(columns={0: 'payment_column', 1: 'nazwa_hr'})

        # exception below raises because slo_hr_names doesnt contain all required personnel names
        # slo_hr dict needs update
        try:
            self.rownumeq(df, df_slo, "Słownik HR jest niepełny, lub zawiera personel bez prawidłowego przypisania "
                          + "(np. ze znakiem zapytania w słowniku).",
                          permissive=self.permissive)
        except ShapesDoesntMatch as e:
            df_slo = df.merge(slo_hr_names, left_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr'],
                              right_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw'], validate='m:1', how='outer')
            df_slo_not_matched = df_slo[df_slo[0].isnull()]
            raise e
        # adds fk to include kat_med kat opk
        df_slo_fk = df_slo.merge(self.fk_class.slo_opk, left_on=['kod_sw', 'nr_opk_hr'], right_on=['kod_sw', 'nr_opk'],
                                 validate='m:1')
        # drops columns with cost information to ensure those are not used further
        unused_cols = [i for i in df_slo_fk.columns if any(map(lambda x: x in i, ['wyn', 'koszt', 'infrast']))]

        # Usuwamy nieuzywane kolumny, by przy procedurach B, C nie pojawiały się problemy, bo nie zawsze w fk sa one przypisane.
        df_slo_fk = df_slo_fk.drop(columns=unused_cols)
        # nobs in df_slo_fk is lower then in df_slo, because not every personnel has
        # fk assigned (there are problems  with B and C types)
        df_slo_fk = df_slo_fk.drop(columns=['nr_opk'])  # usuwa kolumne dla porzadku
        # returns clean hr with translated names and added costs
        return df_slo_fk

    # Funkcja pomocnicza, poprawiająca źle wpisany personel medyczny
    def change_anest_opk(self, df_slo):
        """If kat_med or kat_opk of opk is anaesthesiology, change personnel for anaesthesiologists."""
        # change anesthesiologists opks to anest hat med and opk
        df_slo['kat_med'].mask(  # warunek,wartosc orginalna jezeli falsz, wpisana jeżeli prawda
            ((df_slo['nazwa_hr'] == 'LEKARZ_ANESTEZJOLOG') & (df_slo['kat_med'] != '18')), '43', inplace=True)
        df_slo['kat_opk'].mask(  # warunek,wartosc jezeli falsz
            ((df_slo['nazwa_hr'] == 'LEKARZ_ANESTEZJOLOG') & (df_slo['kat_med'] != '18')), '1', inplace=True)
        df_slo['kat_med'].mask(  # warunek,wartosc jezeli falsz
            ((df_slo['nazwa_hr'] == 'PIELEGNIARKA_ANESTEZJOLOGICZNA') & (df_slo['kat_med'] != '18')), '43',
            inplace=True)
        df_slo['kat_opk'].mask(  # warunek,wartosc jezeli falsz
            ((df_slo['nazwa_hr'] == 'PIELEGNIARKA_ANESTEZJOLOGICZNA') & (df_slo['kat_med'] != '18')), '1', inplace=True)
        df_slo['kat_med'].mask(  # warunek,wartosc jezeli falsz
            ((df_slo['nazwa_hr'] == 'INSTRUMENTARIUSZKA') & (df_slo['kat_med'] != '18')), '43', inplace=True)
        df_slo['kat_opk'].mask(  # warunek,wartosc jezeli falsz
            ((df_slo['nazwa_hr'] == 'INSTRUMENTARIUSZKA') & (df_slo['kat_med'] != '18')), '1', inplace=True)
        return df_slo

    def create_pers_infrast_wagi_czas(self):
        """Responsible for creating tables with HR related information (time, infrast etc) for ABC.xlsx.
         Tables which are used in Excel file are commented with #abc hook. Those tables are then used to set params in
        analysis and rerun calculations.
        """
        # prepares pr_hr for ruther analysis, check in docstrings
        df_slo = self.prepare_pr_hr()
        # if medical event occurs at anaesthesiology ward personnel names are changed
        # further description in docstrings
        df_slo = self.change_anest_opk(df_slo)
        # defines personel distinct group for later aggregations
        self.personel_distinct_groups = self.kwargs['case_group'] + self.unit_id + ['nazwa_hr', 'kat_med', 'kat_opk']
        # defines procedure unit
        self.pr_a_unit = list(set(
            ['kod_ow', 'kod_sw', 'nr_ks', 'icd_9', 'nazwa_pr', 'nr_opk_pr', 'data_wyk', 'nr_ks_pr'] + self.kwargs[
                'case_group'] + ['kat_med', 'kat_opk']))
        # create tables with weights from diffrents opks
        df_slo = df_slo.assign(count=1)
        pr_hr_pers_wagi = df_slo.groupby(self.personel_distinct_groups + ['nr_opk_hr'])['count'].count().reset_index()
        self.pr_hr_pers_wagi = pr_hr_pers_wagi.rename(columns={'count': 'PERSONEL_ZABIEG_LICZBA'})
        # abc hook
        # defines opks for personnel groups who did procedure
        self.pr_hr_pers_wagi = self.add_opk_name(self.pr_hr_pers_wagi)  # pr_hr_pers czas
        # first grouping is used to mitigate situation where there are two the same nazwa_hr rows for one proc unit
        # groupby sums it to make distinct rows for every nazwa_hr
        self.pr_hr_pers_czas = df_slo.groupby(self.pr_a_unit + ['nazwa_hr'])['czas_hr'].sum().reset_index()
        # calculates mean from every distinct hr assigned to realisation of procedure
        # returns df with mean time for personel_disinct groups
        self.pr_hr_pers_czas = self.pr_hr_pers_czas.groupby(self.personel_distinct_groups)[
            'czas_hr'].mean().reset_index()
        # abc hook
        # contains info about time spent on procedure
        self.pr_hr_pers_czas = self.add_opk_name(self.pr_hr_pers_czas)
        # pr-hr infras wagi
        # list of cols created with set to deduplicate entires in list
        groupby_cols = list(set(self.kwargs['case_group'] + self.unit_id + ['nr_opk_pr', 'kat_med', 'kat_opk']))
        # create df with kat_med, kat_opk, its needed for later kat_med, kat_opk assignin
        pre_pr_hr_infras_wagi = self.tar.merge(self.fk_class.slo_opk, left_on=['kod_sw', 'nr_opk_pr'],
                                               right_on=['kod_sw', 'nr_opk'])
        pr_hr_infras_wagi = pre_pr_hr_infras_wagi.groupby(groupby_cols)[
            'ilosc_pr'].sum().reset_index()
        self.pr_hr_infras_wagi = pr_hr_infras_wagi.rename(columns={'ilosc_pr': 'LICZBA_OPK_PR'})
        # abc hook
        # creates summarisation of opks which are necessary for weights calculations
        self.pr_hr_infras_wagi = self.add_opk_name(self.pr_hr_infras_wagi)
        # converts time to int (str formated "HH:MM" in source data)
        self.tar['czas_pr_int'] = self.tar['czas_pr'].apply(self.calc_time)
        # calculates mean procedure duration (for infrastructure calculations)
        pr_hr_infras_czas = self.tar.groupby(self.kwargs['case_group'] + self.unit_id)[
            'czas_pr_int'].mean().reset_index()
        self.pr_hr_infras_czas = pr_hr_infras_czas.rename(columns={'czas_pr_int': 'avg_czas_pr_int'})
        # abc hook
        # final procedure duration
        self.pr_hr_infras_czas = self.add_opk_name(self.pr_hr_infras_czas)

    def assign_pr_hr_hourly_rates(self):
        """Assignes hourly rate for group of personnel to grouping variable."""

        def calc_avg_wyn_h_mean_weights(df, groups, col, substr):
            """Calcualtes mean wyn_h for groups of personel. Ie calcs mean of nurse across all opks engages in procedure.

             Returns df with wyn_h_mean as weighted average cost of hour of work all hrs from diffrent opks."""
            df_filtered = df[df['nazwa_hr'].str.upper().str.contains(substr)]
            df1 = df_filtered.groupby(
                groups).apply(
                lambda x: np.average(x[col], weights=x['PERSONEL_ZABIEG_LICZBA'])).reset_index()
            df2 = df1.rename(columns={0: 'wyn_h_mean'})
            return df2.reset_index()

        # assign costs from based on kod_sw presence in grouping
        if 'kod_sw' not in self.kwargs['case_group']:
            pr_hr_pers_wagi_wyn_h = self.pr_hr_pers_wagi.merge(self.fk, on=['kat_med', 'kat_opk'], validate='m:1')
        else:
            pr_hr_pers_wagi_wyn_h = self.pr_hr_pers_wagi.drop(columns=['kat_med', 'kat_opk']
                                                              ).merge(self.fk, left_on=['kod_sw', 'nr_opk_pr'],
                                                                      right_on=['kod_sw', 'nr_opk'], validate='m:1')

        # potencjalne miejsce na nową funkcjonalność Uli C
        # zasady merga:
        # 1. wprost z danych szpitala
        # 2. lekarze, pielegniarki:
        #     1.przypisanie sredniej na kat me di kat opk tego personelu
        # 2. Psych, diet etc:
        #     1.przypisanie wyn_h_pozost_med w pliku FK, z tego samego OPK
        #     2. Jeżeli nie to srednia z db na ketmed kat opk (?srednia ktora nie uwzglednia zer?)

        personel = []
        for i in (('wyn_h_lekarz', 'LEKARZ'),
                  ('wyn_h_pieleg', 'PIEL'),
                  ('wyn_h_pozost_med', 'POZOST'),
                  ('wyn_h_pozost_nmed', 'INNY'),
                  ('wyn_h_diet', 'DIETETYK'),
                  ('wyn_h_logop', 'LOGOPEDA'),
                  ('wyn_h_perf', 'PERFUZJONISTA'),
                  ('wyn_h_pieleg', 'INSTRUMENTARIUSZKA'),
                  ('wyn_h_rezydent', 'REZYDENT'),
                  ('wyn_h_psych', 'PSYCHOLOG'),
                  ('wyn_h_rehab', 'REHABILITANT'),
                  ('wyn_h_technik', 'TECHNIK'),
                  ('wyn_h_terap_zaj', 'TERAPEUTA_ZAJECIOWY'),
                  ('wyn_h_fiz_med', 'FIZ_MED'),):
            personel.append(
                calc_avg_wyn_h_mean_weights(pr_hr_pers_wagi_wyn_h, self.personel_distinct_groups, i[0], i[1]))

        personel_wyn_h_all = pd.concat(personel, sort=False).sort_values(self.personel_distinct_groups)
        assert personel_wyn_h_all.shape[0] <= pr_hr_pers_wagi_wyn_h.shape[0], 'Error in assinging pr_hr prices'
        assert personel_wyn_h_all.shape[0] == \
               pr_hr_pers_wagi_wyn_h[self.personel_distinct_groups].drop_duplicates().shape[
                   0], 'Error in assinging pr_hr prices'
        return personel_wyn_h_all

    def calc_pr_hr_costs(self):
        """Calculates hr costs in procedure."""
        personel_wyn_h_all = self.assign_pr_hr_hourly_rates()
        # merges time with salaries
        personel_costs = personel_wyn_h_all.merge(self.pr_hr_pers_czas, on=self.personel_distinct_groups,
                                                  validate='1:1')
        personel_costs['koszt_hr_pr_a'] = personel_costs['czas_hr'] * personel_costs['wyn_h_mean']
        personel_costs_sum = personel_costs.groupby(self.kwargs['case_group'] + self.unit_id)[
            'koszt_hr_pr_a'].sum().reset_index()

        ## add infrastructure cost data
        if 'kod_sw' not in self.kwargs['case_group']:
            pr_hr_infras_wagi = self.pr_hr_infras_wagi.merge(self.fk, on=['kat_med', 'kat_opk'], validate='m:1')
        else:
            pr_hr_infras_wagi = self.pr_hr_infras_wagi.merge(self.fk, left_on=['kod_sw', 'nr_opk_pr'],
                                                             right_on=['kod_sw', 'nr_opk'], validate='m:1')

        # calculates weighted average of opks based on frequency in procedure
        pr_hr_infras_wagi = pr_hr_infras_wagi.groupby(self.kwargs['case_group'] + self.unit_id).apply(
            lambda x: np.average(x['infrast_odt_h_bloku'], weights=x['LICZBA_OPK_PR'])).reset_index()
        pr_hr_infras_wagi = pr_hr_infras_wagi.rename(columns={0: 'mean_h_infrast'})

        pr_hr_infras_sum = pr_hr_infras_wagi.merge(self.pr_hr_infras_czas, on=self.kwargs['case_group'] + self.unit_id,
                                                   validate='1:1')
        pr_hr_infras_sum['koszt_infrast_pr_a'] = pr_hr_infras_sum['mean_h_infrast'] * pr_hr_infras_sum[
            'avg_czas_pr_int']
        pr_hr_infras_sum = pr_hr_infras_sum.drop(columns=['mean_h_infrast', 'avg_czas_pr_int', ])
        # calculates final cost
        pr_hr_infras_sum = self.ensure_dtypes(pr_hr_infras_sum)
        personel_costs_sum = self.ensure_dtypes(personel_costs_sum)
        pr_hr_sum = pr_hr_infras_sum.merge(personel_costs_sum, on=self.kwargs['case_group'] + self.unit_id,
                                           validate='1:1')
        pr_hr_sum['koszt_pr_a'] = pr_hr_sum['koszt_infrast_pr_a'] + pr_hr_sum['koszt_hr_pr_a']

        if 'opk_nazwa' in pr_hr_sum.columns:
            # executes for grouping which includes kod_sw
            self.pr_hr_sum = pr_hr_sum.drop(columns=['opk_nazwa'])
        else:
            self.pr_hr_sum = pr_hr_sum

    def calc_from_pricelist(self):
        """Calculates pricelist in groups, the higher the number, the lower priority it has.
        """
        self.create_pricelist()
        b0 = self.raw_pricelist
        b0 = b0[b0['koszt_cp'] != 0]
        b0 = b0[b0['ilosc_cp'] != 0]
        pr_levels = OrderedDict((
            (1, {'groupby_cols': ['kod_sw']}),
            (2, {'groupby_cols': []}),
        ))

        for i in pr_levels:
            groupby = self.pricelist_col_names + pr_levels[i]['groupby_cols']
            b1 = self.del_outliers_with_boxplot(b0, 'koszt_cp', groupby, weights='ilosc_cp')
            df1 = b1.groupby(
                groupby).apply(
                lambda x: np.average(x['koszt_cp']
                                     )).reset_index()
            df1 = df1.rename(columns={0: 'koszt_cp'})
            pr_levels[i]['df'] = df1
        self.pricelist_prices = pr_levels

    def add_cp_prices(self):
        """Adds prices from PR pricelist (CP) for every procedure which has price in CP. Code is using
        pr_levels defined in PrCalc.calc_from_pricelist method which is responsible for prices priority.
        See docs for more info.
        """
        tar_sr_il_cp_parts = []
        internal_sr_il = self.tar_sr_il
        tar_sr_il_cols = set(self.tar_sr_il.columns)
        for i in self.pricelist_prices:
            groupby_cols_set = set(self.pricelist_prices[i]['groupby_cols'])
            intersection = groupby_cols_set & tar_sr_il_cols
            if intersection == groupby_cols_set:
                tar_sr_il_partial_prices = internal_sr_il.merge(self.pricelist_prices[i]['df'],
                                                                how='left',
                                                                left_on=self.file_prices + self.pricelist_prices[i][
                                                                    'groupby_cols'],
                                                                right_on=self.pricelist_col_names +
                                                                         self.pricelist_prices[i]['groupby_cols'],
                                                                validate='m:1')
                internal_sr_il = tar_sr_il_partial_prices[tar_sr_il_partial_prices['koszt_cp'].isnull()].drop(
                    columns=['koszt_cp'])
                tar_sr_il_cp_parts.append(tar_sr_il_partial_prices[tar_sr_il_partial_prices['koszt_cp'].notnull()])
        tar_sr_il = pd.concat(tar_sr_il_cp_parts + [internal_sr_il], sort=False).reset_index(drop=True)
        self.rownumeq(tar_sr_il, self.tar_sr_il, msg='Błąd przy dodawaniu cen z CP, cena dodana ' +
                                                     'zbyt wiele razy')
        self.tar_sr_il = tar_sr_il

    def add_pr_a_prices(self):
        tar_sr_il = self.tar_sr_il
        # deletes cost cols to add new ones if abc is refreshed
        cost_cols = [i for i in tar_sr_il.columns if 'koszt' in i and 'pr_a' in i]
        if cost_cols:
            tar_sr_il = tar_sr_il.drop(columns=cost_cols)
        tar_sr_il = tar_sr_il.merge(self.pr_hr_sum, on=self.kwargs['case_group'] + self.unit_id, how='left')
        self.tar_sr_il = tar_sr_il

    def assign_prices_to_abc(self):
        """Assignes prices from pricelists or from PR_HR calculations based on ABC categories."""
        self.tar_sr_il['abc'] = self.tar_sr_il['abc'].str.upper()
        self.tar_sr_il['koszt_do_analizy'] = np.NaN
        mask_proc_a = self.tar_sr_il['abc'] == 'A'
        self.tar_sr_il['koszt_do_analizy'].mask(mask_proc_a, self.tar_sr_il['koszt_pr_a'], inplace=True)
        mask_proc_c = (self.tar_sr_il['abc'] == 'C') | (
                (self.tar_sr_il['koszt_do_analizy'].isnull()) & mask_proc_a)
        self.tar_sr_il['koszt_do_analizy'].mask(mask_proc_c, self.tar_sr_il['koszt_cp'], inplace=True)
        self.tar_sr_il['koszt_do_analizy'].mask(self.tar_sr_il['koszt_do_analizy'].isnull(), 0, inplace=True)

    def generate_event_cost(self):
        """Calculates cost of medical event."""
        super(PrCalc, self).generate_event_cost()
        self.tar_sr_il['koszt_zdarzenia'] = self.tar_sr_il['koszt_do_analizy'] * self.tar_sr_il['sr_wyst_w_przyp']
        self.summarize_event_costs()

    def calc_tariff(self):
        """Calculates tariff for PR."""
        groupby_cols = (self.kwargs['case_group'] + ['abc'])
        proc_by_abc = self.tar_sr_il.groupby(groupby_cols)['koszt_zdarzenia'].sum().reset_index(
            name="suma_%s" % self.table_type).set_index(groupby_cols)
        proc_unstacked = proc_by_abc.unstack().reset_index()
        new_cols = ['{}_{}'.format(i, j) if
                    j else '{}'.format(i) for i, j in
                    zip(proc_unstacked.columns.get_level_values(0), proc_unstacked.columns.get_level_values(1))]
        proc_unstacked.columns = new_cols
        sum_proc = self.tar_sr_il.groupby(self.kwargs['case_group'])['koszt_zdarzenia'].sum().reset_index(
            name="suma_%s" % self.table_type).set_index(self.kwargs['case_group'])
        proc_all = proc_unstacked.merge(sum_proc, on=self.kwargs['case_group'])

        check = (proc_all['suma_pr'] - proc_all[[i for i in proc_all.columns if i in ['suma_pr_C', 'suma_pr_A']]].sum(
            axis=1))
        assert (round(check, 1) == 0).all()
        self.tariff = proc_all


