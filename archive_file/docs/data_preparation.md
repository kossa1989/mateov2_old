## Przygotowanie danych

Dane, które są obecnie w bazie wymagają aktualizacji wraz z aktualizowaniem bazy WB17 przez zespoł DPD. Aby zaktualizować dane należy wygenerować pliki CSV z bazy SAS'a i zaczytać pliki do MySQL'a.

1. Na SAS'ie trzeba włączyć kod, który został wklejony do pliku pytar_calc.models.sas_daneb_prep.txt. Program sasowy znajduje się również w lokalizacji `T:\organizacyjne_robocze\pytar_wyciagnie_danych.egp`
1. Do wygenerowania plików csv z bazy służy skrypt Python, który znajduje się w pytar_calc.models.wgranie_danych.py, skrypt powstał na podstawie notebooka znajdującego się na maszynie aotmitsassrv1 w sciezce `C:\Users\m.marczak\wgranie_danych.ipynb`. Skrypt odwołuje się do plików csv z serwera aotmitsassrv1 więc powinien być tam wywoływany. Jeżeli chcesz wykonać skrypt jako notebook (np do debugowania, nauki itd) to włącz na aotmitsassrv1 Anaconda Navigator i tam uruchmon Jupyter Notebook. Potem włącz odpowiedni skrypt i wywowuj kolejno komórki.
1. Jeżeli zmieniają się słowniki, to nalezy włączyć program znajdujący się w `scripts/load_dicts.py` żeby program zaczytał nowe słowniki.