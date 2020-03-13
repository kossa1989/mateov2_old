"""
Porównanie dwoch ABC przy liczeniu na pacjenta, zwalidowanie z metodologią Uli Cegłowskiej.
"""

import pandas as pd

sheet_comparison = 'PR'
abc1 = r'T:\organizacyjne_robocze\012_Taryfikator\test\ABC.xlsx'
abc2 = r'T:\organizacyjne_robocze\012_Taryfikator\test\pr.xlsx'

abc1 = pd.read_excel(abc1, sheet_name=sheet_comparison)
abc2 = pd.read_excel(abc2)
abc1_pac = ['kod_prod', 'kod_dod']
abc2_pac = ['kod_sw', 'nr_ks']
unit = []
if not abc1.shape[0] == abc2.shape[0]:  # assert if equal nobs
    print('Sheets of diffrent shape.')
    abc1_count = abc1.groupby(abc1_pac).count().iloc[:, [0]].reset_index()
    abc2_count = abc2.groupby(abc2_pac).count().iloc[:, [0]].reset_index()
    all = abc1_count.merge(abc2_count, left_on=abc1_pac, right_on=abc2_pac)
    # patients with diffrent numorws are in table diff_patients
    col = abc1_count.columns[-1]
    diff_patients = all[all[col]!=all['Unnamed: 0']]
    print('Diffrent shapes of data: ', diff_patients, sep='\n\n')

koszt_pac1 = (abc1[abc1_pac + ['suma_pr']]).drop_duplicates()
koszt_pac2 = (abc2[abc2_pac + ['sum_koszt_gr']]).drop_duplicates()
cost_diff = koszt_pac1.merge(koszt_pac2, left_on=abc1_pac, right_on=abc2_pac)
cost_diff['diff'] = cost_diff['suma_pr']-cost_diff['sum_koszt_gr']
cost_diff.sort_values('diff', inplace=True)
pl_id2 = ['icd_9','nazwa_pr','nr_opk_pr','indeks_mat_pl']
pl_id1 = ['NAZWA','UNIT_NAZWA','nr_opk_pl','INDEKS_MAT']
abcs_comparison = abc1.merge(abc2, left_on=abc1_pac+pl_id1 , right_on=abc2_pac+pl_id2, validate="1:1")
abcs_comparison.to_excel(r'T:\organizacyjne_robocze\012_Taryfikator\test\abc_comp.xlsx')


# compare osds
