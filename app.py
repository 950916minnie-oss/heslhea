import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定與視覺層級優化 CSS
st.set_page_config(page_title="全球港口壅塞效率與分析系統", layout="wide")
st.markdown("""
    <style>
    /* 主標題與副標題：維持最顯眼、最有氣勢的大字 */
    .super-title {
        font-size: 46px !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
        line-height: 1.3 !important;
        display: block;
        margin-bottom: 15px;
    }
    .super-sub {
        font-size: 30px !important;
        font-weight: bold !important;
        color: #4B5563 !important;
        line-height: 1.4 !important;
        display: block;
        margin-bottom: 20px;
    }
    /* 三大指標數據調小，絕對不搶主標題風采 */
    [data-testid="stMetricValue"] { 
        font-size: 30px !important; 
        font-weight: bold !important; 
    }
    [data-testid="stMetricLabel"] p { 
        font-size: 18px !important; 
    }
    /* 側邊欄與表格文字 */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { font-size: 20px !important; }
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 頂端標題區
st.markdown('<span class="super-title">🚢 全球海運港口績效與船舶效率分析系統</span>', unsafe_allow_html=True)
st.markdown('<span class="super-sub">副標題：港口壅塞效率與分析 —— 基於 UNCTAD 航運大數據</span>', unsafe_allow_html=True)
st.write("數據來源：聯合國貿易和發展會議 (UNCTAD) 官方統計資料 (2022-2023)")
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
st.markdown("### 📈 各船型在港停留時間對比 (橫向壅塞效率分析)")
if not vessel_comparison_df.empty:
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value']).copy()
    if not chart1_df.empty:
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

# 6. 🔥【氣泡圖大復活】船舶載重能力與噸位分析 (氣泡圖完整畫圖邏輯)
st.markdown("### 🚢 船舶載運規模與載重噸位 (DWT) 關聯分析")
st.markdown("*(數據科學解讀：此圖呈現不同船型的平均總噸位 GT 與載重能力 DWT 的線性關係，圓點越大代表船隻物理體積越大。)*")

if not vessel_comparison_df.empty:
    scatter_df = vessel_comparison_df.dropna(subset=['Average_size_GT_of_vessels_Value', 'Average_cargo_carrying_capacity_dwt_per_vessel_Value']).copy()
    if not scatter_df.empty:
        vessel_type_scatter = {
            "Liquid bulk carriers": "Liquid bulk carriers (液體散裝船)",
            "Liquefied petroleum gas carriers": "LPG carriers (液化石油氣船)",
            "Liquefied natural gas carriers": "LNG carriers (液化天然氣船)",
            "Dry bulk carriers": "Dry bulk carriers (乾散裝船)",
            "Dry breakbulk carriers": "Dry breakbulk (雜貨船)",
            "Container ships": "Container ships (貨櫃船)"
        }
        scatter_df['Type_Scatter_CN'] = scatter_df['CommercialMarket_Label'].map(vessel_type_scatter).fillna(scatter_df['CommercialMarket_Label'])

        fig_scatter = px.scatter(
            scatter_df, x='Average_size_GT_of_vessels_Value', y='Average_cargo_carrying_capacity_dwt_per_vessel_Value',
            size='Average_size_GT_of_vessels_Value', color='Type_Scatter_CN',
            labels={
                'Average_size_GT_of_vessels_Value': '平均船舶總噸位 (Average Size GT)',
                'Average_cargo_carrying_capacity_dwt_per_vessel_Value': '平均載重噸位 (Average DWT)',
                'Type_Scatter_CN': '船舶類型 (Vessel Type)'
            },
            title="🔮 停靠船型之規模 (GT) 與實際載重能力 (DWT) 交叉關聯圖"
        )
        fig_scatter.update_layout(font=dict(size=14), title_font=dict(size=18))
        st.plotly_chart(fig_scatter, use_container_width=True) # 之前就是漏掉這一行！補回來了！
    else:
        st.info("💡 該觀測條件下缺少船隻噸位與載重能力的對應數據。")
else:
    st.info("💡 提示：『World』無細分船型交叉氣泡圖。切換至具體國家（如 United States of America）即可顯示。")

st.markdown("---")

# 7. 數據統計摘要與明細 (含藍色名詞解釋框)
st.markdown("### 📋 數據科學統計摘要與原始明細")
tab1, tab2 = st.tabs(["🔍 資料敘述性統計", "📋 原始篩選數據明細"])

with tab1:
    if not filtered_df
