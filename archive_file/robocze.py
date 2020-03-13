# Jakiś robocyz plik, oryginalnie był w calc.robocze.py


import sys
import numpy as np
sys.path = sys.path + ['C:\\Users\\m.marczak\\PycharmProjects\\pytar_calc\\pytar_calc']
from pytar_calc.calc.osd import SmCalc, FkSzcz
from calc.plwm import WmCalc, PlCalc
from calc.og import OgCalc
from calc.pr import PrCalc
from calc.start import QuerySm
import random

from pytar_calc.shared.data_descriptions import dszcz_onk_42, wb17

options = {'case_group': ['kod_prod', 'kod_sw', 'nr_ks'],
           'fake_data': True,
           'path': r'T:\organizacyjne_robocze\tmp\pytar_test',
           'schema': 'wb17',
           'price_priority':'cena_z_pliku',
           }

query_sm_sql_query = f"""
        create table %s as
        select t1.nr_ks, t1.kod_sw, t1.kod_prod, '1' as kod_dod
        from {options['schema']}.sm t1 inner join {options['schema']}.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks
        where kod_prod like "5.51.01.0005047"
"""

data_description = {**options, **wb17}
uid = 'wb17_123'# % random.randint(0,10**10)
query_sm = QuerySm(query_sm_sql_query, uid, **data_description)

fk = FkSzcz(**data_description)
og = OgCalc('og', query_sm, uid, **data_description)
og.create_tar()


##%%##
pr = PrCalc('pr', query_sm, uid, og=og.og, fk=fk, **data_description)
pr.create_tar()
pr.create_tar_sr_il_abc()
pr.calc_from_pricelist()
pr.add_cp_prices()
pr.tar_sr_il.to_excel(r'T:\organizacyjne_robocze\012_Taryfikator\test\pr.xlsx')
# PR_HR
pr.create_tar_pr_hr()
pr.create_pers_infrast_wagi_czas()
pr.calc_pr_hr_costs()
pr.add_pr_a_prices()
pr.assign_prices_to_abc()
pr.generate_event_cost()
##%%##

##
pr = PrCalc('pr', query_sm, uid, og=og.og, fk=fk, **data_description)
# self = pr
pr.create_tar()
pr.create_tar_sr_il_abc()
pr.create_tar_pr_hr()
pr.create_pers_infrast_wagi_czas()
pr.calc_pr_hr_costs()
pr.calc_from_pricelist()
pr.tar_sr_il.shape

pr.add_cp_prices()
pr.add_pr_a_prices()
# dwie funkcje, które maja wplyw po zmianie wspolczynnikow
pr.assign_prices_to_abc()
pr.generate_event_cost()
pr.calc_tariff()
# pr.tar_sr_il.to_excel('pr.xlsx')

self = pr
self.create_pricelist()

df1 = b0.groupby(
    self.pricelist_col_names).apply(
    lambda x: np.average(x['koszt_cp']
                         , weights=x['ilosc_cp']
                         )).reset_index()
df1 = df1.rename(columns={0: 'koszt_cp'})
self.pricelist_prices = df1
df1


def f(ds, col, val):
    return ds[ds[col] == val]


wm = WmCalc('wm', query_sm, uid, og=og.og, fk=fk, **data_description)
wm.create_tar()
wm.calc_from_pricelist()
wm.calc_from_unit_price()
wm.unit_prices.rename(columns={0: 'cena_z_pliku'}).head()
wm.create_tar_sr_il()
a = wm.tar_sr_il
# *************************************
wm.add_pricelist()
wm.add_unit_price()
# dwie funkcje, które maja wplyw po zmianie wspolczynnikow
wm.generate_event_cost()
wm.calc_tariff()
wm.tar_sr_il.to_excel('e2.xlsx')

pl = PlCalc('pl', query_sm, uid, og=og.og, fk=fk, **data_description)
pl.create_tar()
pl.create_tar_sr_il()
pl.calc_from_pricelist()
pl.add_pricelist()
pl.calc_from_unit_price()
pl.add_unit_price()

# dwie funkcje, które maja wplyw po zmianie wspolczynnikow
pl.generate_event_cost()
pl.calc_tariff()
pl.tar_sr_il.to_excel('pl1.xlsx')

sm = SmCalc('sm', query_sm, uid, og=og.og, fk=fk, **data_description)
sm.create_tar()
sm.prepare_table_to_calc_osd()
sm.calc_new_osd()
