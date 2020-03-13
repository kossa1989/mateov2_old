drop DATABASE IF EXISTS test_daneb;
create database test_daneb;

CREATE TABLE test_daneb.`cp` (
  `kod_ow` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `kod_sw` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `nr_opk_pr` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `rok` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `miesiace` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `icd_9` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `nazwa_pr` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `koszt_cp_txt` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `koszt_cp` double DEFAULT NULL,
  `ilosc_cp` double DEFAULT NULL,
  `ilosc_cp_txt` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `id_rekordu` decimal(11,0) DEFAULT NULL,
  `upd_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci

;

CREATE TABLE test_daneb.`og` (
  `ksiega_rok` double DEFAULT NULL,
  `ksiega_nr` double DEFAULT NULL,
  `ksiega_poz` double DEFAULT NULL,
  `ksiega_nr_dziecka` double DEFAULT NULL,
  `kod_ow` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `kod_sw` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `nr_ks` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `id_pacjenta` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `data_przyj` date DEFAULT NULL,
  `data_zak` date DEFAULT NULL,
  `tr_przyj` decimal(11,0) DEFAULT NULL,
  `tr_wyp` decimal(11,0) DEFAULT NULL,
  `id_rekordu` decimal(11,0) DEFAULT NULL,
  `upd_date` date DEFAULT NULL,
  `data_urodz` date DEFAULT NULL,
  `wiek` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`om` (
  `KOD_OW` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `KOD_SW` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `indeks_mat` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `EAN` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `SUBST_CZYNNA_RODZAJ_WM` varchar(450) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `ZAWARTOSC_SUBST_CZYNNEJ` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `NAZWA` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `JEDN_MIARY` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `liczba_jedn_miary_txt` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `liczba_jedn_miary` double DEFAULT NULL,
  `JEDN_MIARY_OPAK` varchar(250) COLLATE utf8_polish_ci DEFAULT 'NULL',
  `liczba_zakup_opak_txt` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `liczba_zakup_opak` double DEFAULT NULL,
  `wartosc_txt` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `wartosc` double DEFAULT NULL,
  `ID_REKORDU` decimal(11,0) DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  KEY `nazwa_jedn_` (`NAZWA`,`JEDN_MIARY`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`pl` (
  `KOD_OW` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_SW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `INDEKS_MAT_PL` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_PL` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `DATA_WYK` date DEFAULT NULL,
  `NAZWA_PL` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `JEDN_MIARY_PL` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `LICZBA_PODANYCH_JEDN_MIARY_TXT` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `LICZBA_PODANYCH_JEDN_MIARY` double DEFAULT NULL,
  `KOSZT_JEDNOSTKI` double DEFAULT NULL,
  `KOSZT_JEDNOSTKI_TXT` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ID_REKORDU` decimal(11,0) DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=302181 DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`pr` (
  `KOD_OW` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_SW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_ZLEC` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `DATA_WYK` date DEFAULT NULL,
  `ICD_9` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NAZWA_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ILOSC_PR` double DEFAULT NULL,
  `CZAS_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ID_REKORDU` double DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=167236 DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`pr_hr` (
  `KOD_OW` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_SW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `DATA_WYK` date DEFAULT NULL,
  `ICD_9` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NAZWA_PR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_HR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NAZWA_HR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ILOSC_HR` double DEFAULT NULL,
  `CZAS_JEDNEGO_HR` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ID_REKORDU` decimal(11,0) DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59801 DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`sm` (
  `KOD_OW` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_SW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_SM` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `DATA_ROZP_PROD` date DEFAULT NULL,
  `DATA_ZAK_PROD` date DEFAULT NULL,
  `GODZ_ROZP_PROD` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `GODZ_ZAK_PROD` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_ZAKRESU` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_PROD` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ROZP_GL` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ROZP_WSP` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ROZP_POW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ILOSC_SM_TXT` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ILOSC_SM` double DEFAULT NULL,
  `ID_REKORDU` decimal(11,0) DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13656 DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;

CREATE TABLE test_daneb.`wm` (
  `KOD_OW` varchar(135) COLLATE utf8_polish_ci DEFAULT NULL,
  `KOD_SW` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `INDEKS_MAT_WM` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_OPK_WM` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `NR_KS` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `DATA_WYK` date DEFAULT NULL,
  `NAZWA_WM` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `JEDN_MIARY_WM` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `LICZBA_ZUZYTYCH_JEDN_MIARY_TXT` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `LICZBA_ZUZYTYCH_JEDN_MIARY` double DEFAULT NULL,
  `KOSZT_JEDNOSTKI` double DEFAULT NULL,
  `KOSZT_JEDNOSTKI_TXT` mediumtext COLLATE utf8_polish_ci DEFAULT NULL,
  `ID_REKORDU` decimal(11,0) DEFAULT NULL,
  `UPD_DATE` date DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=319289 DEFAULT CHARSET=utf8 COLLATE=utf8_polish_ci
;
