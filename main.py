"""
ScoreOrbit 多学科合格考助手 - 统一入口
沪教版高中 | 生物 · 物理 · 化学 · 历史
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
**学科**: 生物 · 物理 · 化学 · 历史 · 地理 · 政治  
**数据**: 
- 生物: 156个知识点
- 物理: 85个知识点  
- 化学: 22个知识点
- 历史: 398个知识点
- 地理: 43个知识点
- 政治: 48个知识点

**试卷**: 历年真题 + 模拟卷
""")
# 学科选择
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 选择学科")

# 使用radio选择学科
subject = st.sidebar.radio(
    "学科",
    ["🧬 生物", "⚛️ 物理", "🧪 化学", "📜 历史", "🌍 地理", "🏛️ 政治"],
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
elif subject == "🧪 化学":
    from subjects.chemistry import show_chemistry
    show_chemistry()
elif subject == "📜 历史":
    from subjects.history import show_history
    show_history()
elif subject == "🌍 地理":
    from subjects.geography import show_geography
    show_geography()
elif subject == "🏛️ 政治":
    from subjects.politics import show_politics
    show_politics()
    
# 页脚
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>© 2026 ScoreOrbit | 祝同学们合格考顺利通过！🎉</p>",
    unsafe_allow_html=True
)