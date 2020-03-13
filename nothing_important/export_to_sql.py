import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from sas7bdat_converter.converter import SASConverter
import sqlalchemy
import pymysql
from decouple import config


#Export CSV to MySQL

"""Function log the progress of BackUpper"""
class DbTool():
    dbconnector='pymysql'
    engine_config='mysql+%s://daneb:QazWsx1324@aotmitsassrv1:3306/test_42'

    def log_to_file(self, to_log):
        time_now = datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S")
        command_log = '[' + str(time_now) + ']' + " === " + to_log
        # print(command_log) #Test command_log
        f = open("cmd_logs.txt", "a+")
        f.write('MSG >>> ' + command_log + "\n")
        print(to_log)
        return

    def import_xlsx_to_mysql(self):
        dbconnector = 'pymysql'
        engine_config = 'mysql+%s://daneb:QazWsx1324@aotmitsassrv1:3306/onk42'
        dbconnector = 'pymysql'
        engine = sqlalchemy.create_engine(engine_config  % dbconnector)

        self.path_to_csv = {
            # 'cp': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\cp.xlsx',
            'og': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\mod\\og.xlsx',
            # 'og_wiek': 'T:\\organizacyjne_robocze\\012_Taryfikator\\test\\pk\\og_wiek.csv',
            # 'om': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\om.xlsx',
            # 'opk': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\opk.xlsx',
            # 'pl': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\pl.xlsx',
            # 'pr': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\pr.xlsx',
            # 'pr_hr': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\pr_hr.xlsx',
            # # 'pr_hr_csz_id': 'T:\\organizacyjne_robocze\\012_Taryfikator\\test\\pk\\pr_hr_csz_id.csv',
            # 'sm': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\sm.xlsx',
            # 'wm': 'T:\\organizacyjne_robocze\\012_Taryfikator\postepowanie_42_pytar_test\\bazaSAS\\wm.xlsx'
            # nfz_
        }

        self.parse_date_columns = ['upd_date', ]

        for key, value in self.path_to_csv.items():
            try:
                self.log_to_file('--==File {0} ==--'.format(value))
                self.log_to_file('--==Import data to DATAFRAME ==--')
                df = pd.read_excel(value)
                # df = pd.read_csv(value, low_memory=False, parse_dates = list_date)
                self.log_to_file('--==Exporting data to MySQL DB ==--')
                df.to_sql(
                    name=key,
                    con=engine,
                    index=False,
                    if_exists='replace'
                )
                msg_fin = "--==Export Data to MySQL finnished - table:{0}==..".format(key)
                self.log_to_file(msg_fin)
            except Exception as e:
                print(e)
                self.log_to_file(str(e))
                self.log_to_file("--== Error with exporting: {0}==--".format(key))
                print("--== Error with exporting{0}==--".format(key))

x = DbTool()
x.import_xlsx_to_mysql()