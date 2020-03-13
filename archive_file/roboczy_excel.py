#Jakiś roboczy excel Mateusza, przeniesiony z calc.roboczy_excel.py

import pandas as pd
df = a.tar_sr_il_abc

work_path = r'C:\Users\m.marczak\Documents\anitko\13lip'

coldict = {'wsp':'#31345c', 'wsp_dni':'#31345c'}

# def highlight_cols(s, coldict):
#     if s.name in coldict.keys():
#         return ['color: {}'.format(coldict[s.name])] * len(s)
#     return [''] * len(s)
#
#
# styled = df.style.apply(highlight_cols, coldict=coldict)

# styled.to_excel(writer, sheet_name='PR')

from pytar_calc.calc.start import  data_description as kwargs
self = pl
self.tar_sr_il['koszt_pl'] = self.tar_sr_il['cena_jedn'] * self.tar_sr_il['sr_wyst_w_przyp']
tar_sr_il = self.tar_sr_il.groupby(kwargs['case_group'])['koszt_pl'].sum().reset_index()
taryfa_pl = tar_sr_il.rename(columns={'koszt_pl':'suma_pl'})
taryfa_pl

self = wm
self.tar_sr_il['koszt_wm'] = self.tar_sr_il['cena_jedn'] * self.tar_sr_il['sr_wyst_w_przyp']
tar_sr_il = self.tar_sr_il.groupby(kwargs['case_group'])['koszt_wm'].sum().reset_index()
taryfa_wm = tar_sr_il.rename(columns={'koszt_wm':'suma_wm'})
taryfa_wm.head()

