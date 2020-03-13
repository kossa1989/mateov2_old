""" Jest zmieniony plik z(oryg Pytara) models.pytar.py ... - PK
Nazwa niestety nie wiele mówiła, więc została zmieniona"""
# TODO trzeba w przyszłoci ten plik, zmienić podczas usuwania pliku excel ABC
import sqlalchemy as sa
import datetime
from sqlalchemy.ext.declarative import declarative_base
from database.db import DbEngine
engine = DbEngine.create_engine('pytar')
a = engine.connect()
Base = declarative_base()

class BasicColumnsMixin(object):
    id = sa.Column(sa.Integer, primary_key=True)
    creation_date = sa.Column(sa.DateTime, default=datetime.datetime.now)
    update_date = sa.Column(sa.DateTime, onupdate=datetime.datetime.now)

class Query_sm_all(Base, BasicColumnsMixin):
    __tablename__ = 'query_sm_all'

    path = sa.Column(sa.Text)
    query_sm = sa.Column(sa.Text)
    ip = sa.Column(sa.String(length = 17))

    def __repr__(self):
        return "query_sm nr %s, folder: %s" % (self.id, self.path[-10:])

class Pl_wm(Base, BasicColumnsMixin):
    __tablename__ = 'pl_wm'

    nazwa = sa.Column(sa.String(length = 500))
    jedn_miary = sa.Column(sa.String(length = 40))
    pl_wm = sa.String(length = 2)

# Query_sm_all.metadata.create_all(engine)

class AbcHistory(Base, BasicColumnsMixin):
    __tablename__='abc_history'
    user = sa.Column(sa.String(length = 40))
    query_sm_all_id = sa.Column(sa.Integer,
        sa.ForeignKey('query_sm_all.id'))


#engine = DbEngine.create_engine('pytar')