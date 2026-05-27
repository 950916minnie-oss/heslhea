import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定與安全的字體放大 CSS (移除會波及 div 的錯誤設定)
st.set_page_config(page_title="全球港口壅塞效率與分析系統", layout="wide")
st.markdown("""
    <style>
    /* 放大一般內文與列表字體 */
    p, li, a, span { font-size: 20px !important; line-height: 1.6 !important; }
    /* 放大側邊欄文字 */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { font-size: 20px !important; }
    /* 放大 KPI 卡片數字與標籤 */
    [data-testid="stMetricValue"] { font-size: 40px !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] p { font-size: 22px !important; }
    /* 放大表格內文字體 */
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 使用完全獨立且不受干擾的 HTML 標籤呈現超級大標題
st.markdown("<div style='text-align: left; margin-bottom: 10px;'><span style='font-size: 45px !important; font-weight: bold !important; color: #1E3A8A;'>🚢 全球海運港口績效與船舶效率分析系統</span></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: left; margin-bottom: 20px;'><span style='font-size: 30px !important; font-weight: bold !important; color: #4B5563;'>副標題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據</span></div>", unsafe_allow_html=True)
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

# 4. 核心數據大字卡
st.markdown(f"### 📊 觀測焦點：{selected_economy} 在 {selected_period} 的核心數據總覽")
all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

if not all_ships_data.empty:
    val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
    val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
    val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0]
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="⏱️ 船舶在港停留時間中位數", value=f"{val1} 天" if pd.notna(val1) else "無資料")
    with col2: st.metric(label="⏳ 停靠船舶平均船齡", value=f"{val2} 年 (最老約27年)" if pd.notna(val2) else "無資料")
    with col3: st.metric(label="⚖️ 平均船舶總噸位 (GT)", value=f"{val3:,.0f} 噸" if pd.notna(val3) else "無資料")
else:
    st.warning("⚠️ 該國家在此期間內無綜合 (All ships) 數據。")

st.markdown("---")

# 5. 各船型在港停留時間長條圖
st.markdown("### 📈 各船型在港停留
