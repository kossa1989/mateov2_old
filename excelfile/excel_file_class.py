import datetime
import os
from shutil import copyfile
import pandas as pd



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