# slownik hr
# slownik pr
# pliki fk od dziewczyn
# slo kat med i kat opk
# slowniki wrzucimy do pickla, przy wlaczaniu analizy program porowna date ostatniego pliku slownikowego
# z data pliku obecnego, jezeli ostatnia data byla wczesniej, to znaczy ze czas zaktualizowac slownik,
#  wtedy do tabeli ze slownikami
# wchodzi nowy rekord z nową datą i sciezką do nowego słownika. Przy włączaniu programu program łąduje najnowszy słownik
# zgodnie z tabelą zawierającą info o slownikach
# do pamięci.

# asd

from .query_history import BasicColumnsMixin

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Dicts(Base, BasicColumnsMixin):
    __tablename__ = 'dicts'
    name = sa.Column(sa.String(length = 100))
    path_input = sa.Column(sa.String(length = 500))
    path_output = sa.Column(sa.String(length=500))
    path_pickle = sa.Column(sa.String(length=500))
    last_modified = sa.Column(sa.DateTime)
    checksum =  sa.Column(sa.String(length=32))
    type = sa.Column(sa.String(length = 20))