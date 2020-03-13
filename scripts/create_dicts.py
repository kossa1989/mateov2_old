schema = 'wb17'
outpath = r"T:\organizacyjne_robocze\012_Taryfikator\slowniki\do_przeslownikowania"
import datetime

import pandas as pd

from calc.base_calc import UtilTools
from calc.osd import FkSzcz
#from pytar_calc.models.daneb import engine_tmp #TODO zmienic tutaj config do DB
from database.db import DbEngine
engine_tmp = DbEngine.create_engine('tmp')

# check dict for hr
pr_hr = pd.read_sql("select distinct kod_sw, nr_opk_hr, nazwa_hr from % s.pr_hr" % schema, engine_tmp)
utils = UtilTools()
hr_dict = utils.get_latest_dict('hr')
hr_post_dictum = pr_hr.merge(hr_dict, left_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr'],
                             right_on=['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw'], how='left',
                             indicator=True)
should_add = hr_post_dictum[hr_post_dictum['_merge'] == 'left_only']
needs_mapping = should_add[['kod_sw', 'nr_opk_hr', 'nazwa_hr_x']].rename(columns={'nazwa_hr_x': 'nazwa_hr_sw'})
fk = FkSzcz(rok='2017')
slo_opk = fk.slo_opk()
to_export = needs_mapping.merge(slo_opk, left_on=['kod_sw', 'nr_opk_hr'], right_on=['kod_sw', 'nr_opk_list'])
to_export = to_export.assign(nazwa_hr='')
to_export.to_excel(outpath + r'\pr_hr_dict_%s.xlsx' % datetime.datetime.now().__str__().replace(':', '_').replace(' ', '_'))

print(123)