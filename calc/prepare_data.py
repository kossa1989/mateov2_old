

import pandas as pd
import sqlalchemy as sa
from calc.base_calc import UtilTools
from dictionary.tariff_scheme import wb17
#from pytar_calc.shared.db import session, engine  # TODO do rekonfiguracji
from models import query_history
from decouple import config
from database.db import DbEngine,DbSession
engine = DbEngine.create_engine('pytar')
session = DbSession.get_session(engine)

##### ----===DANE Z PIERWOTNEGO PYTARA===----
##### Dane zostały skopiowane, lecz zakomentowałem to, ponieważ nie powinny być tutaj na sztywno przypisywane.
##### Chciałem mieć deficjincję, by zawsze móc wrócić do standardowych zmiennych. - PK

data_description = wb17 # Zmieniono w stosunku oryginalnego PyTara i pobrano dane bezpoścrednio z tariff_scheme.wb17

# data_description = {
#     'patient_id': ['nr_ks', 'kod_sw'],
#     # pl_id, czyli grupowanie do wyliczenia przebiegu
#     'pl_id': ['nazwa_pl', 'jedn_miary_pl', 'nr_opk_pl'],
#     'pl_quantity': 'liczba_podanych_jedn_miary',
#     'wm_id': ['nazwa_wm', 'jedn_miary_wm', 'nr_opk_wm'],
#     'wm_quantity': 'liczba_zuzytych_jedn_miary',
#     'pr_id': ['icd_9', 'nazwa_pr'],
#     'pr_quantity': 'ilosc_pr',
#     # prices, czyli grupowanie do obliczenia ceny leku
#     'pl_prices': ['nazwa_pl', 'jedn_miary_pl'],
#     'wm_prices': ['nazwa_wm', 'jedn_miary_wm'],
#     'om_prices': ['nazwa', 'jedn_miary'],
#     'pr_prices': ['icd_9', 'nazwa_pr'],
#     'cp_prices': ['icd_9', 'nazwa_pr'],
#     'wm_unit_price': ['cena_jednostki'],
#     'rok': '2017',
# }
#
options = {'case_group': ['kod_prod', 'kod_sw', 'nr_ks'],
           'fake_data': True,
           'path': r'T:\organizacyjne_robocze\tmp\pytar_test',
           'schema': 'wb17',
           }

data_description = data_description.update(options)

username = 'm.marczak'
#
# query_sm_table_name = 'tmp.query_sm_%s' % uid  # ZAKOMENTOWANE, Bo chyba nigdzie nie uzywane
#
query_sm_sql_query = """
        create table %s as
        select t1.nr_ks, t1.kod_sw, t1.kod_prod, '1' as kod_dod
        from daneb.sm t1 inner join daneb.og t2 on t1.kod_sw=t2.kod_sw and t1.nr_ks=t2.nr_ks
        where kod_prod like "5.51.01.0006097"
"""



class QuerySm(UtilTools):
    """QuerySm class prepares patients population for analysis. Query is used to get patients and create entry
    in metadata table. Stores query_sm in self.query_sm."""

    def __init__(self, sql_query, uid, nr_ks_odrzucone=None, **kwargs):
        """Checks if there is entry about this analysis in query_sm_all or adds one if not."""
        super(QuerySm, self).__init__()
        self.uid = uid
        self.table_name = 'tmp.query_sm_%s' % self.uid
        self.query = sql_query % self.table_name
        self.query_sm_table_name = 'tmp.query_sm_%s' % self.uid
        self.engine = engine
        self.kwargs = kwargs
        # qsm_obj = session.query(pytar.Query_sm_all).filter(pytar.Query_sm_all.path == self.kwargs['path']).first() ##### nieużywany nawet w pierwotnym pytarze
        self.get_query_sm()

        if nr_ks_odrzucone:
            # 26 02 19 - nie rozumiem co tu sie dzieje/dlaczego
            qsm_dedup = self.query_sm[self.kwargs['patient_id']].drop_duplicates()
            self.query_sm = self.query_sm.merge(qsm_dedup, on=self.kwargs['patient_id'], how='inner')

    def dispatch(self):
        """Main method to add metadata and get df from database."""
        self.get_query_sm()

    def create_query_sm_table(self):
        self.execute_query(self.engine, self.query, raise_excpetions = True)

    def add_qsm_to_register(self):
        """Adds entry to db"""

        query_sm_wpis_do_db = query_history.Query_sm_all(path=self.kwargs['path'], query_sm=query_sm_sql_query,
                                                         ip=config('IP_ADDR'))
        session.add(query_sm_wpis_do_db)
        session.commit()

    def get_query_sm(self):
        """Retrieves query_sm data from database."""
        try:
            self.query_sm = pd.read_sql_query('select * from %s' % self.query_sm_table_name, self.engine)
        except sa.exc.ProgrammingError:
            self.create_query_sm_table()
            self.add_qsm_to_register()
            self.query_sm = pd.read_sql_query('select * from %s' % self.query_sm_table_name, self.engine)

        self.columns = self.query_sm.columns
        self.validate()

    def validate(self):
        """Validates if query_sm has duplicated rows."""
        if not self.query_sm[self.query_sm[self.kwargs['patient_id']].duplicated()].empty:
            raise Exception(
                'Query SM zawiera duplkaty, poprawne query sm zawiera jeden wiersz na jednego pacjenta (kod_sw, nr_ks)')
