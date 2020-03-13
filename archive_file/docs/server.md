## Obsługa serwera

Program działa w trybie serwera na Django 2.2. W Django został zmodyfikowany ROOT_URL. Serwer czerpie z kodu, który znajduje się w równoległym folderze, więc przy uruchamianiu serwera należy zmodyfikować pythonpath serwera:
 
    manage.py {some cmd} --pythonpath={/sciezka/do/kodu/pytara} --settings=server.server.settings
    
Przy uruchamianiu komend do zarządzania serwerem należy zmieniać ścieżkę do pythonpath na swoją w  wersji developerskiej. Zmiana ścieżek powstała w konsekwencji dodania do folderu z rootem django folderu z pytarem i koniecznosci rozszerzenia ścieżki wyszukiwania modułów.

Przy ustawianiu **skryptu** uruchamiającego **serwer w pycharmie** należy w parametrach dodać `--pythonpath` i `--settings` jak wyżej.

#### Start serwera

Z poziomu katalogu root'a pytara (tam gdzie są foldery pytar i server):

    /path/to/python manage.py runserver 0.0.0.0:9011 --pythonpath={/sciezka/do/kodu/pytara} --settings=server.server.settings
    
np z poziomu folderu D:\pytar:

    .\.venv\Scripts\python.exe .\server\manage.py runserver 0.0.0.0:9011 --pythonpath=D:\pytar --settings=server.server.settings