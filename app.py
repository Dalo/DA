import streamlit as st
import pandas as pd
from scipy import stats
import plotly.express as px

# 設定網頁標題與排版
st.set_page_config(page_title="教育數據分析系統", layout="wide")

st.title("教育數據T檢定與滿意度分析系統")
st.info("上傳Excel後，系統將自動處理資料轉型並產生統計圖表。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳Excel檔案", type=["xlsx", "xls"])

if uploaded_file:
    # 讀取數據
    df = pd.read_excel(uploaded_file)
    st.subheader("數據預覽")
    st.dataframe(df.head(10))

    # 2. 側邊欄設定
    st.sidebar.header("參數設定")
    all_cols = df.columns.tolist()
    
    pre_col = st.sidebar.selectbox("選取【前測】欄位", all_cols)
    post_col = st.sidebar.selectbox("選取【後測】欄位", all_cols)
    sat_cols = st.sidebar.multiselect("選取【滿意度】相關欄位(選所有滿意度問題喔)", all_cols)

    if st.sidebar.button("開始分析"):
        st.divider()
        
        # --- A. 資料清理與轉換 (解決 Object 型態報錯) ---
        df[pre_col] = pd.to_numeric(df[pre_col], errors='coerce')
        df[post_col] = pd.to_numeric(df[post_col], errors='coerce')
        
        # 剔除空值
        df_clean = df.dropna(subset=[pre_col, post_col]).copy()
        
        # --- B. T 檢定分析 ---
        st.subheader("學習成效T檢定 (Paired T-Test)")
        
        diff = df_clean[post_col] - df_clean[pre_col]
        
        if diff.std() == 0 or len(df_clean) < 2:
            st.warning("數據樣本不足或缺乏變異量，無法計算T檢定。")
        else:
            t_stat, p_val = stats.ttest_rel(df_clean[post_col], df_clean[pre_col])
            mean_pre = df_clean[pre_col].mean()
            mean_post = df_clean[post_col].mean()
            
            # 顯示主要數據卡片
            c1, c2, c3 = st.columns(3)
            c1.metric("前測平均", f"{mean_pre:.2f}")
            c2.metric("後測平均", f"{mean_post:.2f}", f"{mean_post-mean_pre:+.2f}")
            
            sig_text = "效果顯著" if p_val < 0.05 else "效果不顯著"
            c3.metric("P 值 (顯著性)", f"{p_val:.4f}", sig_text)

            # 學術描述建議
            st.write(f"有效樣本數：{len(df_clean)}")
            if p_val < 0.05:
                st.success(f"統計結果：P值小於0.05，代表教學活動對學員表現有顯著提升。")
            else:
                st.info(f"統計結果：P值大於0.05，尚未達到統計學上的顯著差異。")

        # --- C. 滿意度圖表 (Plotly 方案：解決中文亂碼) ---
        if sat_cols:
            st.divider()
            st.subheader("滿意度平均分數統計")
            
            # 強制將滿意度轉為數字
            for col in sat_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 計算平均
            sat_means = df[sat_cols].mean().reset_index()
            sat_means.columns = ['評價題目', '平均分數']
            
            # 繪製 Plotly 圖表
            fig = px.bar(
                sat_means, 
                x='評價題目', 
                y='平均分數', 
                text='平均分數', 
                color='平均分數',
                color_continuous_scale='Blues',
                title="滿意度各題項平均值"
            )
            
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(yaxis_range=[0, 5.5], xaxis_tickangle=-45)
            
            st.plotly_chart(fig, use_container_width=True)
            st.balloons() # 分析成功小特效
else:
    st.info("請從左側上傳Excel檔案以開始數據分析。")
