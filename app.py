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

st.markdown("<h1 style='font-size: 42px !important;'>🚢 全球海運港口績效與船舶效率分析系統</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size: 30px !important;'><b>副標題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據</b></h2>", unsafe_allow_html=True)
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

# 4. 關鍵績效指標 (KPI 卡片)
st.markdown(f"### 📊 觀測焦點：{selected_economy} 在 {selected_period} 的核心數據總覽")
all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

if not all_ships_data.empty:
    val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
    val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
    val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0]
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="⏱️ 船舶在港停留時間中位數", value=f"{val1} 天" if pd.notna(val1) else "無資料")
    with col2: col2.metric(label="⏳ 停靠船舶平均船齡", value=f"{val2} 年 (最老約27年)" if pd.notna(val2) else "無資料")
    with col3: col3.metric(label="⚖️ 平均船舶總噸位 (GT)", value=f"{val3:,.0f} 噸" if pd.notna(val3) else "無資料")
else:
    st.warning("⚠️ 該國家在此期間內無綜合 (All ships) 數據。")

st.markdown("---")

# 5. 各船型在港停留時間長條圖
st.markdown("### 📈 各船型在港停留時間對比 (橫向壅塞效率分析)")
if not vessel_comparison_df.empty:
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value']).copy()
    if not chart1_df.empty:
        # 中英文並列對照表，加入換行標籤 <br> 讓字平躺
        vessel_type_combined = {
            "Liquid bulk carriers": "Liquid bulk carriers<br>(液體散裝船/油輪)",
            "Liquefied petroleum gas carriers": "Liquefied petroleum gas carriers<br>(液化石油氣船)",
            "Liquefied natural gas carriers": "Liquefied natural gas carriers<br>(液化天然氣船)",
            "Dry bulk carriers": "Dry bulk carriers<br>(乾散裝船/穀物礦石)",
            "Dry breakbulk carriers": "Dry breakbulk carriers<br>(雜貨船/散裝箱)",
            "Container ships": "Container ships<br>(貨櫃船/標準箱)"
        }
        chart1_df['Vessel_Type_Combined'] = chart1_df['CommercialMarket_Label'].map(vessel_type_combined).fillna(chart1_df['CommercialMarket_Label'])
        
        fig_time = px.bar(
            chart1_df, x='Vessel_Type_Combined', y='Median_time_in_port_days_Value',
            labels={'Vessel_Type_Combined': '船舶類型 (Vessel Type)', 'Median_time_in_port_days_Value': '在港停留天數中位數 (Days)'},
            color='Median_time_in_port_days_Value', color_continuous_scale='Reds', title="🏆 各類型船隻卡在港口的天數"
        )
        fig_time.update_coloraxes(colorbar_title_text="在港天數")
        fig_time.update_xaxes(tickangle=0) # 強制文字保持水平不傾斜
        fig_time.update_layout(font=dict(size=14), title_font=dict(size=20))
        st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("💡 無個別船型資料。")

st.markdown("---")

# 6. 數據統計摘要與明細 (防斷尾精簡版)
st.markdown("### 📋 數據科學統計摘要與原始明細")
tab1, tab2 = st.tabs(["🔍 資料敘述性統計", "📋 原始篩選數據明細"])

with tab1:
    if not filtered_df.empty:
        st.dataframe(filtered_df.describe().T, use_container_width=True, height=280, column_config={
            "count": "📊 樣本筆數 (Count)", "mean": "📈 平均值 (Mean)", "std": "📉 標準差 (Std)",
            "min": "⬇️ 最小值 (Min)", "25%": "¼ 25%分位數", "50%": "🌓 中位數 (50%)",
            "75%": "¾ 75%分位數", "max": "⬆️ 最大值 (Max)"
        })

with tab2:
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True, height=300)
