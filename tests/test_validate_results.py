import unittest
from unittest import mock

import pandas as pd
from sqlalchemy import MetaData

from pytar_calc.calc.og import OgCalc
from pytar_calc.calc.plwm import WmCalc, PlCalc
from pytar_calc.calc.pr import PrCalc
from pytar_calc.calc.start import QuerySm
from pytar_calc.models.daneb import engine_tmp
from pytar_calc.calc.osd import FkSzcz
from pytar_calc.calc.osd import SmCalc
from pytar_calc.shared.data_descriptions import wb17
from pytar_calc.tests.external_data import fk_df
from pytar_calc.tests.set_up_db import TestDB
import random

class FkMock:
    pass


class TestTariffNaPacjenta(TestDB):
    """Test of main workflow.
    """
    DEBUG = True
    options = {'case_group': ['kod_prod', 'kod_sw', 'nr_ks'],
               'path': r'T:\organizacyjne_robocze\tmp\pytar_test',
               'schema': 'wb17',
               'price_priority': 'cena_z_pliku'
               }
    wb17.update(options)
    data_description = wb17
    uid = '%s' % random.randint(0,9999999)
    query_sm_sql_query = f"""
        create table %s as
        select t1.nr_ks, t1.kod_sw, t1.kod_prod, '1' as kod_dod
        from {options['schema']}.sm t1 inner join {options['schema']}.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks
        where kod_prod like "5.51.01.0005047"
"""

    fk = FkMock()
    fk.fk_szcz = fk_df
    fk.fk = fk_df


    @classmethod
    def setUpClass(cls):
        query_sm = QuerySm(cls.query_sm_sql_query, cls.uid, **cls.data_description)
        og = OgCalc('og', query_sm, cls.uid, **cls.data_description)
        og.create_tar()
        cls.query_sm = query_sm
        cls.og = og
        if cls.options['schema'] == 'wb17':
            cls.fk = FkSzcz(**cls.data_description, query_sm=cls.query_sm)

    @classmethod
    def tearDownClass(cls):
        if not cls.DEBUG:
            metadata = MetaData(engine_tmp)
            metadata.reflect(engine_tmp)
            tables_to_drop = [i for i in metadata.tables if cls.uid.casefold() in i]
            for i in tables_to_drop:
                metadata.tables[i].drop()

    def test_wm(self):
        wm = WmCalc('wm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        wm.create_tar()
        wm.calc_from_pricelist()
        wm.calc_from_unit_price()
        wm.create_tar_sr_il()
        sr_il_nobs = wm.tar_sr_il.shape[0]
        wm.add_pricelist()
        self.assertEqual(sr_il_nobs, wm.tar_sr_il.shape[0])
        wm.add_unit_price()
        self.assertEqual(sr_il_nobs, wm.tar_sr_il.shape[0])
        # dwie funkcje, które maja wplyw po zmianie wspolczynnikow
        wm.generate_event_cost()
        self.assertEqual(sr_il_nobs, wm.tar_sr_il.shape[0])
        wm.calc_tariff()
        if self.options['schema'] == 'test_daneb':
            self.assertEqual(wm.tariff.at[0, 'suma_wm'], 4.5, 'WM prices diffrent')
        del wm
        wm = WmCalc('wm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        dispatchers_commands_wm = ['create_tar', 'calc_from_pricelist', 'calc_from_unit_price', 'create_tar_sr_il',
                                   'add_pricelist', 'add_unit_price', 'generate_event_cost', 'calc_tariff', ]
        for i in dispatchers_commands_wm:
            _method = getattr(wm, i, None)
            _method()
        if self.options['schema'] == 'test_daneb':
            self.assertEqual(wm.tariff.at[0, 'suma_wm'], 4.5, 'WM prices diffrent')

    def test_pl(self):
        pl = PlCalc('pl', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        pl.create_tar()
        pl.create_tar_sr_il()
        sr_il_nobs = pl.tar_sr_il.shape[0]
        pl.calc_from_pricelist()
        self.assertEqual(sr_il_nobs, pl.tar_sr_il.shape[0])
        pl.add_pricelist()
        self.assertEqual(sr_il_nobs, pl.tar_sr_il.shape[0])
        pl.calc_from_unit_price()
        self.assertEqual(sr_il_nobs, pl.tar_sr_il.shape[0])
        pl.add_unit_price()
        self.assertEqual(sr_il_nobs, pl.tar_sr_il.shape[0])
        pl.generate_event_cost()
        self.assertEqual(sr_il_nobs, pl.tar_sr_il.shape[0])
        pl.calc_tariff()

    def test_pr(self):
        pr = PrCalc('pr', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        pr.create_tar()
        pr.create_tar_sr_il_abc()
        sr_il_nobs = pr.tar_sr_il.shape[0]
        pr.calc_from_pricelist()
        pr.add_cp_prices()
        self.assertEqual(sr_il_nobs, pr.tar_sr_il.shape[0])
        # PR_HR
        pr.create_tar_pr_hr()
        pr.create_pers_infrast_wagi_czas()
        pr.calc_pr_hr_costs()
        self.assertEqual(sr_il_nobs, pr.tar_sr_il.shape[0])
        pr.add_pr_a_prices()
        self.assertEqual(sr_il_nobs, pr.tar_sr_il.shape[0])
        pr.assign_prices_to_abc()
        self.assertEqual(sr_il_nobs, pr.tar_sr_il.shape[0])
        pr.generate_event_cost()
        self.assertEqual(sr_il_nobs, pr.tar_sr_il.shape[0])
        pr.tar_sr_il.to_excel(r'T:\organizacyjne_robocze\012_Taryfikator\test\pr.xlsx')

    def test_if_osd_calculates_without_exceptions(self):
        sm = SmCalc('sm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        sm.create_tar()
        sm.filter_opks()
        sm.osd_with_intra_hosp_migrations()
        print('')

    @mock.patch('pytar_calc.shared.helper.Freezer._freeze_df')
    def test_freeze(self, patch):
        wm = WmCalc('wm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        wm.create_tar()
        wm.create_tar_sr_il()
        wm.freeze('tar_sr_il')
        self.assertEqual(patch.call_count, 1)
        wm.freeze(['tar_sr_il', 'tar_sr_il'])
        self.assertEqual(patch.call_count, 3)

    def test_freeze_history(self):
        wm = WmCalc('wm', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
        num_of_files = len(list((wm.path / 'arch').glob('*')))
        data = {'var': [10, 1, 100, 1],
                'weights': [9, 100, 1, 9],
                'groups': ['g1', 'g1', 'g1', 'g2']
                }
        df = pd.DataFrame(data)
        wm.df = df
        wm.freeze('df')
        data = {'var': [101, 1, 100, 1],
                'weights': [9, 100, 1, 9],
                'groups': ['g1', 'g1', 'g1', 'g2']
                }
        df = pd.DataFrame(data)
        # in spite of two Freezer.freeze calls freezes one file instead of two because second call overrides first file
        wm.freeze('df')
        num_of_files_add_1 = len(list((wm.path / 'arch').glob('*')))
        self.assertEqual(num_of_files + 1, num_of_files_add_1)

if __name__ == '__main__':
    unittest.main()
