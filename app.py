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
    
    /* 🔥【核心關鍵】強制穿透並放大 st.dataframe 表格內部的所有中英文字體與欄位名 */
    [data-testid="stDataFrame"] *, .glideDataGrid-canvas, [role="gridcell"] {
        font-size: 18px !important;
    }
    /* 調整表格行高，避免字體放大後重疊 */
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
st.info("💡 **小撇步**：請將滑鼠移到下方數據欄位旁的 **[?] 小問號** 上，系統將自動跳出專有名詞的學術定義白話文解釋喔！")

all_ships_data = filtered_df[filtered_df['CommercialMarket_Label'] == 'All ships']

col1, col2, col3 = st.columns(3)
if not all_ships_data.empty:
    with col1:
        val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
        st.metric(
            label="⏱️ 船舶在港停留時間中位數", 
            value=f"{val1} 天" if pd.notna(val1) else "無資料",
            help="【塞港度核心變數】代表船隻進港後，從在外海排隊、靠岸、裝卸貨物到離港，所有人花費時間的中位數。天數愈長，代表港口壅塞打結愈嚴重。"
        )
    with col2:
        val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
        st.metric(
            label="⏳ 停靠船舶平均船齡", 
            value=f"{val2} 年" if pd.notna(val2) else "無資料",
            help="【運力老化指標】代表來這個國家停靠的所有船隻平均幾歲。老舊船隻（如美國高達 27 年）容易發生機械故障，是拖累裝卸效率的隱形炸彈。"
        )
    with col3:
        val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0]
        st.metric(
            label="⚖️ 平均船舶總噸位 (GT)", 
            value=f"{val3:,.0f} 噸" if pd.notna(val3) else "無資料",
            help="【港口基礎設施負荷指標】Gross Tonnage 總噸位代表船隻的總內部體積規模。數字愈大代表來的船都是國際超級巨輪，極度考驗港口吃水深度與自動化吊車基礎設施。"
        )
else:
    st.warning("⚠️ 該國家在此期間內無綜合 (All ships) 數據。")

st.markdown("---")

# 5. 港口壅塞度與時間對比 (長條圖優化)
st.markdown("### 📈 各船型在港停留時間對比 (橫向壅塞效率分析)")
if not vessel_comparison_df.empty:
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value'])
    if not chart1_df.empty:
        fig_time = px.bar(
            chart1_df,
            x='CommercialMarket_Label',
            y='Median_time_in_port_days_Value',
            labels={'CommercialMarket_Label': '船舶類型 (Vessel Type)', 'Median_time_in_port_days_Value': '在港停留天數中位數 (Days)'},
            color='Median_time_in_port_days_Value',
            color_continuous_scale='Reds',
            title=f"🏆 實證對比：{selected_economy} 各類型船隻卡在港口的天數 (天數愈長愈壅塞)"
        )
        fig_time.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("💡 該地區在此期間內，沒有個別船型的詳細在港時間數據。")
else:
    st.info("💡 無個別船型資料。")

st.markdown("---")

# 6. 船舶載重能力與噸位分析
st.markdown("### 🚢 船舶載運規模與載重噸位 (DWT) 關聯分析")
st.markdown("*(數據科學解讀：此圖呈現不同船型的平均總噸位 GT 與載重能力 DWT 的線性關係，圓點越大代表船隻物理體積越大。)*")

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
            'Average_cargo_carrying_capacity_dwt_per_vessel_Value': '平均載重噸位 (Average DWT - 船隻能載多重的貨)',
            'CommercialMarket_Label': '船舶類型'
        },
        title=f"🔮 規模分佈：{selected_economy} 停靠船型之規模 (GT) 與實際載重能力 (DWT) 交叉關聯圖"
    )
    fig_scatter.update_layout(font=dict(size=16), title_font=dict(size=20))
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("💡 該國家/地區缺少船隻噸位與載重能力的對應數據。")

st.markdown("---")

# 7. 數據統計摘要與明細 (優化表格寬度與顯示)
st.markdown("### 📋 數據科學統計摘要與原始明細")

tab1, tab2 = st.tabs(["🔍 資料敘述性統計 (Kaggle EDA 經典特徵)", "📋 原始篩選數據明細 (Excel 樣式表格)"])

with tab1:
    st.markdown("#### 📝 目前篩選數據的數值特徵摘要 (Summary Statistics)")
    if not filtered_df.empty:
        # 這裡特別加上 height 參數讓表格高度固定，方便閱讀放大後的字
        st.dataframe(filtered_df.describe().T, use_container_width=True, height=400)
    else:
        st.write("無資料。")

with tab2:
    st.markdown("#### 📝 原始資料表格明細 (提供下載與線性審查)")
    st.dataframe(filtered_df, use_container_width=True, height=400)
