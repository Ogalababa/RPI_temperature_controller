import os.path

import plotly.express as px
import streamlit as st
import time
from ToDB import ConnectToDB
from __init__ import *


db = ConnectToDB("Status", os.path.join(current_dir, 'data'))

while True:
    df = db.read_from_sql()
    fig = px.line(df, x="时间", y=df.columns,
                  hover_data=['加温风扇', '降温风扇', '陶瓷灯', 'UV 灯', '日光灯'])
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    time.sleep(60)

