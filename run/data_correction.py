# ！/usr/bin/python3
# coding:utf-8
# sys
import pandas as pd
from scipy.stats import zscore
import os
from sqlalchemy import create_engine

conn = create_engine(
    f'sqlite:///{os.path.join("/", "home", "jiawei", "RPI_temperature_controller", "data", "Status.db")}').connect()
df = pd.read_sql_table("Status", conn)
# 1. 加载数据
data = df.copy()
data['时间'] = pd.to_datetime(data['时间'])
data.drop(columns=['level_0','index','温度_zscore','湿度_zscore','温度_anomaly','湿度_anomaly'], inplace=True)

# 2. 使用z分数方法检测异常值
data['温度_zscore'] = zscore(data['温度'])
data['湿度_zscore'] = zscore(data['湿度'])

data['温度_anomaly'] = abs(data['温度_zscore']) > 3
data['湿度_anomaly'] = abs(data['湿度_zscore']) > 3

anomalies = data[(data['温度_anomaly']) | (data['湿度_anomaly'])]


# 3. 使用前后数据的平均值替换异常值
def replace_with_neighbors_average(series, anomalies_index):
    for idx in anomalies_index:
        if 0 < idx < len(series) - 1:
            series.iloc[idx] = (series.loc[idx - 1] + series.loc[idx + 1]) / 2
    return series


data['温度'] = replace_with_neighbors_average(data['温度'], anomalies[anomalies['温度_anomaly']].index)
data['湿度'] = replace_with_neighbors_average(data['湿度'], anomalies[anomalies['湿度_anomaly']].index)
data.drop(columns=['温度_zscore','湿度_zscore','温度_anomaly','湿度_anomaly'], inplace=True)

data.to_sql("Status", conn, if_exists="replace")

conn.close()
