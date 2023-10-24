# ！/usr/bin/python3
# coding:utf-8
# sys
import os.path
import sqlite3

import pandas as pd
from sqlalchemy import create_engine
from __init__ import *


class ConnectToDB:
    def __init__(self, db_name, path):
        self.db_path = os.path.join(path, f'{db_name}.db')
        self.conn = create_engine(f'sqlite:///{self.db_path}').connect()
        self.db_name = db_name

    def save_to_sql(self, data_dict):
        data_df = pd.DataFrame({key: [value] for key, value in data_dict.items()})
        data_df.to_sql(self.db_name, self.conn, index=False, if_exists='append')

    def read_from_sql(self, table_name="Status"):
        df = pd.read_sql_table(table_name, self.conn)
        return df

    def set_target_temp(self, tabel_name: str, data_dict: dict):
        data_df = pd.DataFrame({key: [value] for key, value in data_dict.items()})
        data_df.to_sql(tabel_name, self.conn, index=False, if_exists='replace')


if __name__ == "__main__":
    # 连接到数据库
    conn = sqlite3.connect(os.path.join('/', 'home', 'jiawei', 'RPI_temperature_controller', "data", "Status.db"))
    # 创建一个游标对象
    cursor = conn.cursor()
    # 执行 SQL 查询以获取数据
    cursor.execute('SELECT * FROM button')
    # 读取所有行数据
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    # 打印数据
    for row in rows[-10:]:
        for i in range(10):
            print(f'{column_names[i]}:{row[i]}', end=', ')
        print('\n')
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
