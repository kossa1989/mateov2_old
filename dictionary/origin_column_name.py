"""inside there are dicts with origin names of the columns from cp, og, ok tables etc. This is nessesary to compare
and check DataFrame with default scheme names of the columns. Below files are from 2017"""

#do uzupełnienia dtype kolumn
cp = {
    "kod_ow":       "",
    "kod_sw":       "",
    "nr_opk_pr":    "",
    "rok":          "",
    "miesiace":     "",
    "icd_9":        "", #WAŻNE POLE, po nim będziemy grupować
    "nazwa_pr":     "",
    "koszt_cp_txt": "",
    "ilosc_cp":     "",
    "ilosc_cp_txt": "",
    "CSZ16_CP_UD":  "",
    "upd_date":     "",
    "kw":           ""
}

#do uzupełnienia dtype kolumn
og = {
    "id_swd":       "",
    "prod_jedn":    "",
    "prod_kontr":   "",
    "data_od":      "",
    "data_do":      "",
    "cena":         "",
    "lb_jedn":      "",
    "rozliczone_ryczaltem":     "",
    "ksiega_rok":   "",
    "ksiega_nr":    "",
    "ksiega_poz":   "",
    "ksiega_nr_dziecka":        "",
}

om = {
    "kod_ow":       "",
    "kod_sw":       "",
    "indeks_mat":   "",
    "ean":          "",
    "subst_czynna_rodzaj_wm":   "",
    "zawartosc_subs_czynnej":   "",
    "nazwa":        "",
    "jedn_miary":   "",
    "liczba_jedn_miary_txt":    "",
    "liczba_jedn_miary":        "",
    "jedn_miary_opak":          "",
    "liczba_zakup_opak_txt":    "",
    "liczba_zakup_opak":        "",
    "wartosc_txt":  "",
    "wartosc":      "",
    "csz16_om_id":  "",
    "upd_date":     "",
    "kw":           ""
}

pl = {
    "kod_ow":       "",
    "kod_sw":       "",
    "indeks_mat_pl":            "",
    "nr_opk_pl":    "",
    "nr_ks":        "",
    "data_wyk":     "",
    "nazwa_pl":     "",
    "jedn_miary_pl":            "",
    "liczba_podanych_jedn_miary_txt":   "",
    "liczba_podanych_jedn_miary:":      "",
    "koszt_jednostki_txt":      "",
    "koszt_jednostki":          "",
    "csz16_pl_id":  "",
    "upd_date":     "",
    "kw":           ""
}

pr = {
    "kod_ow":       "",
    "kod_sw":       "",
    "nr_ks":        "",
    "nr_opk_zlec":  "",
    "nr_opk_pr":    "",
    "nr_ks_pr":     "",
    "data_wyk":     "",
    "icd_9":        "",
    "nazwa_pr":     "",
    "ilosc_pr":     "",
    "czas_pr":      "",
    "csz16_pr_id":  "",
    "upd_date":     "",
    "kw":           ""
}

pr_hr = {
    "kod_ow":       "",
    "kod_sw":       "",
    "nr_ks":        "",
    "nr_ks_pr":     "",
    "data_wyk":     "",
    "icd_9":        "",
    "nazwa_pr":     "",
    "nr_opk_hr":    "",
    "nazwa_hr":     "",
    "ilosc_hr":     "",
    "czas_jednego_hr":         "",
    "csz16_pr_hr_id":          "",
    "upd_date":     "",
    "kw":           ""
}

sm = {
    "kod_ow":       "",
    "kod_sw":       "",
    "nr_opk_sm":    "",
    "nr_ks":        "",
    "data_rozp_prod":           "",
    "data_zak_prod":            "",
    "godz_rozp_prod":           "",
    "godz_zak_prod":            "",
    "kod_zakresu":              "",
    "kod_prod":                 "",
    "rozp_gl":      "",
    "rozp_wsp":     "",
    "rozp_pow":     "",
    "ilosc_sm_txt": "",
    "ilosc_sm":     "",
    "csz16_sm_id":  "",
    "upd_date":     "",
    "kw":           "",
    "kod_zakresu_rehosp":       "",
    "kod_prod_rehosp":          "",
    "uwagi_rehosp": ""
}

wm = {
    "kod_ow":       "",
    "kod_sw":       "",
    "indeks_mat_wm":            "",
    "nr_opk_wm":    "",
    "nr_ks":        "",
    "data_wyk":     "",
    "nazwa_wm":     "",
    "jedn_miary_wm":            "",
    "liczba_zuzytych_jedn_miary_txt":   "",
    "liczba_zuzytych_jedn_miary":       "",
    "koszt_jednostki_txt":      "",
    "koszt_jednostki":          "",
    "CSZ16_wm_ID":              "",
    "upd_date":     "",
    "kw":           ""
}

