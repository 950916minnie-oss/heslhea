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

if not all_ships_data.empty:
    val1 = all_ships_data['Median_time_in_port_days_Value'].values[0]
    val2 = all_ships_data['Average_age_of_vessels_years_Value'].values[0]
    val3 = all_ships_data['Average_size_GT_of_vessels_Value'].values[0]
    
    txt1 = f"{val1} 天" if pd.notna(val1) else "無資料"
    txt2 = f"{val2} 年 (最老約27年)" if pd.notna(val2) else "無資料"
    txt3 = f"{val3:,.0f} 噸" if pd.notna(val3) else "無資料"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="⏱️ 船舶在港停留時間中位數", value=txt1)
    with col2:
        st.metric(label="⏳ 停靠船舶平均船齡", value=txt2)
    with col3:
        st.metric(label="⚖️ 平均船舶總噸位 (GT)", value=txt3)
else:
    st.warning("⚠️ 該國家在此期間內無綜合 (All ships) 數據。")

st.markdown("---")

# 5. 港口壅塞度與時間對比 (長條圖優化)
st.markdown("### 📈 各船型在港停留時間對比 (橫向壅塞效率分析)")
if not vessel_comparison_df.empty:
    chart1_df = vessel_comparison_df.dropna(subset=['Median_time_in_port_days_Value']).copy()
    if not chart1_df.empty:
        # 🔥【最新核心優化】建立船型中英文對照表
        vessel_type_cn = {
            "Liquid bulk carriers": "液體散裝船 (油輪)",
            "Liquefied petroleum gas carriers": "液化石油氣船 (LPG)",
            "Liquefied natural gas carriers": "液化天然氣船 (LNG)",
            "Dry bulk carriers": "乾散裝船 (穀物/礦石)",
            "Dry breakbulk carriers": "雜貨船 (散裝箱)",
            "Container ships": "貨櫃船 (標準箱)"
        }
        # 將英文欄位轉換為中文新欄位
        chart1_df['Vessel_Type_CN'] = chart1_df['CommercialMarket_Label'].map(vessel_type_cn).fillna(chart1_df['CommercialMarket_Label'])
        
        fig_time = px.bar(
            chart1_df,
            x='Vessel_Type_CN',  # 這裡改成中文欄位，X 軸就會直接變中文！
            y='Median_time_in_port_days_Value',
            labels={
                'Vessel_Type_CN': '船舶類型 (Vessel Type)', 
                'Median_time_in_port_days_Value': '在港停留天數中位數 (Days)'
            },
            color='Median_time_in_port_days_Value',
            color_continuous_scale='Reds',
            title="🏆 各類型船隻卡在港口的天數"
        )
        # 優化右側色條 (Colorbar) 顯示標題
        fig_time.update_coloraxes(colorbar_title_text="在港天數")
        fig_time.update_layout(font=dict(size=16), title_font=dict(size=20))
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("💡 該地區在此期間內無個別船型詳細數據。")
else:
    st.info("💡 無個別船型資料。")

st.markdown("---")

# 6. 船舶載重能力與噸位分析
st.markdown("### 🚢 船舶載運規模與載重噸位 (DWT) 關聯分析")
st.markdown("*(數據科學解讀：此圖呈現不同船型的平均總噸位 GT 與載重能力 DWT 的線性關係，圓點越大代表船隻物理體積越大。)*")

scatter_df = vessel_comparison_df.dropna(subset=['Average_size_GT_of_vessels_Value', 'Average_cargo_carrying_capacity_dwt_per_vessel_Value']).copy()

if not scatter_df.empty:
    # 同步把散佈圖（氣泡圖）的分類標籤也換成中文
    vessel_type_cn = {
        "Liquid bulk carriers": "液體散裝船 (油輪)",
        "Liquefied petroleum gas carriers": "液化石油氣船 (LPG)",
        "Liquefied natural gas carriers": "液化天然氣船 (LNG)",
        "Dry bulk carriers": "乾散裝船 (穀物/礦石)",
        "Dry breakbulk carriers": "雜貨船 (散裝箱)",
        "Container ships": "貨櫃船 (標準箱)"
    }
    scatter_df['Vessel_Type_CN'] = scatter_df['CommercialMarket_Label'].map(vessel_type_cn).fillna(scatter_df['CommercialMarket_Label'])

    fig_scatter = px.scatter(
        scatter_df,
        x='Average_size_GT_of_vessels_Value',
        y='Average_cargo_carrying_capacity_dwt_per_vessel_Value',
        size='Average_size_GT_of_vessels_Value',
        color='Vessel_Type_CN',  # 圖例也改成中文！
        labels={
            'Average_size_GT_of_vessels_Value': '平均船舶總噸位 (Average Size GT)',
            'Average_cargo_carrying_capacity_dwt_per_vessel_Value': '平均載重噸位 (Average DWT - 船隻能載多重的貨)',
            'Vessel_Type_CN': '船舶類型'
        },
        title="🔮 停靠船型之規模 (GT) 與實際載重能力 (DWT) 交叉關聯圖"
    )
    fig_scatter.update_layout(font=dict(size=16), title_font=dict(size=20))
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("💡 該國家/地區缺少船隻噸位與載重能力的對應數據。")

st.markdown("---")

# 7. 數據統計摘要與明細
st.markdown("### 📋 數據科學統計摘要與原始明細")

tab1, tab2 = st.tabs(["🔍 資料敘述性統計 (Kaggle EDA 經典特徵)", "📋 原始篩選數據明細 (Excel 樣式表格)"])

with tab1:
    st.markdown("#### 📝 目前篩選數據的數值特徵摘要 (Summary Statistics)")
    if not filtered_df.empty:
        # 顯示統計摘要表格
        st.dataframe(
            filtered_df.describe().T, 
            use_container_width=True, 
            height=320,
            column_config={
                "count": "📊 樣本筆數 (Count)",
                "mean": "📈 平均值 (Mean)",
                "std": "📉 標準差 (Std)",
                "min": "⬇️ 最小值 (Min)",
                "25%": "¼ 25%分位數",
                "50%": "🌓 中位數 (50%)",
                "75%": "¾ 75%分位數",
                "max": "⬆️ 最大值 (Max)"
            }
        )
        
        st.markdown("---")
        st.markdown("### 📖 表格左側【海運英文專有名詞】中文白話文對照解釋")
        
        st.info("""
        * **`Average_age_of_vessels_years_Value`**
          * ➡️ **【停靠船舶平均船齡】**：代表前來停靠的所有船隻平均年齡（歲）。
        * **`Median_time_in_port_days_Value`**
          * ➡️ **【船舶在港停留時間中位數】**：代表船隻進港到離開（含排隊、裝卸、出港）所花費的天數。為衡量塞港最核心的指標。
        * **`Average_size_GT_of_vessels_Value`**
          * ➡️ **【平均船舶總噸位】**：Gross Tonnage (GT) 代表船隻的總內部體積空間。數字愈大，代表來的船體積規模愈大。
        * **`Average_cargo_carrying_capacity_dwt_per_vessel_Value`**
          * ➡️ **【平均船舶載重噸位】**：Deadweight Tonnage (DWT) 代表船隻實際「能載運的貨物總重量」。
        * **`Average_container_carrying_capacity_TEU_per_container_ship_Value`**
          * ➡️ **【貨櫃船平均運載量 (TEU)】**：TEU 代表 20 呎標準貨櫃。此指標代表平均一艘貨櫃船能載多少個標準箱。
        * **`Maximum_size_GT_of_vessels_Value`**
          * ➡️ **【停靠最大船舶總噸位】**：觀測期間內，該港口接待過體積最大（GT 最大）的那一艘超級巨輪。
        * **`Maximum_cargo_carrying_capacity_dwt_of_vessels_Value`**
          * ➡️ **【停靠最大船舶載重噸位】**：觀測期間內，該港口接待過載貨重量最重（DWT 最大）的那一艘超級巨輪。
        * **`Maximum_container_carrying_capacity_TEU_of_container_ships_Value`**
          * ➡️ **【停靠最大貨櫃船運載量 (TEU)】**：觀測期間內，該港口接待過能載最多貨櫃箱的巨無霸貨櫃船容量。
        """)
    else:
        st.write("無資料。")

with tab2:
    st.markdown("#### 📝 原始資料表格明細 (提供下載與線性審查)")
    st.dataframe(filtered_df, use_container_width=True, height=400)
