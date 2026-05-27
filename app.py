import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定 (開啟寬螢幕模式)
st.set_page_config(page_title="全球港口壅塞效率與分析系統", layout="wide")

# =================【最新表格專屬放大 CSS 區塊】=================
st.markdown("""
    <style>
    /* 1. 強制放大全網頁基礎文字 */
    html, body, p, div, span, li, a {
        font-size: 20px !important; 
        line-height: 1.6 !important;
    }
    /* 2. 強制放大側邊欄文字 */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        font-size: 20px !important;
    }
    /* 3. 強制放大大數字欄位 (st.metric) */
    [data-testid="stMetricValue"] {
        font-size: 40px !important; 
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 22px !important;
    }
    
    /* 強制穿透並放大 st.dataframe 表格內部的所有中英文字體與欄位名 */
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] {
        font-size: 18px !important;
    }
    [data-testid="stDataFrame"] div {
        font-family: "微軟正黑體", sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)
# =============================================================

# 網頁大標題與副標題
st.markdown("<h1 style='font-size: 42px !important;'>🚢 全球海運港口績效與船舶效率分析系統</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size: 30px !important;'><b>副標題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據</b></h2>", unsafe_allow_html=True)
st.markdown("數據來源：聯合國貿易和發展會議 (UNCTAD) 官方統計資料 (2022-2023)")
st.markdown("---")

# 2. 讀取與快取資料
@st.cache_data
def load_data():
    df = pd.read_csv("Maritime Port Performance Project Dataset.csv")
    clean_cols = [col for col in df.columns if not col.endswith('_MissingValue')]
    df_clean = df[clean_cols].copy()
    if 'Unnamed: 0' in df_clean.columns:
        df_clean = df_clean.drop(columns=['Unnamed: 0'])
    return df_clean

df = load_data()

# 3. 側邊欄互動篩選器
st.sidebar.markdown("# 🔍 觀測條件設定")
all_economies = sorted(df['Economy_Label'].unique())
selected_economy = st.sidebar.selectbox("💡 請選擇觀測國家/地區", all_economies, index=all_economies.index('World') if 'World' in all_economies else 0)

all_periods = sorted(df['period'].unique())
selected_period = st.sidebar.selectbox("💡 請選擇統計期間", all_periods)

# 根據篩選條件過濾資料
filtered_df = df[(df['Economy_Label'] == selected_economy) & (df['period'] == selected_period)]
vessel_comparison_df = filtered_df[filtered_df['CommercialMarket_Label'] != 'All ships']

# ==================== 網頁主內容區 ====================

# 4. 關鍵績效指標 (KPI 分類總覽)
st.markdown(f"### 📊 觀測焦點：{selected_economy} 在 {selected_period} 的核心數據總覽")

all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

col1, col2, col3 = st.columns(3)
if not all_ships_data.empty:
    with col1:
        val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
        st.metric(label="⏱️ 船舶在港停留時間中位數", value=f"{val1} 天" if pd.notna(val1) else "無資料")
    with col2:
        val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
        st.metric(label="⏳ 停靠船舶平均船齡", value=f"{val2} 年" if pd.notna(val2) else "無
