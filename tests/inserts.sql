INSERT INTO test_daneb.og (ksiega_rok, ksiega_nr, ksiega_poz, ksiega_nr_dziecka, kod_ow, kod_sw, nr_ks, id_pacjenta, data_przyj, data_zak, tr_przyj, tr_wyp, id_rekordu, upd_date, data_urodz, wiek) VALUES (2017, 12, 12, 0, '02', '12', '12', '01', '2019-03-01', '2019-03-10', 3, 5, 2, null, null, 50);

INSERT INTO test_daneb.sm (KOD_OW, KOD_SW, NR_OPK_SM, NR_KS, DATA_ROZP_PROD, DATA_ZAK_PROD, GODZ_ROZP_PROD, GODZ_ZAK_PROD, KOD_ZAKRESU, KOD_PROD, ROZP_GL, ROZP_WSP, ROZP_POW, ILOSC_SM_TXT, ILOSC_SM, ID_REKORDU, UPD_DATE, id) VALUES ('02', '12', '1', '12', '2019-03-01', '2019-03-07', '15:00', '16:00', '123', '5.51', 'A34', 'A54', null, null, 1, null, null, 13656);

INSERT INTO test_daneb.pl (KOD_OW, KOD_SW, INDEKS_MAT_PL, NR_OPK_PL, NR_KS, DATA_WYK, NAZWA_PL, JEDN_MIARY_PL, LICZBA_PODANYCH_JEDN_MIARY_TXT, LICZBA_PODANYCH_JEDN_MIARY, KOSZT_JEDNOSTKI, KOSZT_JEDNOSTKI_TXT, ID_REKORDU, UPD_DATE, id) VALUES ('02', '12', '1', '1', '12', '2019-03-02', 'paracetamol', 'tabletka', null, 100, 56, null, null, null, 302181);

INSERT INTO test_daneb.wm (KOD_OW, KOD_SW, INDEKS_MAT_WM, NR_OPK_WM, NR_KS, DATA_WYK, NAZWA_WM, JEDN_MIARY_WM, LICZBA_ZUZYTYCH_JEDN_MIARY_TXT, LICZBA_ZUZYTYCH_JEDN_MIARY, KOSZT_JEDNOSTKI, KOSZT_JEDNOSTKI_TXT, ID_REKORDU, UPD_DATE, id) VALUES ('02', '12', '13123', '500-10', '12', '2019-03-08', 'okluder', 'szt.', null, 3, 120, null, null, null, 319289);

INSERT INTO test_daneb.pr (KOD_OW, KOD_SW, NR_KS, NR_OPK_ZLEC, NR_OPK_PR, NR_KS_PR, DATA_WYK, ICD_9, NAZWA_PR, ILOSC_PR, CZAS_PR, ID_REKORDU, UPD_DATE, id) VALUES ('02', '12', '12', '500-02', '500-10', '123', '2019-03-15', '92.87', 'implantacja okludera', 3, '120', null, null, 167236);

INSERT INTO test_daneb.pr_hr (KOD_OW, KOD_SW, NR_KS, NR_KS_PR, DATA_WYK, ICD_9, NAZWA_PR, NR_OPK_HR, NAZWA_HR, ILOSC_HR, CZAS_JEDNEGO_HR, ID_REKORDU, UPD_DATE, id) VALUES ('02', '12', '12', '123', '2019-03-15', '92.87', 'implantacja okludera', '500-600', 'lekarz', 2, '1:30', null, null, 59801);

INSERT INTO test_daneb.om (KOD_OW, KOD_SW, indeks_mat, EAN, SUBST_CZYNNA_RODZAJ_WM, ZAWARTOSC_SUBST_CZYNNEJ, NAZWA, JEDN_MIARY, liczba_jedn_miary_txt, liczba_jedn_miary, JEDN_MIARY_OPAK, liczba_zakup_opak_txt, liczba_zakup_opak, wartosc_txt, wartosc, ID_REKORDU, UPD_DATE) VALUES ('02', '12', '1', 'NULL', 'NULL', 'NULL', 'paracetamol', 'tabletka', null, 10, 'op.', null, 100, null, 1000, null, null);
INSERT INTO test_daneb.om (KOD_OW, KOD_SW, indeks_mat, EAN, SUBST_CZYNNA_RODZAJ_WM, ZAWARTOSC_SUBST_CZYNNEJ, NAZWA, JEDN_MIARY, liczba_jedn_miary_txt, liczba_jedn_miary, JEDN_MIARY_OPAK, liczba_zakup_opak_txt, liczba_zakup_opak, wartosc_txt, wartosc, ID_REKORDU, UPD_DATE) VALUES ('02', '12', '13123', 'NULL', 'NULL', 'NULL', 'okluder', 'szt.', null, 30, 'op.', null, 20, null, 900, null, null);

INSERT INTO test_daneb.cp (kod_ow, kod_sw, nr_opk_pr, rok, miesiace, icd_9, nazwa_pr, koszt_cp_txt, koszt_cp, ilosc_cp, ilosc_cp_txt, id_rekordu, upd_date) VALUES ('02', '12', '500-400', '2017', '1-12', '92.87', 'implantacja okludera', null, 9000, 30, null, null, null);
