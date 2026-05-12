"""
ScoreOrbit 多学科合格考助手 - 统一入口
沪教版高中 | 生物 · 物理 · 化学
"""
import streamlit as st
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 页面配置
st.set_page_config(
    page_title="ScoreOrbit · 合格考助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .subject-card {
        padding: 2rem;
        text-align: center;
        border-radius: 10px;
        background: #f0f2f6;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .subject-card:hover {
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown("""
<div class="main-header">
    <h1>🎓 ScoreOrbit · 合格考助手</h1>
    <p>沪教版高中 | 知识点 + 真题 + 模拟卷 | 多学科支持</p>
</div>
""", unsafe_allow_html=True)

# 侧边栏信息
st.sidebar.title("📚 ScoreOrbit")
st.sidebar.info("""
**版本**: v2.0  
**学科**: 生物 · 物理  
**数据**: 156个生物知识点 + 物理知识点  
**试卷**: 历年真题 + 模拟卷
""")

# 学科选择
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 选择学科")

# 使用radio选择学科
subject = st.sidebar.radio(
    "学科",
    ["🧬 生物", "⚛️ 物理", "🧪 化学"],
    index=0,
    format_func=lambda x: x
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 提示: 试卷文件需单独获取，请联系狄老师")

# 根据选择显示对应学科
if subject == "🧬 生物":
    from subjects.biology import show_biology
    show_biology()
elif subject == "⚛️ 物理":
    from subjects.physics import show_physics
    show_physics()
else:
    st.info("🧪 化学学科正在开发中，敬请期待...")
    st.markdown("""
    ### 化学学科规划
    
    预计包含内容：
    - 必修一：物质及其变化、海水中的重要元素
    - 必修二：化学反应与能量、有机化学基础
    - 历年真题 + 模拟试卷
    
    🚀 开发中，近期上线！
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>© 2026 ScoreOrbit | 祝同学们合格考顺利通过！🎉</p>",
    unsafe_allow_html=True
)