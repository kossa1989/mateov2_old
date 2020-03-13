

"""Plik chyba będzie niepotrzebny, sluzyl do wgrywnaia danych do SQLa - Paweł Kosowski"""

# coding: utf-8

# In[6]:

import sqlalchemy as sa
import pandas as pd
def chck(df,col):
    return df[df[col].duplicated()]
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from IPython.display import clear_output
engine = sa.create_engine('mysql://daneb:%s@localhost:3306/wb17?charset=utf8'%passwd)
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)
# employees = Base.classes.employees
# df = pd.read_sql('select * from employees', session.connection())
# df
# print(employees.__table__.columns)
clear_output()


# In[7]:

df = pd.read_sql('select * from patient_cards', session.connection())


# In[3]:

zbeki = ["ZB_%s"%i for i in range(8,18)]
# df
zbeki
for i in df.itertuples():
    for j in zbeki:
        print(f"""insert into kartajgp_iczmp.patient_card_stages (patient_card_id, name, stage) values ({i.id}, "","{j}");""")


# In[19]:

import numpy as np


# In[4]:

a = pd.read_excel('PROCEDURY_190203.xlsx')
a


# In[17]:

proc = pd.read_sql('select * from dict_procedures', session.connection())


# In[5]:

a=a.fillna('')
a['nazwa_gotowa'] = a['nazwa']+ ' // ' + a['OPK']
a_non_opk = a[a['OPK']=='']

proc.merge(a_non_opk, left_on='name',right_on='nazwa')


# In[ ]:




# In[20]:

pl_wm = pd.read_excel('PL_WM_PROD_WYR.xlsx')
pl = pl_wm[pl_wm['RODZAJ']=='Produkt leczniczy']
pl_d = {
    'NAZWA_HANDLOWA':'name',
    'JEDNOSTKA_PRZYJECIOWA':'volume_unit',
    'CENA_OST_DOSTAWY_2017_BRUTTO':'price',
    'NAZWA_MIEDZYNARODOWA':'substance'
}
pl1 = pl[list(pl_d.keys())]
pl2 = pl1.rename(columns=pl_d)
# pl2.to_sql('dict_pharmaceuticals', engine, if_exists='append', index=False)


# In[22]:

pl_wm = pd.read_excel('PL_WM_PROD_WYR.xlsx')
wm = pl_wm[pl_wm['RODZAJ']=='Wyrób medyczny']
wm_d = {
    'NAZWA_HANDLOWA':'name',
    'JEDNOSTKA_PRZYJECIOWA':'volume_unit',
    'CENA_OST_DOSTAWY_2017_BRUTTO':'price',
}
wm1 = wm[list(wm_d.keys())]
wm2 = wm1.rename(columns=wm_d)
# wm2.to_sql('dict_medical_products', engine, if_exists='append', index=False)


# In[39]:

hr = pd.read_excel('PROCEDURY-KLINIKI (1).xlsx')
hr1 = hr[['Unnamed: 1']]
hr2 = hr1.rename(columns={'Unnamed: 1': 'name'})
hr3 = hr2[hr2.index>2]
# hr3.to_sql('dict_employee_groups', engine, if_exists='append', index=False)
hr3


# In[38]:

pr = pd.read_excel('3_ICZMP_USŁUGI 11102018.xls')
pr_d = {
    'NAZWA_PEŁNA_USŁUGI':'name',
    'ICD-9':'icd_code',
    'OPK_NAZWA':'opk2_name',
    'CENA':'price',
    'TYP_USŁUGI':'type',
    'ID_USŁUGI':'service_id',
    'KOD_USŁUGI':'service_code'      
}
pr1 = pr[list(pr_d.keys())]
pr2 = pr1.rename(columns=pr_d)
# pr2.to_sql('dict_procedures', engine, if_exists='append', index=False)


# In[47]:

#dodatkowe procedury z cenami 0

pr_dod = pd.read_excel('PROCEDURY-KLINIKI (1).xlsx', sheet_name=None)
pr_dod = pr_dod['procedury']
pr_dod1 = pr_dod.rename(columns={'Procedury w Klinikach':'name'})
pr_dod1['price']=0
pr_dod1['type']='uwzglednione w koszcie OSD, cena do wyjasnienia'
pr_dod1['service_code']='uwzglednione w koszcie OSD, cena do wyjasnienia'

# pr_dod1.to_sql('dict_procedures', engine, if_exists='append', index=False)


# In[13]:

og = pd.read_excel('DaneStatystyczne2017v4.xlsx', skiprows=1)
pc = pd.read_sql('select * from patient_cards', session.connection())


# In[79]:

og1 = og[['Rok','Numer','Pozycja','Numer dziecka','Dt rozp. Pobytu','Dt zak. Pobytu','Nazwa oddziału']]
og2 = og1.assign(book_number=og1['Rok'].astype(str)+'-'+og1['Numer'].astype(str)+'-'+og1['Pozycja'].astype(str))
og3 = og2.assign(book_num_join = 
    np.where(og2['Numer dziecka'].fillna(0)!=0, og2['book_number']+'.'+og2['Numer dziecka']\
             .fillna(0).astype(int).astype(str), og2['book_number']))
og4 = og3[['Nazwa oddziału','book_num_join', 'Dt zak. Pobytu','Dt rozp. Pobytu']]
og5 = og4.rename(columns={'Nazwa oddziału':'ward_name','book_num_join':'book_number',
                    'Dt rozp. Pobytu':'date_from','Dt zak. Pobytu':'date_to'})
hosp_hist = og5.merge(pc[['book_number','id']], on='book_number')
assert hosp_hist['book_number'].drop_duplicates().size+1==pc.shape[0]
#+1 w asercie, poniewaz jest test pacjent
hosp_hist_to_add = hosp_hist.drop_duplicates().rename(columns={'id':'patient_card_id'})
hosp_hist_to_add = hosp_hist_to_add.drop(columns='book_number')


# In[80]:

# hosp_hist_to_add.to_sql('patient_card_hospitalization_history',engine,if_exists='append', index=False)


# In[83]:

pr = pd.read_excel('PROC_DO_APP/3_ICZMP_USŁUGI 11102018.xls')
zd1 = pd.read_excel('PROC_DO_APP/ICZMP BADANIA LAB1 15102018.xlsx')
zd2 = pd.read_excel('PROC_DO_APP/ICZMP BADANIA LAB2 15102018.xlsx')


# In[84]:

zd = pd.concat([zd1,zd2])
# zd_slo = zd.merge(pr, left_on='FullName', right_on='NAZWA_PEŁNA_USŁUGI', how='left')
# zd_non_slo = zd_slo[zd_slo['NAZWA_PEŁNA_USŁUGI'].isnull()]
# zd_non_slo['FullName'].drop_duplicates()#.to_excel('procedury_bez_odpowiednika_w_cenniku_12102018.xlsx')
pr_slo_app = pd.read_sql('select * from dic_procedures', session.connection())
og_app = pd.read_sql('select * from patient_cards', session.connection())

