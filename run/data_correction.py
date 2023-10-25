# ！/usr/bin/python3
# coding:utf-8
# sys
import pandas as pd
from __init__ import *
import os
from sqlalchemy import create_engine


conn = create_engine(f'sqlite:///{os.path.join("/", "home", "jiawei", "RPI_temperature_controller", "data", "Status.db")}').connect()
df = pd.read_sql_table("Status", conn)
corrected_df = df.copy()

# 遍历每个测量列
for column in ['温度', '湿度']:
    # 计算每个点与其周围点的平均值的差异
    diff = df[column] - df[column].rolling(window=3, center=True).mean()
    # 如果差异大于某个阈值（例如，固定阈值5或基于标准偏差的阈值），则修正该点
    # threshold = 3 * diff.std()
    threshold = 4
    outliers = diff.abs() > threshold
    # 用前后点的平均值替换异常值
    corrected_df.loc[outliers, column] = (df[column].shift()[outliers] + df[column].shift(-1)[outliers]) / 2

corrected_df.to_sql("Status", conn, if_exists="replace")

conn.close()
