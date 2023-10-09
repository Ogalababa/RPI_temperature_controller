# ！/usr/bin/python3
# coding:utf-8
# sys
import os.path
import sqlite3

import pandas as pd

from __init__ import *
from sqlalchemy import create_engine


class ConnectToDB:
    def __init__(self, db_name, path):

        self.db_path = os.path.join(path, f'{db_name}.db')
        self.conn = create_engine(f'sqlite:///{self.db_path}').connect()
        self.db_name = db_name

    def save_to_sql(self, data_dict):
        data_df = pd.DataFrame({key: [value] for key, value in data_dict.items()})
        data_df.to_sql(self.db_name, self.conn, index=False, if_exists="append")

    def read_from_sql(self):
        pd.read_sql_table(self.db_name, self.conn)
        return pd


if __name__ == "__main__":
    # 连接到数据库
    conn = sqlite3.connect(os.path.join("data", "Status.db"))
    # 创建一个游标对象
    cursor = conn.cursor()
    # 执行 SQL 查询以获取数据
    cursor.execute('SELECT * FROM Status')
    # 读取所有行数据
    rows = cursor.fetchall()
    # 打印数据
    for row in rows[-10:]:
        print(row)
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
