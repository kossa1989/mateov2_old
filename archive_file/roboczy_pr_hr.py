#poniże jest gotowe całe pr hr, teraz trzeba je tylko ubrać w klasę i przepisać zręcznie do programu. ewentualnie sprawdzić
#i zastanowić się czy będzie się dobrze liczyło gdy zapuścimy taryfikator na procedurę albo świadczenidoawcę, albo ogólny na kod produktu

# Paweł Kosowski - jest to plik roboczy przeniesiony z shared.roboczy.py (org pytar). Plik jest do przeanalizowania i sprawdzenia co dkokladnie ma byc zrobione tutaj


import numpy as np
import pandas as pd

from pytar_calc.calc.pr import *


def excel(df):
    args = locals()
    import time
    df.to_excel(r'C:\Users\m.marczak\Documents\anitko\13lip\zb_%s.xlsx' % (time.time()))
e=excel

a = PrCalc('pr', query_sm, uid, og=og.tar, **data_description)
a.create_tar_sr_il_abc()
a.tar_sr_il.head()
a.create_tar_pr_hr()
a.create_pers_infrast()

pd.set_option('display.max_columns', 500)

def calc_time(x):
    y = x.split(':')
    try:
        return float(y[0]) + float(y[1])/60
    except ValueError:
        return 0

# kopiuje wcześniejsze tabele
df = a.tar_pr_hr.copy()
fk = a.fk_szcz.copy()
fk = fk.rename(columns={'kod_nfz':'kod_sw', 'opk_nr':'nr_opk','x-do wyrzucenia powtórka':'x-powt'})
slo_hr = a.slo_hr
# bierze tylko te opki kore asia zaakceptowala i sa w danym roku
#?? delegacja na oddzielną metodę, można liczyć na opk i na kat med kat opk dzieki temu zaleznie co sie w tamtej metodzie podstawi
fk = fk[(fk['rok'].str.strip()==a.kwargs['rok'])&(fk['x-powt']=='1')]
df['czas_jednego_hr_int'] = df['czas_jednego_hr'].apply(calc_time)
df['total_time'] = df['czas_jednego_hr_int'] * df['ilosc_hr']
df_slo = df.merge(slo_hr, left_on=['kod_sw','nr_opk_hr','nazwa_hr'], right_on=['kod_sw','nr_opk_hr','nazwa_hr_sw'], validate='m:1')
df_slo = df_slo.drop(columns=['nazwa_hr_x'])
df_slo = df_slo.rename(columns={'nazwa_hr_y':'nazwa_hr'})
#wyciaga z fk tylko te kolumny ktore sa porzebne. docelowo to powinno byc robione na instancji, zeby mozna bylo eksportować plik fk
# albo na jakims wrapperze isntacji żeby wszystkie Calc'i korzystaly z tej samej fki
fk_pers = fk[['wyn_h_lekarz','wyn_h_pieleg','wyn_h_pozost_med','wyn_h_pozost_nmed', 'kod_sw','nr_opk', 'kat_med','kat_opk','infrast_odt_h_bloku']]
df_slo = df_slo.merge(fk_pers, left_on=['kod_sw','nr_opk_hr'], right_on=['kod_sw','nr_opk'], validate='m:1')
df_slo = df_slo.drop(columns=['nr_opk']) #usuwa kolumne dla porzadku

# zmienia anestezjologow, do innej metody
df_slo['kat_med'].mask(# warunek,wartosc orginalna jezeli falsz, wpisana jeżeli prawda
    ((df_slo['nazwa_hr']=='LEKARZ ANESTEZJOLOG') & (df_slo['kat_med']!='18')),'43')
df_slo['kat_opk'].mask(# warunek,wartosc jezeli falsz
    ((df_slo['nazwa_hr']=='LEKARZ ANESTEZJOLOG') & (df_slo['kat_med']!='18')),'1')
df_slo['kat_med'].mask(# warunek,wartosc jezeli falsz
    ((df_slo['nazwa_hr']=='PIELEGNIARKA ANESTEZJOLOGICZNA') & (df_slo['kat_med']!='18')),'43')
df_slo['kat_opk'].mask(# warunek,wartosc jezeli falsz
    ((df_slo['nazwa_hr']=='PIELEGNIARKA ANESTEZJOLOGICZNA') & (df_slo['kat_med']!='18')),'1')


# pr_hr_pers_wagi
# określa czym jednostkową grupę perosnelu
personel_distinct_groups = a.kwargs['case_group']+a.unit_id +['nazwa_hr',]
pr_hr_pers_wagi = df_slo.groupby( personel_distinct_groups+['nr_opk_hr'] )['kat_opk'].count().reset_index()
pr_hr_pers_wagi = pr_hr_pers_wagi.rename(columns={'kat_opk':'PERSONEL_ZABIEG_LICZBA'})
#pr_hr_pers czas
pr_hr_pers_czas = df_slo.groupby(personel_distinct_groups)['czas_jednego_hr_int'].sum().reset_index()
# pr-hr infras wagi
pr_hr_infras_wagi = a.tar.groupby(a.kwargs['case_group']+a.unit_id +['nr_opk_pr'])['id'].count().reset_index()
pr_hr_infras_wagi = pr_hr_infras_wagi.rename(columns={'id':'LICZBA_OPK_PR'})


#zwraca wyjątek, jeżeli jest kilka nierozroznialnych procedur, albo do error loga
# if not pr_hr_infras_wagi[pr_hr_infras_wagi['LICZBA_OPK_PR']>1].empty:
#     raise Exception('More than one procedure in unit pr')

# pr-hr infras czas
a.tar['czas_pr_int'] = a.tar['czas_pr'].apply(calc_time)
#liczy sredni czas na procedura w jednostce
pr_hr_infras_czas = a.tar.groupby(a.kwargs['case_group']+a.unit_id)['czas_pr_int'].mean().reset_index()
pr_hr_infras_czas = pr_hr_infras_czas.rename(columns={'czas_pr_int':'avg_czas_pr_int'})

pr_hr_pers_wagi_wyn_h  = pr_hr_pers_wagi.merge(fk_pers, left_on=['kod_sw','nr_opk_hr'], right_on=['kod_sw','nr_opk'], validate='m:1')


#oblicza koszt personelu, dzilei na grupy i przypisuje wynagrodzenia potem laczy w pd concat

def calc_avg_wyn_h_mean_weights(df,groups, col, substr):
    df_filtered = df[df['nazwa_hr'].str.upper().str.contains(substr)]
    df1 = df_filtered.groupby(
        groups).apply(
        lambda x: np.average(x[col], weights=x['PERSONEL_ZABIEG_LICZBA'])).reset_index()
    df2 = df1.rename(columns={0: 'wyn_h_mean'})
    return df2.reset_index()


personel = []
for i in (('wyn_h_lekarz', 'LEKAR'),
            ('wyn_h_pieleg', 'PIEL'),
            ('wyn_h_pozost_med', 'POZOST'),
            ('wyn_h_pozost_nmed', 'INNY'),):
    personel.append(calc_avg_wyn_h_mean_weights(pr_hr_pers_wagi_wyn_h,personel_distinct_groups, i[0], i[1]))
personel_wyn_h_all = pd.concat(personel).sort_values(personel_distinct_groups)
#laczy czas z wynagrodzeniem
personel_costs = personel_wyn_h_all.merge(pr_hr_pers_czas, on=personel_distinct_groups, validate='1:1')
personel_costs['koszt_hr'] = personel_costs['czas_jednego_hr_int']*personel_costs['wyn_h_mean']
personel_costs_sum = personel_costs.groupby(a.kwargs['case_group']+a.unit_id)['koszt_hr'].sum().reset_index()

## infrastruktura
pr_hr_infras_wagi = pr_hr_infras_wagi.merge(fk_pers, left_on=['kod_sw','nr_opk_pr'], right_on=['kod_sw','nr_opk'], validate='m:1')

#tutaj nie ma kilku grup jak w personelu, wiec srednia wazona liczona jest wprost
pr_hr_infras_wagi = pr_hr_infras_wagi.groupby(a.kwargs['case_group']+a.unit_id).apply(
    lambda x: np.average(x['infrast_odt_h_bloku'], weights=x['LICZBA_OPK_PR'])).reset_index()
pr_hr_infras_wagi  = pr_hr_infras_wagi.rename(columns = {0:'mean_h_infrast'})

pr_hr_infras_sum = pr_hr_infras_wagi.merge(pr_hr_infras_czas, on=a.kwargs['case_group']+a.unit_id,validate='1:1')
pr_hr_infras_sum['koszt_infrast'] = pr_hr_infras_sum['mean_h_infrast']*pr_hr_infras_sum['avg_czas_pr_int']
pr_hr_infras_sum = pr_hr_infras_sum.drop(columns=[ 'mean_h_infrast', 'avg_czas_pr_int',])
#oblicza koncowy koszt ptr
pr_hr_sum = pr_hr_infras_sum.merge(personel_costs_sum, on=a.kwargs['case_group']+a.unit_id,validate='1:1')
pr_hr_sum['koszt_pr'] = pr_hr_sum['koszt_infrast']+pr_hr_sum['koszt_hr']
pr_hr_sum.columns

################################DOTAD OK




sorted(list(fk.columns))


fk_pers[fk_pers[['kod_sw','nr_opk']].duplicated()]

df_slo['nr_opk_hr'].unique()
#dorobic tu joina ze slownikem FK zeby przypisac jezeli lek/piel jest z opk anest to zeby był jako anest
#przypisac ceny anestezjologow do wierszy lekarz anestezjolog

df_slo[['nazwa_hr','nr_opk_hr']].head()

df.columns

df_g = df.groupby(a.single_pr+['nazwa_hr', 'nr_opk_hr'])
df_g.sum().head()
fk = a.fk_szcz.copy()
fk['rok']
print(list(a.fk_szcz.columns))

x = df['czas_jednego_hr'][3]

slo_hr.columnss

slo_hr



a = pd.asd

p = r'T:\organizacyjne_robocze\012_Taryfikator\slowniki\pytar\dict_output\FK_SZCZEGOLOWY_2018_07_20_14_07.xlsx'
a = pd.read_excel(p)
a['ROK']

p = r'T:\organizacyjne_robocze\012_Taryfikator\slowniki\pytar\dict_output\FK_SZCZEGOLOWY_2018_07_20_14_07.xlsx.pkl'







