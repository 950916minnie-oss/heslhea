import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁設定與大字體 CSS
st.set_page_config(page_title="全球港口壅塞效率與分析系統", layout="wide")
st.markdown("""
    <style>
    html, body, p, div, span, li, a { font-size: 20px !important; line-height: 1.6 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { font-size: 20px !important; }
    [data-testid="stMetricValue"] { font-size: 40px !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] p { font-size: 22px !important; }
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] { font-size: 18px !important; }
    [data-testid="stDataFrame"] div { font-family: "微軟正黑體", sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)

# 大標題與副標題正常顯示
st.markdown("<h1 style='font-size: 42px !important;'>🚢 全球海運港口績效與船舶效率分析系統</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size: 30px !important;'><b>副標題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據</b></h2>", unsafe_allow_html=True)
st.markdown("數據來源：聯合國貿易和發展會議 (UNCTAD) 官方統計資料 (2022-2023)")
st.markdown("---")

# 2. 讀取資料
@st.cache_data
def load_data():
    df = pd.read_csv("Maritime Port Performance Project Dataset.csv")
    clean_cols = [col for col in df.columns if not col.endswith('_MissingValue')]
    df_clean = df[clean_cols].copy()
    if 'Unnamed: 0' in df_clean.columns:
        df_clean = df_clean.drop(columns=['Unnamed: 0'])
    return df_clean

df = load_data()

# 3. 側邊欄篩選
st.sidebar.markdown("# 🔍 觀測條件設定")
all_economies = sorted(df['Economy_Label'].unique())
selected_economy = st.sidebar.selectbox("💡 請選擇觀測國家/地區", all_economies, index=all_economies.index('World') if 'World' in all_economies else 0)

all_periods = sorted(df['period'].unique())
selected_period = st.sidebar.selectbox("💡 請選擇統計期間", all_periods)

filtered_df = df[(df['Economy_Label'] == selected_economy) & (df['period'] == selected_period)]
vessel_comparison_df = filtered_df[filtered_df['CommercialMarket_Label'] != 'All ships']

# 4. 關鍵績效
