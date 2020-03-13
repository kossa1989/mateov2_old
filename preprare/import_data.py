#import helpfunction like logging etc.
from nothing_important.log_to_file import HelpFunc

import pandas as pd
import sqlalchemy
from decouple import config


class Import_Data_SQL(HelpFunc):

    def import_data_to_dataframe(self, table_name):
        dbconnector = config('dbconnector')
        engine = sqlalchemy.create_engine(config('engine_config')  % dbconnector)
        try:
            df = pd.read_sql_table(
                table_name,
                engine
            )
            #df.columns = [x.upper() for x in df.columns]
            df.columns = df.columns.str.upper()
            column_name = df.columns
            print(df)
            print(column_name)
            print(df.dtypes)
            self.log_to_file("DataFrame Data imported")
            return df, column_name
        except:
            print("Error with import Data from MySQL")
            self.log_to_file("Error with import Data from MySQL")
    # print('test commita')


x = Import_Data_SQL()
x.import_data_to_dataframe("cp")