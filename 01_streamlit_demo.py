#!/usr/bin/env python3
"""
Streamlit 入门 Demo
展示常用组件、状态管理、图表绘制等核心功能
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="Streamlit 入门 Demo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主标题
st.title("🚀 Streamlit 快速入门 Demo")
st.markdown("这是一个展示 Streamlit 常用功能的示例应用")

# ===== 侧边栏 =====
st.sidebar.header("⚙️ 控制面板")
st.sidebar.markdown("---")

# 侧边栏输入组件
user_name = st.sidebar.text_input("你的名字", value="访客")
user_age = st.sidebar.slider("年龄", min_value=1, max_value=100, value=25)
favorite_color = st.sidebar.selectbox(
    "喜欢的颜色",
    options=["红色", "蓝色", "绿色", "黄色", "紫色"]
)
enable_advanced = st.sidebar.checkbox("启用高级功能", value=True)

st.sidebar.markdown("---")
st.sidebar.info(f"👋 欢迎, {user_name}!")

# ===== 主内容区域 =====

# 1. 文本与 Markdown
st.header("📝 1. 文本显示")
col1, col2 = st.columns(2)

with col1:
    st.subheader("基础文本")
    st.write("这是普通文本")
    st.success("✅ 成功提示")
    st.info("ℹ️ 信息提示")
    st.warning("⚠️ 警告提示")
    st.error("❌ 错误提示")

with col2:
    st.subheader("Markdown 支持")
    st.markdown("""
    - **粗体文本**
    - *斜体文本*
    - `代码片段`
    - [链接](https://streamlit.io)
    
    支持数学公式: $E = mc^2$
    """)

# 2. 输入组件
st.header("🎛️ 2. 输入组件")
col1, col2, col3 = st.columns(3)

with col1:
    text_input = st.text_input("文本输入", placeholder="输入一些文字...")
    number_input = st.number_input("数字输入", min_value=0, max_value=100, value=50)

with col2:
    date_input = st.date_input("日期选择", value=datetime.now())
    time_input = st.time_input("时间选择")

with col3:
    radio_choice = st.radio("单选", ["选项 A", "选项 B", "选项 C"])
    multiselect = st.multiselect(
        "多选",
        options=["Python", "JavaScript", "Go", "Rust"],
        default=["Python"]
    )

# 3. 按钮与状态管理
st.header("🔘 3. 按钮与状态")

# 初始化 session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'messages' not in st.session_state:
    st.session_state.messages = []

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ 计数 +1"):
        st.session_state.counter += 1

with col2:
    if st.button("➖ 计数 -1"):
        st.session_state.counter -= 1

with col3:
    if st.button("🔄 重置"):
        st.session_state.counter = 0

with col4:
    st.metric(
        label="当前计数",
        value=st.session_state.counter,
        delta=1 if st.session_state.counter > 0 else 0
    )

# 4. 数据展示
st.header("📊 4. 数据表格与图表")

# 生成示例数据
@st.cache_data
def generate_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    return pd.DataFrame({
        '日期': dates,
        '销售额': np.random.randint(100, 1000, size=30),
        '访问量': np.random.randint(500, 5000, size=30),
        '转化率': np.random.uniform(0.01, 0.1, size=30)
    })

df = generate_data()

# 数据表格
st.subheader("数据表格")
st.dataframe(df, use_container_width=True)

# 图表展示
col1, col2 = st.columns(2)

with col1:
    st.subheader("折线图")
    st.line_chart(df.set_index('日期')[['销售额', '访问量']])

with col2:
    st.subheader("面积图")
    st.area_chart(df.set_index('日期')['转化率'])

# 5. 进度条与状态
if enable_advanced:
    st.header("⏱️ 5. 进度指示器")
    
    col1, col2 = st.columns(2)
    
    with col1:
        progress_value = st.slider("调整进度", 0, 100, 50)
        st.progress(progress_value / 100)
    
    with col2:
        st.metric(
            label="完成度",
            value=f"{progress_value}%",
            delta=f"{progress_value - 50}%"
        )

# 6. 文件上传（演示）
st.header("📁 6. 文件上传")
uploaded_file = st.file_uploader(
    "选择一个 CSV 文件",
    type=['csv'],
    help="上传 CSV 文件查看前几行数据"
)

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        st.success(f"✅ 文件上传成功！共 {len(uploaded_df)} 行数据")
        st.dataframe(uploaded_df.head(10))
    except Exception as e:
        st.error(f"❌ 文件读取失败: {e}")

# 7. Expander 与 Tabs
st.header("📂 7. 可折叠内容与标签页")

# Expander
with st.expander("点击展开查看更多信息"):
    st.write("""
    这是一个可折叠的内容区域，适合放置：
    - 详细说明
    - 技术文档
    - 高级设置
    - 调试信息
    """)
    st.code("""
    # Python 代码示例
    def hello_streamlit():
        return "Hello, Streamlit!"
    """, language='python')

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 图表", "📋 数据", "⚙️ 设置"])

with tab1:
    st.write("这是图表标签页")
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    st.line_chart(chart_data)

with tab2:
    st.write("这是数据标签页")
    st.dataframe(chart_data)

with tab3:
    st.write("这是设置标签页")
    st.checkbox("启用通知")
    st.checkbox("自动保存")
    st.selectbox("主题", ["浅色", "深色", "自动"])

# 8. 交互式示例
st.header("🎮 8. 交互式计算器")

col1, col2, col3 = st.columns(3)

with col1:
    num1 = st.number_input("第一个数", value=10.0, format="%.2f")

with col2:
    operation = st.selectbox("运算符", ["+", "-", "×", "÷"])

with col3:
    num2 = st.number_input("第二个数", value=5.0, format="%.2f")

if st.button("🧮 计算", type="primary"):
    try:
        if operation == "+":
            result = num1 + num2
        elif operation == "-":
            result = num1 - num2
        elif operation == "×":
            result = num1 * num2
        elif operation == "÷":
            if num2 == 0:
                st.error("❌ 除数不能为 0")
                result = None
            else:
                result = num1 / num2
        
        if result is not None:
            st.success(f"✅ 结果: {num1} {operation} {num2} = **{result:.2f}**")
    except Exception as e:
        st.error(f"❌ 计算错误: {e}")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🎉 Streamlit Demo v1.0 | 
    <a href='https://docs.streamlit.io' target='_blank'>文档</a> | 
    <a href='https://streamlit.io/gallery' target='_blank'>示例库</a>
    </p>
</div>
""", unsafe_allow_html=True)

# 侧边栏底部信息
st.sidebar.markdown("---")
st.sidebar.caption(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.caption("Python Streamlit Demo")
