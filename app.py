import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة المخزون الطبي",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RTL Support with Custom CSS
st.markdown("""
    <style>
    .main {direction: rtl; text-align: right;}
    .stDataFrame {direction: rtl;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .alert-high {background: #ff6b6b; color: white; padding: 10px; border-radius: 5px;}
    .alert-medium {background: #ffa502; color: white; padding: 10px; border-radius: 5px;}
    .alert-ok {background

