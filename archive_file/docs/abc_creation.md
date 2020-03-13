## Szczegółowy opis tworzenia agregacji do ABC

Dane do instancji dziedzinowych są pozyskiwane za pomocą rodziny metod create_tar(). Metody zajmują się interakcją z bazą danych i innymi źródłami i jako efekt działania zapisują `pd.DataFrame` do instancji dziedzinowej. W przypadku chęci dodania nowych źródeł danych (inna baza, inne pliki, inne dowolne źródło) należy modyfikować wyłącznie metody z rodziny create_tar(), ponieważ wszystkie późniejsze metody oczekują tylko `pd.DataFrame`'ów w atrybucie self.tar.

Analiza tworzenia agregacji zostanie przedstawiona na przykładzie pliku **PL**.

Kolejność wykonywania metod w celu przygotowania pierwszej agregacji do ABC.xlsx:

1. Inicjalizacja klasy dziedzinowej
1. Wywołanie `create_tar_sr_il()`
1. Wywołanie `calc_from_pricelist()`
1. Wywołanie `calc_from_unit_price()`
1. Wywołanie `add_pricelist()`
1. Wywołanie `add_unit_price()`


#### Inicjalizacja klasy dziedzinowej

    #1 self.pl = PlCalc('pl', self.query_sm, self.uid, og=self.og.og, fk=self.fk, **self.data_description)
    
W tym kroku tworzona jest instancja klasy PlCalc, która zajmuje się obliczeniem taryfy końcowej i przygotowaniem pliku ABC. Do instancji przekazujemy następujące argumenty:

* jakiej tabeli dotyczy (wpis `'pl'`)
* populację wejściową pacjentów (`self.query_sm`).
* unikalny identyfikator analiz generowany na podstawie hasha MD5 ze ścieżki (identyfikator jest unikalny, ponieważ z założenia w jednej ścieżce znajduje się jedna analiza) `self.uid`
* DataFrame OG zawierający informacje ogólne na temat agregacji
* Gotową klasę z danymi FK (`self.fk`)
* pozostałe parametry analizy jako rozpakowanie słownika (`**self.data_description`)

Aby w pełni zrozumieć co dzieje się podczas inicjalizacji należy przejść przez kontstruktor klasy dziedzinowej PlCalc i wszystkie pozostałe konstruktury, które są wywoływane tj:

    PlCalc>PlWmCalc>PlWmPrCalc>Calc
    
Klasa Calc jest nadrzędna do wszystkich innych, jest rodzicem każdej innej klasy. W konstruktorze klasy Calc przechwytywane są wszystkie parametry przekazywane do klasy dziedzinowej i zapisywane do tworzonej instancji. Dzięki takiemu podejściu w całym cyklu życia instancji dziedzinowej mamy dostęp do plików potrzebnych do przeprowadzenia analizy. Np:
    
    self.fk_class = fk
    self.fk = getattr(fk, 'fk', None)
    
W instancji dziedzinowej zapisywana jest klasa FK, a w atrybucie `self.fk` zapisywany jest sam plik z danymi finansowo księgowymi. Kontynuując przykład #1, po inicjalizacji możemy się odnosić do klasy FK: `pl.fk_class` lub do samego pliku finansowo księgowego: `pl.fk`.

#### Wywołanie create_tar_sr_il()

1. W pierwszym kroku wywoływane jest `create_tar()`, które przygotowuje dane źródłowe i zapisuje wszystkie wiersze odpowiadające temu query_sm do atrybutu `tar`.
1. Następnie ustalane jest grupowanie tj. lista kolumn względem których będziemy później grupować rekordy.
1. Kolejnym krokiem jest ustalenie średniej wystąpień w przypadku czyli określenie ile zdarzeń medycznych pojawia się na pacjenta w określonym grupowaniu - case_group.
1. Dodanie kolumn, które później będą służyły do wpisania współczynników (kolumny zaczynające od wsp lub gr_wsp)
1. Dodanie wieku i czasu (w przypadku agregacji średnich)
1. Sprawdzenie czy wiersze nie przemnożyły się podczas łączenia.
1. Zapisanie tabeli w instancji. 
