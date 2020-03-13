import unittest
import os
print(os.getcwd())
from pytar_calc.models.daneb import engine



class TestDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('create_tables.sql', 'r') as sql_file:
            sql = sql_file.read()
            for i in sql.split(';'):
                if i.strip():
                    engine.execute(i)

        with open('inserts.sql', 'r') as sql_inserts:
            sql = sql_inserts.read()
            for i in sql.split(';'):
                if i.strip():
                    engine.execute(i)

    def test_db(self):
        pass

    @classmethod
    def tearDownClass(cls):
        # engine.execute("drop database test_daneb;")
        pass

if __name__ == '__main__':
    unittest.main()
