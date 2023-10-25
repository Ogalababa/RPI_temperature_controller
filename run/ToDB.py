# ！/usr/bin/python3
# coding:utf-8
# sys
import os.path
import sqlite3
import pandas as pd
from sqlalchemy import create_engine


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
    # 获取所有表的名称
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # 对于每个表，打印其名称以及最后一条记录
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 1")
        last_record = cursor.fetchone()
        if last_record:
            column_names = [description[0] for description in cursor.description]
            for i, value in enumerate(last_record):
                print(f'{column_names[i]}: {value}', end=', ')
            print('\n')
        else:
            print("No records found in this table.\n")

    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
