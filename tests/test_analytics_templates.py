import pathlib
import unittest

import pandas as pd

from pytar_calc.analytic_templates import wb17


class AnalyticsTeplatesWB17TestCase(unittest.TestCase):
    """Qsm must me real query (in specified schema) like query_sm to get data from db."""
    path = r'T:\organizacyjne_robocze\tmp\pytar_test'

    qsm  = """create table %s as select t1.nr_ks, t1.kod_sw, t1.kod_prod from wb17.sm t1 inner join wb17.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks where kod_prod like "5.51.01.0016006" limit 100"""


    AnalyticClass = wb17.AnalyseData

    def tearDown(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group=['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()


    def test_01_template_generates_abc(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()
        analysis.main()
        self.assertTrue(ABC.exists())

    def test_02_template_recalculates_event_costs_wsp_wsp_dni(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if not ABC.exists():
            analysis.main()
        # prepare excel
        abc = pd.read_excel(ABC, sheet_name=None, index_col=0)
        abc['PL']['wsp_dni'] = 3
        abc['PR']['wsp_dni'] = 3
        abc['WM']['wsp'] = 3
        excel_writer = pd.ExcelWriter(ABC.__str__(), engine='xlsxwriter')
        for k, v in abc.items():
            v.to_excel(excel_writer, sheet_name=k, index=True)
        excel_writer.save()
        analysis.main()
        self.assertTrue((analysis.pl.tar_sr_il['wsp_dni'] == 3).all())
        self.assertTrue((analysis.wm.tar_sr_il['wsp'] == 3).all())
        self.assertTrue(((analysis.wm.tar_sr_il['koszt_zdarzenia'] == abc['WM']['cena_do_analizy'] * 3)
                         | analysis.wm.tar_sr_il['koszt_zdarzenia'].isnull()).all())

    def test_abc_reassign_prices(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if not ABC.exists():
            #create abc with main process
            analysis.main()
        # prepare excel
        abc = pd.read_excel(ABC, sheet_name=None, index_col=0)
        abc['PR']['abc'] = 'C'
        excel_writer = pd.ExcelWriter(ABC.__str__(), engine='xlsxwriter')
        for k, v in abc.items():
            v.to_excel(excel_writer, sheet_name=k)
        excel_writer.save()
        analysis.main()
        self.assertTrue((analysis.pr.tar_sr_il['koszt_do_analizy'] == analysis.pr.tar_sr_il['koszt_do_analizy']).all())
        analysis.pr.tar_sr_il['abc'] = 'A'
        analysis.generate_event_cost_pr()

    def test_pr_grp(self):
        """Test grp wsp on pr file."""
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        analysis.set_up()
        analysis.basic_pr()
        # check gr_wsp
        nr_ks = analysis.pr.tar_sr_il.at[4, 'nr_ks']
        analysis.pr.tar_sr_il['grupa'] = analysis.pr.tar_sr_il['grupa'].mask(analysis.pr.tar_sr_il['nr_ks'] == nr_ks,
                                                                             'g1')
        analysis.pr.tar_sr_il['gr_wsp'] = analysis.pr.tar_sr_il['grupa'].mask(analysis.pr.tar_sr_il['nr_ks'] == nr_ks,
                                                                              1)
        analysis.generate_event_cost_pr()
        new_tar_sr_il = analysis.pr.tar_sr_il[analysis.pr.tar_sr_il['nr_ks'] == nr_ks]
        self.assertTrue((new_tar_sr_il['sr_wyst_w_przyp'] < 1).all(),
                        'Przeliczanie wsp grupowych nie działa prawidłowo')

    def test_pr_grp_dni(self):
        """Test grp wsp_dni on pr file."""
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        analysis.set_up()
        analysis.basic_pr()
        # check gr_wsp_dni
        nr_ks_2 = analysis.pr.tar_sr_il.at[7, 'nr_ks']
        analysis.pr.tar_sr_il['grupa'] = analysis.pr.tar_sr_il['grupa'].mask(
            analysis.pr.tar_sr_il['nr_ks'] == nr_ks_2,
            'g1')
        analysis.pr.tar_sr_il['gr_wsp_dni'] = analysis.pr.tar_sr_il['grupa'].mask(
            analysis.pr.tar_sr_il['nr_ks'] == nr_ks_2,
            1)
        analysis.generate_event_cost_pr()
        new_tar_sr_il = analysis.pr.tar_sr_il[analysis.pr.tar_sr_il['nr_ks'] == nr_ks_2]
        self.assertTrue((new_tar_sr_il['sr_wyst_w_przyp'] / new_tar_sr_il['czas_hosp'].astype(int) < 1).all(),
                        'Przeliczanie wsp grupowych nie działą prawidłowo')

    def test_if_abc_enables_baza_fk_parameters_no_proxy_excel(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        analysis.set_up()
        analysis.basic_pr()
        analysis.generate_event_cost_pr()
        pra_1 = analysis.pr.tar_sr_il.koszt_pr_a
        analysis.pr.fk['infrast_odt_h_bloku'] = 9999990
        analysis.generate_event_cost_pr()
        pra_2 = analysis.pr.tar_sr_il.koszt_pr_a
        self.assertTrue((pra_1 != pra_2).all())
        analysis.fk.fk['infrast_odt_h_bloku'] = 0.000001
        analysis.generate_event_cost_pr()
        pra_3 = analysis.pr.tar_sr_il.koszt_pr_a
        pra_comb = pra_1 != pra_2
        self.assertTrue((pra_comb != pra_3).all())
        self.assertTrue((pra_1 != pra_3).all())

    def test_if_abc_enables_baza_fk_params_with_excel(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if not ABC.exists():
            analysis.main()
        # prepare excel
        abc = pd.read_excel(ABC, sheet_name=None, index_col=0)
        abc['BAZA_FK']['infrast_odt_h_bloku'] = 999999999999
        excel_writer = pd.ExcelWriter(ABC.__str__(), engine='xlsxwriter')
        for k, v in abc.items():
            v.to_excel(excel_writer, sheet_name=k, index=True)
        excel_writer.save()
        analysis.main()
        pr_a_1 = analysis.pr.tar_sr_il['koszt_pr_a']
        # check if any of pra have very big values
        self.assertTrue(pr_a_1[pr_a_1>1000000].count()>1)

    def test_tariff(self):
        analysis = self.AnalyticClass(self.path, self.qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        analysis.set_up()
        analysis.run_basic()
        analysis.generate_event_costs()
        analysis.calc_tariffs()
        analysis.write_tariff()

    def test_if_works_just_fine_na_pacjenta(self):
        analysis = self.AnalyticClass(self.path, self.qsm, permissive=True,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'])
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()
        analysis.main()

    def test_if_it_works_on_jgp_swd_level(self):
        analysis = self.AnalyticClass(self.path, self.qsm, permissive=True,
                                      case_group=['kod_prod', 'kod_sw'])
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()
        analysis.main()

    def test_if_it_works_on_jgp_level(self):
        analysis = self.AnalyticClass(self.path, self.qsm, permissive=True,
                                      case_group=['kod_prod'])
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()
        analysis.main()


class AnalyticalCasesWB17TestCase(unittest.TestCase):
    """Qsm must me real query (in specified schema) like query_sm to get data from db."""
    path = r'T:\organizacyjne_robocze\tmp\pytar_test'

    AnalyticClass = wb17.AnalyseData

    def setUp(self):
        qsm=''
        analysis = self.AnalyticClass(self.path, qsm,
                                      case_group=['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()


    def test_error_wb17_for_C29_code_just_works(self):
        qsm = """create table %s as select t1.nr_ks, t1.kod_sw, t1.kod_prod from wb17.sm t1 inner join wb17.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks where kod_prod like "5.51.01.0016006" """
        analysis = self.AnalyticClass(self.path, qsm,
                                      case_group = ['kod_prod', 'kod_sw', 'nr_ks'], permissive=True)
        ABC = pathlib.Path(analysis.path).joinpath('ABC.xlsx')
        if ABC.exists():
            ABC.unlink()
        analysis.main()
        self.assertTrue(ABC.exists())