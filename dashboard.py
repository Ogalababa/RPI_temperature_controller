# ！/usr/bin/python3
# coding:utf-8
# sys

import os.path
import time
import pandas as pd

import plotly.express as px
import streamlit as st

from run.ToDB import ConnectToDB
from __init__ import *


def to_csv():
    dataframe = db.read_from_sql()
    # 将 DataFrame 转换为 CSV 格式的字符串
    return dataframe.to_csv(index=False).encode('utf-8')


# 设置页面配置
st.set_page_config(
    page_title="实时数据监控",  # 页面标题
    layout="wide",  # 页面布局为 wide mode
    initial_sidebar_state="collapsed",  # 初始时侧边栏是关闭的
)

# 连接数据库
db = ConnectToDB("Status", os.path.join(current_dir, 'data'))

# 创建一个空的占位符
both = st.empty()
humility = st.empty()
temperature = st.empty()

# 添加一个滑块来让用户选择刷新间隔
refresh_interval = st.sidebar.slider('选择刷新间隔（秒）', min_value=1, max_value=120, value=60)
# Save the input Day and Night target temperatures to the database.
# 添加目标温度输入
temp_df = db.read_from_sql("target_temp")
day_temp = temp_df["日间温度"][0]
night_temp = temp_df['夜间温度'][0]
day_target_temp = st.sidebar.number_input('日间目标温度', min_value=20, max_value=32, value=day_temp)
night_target_temp = st.sidebar.number_input('夜间目标温度', min_value=20, max_value=32, value=night_temp)

if st.sidebar.button('保存'):
    data_to_save = {
        "日间温度": day_target_temp,
        "夜间温度": night_target_temp
    }
    db.set_target_temp("target_temp", data_to_save)
    st.sidebar.success('目标温度已成功保存到数据库！')

col1, col9, col2, col3 = st.columns(4)
metric1 = col1.empty()
metric2 = col2.empty()
metric3 = col3.empty()
metric9 = col9.empty()
# 创建另外四列
col4, col5, col6, col7, col8 = st.columns(5)
# 在每列中显示度量值
metric4 = col4.empty()
metric5 = col5.empty()
metric6 = col6.empty()
metric7 = col7.empty()
metric8 = col8.empty()

# 在侧边栏添加下载按钮
csv_str = to_csv()
st.sidebar.download_button(
    label="Download data as CSV",
    data=csv_str,
    file_name="data.csv",
    mime="text/csv",
    key="download_csv_button"
)

while True:
    # 从数据库中读取数据
    df = db.read_from_sql()

    # 创建图形
    both_temp = px.line(df[-1500:], x="时间", y=['湿度', '温度', '目标温度'],
                        hover_data=['加温风扇', '降温风扇', '陶瓷灯', 'UV 灯', '日光灯'],
                        markers=True)
    fig_hum = px.line(df, x="时间", y='湿度',
                      hover_data=['湿度', '加温风扇', '降温风扇', '陶瓷灯', 'UV 灯', '日光灯'],
                      markers=True)

    fig_temp = px.line(df, x="时间", y=['温度', '目标温度'],
                       hover_data=['湿度', '加温风扇', '降温风扇', '陶瓷灯', 'UV 灯', '日光灯'],
                       markers=True
                       )

    # 设置线条颜色
    fig_hum.update_traces(line=dict(color='#FF8080'))
    fig_temp.update_traces(line=dict(color='#687EFF'), selector=dict(legendgroup='温度'))
    fig_temp.update_traces(line=dict(color='#CFBAF0'), selector=dict(legendgroup='目标温度'))
    # # 为 '湿度' 折线设置颜色
    #
    both_temp.update_traces(line=dict(color='#FF8080'), selector=dict(legendgroup='湿度'))
    # 为 '温度' 折线设置颜色
    both_temp.update_traces(line=dict(color='#687EFF'), selector=dict(legendgroup='温度'))
    # 设置线条颜色
    both_temp.update_traces(line=dict(color='#CFBAF0'), selector=dict(legendgroup='目标温度'))

    # 更新占位符中的内容
    both.plotly_chart(both_temp, theme="streamlit", use_container_width=True)
    humility.plotly_chart(fig_hum, theme="streamlit", use_container_width=True)
    temperature.plotly_chart(fig_temp, theme="streamlit", use_container_width=True)

    # 获取最后一行数据
    last_row = df.tail(1)
    # 创建三列

    # 在每列中显示度量值
    metric1.metric("当前温度", f"{last_row['温度'].values[0]:.2f} °C")
    metric9.metric("目标温度", f"{last_row['目标温度'].values[0]:.2f} °C")
    metric2.metric("湿度", f"{last_row['湿度'].values[0]:.2f} %")

    # 将 numpy.datetime64 转换为 datetime，然后格式化为字符串
    last_update_time = pd.to_datetime(last_row['时间'].values[0]).strftime('%H:%M:%S')
    metric3.metric("最后更新", last_update_time)
    metric4.metric("加温风扇", last_row['加温风扇'].values[0])
    metric5.metric("降温风扇", last_row['降温风扇'].values[0])
    metric6.metric("陶瓷灯", last_row['陶瓷灯'].values[0])
    metric7.metric("UV 灯", last_row['UV 灯'].values[0])
    metric8.metric("日光灯", last_row['日光灯'].values[0])
    # 等待指定的时间间隔
    time.sleep(refresh_interval)
