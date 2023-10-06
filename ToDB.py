# ！/usr/bin/python3
# coding:utf-8
# sys
import os.path
from datetime import datetime

import pandas as pd
import pytz
import sqlalchemy

from __init__ import *
from sqlalchemy import create_engine


class ConnectToDB:
    def __init__(self, db_name, path):

        self.db_path = os.path.join(path, f'{db_name}.db')
        self.conn = create_engine(f'sqlite:///{self.db_path}').connect()
        self.db_name = db_name

    def save_to_sql(self, data_dict):
        df = pd.DataFrame(data_dict)
        print(data_dict)
        df.to_csv(f'{os.path.join(current_dir, "data", self.db_name)}.csv', index=True, if_exists="append")
        # df.to_sql(self.db_name, self.conn, index=True, if_exists="append")

    def read_from_sql(self):
        pd.read_sql_table(self.db_name, self.conn)
        return pd
