import sqlalchemy as sa
from sqlalchemy import orm
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# done

class DbEngine:

    def create_engine(name):
        engine_conf = config(name)
        engine = sa.create_engine(engine_conf, pool_pre_ping=True)
        return engine


class DbSession:
    def get_session(engine):
        session = orm.Session(engine)
        return session

