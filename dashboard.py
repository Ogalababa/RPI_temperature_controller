import os.path
import time

import plotly.express as px
import streamlit as st

from ToDB import ConnectToDB
from __init__ import *

# 设置页面配置
st.set_page_config(
    page_title="实时数据监控",  # 页面标题
    layout="wide",  # 页面布局为 wide mode
    initial_sidebar_state="collapsed",  # 初始时侧边栏是关闭的
)

# 连接数据库
db = ConnectToDB("Status", os.path.join(current_dir, 'data'))

# 创建一个空的占位符
placeholder = st.empty()

# 添加一个滑块来让用户选择刷新间隔
refresh_interval = st.sidebar.slider('选择刷新间隔（秒）', min_value=1, max_value=60, value=10)

while True:
    # 从数据库中读取数据
    df = db.read_from_sql()

    # 创建图形
    fig = px.line(df, x="时间", y=['温度', '湿度'],
                  hover_data=['加温风扇', '降温风扇', '陶瓷灯', 'UV 灯', '日光灯'])

    # 更新占位符中的内容
    placeholder.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # 获取最后一行数据
    last_row = df.tail(1)
    # 创建三列
    col1, col2, col3 = st.columns(3)
    metric1 = col1.empty()
    metric2 = col2.empty()
    metric3 = col3.empty()
    # 在每列中显示度量值
    metric1.metric("温度", f"{last_row['温度'].values[0]:.2f} °C")
    metric2.metric("湿度", f"{last_row['湿度'].values[0]:.2f} %")
    metric3.metric("最后更新", f"{last_row['时间'].values[0]} ")

    # 创建另外四列
    col4, col5, col6, col7, col8 = st.columns(5)
    # 在每列中显示度量值
    metric4 = col4.empty()
    metric5 = col5.empty()
    metric6 = col6.empty()
    metric7 = col7.empty()
    metric8 = col8.empty()
    metric4.metric("加温风扇", last_row['加温风扇'].values[0])
    metric5.metric("降温风扇", last_row['降温风扇'].values[0])
    metric6.metric("陶瓷灯", last_row['陶瓷灯'].values[0])
    metric7.metric("UV 灯", last_row['UV 灯'].values[0])
    metric8.metric("日光灯", last_row['日光灯'].values[0])

    # 等待指定的时间间隔
    time.sleep(refresh_interval)
