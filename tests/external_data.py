import pandas as pd


fk = {'kod_sw': ['12','12','12','12'],
'nr_opk': ['500-600','500-10','500-123','500-1000'],
'kat_med': ['1','2','3','4'],
'kat_opk': ['2','6','7','8'],
'infrast_odt_h_bloku': ['100','200','300','400'],
'opk_nazwa': ['Kardiologia','Nefrologia','Gastrologia','Ortopedoncja'],
'nowy_osobodzien_koszt': ['100','','',''],
'wyn_h_lekarz': ['100','200','300','400'],
'wyn_h_pieleg': ['100','200','300','400'],
'wyn_h_perf': ['100','200','300','400'],
'wyn_h_psych': ['100','200','300','400'],
'wyn_h_diet': ['100','200','300','400'],
'wyn_h_logop': ['100','200','300','400'],
'wyn_h_rehab': ['100','200','300','400'],
'wyn_h_fiz_med': ['100','200','300','400'],
'wyn_h_technik': ['100','200','300','400'],
'wyn_h_terap_zaj': ['100','200','300','400'],
'wyn_h_pozost_med': ['100','200','300','400'],
'wyn_h_pozost_nmed': ['100','200','300','400'],
'wyn_h_rezydent': ['100','200','300','400'],
'kod_resort': ['100','200','300','400'],}


fk_df = pd.DataFrame(fk)
