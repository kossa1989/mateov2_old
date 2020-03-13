import pandas as pd

new = pd.read_excel(r'T:\organizacyjne_robocze\012_Taryfikator\test\taryfa_17_0001_pacjent_20maj2019_16_46_50\osd.xlsx')
tar = pd.read_excel(r'T:\organizacyjne_robocze\012_Taryfikator\test\taryfa_17_0001_pacjent_20maj2019_16_46_50\TARYFA_20maj2019_16_46_50.xlsx')

all = new.merge(tar, left_on=['kod_sw','nr_ks'], right_on=['kod_swd','nr_ks_gl'])

all.shape[0]==new.shape[0]

all['roznica'] = all['koszt_pobytu']-all['koszt_osd']
rozne = all['roznica'][round(all['roznica'], 2)!=0]
a = all[round(all['roznica'], 2)!=0]
print(123)
