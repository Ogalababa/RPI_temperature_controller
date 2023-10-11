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
    initial_sidebar_state="collapsed",  # 初始时侧边栏是展开的

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

    # 等待指定的时间间隔
    time.sleep(refresh_interval)
