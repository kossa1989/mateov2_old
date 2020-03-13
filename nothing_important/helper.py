import datetime
import hashlib
import os
from shutil import copyfile
import sqlalchemy

import pandas as pd


class Md5Calculation():
    def calculateMD5(self, filename, block_size=2 ** 20):
        """Returns MD% checksum for given file.
        """

        md5 = hashlib.md5()
        try:
            file = open(filename, 'rb')
            while True:
                data = file.read(block_size)
                if not data:
                    break
                md5.update(data)
            file.close()
        except IOError:
            print('File \'' + filename + '\' not found!')
            return None
        except:
            return None

        return md5.hexdigest()

#TODO ta klasa musi zostac przeniesiona ?? Trzeba sprawdzić czy nie jest wykorzystywana przy ABC?
class ExcelFile():
    """Handles Excel files in analysis."""

    def __init__(self, filename, rel_path=False, exports={}, **kwargs):
        self.path = kwargs['path']
        if rel_path:
            self.path = self.path + '/%s' % rel_path
            self.exports = exports
        self.filename = filename
        self.suffix = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    def check_if_dir_exists(self):
        """Checks if dir exists and creates new one if it doesnt."""
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def create_backup(self):
        """Creates copy of file by appending datetime to name."""
        if '%s.xlsx' % self.filename in os.listdir(self.path):
            outfile = self.path + r'\%s_%s.xlsx' % (self.filename, self.suffix)
            infile = self.path + r'\%s.xlsx' % self.filename
            copyfile(infile, outfile)
        else:
            pass

    def write_excel(self):
        """Create Excel file from dict key:value, where key is sheetname and value is pd.DataFrame.

        Dict should be specified in class constructor.
        """
        self.check_if_dir_exists()
        self.create_backup()
        writer = pd.ExcelWriter(self.path + r'\%s.xlsx' % self.filename, engine='xlsxwriter')
        for i in self.exports:
            self.exports[i].to_excel(writer, sheet_name=i.upper(), index=True)
        writer.close()

#TODO to samo co wyżej
class AbcExcel(ExcelFile):
    """Handles logic in ABC file based on ExcelFile."""

    def __init__(self, **kwargs):
        super(AbcExcel, self).__init__(filename='ABC', **kwargs)
        self.kwargs = kwargs
        self.exports = {'pl': kwargs['pl'].tar_sr_il,
                        'wm': kwargs['wm'].tar_sr_il,
                        'pr': kwargs['pr'].tar_sr_il,
                        'pr_hr_pers_wagi': kwargs['pr'].pr_hr_pers_wagi,
                        'pr_hr_pers_czas': kwargs['pr'].pr_hr_pers_czas,
                        'pr_hr_infras_wagi': kwargs['pr'].pr_hr_infras_wagi,
                        'pr_hr_infras_czas': kwargs['pr'].pr_hr_infras_czas,
                        'baza_fk': kwargs['fk'].fk,
                        'nr_ks_odrzucone': pd.DataFrame({'nr_ks': [], 'kod_sw': []}),
                        }


class TariffExcel(ExcelFile):
    def __init__(self, **kwargs):
        super(TariffExcel, self).__init__(filename='taryfa', **kwargs)
        self.path = self.path + '\\taryfa_%s' % (self.suffix)
        self.exports = {'tariff':kwargs['tariff']}


class ShapesDoesntMatch(Exception):
    pass


""" do przerobienia/usuniecia po pozbyciu się pliku ABC - PK"""
class Freezer:
    """Class to archive past versions of ABC's files. Takes attrs arg (list of var names types pd.DataFrame) to archive."""

    def __init__(self, obj, attrs, table_type):
        self.obj = obj
        self.attrs = [attrs] if isinstance(attrs, str) else attrs
        self.now = datetime.datetime.now()
        self.outpath = obj.path / 'arch'
        self.table_type = table_type
        self.time_fmt = '%Y%m%d%H%M%S'
        # compression is infered from suffix
        self.suffix = 'pickle.gzip'

    def _freeze_df(self, attr, path):
        df = getattr(self.obj, attr, path)
        df_to_freeze = df.assign(date_frozen=self.now)
        if not self.outpath.exists():
            self.outpath.mkdir()
        df_to_freeze.to_pickle(path)

    def serialize_name(self, name):
        return '{0}_{1}_{2}.{3}'.format(self.table_type, name, self.now.strftime(self.time_fmt),self.suffix)

    def list_files(self, path):
        files = {}
        for i in path.rglob('*.%s' % self.suffix):
            # deserializes name
            tokens = i.name.split('_')
            table_type = tokens[0]
            name = tokens[1]
            dt = datetime.datetime.strptime(tokens[2].split('.')[0], self.time_fmt)
            files.setdefault(table_type, []).append((name, dt))
            # sort archived files asc to retrieve latest version
        return {k: sorted(v, key=lambda x: x[1]) for k, v in files.items()}

    def freeze(self):
        for i in self.attrs:
            frozen_name = self.outpath / self.serialize_name(i)
            if self.outpath.exists():
                files = self.list_files(self.outpath)
                # files is list of files with archived entries
                # need to subtract one from previous to get full history and calculate last ABC to
                # process current one and spot differences
            self._freeze_df(i, frozen_name)

# Pomocnicza klasa do wrzucania słowników do BazyDanych
class Export_dict_to_sql():
    def export_to_sql(self):
        path = "T:\\organizacyjne_robocze\\012_Taryfikator\\slowniki\\pytar\\SLO_ABC\\slo_abc_4_lipca_18.xlsx"

        engine_config = 'mysql+pymysql://daneb:QazWsx1324@aotmitsassrv1:3306/slowniki'

        engine = sqlalchemy.create_engine(engine_config)

        df = pd.read_excel(path)
        print('done read')
        df.to_sql(
            name='slo_abc',
            con=engine,
            index=False,
            if_exists='replace'
        )

# Funkcja przeniesiona z pliku logger.py z shared. Jest to plik logujący wiadomości jakie sie pokażą. Plik logger.py zniknął wtej wersji pytara
class Logger:
    msg_list = []
    def __init__(self, prefix):
        self.prefix = prefix
    def add(self,msg):
        self.msg_list.append(self.prefix + ' - ' + msg)
    def __str__(self):
        return str(self.__class__.msg_list)