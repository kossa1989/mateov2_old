

def e(df):
    import time
    work = r'C:\Users\m.marczak\Documents\anitko\17lip'
    df.to_excel(work +r'\zb_%s.xlsx' % time.time())


from functools import reduce
import pandas as pd
from calc.osd import SmCalc, FkSzcz
from calc.plwm import WmCalc, PlCalc
from calc.og import OgCalc
from calc.pr import PrCalc

from calc.prepare_data import query_sm_sql_query, QuerySm # nieuzywane data_description,uid,
from excelfile.excel_file_class import AbcExcel, TariffExcel
# fk musi być zdefiniowaną zmienną w środowisku

#male zmiany data_description
from dictionary.tariff_scheme import wb17


# data_description['path'] = ''

data_description = wb17 # import danych z tariff_scheme
query_sm = QuerySm(query_sm_sql_query,uid, **data_description)


class CalcTariff():
    def __init__(self, query_sm, dfs = None):
        self.dfs = dfs
        self.query_sm = query_sm

        self.calc_tariff(self.query_sm)

    def calc_tariff(self, query_sm):
        og = OgCalc('og', query_sm, uid, **data_description)
        og.create_tar()
        fk = FkSzcz(**data_description)

        if not self.dfs:
            pr = PrCalc('pr', query_sm, uid, og=og.og, fk=fk,**data_description)
            pr.create_tar()
            pr.create_tar_sr_il_abc()
            pr.tar.head()
            pr.create_tar_pr_hr()
            pr.create_pers_infrast_wagi_czas()
            pr.calc_from_pricelist()
            pr.calc_pr_hr_costs()
            pr.add_cp_prices()
            pr.add_pr_a_prices()
            # dwie funkcje, które maja wplyw po zmianie wspolczynnikow
            pr.assign_prices_to_abc()
            pr.generate_event_cost()
            pr.calc_tariff()

            wm = WmCalc('wm', query_sm, uid, og=og.og, fk=fk,**data_description)
            wm.create_tar()
            wm.calc_from_pricelist()
            wm.calc_from_unit_price()
            wm.create_tar_sr_il()
            wm.add_pricelist()
            wm.add_unit_price()
            # dwie funkcje, które maja wplyw po zmianie wspolczynnikow
            wm.generate_event_cost()
            wm.calc_tariff()

            pl = PlCalc('pl', query_sm, uid, og=og.og, fk=fk,**data_description)
            pl.create_tar()
            pl.create_tar_sr_il()
            pl.calc_from_pricelist()
            pl.add_pricelist()
            # dwie funkcje, które maja wplyw po zmianie wspolczynnikow
            pl.generate_event_cost()
            pl.calc_tariff()

            sm = SmCalc('sm', query_sm, uid, og=og.og,fk=fk, **data_description)
            sm.calc_osd_nr_opk()
            sm.calc_tariff()

            dfs = [pl.sum,wm.sum,pr.sum,sm.sum]
            df_final = reduce(lambda left, right: pd.merge(left, right, on=data_description['case_group']), dfs)
            df_final['TARYFA'] = df_final['suma_pl'] + df_final['suma_pr'] + df_final['suma_wm'] + df_final['koszt_osd']

            abc_excel = AbcExcel(pl=pl, wm=wm, pr=pr, **data_description)
            abc_excel.write_excel()
            dfs = abc_excel.read_excel()
            taryfa_raport = TariffExcel(filename = 'taryfa',rel_path='taryfa',exports={'taryfa':df_final}, **data_description)
            taryfa_raport.write_excel()

        #**************************************
        # pr.load_tar_sr_il_imp(dfs['pr'])
        # pr.assign_prices_to_abc()
        # pr.generate_event_cost()
        # pr.calc_tariff()
        #
        # pl.load_tar_sr_il_imp(dfs['pl'])
        # pl.generate_event_cost()
        # pl.tar_sr_il.head()
        # pl.calc_tariff()
        #
        # test_export = ExcelFileAbc(pl=pl, wm=wm, pr=pr, **data_description)
        # test_export.export_ABC()
        #

# tariff = CalcTariff(query_sm)
