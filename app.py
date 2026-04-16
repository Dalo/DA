import streamlit as st
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# 設定網頁標題
st.set_page_config(page_title="前後測數據分析系統", layout="wide")

st.title("📊 教育數據自動化分析系統")
st.write("請上傳 Excel 檔案，系統將自動計算 T 檢定與滿意度圖表。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("選擇 Excel 檔案", type=["xlsx", "xls"])

if uploaded_file:
    # 讀取數據
    df = pd.read_excel(uploaded_file)
    st.subheader("數據預覽")
    st.dataframe(df.head(10)) # 顯示前10筆

    # 2. 側邊欄設定
    st.sidebar.header("分析設定")
    cols = df.columns.tolist()
    pre_col = st.sidebar.selectbox("請選擇【前測】欄位", cols)
    post_col = st.sidebar.selectbox("請選擇【後測】欄位", cols)
    sat_cols = st.sidebar.multiselect("請選擇【滿意度】欄位 (可多選)", cols)

    if st.sidebar.button("開始執行分析"):
        st.divider()
        
        # --- A. 資料清理與轉換 ---
        # 強制轉為數字，解決之前提到的 Object 報錯問題
        df[pre_col] = pd.to_numeric(df[pre_col], errors='coerce')
        df[post_col] = pd.to_numeric(df[post_col], errors='coerce')
        
        # 剔除空值列
        df_clean = df.dropna(subset=[pre_col, post_col]).copy()
        
        # --- B. T 檢定計算 ---
        st.subheader("📌 前後測 T 檢定結果")
        
        diff = df_clean[post_col] - df_clean[pre_col]
        
        if diff.std() == 0:
            st.error("無法計算 T 檢定：所有學生的進步分數完全相同（變異量為 0）。")
        else:
            t_stat, p_val = stats.ttest_rel(df_clean[post_col], df_clean[pre_col])
            mean_pre = df_clean[pre_col].mean()
            mean_post = df_clean[post_col].mean()
            
            # 顯示指標
            c1, c2, c3 = st.columns(3)
            c1.metric("前測平均", f"{mean_pre:.2f}")
            c2.metric("後測平均", f"{mean_post:.2f}", f"{mean_post-mean_pre:+.2f}")
            
            sig_status = "✅ 效果顯著" if p_val < 0.05 else "❌ 效果不顯著"
            c3.metric("P 值 (顯著性)", f"{p_val:.4f}", sig_status)

            # 統計描述
            st.write(f"分析有效樣本數：{len(df_clean)}")
            if p_val < 0.05:
                st.success(f"結果顯示：後測成績與前測有顯著差異 (p < .05)。")
            else:
                st.info(f"結果顯示：未達顯著差異水準 (p > .05)。")

        # --- C. 滿意度圖表 ---
        if sat_cols:
            st.divider()
            st.subheader("🌟 滿意度平均分數")
            
            # 轉換滿意度欄位為數字並計算平均
            for col in sat_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            sat_means = df[sat_cols].mean()
            
            # 繪圖
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=sat_means.index, y=sat_means.values, ax=ax, palette="Blues_d")
            ax.set_ylim(0, 5.5) # 假設滿分5分
            ax.set_ylabel("平均分數")
            
            # 在柱狀圖上方顯示數值
            for i, v in enumerate(sat_means.values):
                ax.text(i, v + 0.1, f"{v:.2f}", ha='center')
                
            st.pyplot(fig)
            
else:
    st.info("請從左側上傳 Excel 檔案以開始分析。")