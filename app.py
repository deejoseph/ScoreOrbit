"""AI生物家教 - 沪教版高中生物试点"""
import streamlit as st
import sys
import os

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from knowledge_graph_loader import BiologyKnowledgeGraph
from review_module import KnowledgeReviewer

# 页面配置
st.set_page_config(
    page_title="AI生物家教 - ScoreOrbit", 
    page_icon="🧬", 
    layout="wide"
)

st.title("🧬 ScoreOrbit · AI生物家教")
st.caption("沪教版高中生物 | 针对合格考/等级考的智能复习助手")

# 初始化系统
@st.cache_resource
def init_system():
    kg = BiologyKnowledgeGraph()
    reviewer = KnowledgeReviewer(kg)
    return kg, reviewer

try:
    kg, reviewer = init_system()
    st.success("✅ 系统已就绪")
except Exception as e:
    st.error(f"❌ 系统初始化失败: {str(e)}")
    st.info("请确保:\n1. Ollama服务正在运行\n2. 已下载qwen2.5-coder:7b模型")
    st.stop()

# 侧边栏
st.sidebar.header("📚 选择章节")
chapters = kg.get_all_chapters()
chapter_names = [f"{c['name']} ({c['module']})" for c in chapters]
selected_idx = st.sidebar.selectbox("选择章节", range(len(chapters)), format_func=lambda x: chapter_names[x])
selected_chapter = chapters[selected_idx]

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 设置")
difficulty = st.sidebar.selectbox("题目难度", ["基础", "中档", "进阶"])
action = st.sidebar.radio("选择模式", ["📖 知识点复习", "✏️ 智能出题"])

# 主界面
col1, col2 = st.columns([2, 1])

with col1:
    if action == "📖 知识点复习":
        st.subheader(f"📖 {selected_chapter['name']}")
        
        # 获取该章节的所有知识点
        kps = kg.get_chapter_knowledge(selected_chapter['id'])
        topics = [kp['name'] for kp in kps]
        
        if topics:
            selected_topic = st.selectbox("选择具体知识点", topics)
            
            if st.button("🚀 开始复习", type="primary"):
                with st.spinner("🤖 AI正在生成复习内容..."):
                    review_content = reviewer.review_topic(selected_chapter['id'], selected_topic)
                    st.markdown(review_content)
        else:
            st.info("该章节暂无详细知识点")
    
    else:  # 智能出题
        st.subheader(f"✏️ {selected_chapter['name']} - {difficulty}难度")
        
        if st.button("🎲 生成题目", type="primary"):
            with st.spinner("🤖 AI正在出题..."):
                result = reviewer.generate_question(selected_chapter['id'], difficulty)
                
                if result.get('success'):
                    st.markdown(result['question_text'])
                    
                    # 显示答案按钮
                    if st.button("🔍 显示答案"):
                        # 提取答案部分
                        text = result['question_text']
                        if "【答案】" in text:
                            answer_part = text.split("【答案】")[1].split("【解析】")[0] if "【解析】" in text else text.split("【答案】")[1]
                            st.success(f"答案: {answer_part.strip()}")
                        else:
                            st.info("答案已在题目中标注")
                else:
                    st.error(f"出题失败: {result.get('error')}")

with col2:
    st.subheader("📊 学习进度")
    st.metric("📚 总章节数", len(chapters))
    st.metric("📖 已学知识点", "0")
    st.metric("✅ 今日练习", "0")
    
    st.markdown("---")
    st.subheader("💡 备考建议")
    st.info("""
    📌 **使用指南**
    1. 选择章节 → 复习知识点
    2. 选择难度 → 生成练习题
    3. 反复练习，巩固薄弱点
    
    🎯 合格考重点：必修一 + 必修二
    """)
    
    st.markdown("---")
    st.subheader("🤖 当前模型")
    st.code("qwen2.5-coder:7b", language="bash")

# 运行命令提示
st.sidebar.markdown("---")
st.sidebar.caption("运行命令: streamlit run app.py")