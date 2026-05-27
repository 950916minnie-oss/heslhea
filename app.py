import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定與 CSS 放大字體
st.set_page_config(page_title="全球港口壅塞效率與分析系統", layout="wide")
st.markdown("""
    <style>
    html, body, p, div, span, li, a { font-size: 20px !important; line-height: 1.6 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { font-size: 20px !important; }
    [data-testid="stMetricValue"] { font-size: 40px !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] p { font-size: 22px !important; }
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] { font-size: 18px !important; }
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

# 5. 各船型在港停留時間長條圖 (精心排版，防止貼上時因字串太長被截斷)
st.markdown("### 📈 各船型在港停留時間對比 (橫向壅塞效率分析)")
if not vessel_comparison_df.empty:
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value']).copy()
    if not chart1_df.empty:
        # 縮短命名，保證不超出網頁黏貼極限
        cmap = {
            "Liquid bulk carriers": "Liquid bulk carriers<br>(液體散裝/油輪)",
            "Liquefied petroleum gas carriers": "LPG carriers<br>(液化石油氣船)",
            "Liquefied natural gas carriers": "LNG carriers<br>(液化天然氣船)",
            "Dry bulk carriers": "Dry bulk carriers<br>(乾散裝船/穀物)",
            "Dry breakbulk carriers": "Dry breakbulk<br>(雜貨船/散裝箱)",
            "Container ships": "Container ships<br>(貨櫃船/標準箱)"
        }
        chart1_df['Type_CN'] = chart1_df['CommercialMarket_Label'].map(cmap).fillna(chart1_df['CommercialMarket_Label'])
        
        fig_time = px.bar(
            chart1_df, x='Type_CN', y='Median_time_in_port_days_Value',
            labels={'Type_CN': '船舶類型', 'Median_time_in_port_days_Value': '在港停留天數中位數 (Days)'},
            color='Median_time_in_port_days_Value', color_continuous_scale='Reds'
        )
        fig_time.update_coloraxes(colorbar_title_text="在港天數")
        fig_time.update_xaxes(tickangle=0) 
        fig_time.update_layout(font=dict(size=14))
        st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("💡 提示：『World』僅包含綜合統計，切換至特定國家（如 United States of America）即可看細分船型圖。")

st.markdown("---")

# 6. 數據統計摘要與明細 (含藍色名詞解釋框)
st.markdown("### 📋 數據科學統計摘要與原始明細")
tab1, tab2 = st.tabs(["🔍 資料敘述性統計", "📋 原始篩選數據明細"])

with tab1:
    if not filtered_df.empty:
        st.dataframe(filtered_df.describe().T, use_container_width=True, height=260, column_config={
            "count": "📊 樣本筆數", "mean": "📈 平均值", "std": "📉 標準差",
            "min": "⬇️ 最小值", "25%": "¼ 25%分位", "50%": "🌓 中位數", "75%": "¾ 75%分位", "max": "⬆️ 最大值"
        })
        st.markdown("---")
        st.info("""
        * **`Average_age_of_vessels_years_Value`** ➡️ **【停靠船舶平均船齡】**：停靠船隻的平均年齡（歲）。
        * **`Median_time_in_port_days_Value`** ➡️ **【船舶在港停留時間中位數】**：進港到排隊離開總天數。
        * **`Average_size_GT_of_vessels_Value`** ➡️ **【平均船舶總噸位】**：Gross Tonnage 船隻內部總體積空間。
        * **`Average_cargo_carrying_capacity_dwt_per_vessel_Value`** ➡️ **【平均船舶載重噸位】**：Deadweight Tonnage 實際能載重。
        * **`Average_container_carrying_capacity_TEU_per_container_ship_Value`** ➡️ **【貨櫃船平均運載量 (TEU)】**：平均能載多少個20呎標準箱。
        * **`Maximum_size_GT_of_vessels_Value`** ➡️ **【停靠最大船舶總噸位】**：接待過體積最大的超級巨輪規模。
        * **`Maximum_cargo_carrying_capacity_dwt_of_vessels_Value`** ➡️ **【停靠最大船舶載重噸位】**：接待過載貨最重的超級巨輪重量。
        * **`Maximum_container_carrying_capacity_TEU_of_container_ships_Value`** ➡️ **【停靠最大貨櫃船運載量 (TEU)】**：接待過載箱數最多的超級貨櫃船。
        """)

with tab2:
    if not filtered_df.empty: st.dataframe(filtered_df, use_container_width=True, height=260)
