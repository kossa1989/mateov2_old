## Słowniki i dane zewnętrzne

Słowniki są przechowywane w ścieżce zdefniowanej w `pytar_calc.shared.config` w zmiennej `DICTIONARIES_OUTPUT_PATH`. Tam są serializowane do postaci obiektów pickle, skąd są zaczytywane do analizy. Słowniki nie są przechowywane w bazie danych, są raczej lustrzanym odbiciem plików Excel przechowywanym z miejscu o którym wiedzą tylko programiści. Akualizacja słowników może odbywać się poprzez dopisanie do istniejącego Excela nowych wierszy i ponowne zaciągnięcie słowników lub wstawienie nowego Excela z dodatkowymi wierszami. Ewidencja aktualnych słowników jest w tabeli pytar.dicts na serwerze mysql na aotmitsassrv1. 

W ramach prowadzonej analizy Taryfikator potrzebuje następujących słowników i danych zewnętrznych:

* słownik personelu PR_HR

    Zawiera okrślenie personelu (przez kolumny kod_sw, nr_opk, nazwa HR), jest wykorzystywany w analizie do ujednolicenia nazewnictwa personelu
        
* plik FK z danymi finansowo-księgowymi (dane szczegółowe na podmiot)

    Plik z danymi finansowo-księgowymi, dane zawierają wartości na podmiot leczniczy. Pierwszy wiersz pliku to legenda, więc pierwszy wiersz jest usuwany przez skrypt, nie trzeba go usuwać ręcznie. Drugi wiersz to nagłówki.

* słownik procedur ABC (przypisanie analityków)
* słownik procedur ABC (przypisanie dra Chajdasa)

Aby zaktualizować słowniki należy umieścić odpowiednie pliki w folderze zdefiniowanym w pliku konfiguracyjnym (pytar/shared/config.py) w zmiennej DICTIONARIES_ROOT_PATH. Pliki powinny być umieszczone w odpowiednim katalogu w zależności od rodzaju.

Wszystkie modyfikacje plików słownikowych są zapisywane do tabeli dicts w bazie pytar. Stamtąd jest brana najnowsza wersja wszystkich słowników.

Słowniki dla pytara są przechowywane w ścieżce:
`T:\organizacyjne_robocze\012_Taryfikator\slowniki\pytar`

#### Informacje techniczne

Słownik danych szczegółowych jest przechowywany w klasie FkSzcz. FkSzcz jest przekazywana do instancji dziedzinowych (Pl, Wm, Pr itd) poprzed argument słowa kluczowego fk=FkSzcz(). Następnie można odnosić się do klasy fk poprzez self.fk_class (przypisanie zdefiniowane w konstruktorze).


