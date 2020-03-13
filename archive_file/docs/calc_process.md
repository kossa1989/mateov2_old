## Opis procesu obliczeniowego i architektury

#### Słowniczek

* **zdarzenie medyczne** - wszystkie działania wykonywane pacjentowi podczas hospitalizacji. Na przykład podanie leku, wyrobu, wykonanie procedury itd.
* **agregacja** - wykonanie podsumowań na danych (np. obliczenie średniej) z użyciem grupowania
* **ABC** - plik, który generuje się w toku analizy i umożliwiaj analitykom zmianę parametrów.
* **query_sm** - tabela, która definiuje pacjentów właczonych do analizy. Tabela musi zawierać nr_ks i kod_sw jako wskazanie na pacjenta, plus wszelkie dodatkowe kolumny, które są umieszczone w agregacji. Np. jeżeli analiza jest na pacjenta, kod świadczeniodawcy i kod produktu to do query_sm powinno być dodane kod_prod.
* **OPK** - **O**środek **P**owstawania **K**osztów, jednostka organizacji szpitala, która najczęściej odzwiercielda oddziały (np. Oddział Kardiologii)
* **ABC** - plik parametryczny lub kategoryzacja procedur na grupy A, B, C, D, S itd.

##### Opis głównego procesu

1. Analiza jest włączana poprzez widok na stronie django (`server.analysis.view.run_pytar`).
1. Po wpisaniu informacji wymaganych do zdefiniowania analizy należy kliknąć na stronie przycisk `Uruchom` i analiza wystartuje.
1. Szablony (główne sterowanie procesem obliczeniowym) są zdefiniowane w `pytar_calc.analytic_templates`. W szablonie zawarte są wszystkie metody potrzebne do wykonania całej analizy i obliczenia taryfy świadczeń. Szablon również czuwa nad przebiegiem analizy i nad plikiem `ABC.xlsx`, który zawiera parametry do analizy. Jeżeli w folderze wskazanym w definicji analizy nie znajduje się plik `ABC.xlsx` to szablon go tworzy. Jeżeli plik już tam jest, to szablon analityczny go zaczytuje i wykorzystuje w dalszych fazach analizy.
1.  Za przeprowadzenie samej analizy odpowiada metoda `main()` szablonu analitycznego, w niej jest zapisana cała logika przetwarzania.
1. W pierszej kolejności metoda sprawdza czy w folderze istnieje plik ABC, jeżeli nie to znaczy że analiza będzie przprowadzana od początku. Wtedy wywołana jest dodatkowa metoda del_obsolete_tables(), która usuwa tabele z bazy danych jeżeli w określonym miejscu była już wcześniej prowadzaona analiza.
1. Następnie analiza jest inicjowana, tworzone są podstawowe tabele potrzebne w późniejszych krokach. Do tego słuzy metoda **SetUp()[opisana dalej]**.
1. Następnie włączana jest metoda **run_basic()[opisana dalej]**, która włącza podstawowe metody dla wybranych analiz. Podstawowe metody to znaczy metody, które są wymagane do pierwszej agregacji danych (czyli agregacji tworzącej plik `ABC.xlsx`).
1. Później wykonywany jest test czy plik ABC istnieje w folderze. Jeżeli istnieje, to na miejsce stworzonych wcześniej agregacji podstawiane są tabele zaczytane z pliku ABC.
1. Następnie wywołana jest metoda **generate_event_costs()[opisana dalej]**, której zadaniem jest stworzenie nowego podsumowania dla danych i ponowne obliczenie kosztów zdarzeń medycznych.
1. Później tworzony i zapisywany jest nowy plik ABC.xlsx uwzględniający wprowadzone parametry.Stary plik ABC jest kopiowany i do jego nazwy jest dołożona aktualna data (tak, żeby były przechowywane wszystkie archiwalne wersje ABC). 
1. Następnie tworzona i zapisywana jest taryfa obliczona z nowych danych.
1. Na końcu do folderu z analizą zapisywane są automatyczne komunikaty, które mówią o problemach/zagrożeniach analizy. 

### Metoda set_up()

Metoda zajmuje się przygotowaniem danych, które będą dzielone przez wszystkie klasy analityczne. Do danych dzielonych zaliczają się:

* Dane FK

    Dane zawierające informacje dotyczące kosztów funkcjonowania ośrodków powstawania kosztów i definicje OPK'ów. Koszty wykorzystywane są głównie przy analizie procedur i osobodnia, w innych miejsach wykorzystywane są definicje OPK'ów (często jest tak, że w danych źródłowych mamy same kody świadczeniodawców i nr_opk, a potem w toku analizy dołączamy nazwę OPK która jest bardziej ilustratywna niż numer).
        
* Dane query_sm (o populacji pacjentów) - query_sm zostało dokładniej opisane w słowniczku.
    
* Dane ogólne (plik OG) - dane ogólne o hospitalizacji potrzebne do dalszej analizy i obliczenia taryfy. Tutaj liczą się średnie czasy hospitalizacji i średni wiek. Średnie czasy mogą być później potrzebne do obliczenia średnich kosztów osobodnia.

* Słownik z definicją analizy (opis formatu danych [`pytar_calc.shared.data_descriptions`] i parametry inicjalizujące analizę [np. ścieżka analizy, kod do query_sm, poziom agregacji i inne]). Słownik z definicją formatu danych zawiera nazwy kolumn z danych, które pełnią określoną rolę w analizie. Np. w słowniku istnieje klucz pl_id, do którego jest przypisana lista kolumn określających jednostkę leku. 

### Metoda run_basic()

Metoda włącza wszystkie analizy dziedzinowe (analiza PL, WM, PR), które powinny zostać wykonane w celu przeprowadzenia podstawowej agregacji danych. Wszystkie kroki do wykonania analiz dziedzinowych znajdują się w metodzie `basic_X` gdzie X to nazwa dziedziny np. base_pl to podstawowa analiza leków.

Na końcu metody `run_basic()` jest liczony koszt osobodnia za pośrednictwem metody `analyse_osd()`. Metody z rodziny `basic` np. `basic_pl` są omówione w dalszej części. Kolejność włączania metod basic zawartych w `run_basic()` jest dowolna. 

### Opis parametrów inicjujących

Przykładowy plik z definicją metadanych (słownik z definicją analizy) i parametrów inicjujących analizę:

    # parametry inicjujące
    options = {'case_group': ['kod_prod', 'kod_sw', 'nr_ks'],
               'path': r'T:\organizacyjne_robocze\tmp\pytar_test',
               'schema': 'wb17',
               'price_priority': 'cena_z_pliku'
               }

    # definicja ról
    wb17 = {
    'patient_id': ['nr_ks', 'kod_sw'],
    'pl_id': ['nazwa_pl', 'jedn_miary_pl', 'nr_opk_pl','indeks_mat_pl'],
    'pl_quantity': 'liczba_podanych_jedn_miary',
    'wm_id': ['nazwa_wm', 'jedn_miary_wm', 'nr_opk_wm','indeks_mat_wm'],
    'wm_quantity': 'liczba_zuzytych_jedn_miary',
    'pr_id': ['icd_9', 'nazwa_pr','nr_opk_pr'],
    'pr_quantity': 'ilosc_pr',
    'join_cols_pr_hr':['icd_9', 'nazwa_pr','nr_ks_pr','data_wyk'],
    'pl_prices': ['nazwa_pl', 'jedn_miary_pl','indeks_mat_pl'],
    'wm_prices': ['nazwa_wm', 'jedn_miary_wm','indeks_mat_wm'],
    'om_prices': ['nazwa', 'jedn_miary','indeks_mat'],
    'pr_prices': ['icd_9', 'nazwa_pr'],
    'cp_prices': ['icd_9', 'nazwa_pr'],
    'wm_unit_price': ['cena_jednostki'],
    'rok': '2017',
    }
    
####### Opisy kolumn:

* **case_group** - grupowanie w analize, lista kolumn do grupowania. W query_sm powinny się znaleźć te kolumny.
* **path** - ścieżka gdzie będzie odpalana analiza
* **price_priority** - czy domyślnie cena dla PL/WM ma być z pliku czy z cennika
* patient_id - wskazanie które kolumny są odpowiedzialne za wydzielenie pacjenta
* pl_id - wskazanie identyfikatora leku, ie ktore kolumny określają lek
* pl_quantity - wskazanie kolumny, która mówi o ilości podanych leków
* wm_id - wskazanie identyfikatora wyrobu medycznego, ie ktore kolumny określają wyrób medyczny
* wm_quantity - wskazanie kolumny, która mówi o ilości podanych wyrobów medycznych
* pr_id - wskazanie identyfikatora procedury, ie ktore kolumny określają jedną procedurę
* pr_quantity - wskazanie kolumny, która mówi o ilości wykonanych leków
* join_cols_pr_hr - wskazanie kolumn do połączenia PR z PR_HR
* pl_prices - okreslenie które kolumny będą służyły do wyliczenia ceny leku z pliku PL (sprawozdane koszty jednostkowe), później względem tych samych kolumn dokładane są ceny do PL
* wm_prices - okreslenie które kolumny będą służyły do wyliczenia ceny wyrobu z pliku WM (sprawozdane koszty jednostkowe), później względem tych samych kolumn dokładane są ceny do WM 
* om_prices - lista kolumn do wyliczenia cen z WM
* pr_prices - lista kolumn do wyliczenia cen z PR
* cp_prices - lista kolumn do wyliczenia cen z CP
* wm_unit_price - która kolumna jest odpowiedzialna za cenę w zakładce WM
* rok - rok postępowania
