import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# --- 配置与数据初始化 ---
st.set_page_config(page_title="我的行程账本", layout="wide")
DATA_FILE = "travel_data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["日期", "城市", "类别", "项目内容", "金额(RMB)", "备注"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- 侧边栏：录入面板 ---
st.sidebar.header("📝 新增记录")
with st.sidebar.form("entry_form", clear_on_submit=True):
    date = st.date_input("日期", datetime.date.today())
    city = st.selectbox("城市", ["杭州", "深圳", "香港", "途中/高速"])
    category = st.selectbox("类别", ["餐饮", "住宿", "景点", "自驾补能", "高速/停车", "购物", "其他"])
    content = st.text_input("项目内容 (如：任天堂商店、Model Y充电)")
    
    col1, col2 = st.columns(2)
    with col1:
        currency = st.radio("币种", ["CNY", "HKD"])
    with col2:
        amount = st.number_input("金额", min_value=0.0)
    
    # 自动汇率换算 (参考 2026 年初汇率)
    final_amount = amount * 0.92 if currency == "HKD" else amount
    
    remark = st.text_area("备注")
    submit = st.form_submit_button("保存记录")

    if submit:
        new_data = {
            "日期": date.strftime("%Y-%m-%d"),
            "城市": city,
            "类别": category,
            "项目内容": content,
            "金额(RMB)": round(final_amount, 2),
            "备注": remark
        }
        save_data(new_data)
        st.success("记录成功！")

# --- 主界面：看板与查询 ---
st.title("🚗 杭深港自驾行程管理")

df_display = load_data()

# 1. 数据统计
if not df_display.empty:
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total_cost = df_display["金额(RMB)"].sum()
    charging_cost = df_display[df_display["类别"] == "自驾补能"]["金额(RMB)"].sum()
    
    col_stat1.metric("总开销", f"¥{total_cost:,.2f}")
    col_stat2.metric("行程天数", len(df_display["日期"].unique()))
    col_stat3.metric("充电总额", f"¥{charging_cost:,.2f}")

    # 2. 图表展示
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("支出构成")
        fig = px.pie(df_display, values='金额(RMB)', names='类别', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("城市开销分布")
        fig_bar = px.bar(df_display.groupby("城市")["金额(RMB)"].sum().reset_index(), 
                         x='城市', y='金额(RMB)', color='城市')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    # 3. 详细列表查询
    st.markdown("---")
    st.subheader("📋 行程明细")
    st.dataframe(df_display.sort_values("日期", ascending=False), use_container_width=True)
else:
    st.info("目前还没有记录，请在左侧侧边栏录入你的第一笔开销。")
