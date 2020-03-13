
# Jest to przeniesiony stary plik data_description z katalogu shared

wb17 = {
    'patient_id': ['nr_ks', 'kod_sw'],
    # pl_id, czyli grupowanie do wyliczenia przebiegu
    'pl_id': ['nazwa_pl', 'jedn_miary_pl', 'nr_opk_pl','indeks_mat_pl'],
    'pl_quantity': 'liczba_podanych_jedn_miary',
    'wm_id': ['nazwa_wm', 'jedn_miary_wm', 'nr_opk_wm','indeks_mat_wm'],
    'wm_quantity': 'liczba_zuzytych_jedn_miary',
    'pr_id': ['icd_9', 'nazwa_pr','nr_opk_pr'],
    'pr_quantity': 'ilosc_pr',
    'join_cols_pr_hr':['icd_9','nr_ks_pr','data_wyk'],
    # prices, czyli grupowanie do obliczenia ceny leku
    'pl_prices': ['jedn_miary_pl','indeks_mat_pl'],
    'wm_prices': ['jedn_miary_wm','indeks_mat_wm'],
    'om_prices': ['jedn_miary','indeks_mat'],
    'pr_prices': ['icd_9', 'nr_opk_pr'],
    'cp_prices': ['icd_9', 'nr_opk_pr'],
    'wm_unit_price': ['cena_jednostki'],
    'rok': '2017',
}

# dszcz_onk_42 = {
#     'patient_id': ['nr_ks', 'kod_sw'],
#     # pl_id, czyli grupowanie do wyliczenia przebiegu
#     'pl_id': ['nazwa_pl', 'jedn_miary_pl', 'nr_opk_pl'],
#     'pl_quantity': 'liczba_podanych_jedn_miary',
#     'wm_id': ['nazwa_wm', 'jedn_miary_wm', 'nr_opk_wm'],
#     'wm_quantity': 'liczba_zuzytych_jedn_miary',
#     'pr_id': ['icd_9', 'nazwa_pr','nr_opk_pr'],
#     'pr_quantity': 'ilosc_pr',
#     'join_cols_pr_hr':['icd_9', 'nazwa_pr','nr_ks_pr','data_wyk'],
#     # prices, czyli grupowanie do obliczenia ceny leku
#     'pl_prices': ['nazwa_pl', 'jedn_miary_pl'],
#     'wm_prices': ['nazwa_wm', 'jedn_miary_wm'],
#     'om_prices': ['nazwa', 'jedn_miary'],
#     'pr_prices': ['icd_9', 'nazwa_pr'],
#     'cp_prices': ['icd_9', 'nazwa_pr'],
#     'wm_unit_price': ['cena_jednostki'],
#     'rok': '2017',
# }