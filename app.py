import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="全球港口績效儀表板", layout="wide")
st.title("🚢 全球海運港口績效與船舶效率儀表板")
st.markdown("數據來源：UNCTAD 統計資料 (2022-2023)")

@st.cache_data
def load_data():
    df = pd.read_csv("Maritime Port Performance Project Dataset.csv")
    clean_cols = [col for col in df.columns if not col.endswith('_MissingValue')]
    return df[clean_cols].copy()

df = load_data()

st.sidebar.header("🔍 篩選條件設定")
all_economies = sorted(df['Economy_Label'].unique())
selected_economy = st.sidebar.selectbox("選擇國家/地區", all_economies, index=all_economies.index('World') if 'World' in all_economies else 0)

all_periods = sorted(df['period'].unique())
selected_period = st.sidebar.selectbox("選擇統計期間", all_periods)

filtered_df = df[(df['Economy_Label'] == selected_economy) & (df['period'] == selected_period)]
vessel_comparison_df = filtered_df[filtered_df['CommercialMarket_Label'] != 'All ships']

st.subheader(f"📊 {selected_economy} 在 {selected_period} 的核心數據總覽")
all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

col1, col2, col3 = st.columns(3)
if not all_ships_data.empty:
    with col1:
        st.metric("船舶在港停留時間中位數", f"{all_ships_data['Median_time_in_port_days_Value'].values[0]} 天")
    with col2:
        st.metric("停靠船舶平均船齡", f"{all_ships_data['Average_age_of_vessels_years_Value'].values[0]} 年")
    with col3:
        st.metric("平均船舶總噸位 (GT)", f"{all_ships_data['Average_size_GT_of_vessels_Value'].values[0]:,}")

st.markdown("---")

st.subheader("📈 各船型績效橫向對比")
fig_time = px.bar(
    vessel_comparison_df,
    x='CommercialMarket_Label',
    y='Median_time_in_port_days_Value',
    labels={'CommercialMarket_Label': '船隻類型', 'Median_time_in_port_days_Value': '在港天數 (中位數)'},
    color='Median_time_in_port_days_Value',
    color_continuous_scale='Reds'
)
st.plotly_chart(fig_time, use_container_width=True)

st.subheader("📋 原始篩選數據明細")
st.dataframe(filtered_df)
