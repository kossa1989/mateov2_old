## Opis architektury

Podstawą do wyliczenia kosztów w dziedzinie zdarzeń medycznych (tj. lekach [PL], wyrobach [WM], procedurach [PR] itp.) jest klasa `Calc`, po której dziedziczą pozostałe klasy. Wszystkie klasy, które po niej dziedziczą powinny eksponować metodę `calc_tariff()`, która jest ostatnią metodą przez uzyksaniem wyniku taryfy, ktory znajdzie się w w atrybucie tariff. 

Calc udostępnia metodę `Calc.tar_sr_il()`, która agreguje dane i tworzy przebiegi referencyjne zapisując później wynik w atrybucie  `tar_sr_il`. Przebieg dalszej analizy polega na dokładaniu informacji do DataFrame'a `tar_sr_il`, tak że na koniec analizy `tar_sr_il` odpowiada tabelom z pliku `ABC.xlsx`.

Rekomendowaną metodą obiegu informacji jest dołączanie do instancji klas dziedzinowych kluczowych tabel, ponieważ takie podejście ułatwia debugowanie i pozwala na dostęp do ważnych zbiorów z każdego miejsca instancji.

Istotne punkty, które powinny być zaimplemetnowane w klasach dziedzinowych:

1. Metoda `create_tar()`, która zajmuje się interakcją z bazą danych i powinna tworzyć `DataFrame` o nazwie `tar` jako atrybut instancji klasy dziedzinowej. DataFrame `tar` powinien zawierać wszystkie informacje potrzebne do wyliczenia cząstkowej taryfy i dane z query_sm potrzebne do agregacji. Poprzez implementację własnych metod `create_tar()` możliwe jest dodanie obsługi innych źródeł danych w tym np. Postgresql, SAS, Vertica, Hive/Impala itd.
2. Metoda `create_tar_sr_il()` jest odpowiedzialna za stworzenie zagregowanego przebiegu na badaną grupę klinicznę (np. jeden pacjent lub wszyscy pacjenci z kodem produktu lub inna dowolna agregacja).
1. Metoda `generate_event_cost()` tworzy nową kolumnę w `tar_sr_il` o nazwie `koszt_zdarzenia`, w której znajduje się koszt wystąpienia zdarzenia medycznego zdefiniowanego w wierszu. Do obliczenia kosztu zdarzenia wykorzystane są dane zawarte w `tar_sr_il` (`sr_wyst_w_przyp` i `koszt_do_analizy`).
2. Możliwość zaciągania pliku `ABC.xlsx` i prowadzenia analizy w opraciu o ten plik. Powinno istnieć miejsce, gdzie możliwe będzie nadpisanie tabeli, bądź nadpisanie wybranych kolumn wartościami z pliku `ABC.xlsx`. Nowe wartości powinny mieć wpływ na wartość taryfy i powinny wynikać ze zmiany przebiegu klinicznego lub cen.   
1. Metoda `calc_tariff()`, która wywołuje wszystkie metody potrzebne do obliczenia taryfy dzinowej. Metoda powinna zapisywać taryfę w zbiorze self.tariff, który jest później wykorzystywany do stworzenia sumy wszystkich taryf cząstkowych i obliczenia ostatecznej taryfy.
2. Ostateczny zbiór z taryfami dziedzinowymi, które mogą być później połączone powinien nazywać się `tariff`, czyli możemy się do niego dostać poprzez `instancja.tariff`.

Stworzenie jednej taryfy powinno być zrobione przez połączenie wszystkich taryf dziedzinowych względem klucza z zachowanie dodatkowych informacji z query_sm.

## User story

Proces pracy z taryfą:

1. Użytkownik wchodzi na strone i loguje się swoimi poświadczeniami AD po LDAP. Na stronie wybiera jeden z dostępnych szablonów analiz lub tworzy nowy jeżeli analiza wymaga odrębnego podejścia.
2. Wybiera istniejącą taryfę (analizy, które były uruchamiane wcześniej przypisują się do konta użytkownika i są później łatwo dostępne przez kliknięcie w zapisanych analizach) lub tworzy nową taryfę podając ścieżkę na dysku T. 
1. Uzytkownik definiuje parametry taryfy określając postępowanie (schemat danych źródłowych np. `"wb17"` dla danych ze współpracy bieżącej z 2017 roku) i poziom agregacji.
2. Użytkownik wybiera dodatkowe opcje np. czy dopuszczać błędy (błędy, które pojawią się w trakcie analizy są zapisywane, a następnie generowane do pliku `messages.txt`).
1. Użytkownik włącza taryfę, generują się pliki `ABC.xlsx` i plik z taryfą w odpowiednim folderze. Folderem, w którym generują się wszystkie pliki jest folder podany przy uruchamianiu analizy.
2. Użytkownik poprawia plik `ABC.xlsx` i ponownie włącza analiza, do momentu zakończenia pracy.

## Workflow informacji

1. Informacje są pobierane za pomocą rodziny metod create_tar.
2. Obecnie jest stworzone połączenie do bazy MySQL ale to może zostac łątwo zmienione poprzez nadpisanie metod create_tar które **jako jedyne** prowadzą interakcje z bazą danych.
2. Kolejne zaczytania potrzebują wzorcowego pliku ABC na którym wywoływana jest metoda `generate_event_cost()`.
1. Przy uruchomieniu program sprawdza czy ten folder jest juz w bazie.
    1. TAK: pobiera ABC i włącza metody z rodizny generate_event_costs. Jeżeli nie ma ABC to zachowuje się tak jakby analiza była pierwszy raz.
    2. NIE: Uruchamia od początku analizę.
