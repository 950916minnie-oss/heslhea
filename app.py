import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全球港口績效與壅塞效率觀測系統", layout="wide")
st.title("🚢 全球海運港口績效與船舶效率分析系統")
st.markdown("### 主題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據")
st.markdown("---")

# 2. 讀取與快取資料
@st.cache_data
def load_data():
    df = pd.read_csv("Maritime Port Performance Project Dataset.csv")
    # 移除缺失值說明的欄位，只保留 Value 數值欄位
    clean_cols = [col for col in df.columns if not col.endswith('_MissingValue')]
    df_clean = df[clean_cols].copy()
    # 移除流水號欄位
    if 'Unnamed: 0' in df_clean.columns:
        df_clean = df_clean.drop(columns=['Unnamed: 0'])
    return df_clean

df = load_data()

# 3. 側邊欄互動篩選器 (互動式網頁的核心)
st.sidebar.header("🔍 觀測條件設定")
all_economies = sorted(df['Economy_Label'].unique())
selected_economy = st.sidebar.selectbox("選擇觀測國家/地區", all_economies, index=all_economies.index('World') if 'World' in all_economies else 0)

all_periods = sorted(df['period'].unique())
selected_period = st.sidebar.selectbox("選擇統計期間", all_periods)

# 根據篩選條件過濾資料
filtered_df = df[(df['Economy_Label'] == selected_economy) & (df['period'] == selected_period)]
vessel_comparison_df = filtered_df[filtered_df['CommercialMarket_Label'] != 'All ships']

# ==================== 網頁主內容區 ====================

# 4. 關鍵績效指標 (KPI 分類總覽)
st.subheader(f"📊 {selected_economy} 在 {selected_period} 的核心數據總覽")
all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

col1, col2, col3 = st.columns(3)
if not all_ships_data.empty:
    with col1:
        val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
        st.metric("船舶在港停留時間中位數 (壅塞指標)", f"{val1} 天" if pd.notna(val1) else "無資料")
    with col2:
        val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
        st.metric("停靠船舶平均船齡 (老舊度指標)", f"{val2} 年" if pd.notna(val2) else "無資料")
    with col3:
        val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0]
        st.metric("平均船舶總噸位 GT (港口負荷指標)", f"{val3:,.0f} 噸" if pd.notna(val3) else "無資料")
else:
    st.warning("⚠️ 該國家在此期間內無綜合 (All ships) 數據。")

st.markdown("---")

# 5. Kaggle 筆記本核心分析一：港口壅塞度與時間對比 (長條圖)
st.subheader("📈 各船型在港停留時間對比 (壅塞效率分析)")
if not vessel_comparison_df.empty:
    # 移除在港時間為空的船型
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value'])
    if not chart1_df.empty:
        fig_time = px.bar(
            chart1_df,
            x='CommercialMarket_Label',
            y='Median_time_in_port_days_Value',
            labels={'CommercialMarket_Label': '船舶類型', 'Median_time_in_port_days_Value': '在港停留天數 (中位數)'},
            color='Median_time_in_port_days_Value',
            color_continuous_scale='Reds',
            title=f"{selected_economy} 各類型船隻卡在港口的天數對比"
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("💡 該地區在此期間內，沒有個別船型的詳細在港時間數據。")
else:
    st.info("💡 無個別船型資料。")

st.markdown("---")

# 6. Kaggle 筆記本核心分析二：船舶載重能力與噸位分析 (散佈圖/氣泡圖)
st.subheader("🚢 船舶載運規模與載重噸位 (DWT) 關聯分析")
st.markdown("*(分析說明：此圖表呈現不同船型的平均總噸位與平均載重能力的關係，圓點越大代表船隻平均體積越大。)*")

# 移除畫圖所需的空值
scatter_df = vessel_comparison_df.dropna(subset=['Average_size_GT_of_vessels_Value', 'Average_cargo_carrying_capacity_dwt_per_vessel_Value'])

if not scatter_df.empty:
    fig_scatter = px.scatter(
        scatter_df,
        x='Average_size_GT_of_vessels_Value',
        y='Average_cargo_carrying_capacity_dwt_per_vessel_Value',
        size='Average_size_GT_of_vessels_Value',
        color='CommercialMarket_Label',
        labels={
            'Average_size_GT_of_vessels_Value': '平均船舶總噸位 (Average Size GT)',
            'Average_cargo_carrying_capacity_dwt_per_vessel_Value': '平均載重噸位 (Average DWT)',
            'CommercialMarket_Label': '船舶類型'
        },
        title=f"{selected_economy} 停靠船型之規模與載重分佈圖"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("💡 該國家/地區缺少船隻噸位與載重能力的對應數據。")

st.markdown("---")

# 7. Kaggle 筆記本核心分析三：數據統計摘要與明細 (把 Notebook 的 df.describe() 搬上網頁)
st.subheader("📋 數據科學統計摘要與原始明細")

tab1, tab2 = st.tabs(["資料敘述性統計 (Notebook 經典分析)", "篩選數據明細 (Excel 表格樣式)"])

with tab1:
    st.markdown("#### 🔍 目前篩選數據的數值特徵摘要 (Summary Statistics)")
    # 排除物件型態欄位，對數值進行敘述性統計 (即 Notebook 中的 df.describe())
    if not filtered_df.empty:
        st.dataframe(filtered_df.describe().T)
    else:
        st.write("無資料。")

with tab2:
    st.markdown("#### 🔍 原始資料表格明細")
    st.dataframe(filtered_df)
