"""Main PyTar Workflow""" # Stary plik analytic_templates.wb17.py
#TODO ten plik, trzeba podpiąć do Django, który będzie do konfiguracji po przeniesieniu Django

import hashlib
import pathlib
from functools import reduce
import pandas as pd
from sqlalchemy import MetaData
from sqlalchemy import create_engine
# DO ZMIANY IMPORTY
from calc.base_calc import UtilTools
from calc.og import OgCalc
from calc.osd import FkSzcz
from calc.osd import SmCalc
from calc.plwm import WmCalc, PlCalc
from calc.pr import PrCalc
from calc.prepare_data import QuerySm ## Nie wiem czy wykorzystywane, dlatego na razie skomentowane, do weryfikacji przy testach rozruchowych
from dictionary.tariff_scheme import wb17
from nothing_important.helper import AbcExcel, TariffExcel
# from pytar_calc.tests.set_up_db import TestDB ##### Na razie nie uzywane, testy

class AnalyseData(): # w pierwotnej wersji PyTara było w klasie dziedziczenie TestDB
    """Main workflow."""

    def __init__(self, path, query_sm, **kwargs):
        self.path = path
        self.query_sm_str = query_sm
        self.uid = hashlib.md5(path.encode()).hexdigest()
        self.data_description = kwargs
        self.case_group = kwargs.get('case_group', ['kod_prod', 'kod_sw', 'nr_ks'])
        self.og = None

    def set_up(self):
        options = {'case_group': self.case_group,
                   'fake_data': False,
                   'path': self.path,
                   'schema': 'wb17',
                   'price_priority': 'cena_z_pliku' # okreslenie priorytetu ceny WM/PL
                   }

        wb17.update(options)
        self.data_description.update(wb17)
        self.query_sm = QuerySm(self.query_sm_str, self.uid, **self.data_description)
        self.fk = FkSzcz(**self.data_description, query_sm=self.query_sm)
        og = OgCalc('og', self.query_sm, self.uid, **self.data_description)
        og.create_tar()
        self.og = og

    def basic_wm(self):
        self.wm = WmCalc('wm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        self.wm.create_tar_sr_il()
        self.wm.calc_from_pricelist()
        self.wm.calc_from_unit_price()
        self.wm.add_pricelist()
        self.wm.add_unit_price()
        return None

    def basic_pl(self):
        self.pl = PlCalc('pl', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        self.pl.create_tar_sr_il()
        self.pl.calc_from_pricelist()
        self.pl.calc_from_unit_price()
        self.pl.add_pricelist()
        self.pl.add_unit_price()
        return None

    def basic_pr(self):
        self.pr = PrCalc('pr', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        self.pr.create_tar_sr_il_abc()
        self.pr.calc_from_pricelist()
        self.pr.add_cp_prices()
        self.pr.create_tar_pr_hr()
        self.pr.create_pers_infrast_wagi_czas()
        return None

    def generate_event_cost_wm(self):
        self.wm.generate_event_cost()
        return None

    def generate_event_cost_pl(self):
        self.pl.generate_event_cost()
        return None

    def generate_event_cost_pr(self):
        self.pr.calc_pr_hr_costs()
        self.pr.add_pr_a_prices()
        self.pr.assign_prices_to_abc()
        self.pr.generate_event_cost()
        return None

    def run_basic(self):
        for func in [self.basic_pl, self.basic_pr, self.basic_wm]:
            # run every basic fx
            func()
        self.analyse_osd()
        return None

    def generate_event_costs(self):
        for func in [self.generate_event_cost_pl, self.generate_event_cost_pr, self.generate_event_cost_wm]:
            # generate all event costs
            func()
        return None

    def generate_ABC(self):
        abc = AbcExcel(**self.__dict__)
        abc.write_excel()
        return None

    def prepare_tariffs(self):
        self.pr.calc_tariff()
        self.wm.calc_tariff()
        self.pl.calc_tariff()
        self.sm.calc_tariff()
        return None

    def join_tariffs(self):
        dfs = [self.pr.tariff, self.pl.tariff, self.wm.tariff, self.sm.tariff]
        dfs = list(map(lambda x: UtilTools.ensure_dtypes(x), dfs))
        self.tariff = reduce(lambda left, right: pd.merge(left, right, on=self.data_description['case_group']), dfs)
        summary_cols = ['suma_pr', 'suma_pl', 'suma_wm', 'koszt_osd']
        tariff_total = self.tariff[summary_cols].sum(axis=1)
        tariff_total.name = 'taryfa'
        self.tariff = self.tariff.join(tariff_total)
        return None

    def join_additional_data(self):
        cols_to_add = ['wiek', 'czas_hosp']
        if 'nr_ks' in self.data_description['case_group']:
            cols_to_add.extend(['tr_przyj', 'tr_wyp',])
        og_data = self.og.og[self.data_description['case_group'] + cols_to_add]
        self.tariff = self.tariff.merge(og_data, on=self.data_description['case_group'])
        return None

    def calc_tariffs(self):
        self.prepare_tariffs()
        self.join_tariffs()
        self.join_additional_data()
        return None

    def analyse_osd(self):
        self.sm = SmCalc('sm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        self.sm.create_tar()
        self.sm.filter_opks()
        self.sm.osd_with_intra_hosp_migrations()
        return None

    def write_tariff(self):
        tariff = TariffExcel(**self.__dict__)
        tariff.write_excel()
        return None

    def del_obsolete_tables(self):
        dbconnector = 'pymysql'
        engine_tmp = create_engine('mysql+%s://daneb:QazWsx1324@aotmitsassrv1:3306/tmp' % dbconnector, pool_pre_ping=True)
        metadata = MetaData(engine_tmp)
        metadata.reflect(engine_tmp)
        tables_to_drop = [i for i in metadata.tables if self.uid.lower() in i]
        for i in tables_to_drop:
            metadata.tables[i].drop()
        return None

    def dump_messages(self):
        any_msgs = any(map(lambda x: getattr(x, 'messages', None), [self.pl, self.wm, self.pr]))
        if any_msgs:
            with open(self.path + '\\messages.txt', 'w') as file:
                for i in [self.pl, self.wm, self.pr, self.fk, self.sm]:
                    for j in i.messages:
                        file.write("{0}:{1}:{2}\n".format(i.table_type, j, i.messages[j]))
        return None

    def main(self):
        # creates Path object for ABC.xlsx
        path = pathlib.Path(self.path)
        abc = path.joinpath('ABC.xlsx')
        # checks if abc file exists in dir to clean database
        # useful when resetting analysis (new analysis in the same path)
        if not abc.exists():
            # deletes tables which are not relevant anymore
            self.del_obsolete_tables()
        # sets up basic tables required for further analysis
        self.set_up()
        # runs all basic classes to prepare file with parameters -  ABC.xlsx
        self.run_basic()
        # loads ABC.xlsx to patch analytics objects with custom data
        if abc.exists():

            abc_contents = pd.read_excel(abc, sheet_name=None, index_col=0)
            self.pl.tar_sr_il = abc_contents['PL']
            self.wm.tar_sr_il = abc_contents['WM']
            self.pr.tar_sr_il = abc_contents['PR']
            self.pr.pr_hr_pers_wagi = abc_contents['PR_HR_PERS_WAGI']
            self.pr.pr_hr_pers_czas = abc_contents['PR_HR_PERS_CZAS']
            self.pr.pr_hr_infras_wagi = abc_contents['PR_HR_INFRAS_WAGI']
            self.pr.pr_hr_infras_czas = abc_contents['PR_HR_INFRAS_CZAS']
            self.pr.nr_ks_odrzucone = abc_contents['NR_KS_ODRZUCONE']
            for scope in [self.pr, self.wm, self.pl]:
                setattr(scope, 'fk', abc_contents['BAZA_FK'])
        self.generate_event_costs()
        self.generate_ABC()
        self.calc_tariffs()
        self.write_tariff()
        self.dump_messages()
        return None