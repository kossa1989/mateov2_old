import datetime
import os
from pathlib import Path
from shutil import copyfile
import pandas as pd
from sqlalchemy.orm import sessionmaker

# from pytar_calc.shared import config  # plik config został przeniesiony do .env dlatego tutaj zmienione zostało na config('zmienna')
from models.externals import Dicts
from nothing_important.helper import Logger
from nothing_important.helper import Md5Calculation
# from pytar_calc.shared.db import engine #TODO zmiana configu DB
from decouple import config
from database.db import DbEngine
engine = DbEngine.create_engine('pytar')
# tworzy sesje do db
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class FileNotChanged(Exception):
    pass


class DictUpdate(Md5Calculation):
    """Klasa słuzy do kopiowania slownikow i zarzadzania wersjami slownikow. Tworzy wpis za kazdy nowy slownik. Główna metoda to add_dict, ona wywołuje
    pozostałe potrzebne do prawidłowego dodania i skopiowania słownika."""

    def __init__(self, type):
        self.type = type.upper()
        self.root = config('DICTIONARIES_ROOT_PATH')
        self.last_version = self.get_last_version()
        self.logger = Logger(self.type)

    def get_last_version(self):
        """Retrieves last version of uploaded dictionary."""
        return session.query(Dicts).filter_by(type=self.type).order_by(Dicts.creation_date.desc()).first()

    def get_newest_file_path(self):
        """Return path of newly added file."""
        path = self.root + '/' + self.type + '/'
        try:
            files = os.listdir(path)
        except FileNotFoundError:
            os.mkdir(path)
            files = os.listdir(path)
        timestamps = [(i, os.path.getmtime(path + i)) for i in files]
        self.newest_file = sorted(timestamps, key=lambda x: x[1]).pop()
        self.newest_file_path = path + self.newest_file[0]
        self.newest_file_path = Path(self.newest_file_path).absolute().__str__()
        return self.newest_file_path

    def copy_file_to_internal_storage(self):
        """Copies file to structured dir with dictionaries"""
        datetimestr = self.last_modified.strftime("%Y_%m_%d_%H_%M")
        self.output_path = Path(
            config('DICTIONARIES_OUTPUT_PATH') + '/' + self.type + '_' + datetimestr + '.xlsx').__str__()
        copyfile(self.newest_file_path, self.output_path)

    def insert_info_to_db(self):
        """Inserts to Dict table information about imported file."""
        new_file = Dicts(name=self.newest_file[0],
                         last_modified=self.last_modified,
                         checksum=self.md5,
                         type=self.type,
                         path_input=self.newest_file_path,
                         path_output=self.output_path,
                         path_pickle=self.output_path + '.pkl')
        self._dict = new_file
        session.add(new_file)

    def copy_file_and_store_metadata(self):
        """Copies file and stores its metadata in db."""
        self.copy_file_to_internal_storage()
        self.insert_info_to_db()

    def add_dict(self):
        """High level method to add new dictionary."""
        try:
            newest_path = self.get_newest_file_path()
        except IndexError:
            # jezeli nie istnieje plik, katalog ze slownikiem jest pusty
            print('Katalog ze słownikiem jest pusty')
            self.logger.add('Katalog ze słownikiem jest pusty')
            return None
        self.md5 = self.calculateMD5(newest_path)
        self.os_timestamp = self.newest_file[1]
        self.last_modified = datetime.datetime.fromtimestamp(self.os_timestamp)

        try:
            # if latest file wasnt in database
            if self.last_version.checksum != self.md5:
                self.copy_file_and_store_metadata()
            else:
                # print('Suma kontrolna poprzedniego słownika jest taka sama, pliki się nie zmieniły.')
                raise FileNotChanged('Plik się nie zmienił.')
        except AttributeError:
            # nie ma pozycji w tabeli slownikowej, pierwsze dodanie pliku
            self.copy_file_and_store_metadata()


class DictPrep:
    """Ta klasa służy do przygotowania instancji wpisu słownikowego. Usuwa duplikaty według wskazanych kolumn z Excela i przygotowuje pickla"""

    def __init__(self, dictUpdateInstance, dedups_columns):
        self.dict = dictUpdateInstance
        self.logger = Logger(self.dict.type)
        self.df = self.load_dict()
        self.path = config('DICTIONARIES_OUTPUT_PATH')
        self.dedups_columns = dedups_columns

    def load_dict(self):
        """Reads dict file and clean up columns."""
        print('ładuję słownik %s' % self.dict.type)
        skiprows = 0
        if self.dict.type=='FK_SZCZEGOLOWY':
            skiprows=1
        df = pd.read_excel(self.dict.newest_file_path, skiprows=skiprows)
        try:
            df.columns = [i.lower() for i in df.columns]
        except AttributeError:
            print('Sprawdź nagłówki kolumn w tabeli, możliwe wartości liczbowe, ze względu na brak metody str.lower()')
        str_type_cols = df.select_dtypes('object')
        df[str_type_cols.columns] = str_type_cols.apply(lambda x: x.astype(str).str.strip())
        return df

    def delete_duplicates(self):
        """Deletes duplicated rows"""
        df = self.df.drop_duplicates(self.dedups_columns)
        self.df = df

    def check_one_proc_multi_abc(self):
        """Sprawdza czy jeden wpis nie ma przypisanych kilku wierszy"""
        # usuwa duplikaty, kiedy wszystkie columny są rozne
        a = self.df.drop_duplicates()
        # sprawdza czy do jednej procedury nie są przypisane dwa ABC
        dups = a[a.duplicated(self.dedups_columns, keep=False)]
        if not dups.empty:
            self.logger.add('Slownik zawiera kilka przypisań do jednego rekordu w grupie')
            self.delete_duplicates()

    def pickle_dict(self):
        """Saves file to pickle"""
        self.df.to_pickle(self.dict.output_path + '.pkl')

    def prepare_dict_and_save(self):
        """"""
        # jezeli mozna usunac duplikaty to usuwa
        if self.dedups_columns:
            self.check_one_proc_multi_abc()
        # zapisuje tabele slownikowa w postaci pickla
        self.pickle_dict()
        # commit db to add rows
        session.commit()
        session.close()

    def __str__(self):
        return self.dict.newest_file_path


# key is dict name, value is the list of columns to check duplicated rows on
# or None if no check needed
dictionaries_list = {
    'hr': ['kod_sw', 'nr_opk_hr', 'nazwa_hr_sw', ],
    'fk_ogolny': None,
    'fk_szczegolowy': None,
    'slo_abc': ['icd_9'],
    'slo_abc_2': ['icd_9'],
}

if __name__ == '__main__':
    for k, v in dictionaries_list.items():
        try:
            t = DictUpdate(k)
            t.add_dict()
            p = DictPrep(t, v)
            p.prepare_dict_and_save()
        except FileNotChanged:
            print('No changes in dict %s.' % k)
