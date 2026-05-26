import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 設定網頁標題
st.set_page_config(page_title="全球港口績效儀表板", layout="wide")
st.title("🚢 全球海運港口績效與船舶效率儀表板")
st.markdown("數據來源：UNCTAD 統計資料 (2022-2023)")

# 2. 讀取資料
@st.cache_data
def load_data():
    df = pd.read_csv("Maritime Port Performance Project Dataset.csv")
    clean_cols = [col for col in df.columns if not col.endswith('_MissingValue')]
    return df[clean_cols].copy()

df = load_data()

# 3. 側邊欄篩選器
st.sidebar.header("🔍 篩選條件設定")
all_economies = sorted(df['Economy_Label'].unique())
selected_economy = st.sidebar.selectbox("選擇國家/地區", all_economies, index=all_economies.index('World') if 'World' in all_economies else 0)

all_periods = sorted(df['period'].unique())
selected_period = st.sidebar.selectbox("選擇統計期間", all_periods)

# 篩選資料
filtered_df = df[(df['Economy_Label'] == selected_economy) & (df['period'] == selected_period)]

# 4. 顯示數據總覽
st.subheader(f"📊 {selected_economy} 在 {selected_period} 的核心數據總覽")

if not filtered_df.empty:
    all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        val1 = all_ships_data['Median_time_in_port_days_Value'].values[0] if not all_ships_data.empty else "無資料"
        st.metric("船舶在港停留時間中位數", f"{val1} 天" if val1 != "無資料" else val1)
    with col2:
        val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0] if not all_ships_data.empty else "無資料"
        st.metric("停靠船舶平均船齡", f"{val2} 年" if val2 != "無資料" else val2)
    with col3:
        val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0] if not all_ships_data.empty else "無資料"
        st.metric("平均船舶總噸位 (GT)", f"{val3:,}" if val3 != "無資料" else val3)

    st.markdown("---")

    # 5. 繪製圖表 (加入防空值保護)
    st.subheader("📈 各船型績效橫向對比")
    vessel_comparison_df = filtered_df[filtered_df['CommercialMarket_Label'] != 'All ships'].dropna(subset=['Median_time_in_port_days_Value'])
    
    if not vessel_comparison_df.empty:
        fig_time = px.bar(
            vessel_comparison_df,
            x='CommercialMarket_Label',
            y='Median_time_in_port_days_Value',
            labels={'CommercialMarket_Label': '船隻類型', 'Median_time_in_port_days_Value': '在港天數 (中位數)'},
            color='Median_time_in_port_days_Value',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("💡 該國家在此期間內，沒有個別船型的詳細在港時間數據。")

    # 6. 原始數據表格
    st.subheader("📋 原始篩選數據明細")
    st.dataframe(filtered_df)
else:
    st.warning("⚠️ 找不到該篩選條件下的數據，請嘗試更換國家或期間。")
