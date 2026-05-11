"""AI生物家教 - 沪教版高中生物试点 (新版知识图谱)"""
import streamlit as st
import sys
import os
import random

# 添加scripts目录到路径（必须在导入本地模块之前）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# 导入本地模块
from knowledge_graph_loader_v2 import BiologyKnowledgeGraph
from question_generator import QuestionGenerator

# 页面配置
st.set_page_config(
    page_title="ScoreOrbit · AI生物家教", 
    page_icon="🧬", 
    layout="wide"
)

# 初始化 session_state
if 'current_question' not in st.session_state:
    st.session_state['current_question'] = None
if 'show_answer' not in st.session_state:
    st.session_state['show_answer'] = False
if 'random_questions' not in st.session_state:
    st.session_state['random_questions'] = None
if 'random_answers' not in st.session_state:
    st.session_state['random_answers'] = {}
if 'show_random_answers' not in st.session_state:
    st.session_state['show_random_answers'] = False

st.title("🧬 ScoreOrbit · AI生物家教")
st.caption("沪教版高中生物 | 基于156个核心考点的智能复习助手")

# 初始化系统
@st.cache_resource
def init_system():
    kg = BiologyKnowledgeGraph()
    return kg

try:
    kg = init_system()
    st.success(f"✅ 系统已就绪 | 共 {kg.get_statistics()['total']} 个核心知识点")
except Exception as e:
    st.error(f"❌ 系统初始化失败: {str(e)}")
    st.stop()

# 获取统计信息
stats = kg.get_statistics()

# 侧边栏导航
st.sidebar.title("🧬 ScoreOrbit")

# 页面导航
page = st.sidebar.radio(
    "📚 导航",
    ["📖 学习模式", "📝 模拟考试"]
)

if page == "📝 模拟考试":
    # 跳转到模拟考试页面
    st.switch_page("pages/01_exam.py")

# 学习模式
st.sidebar.header("📚 学习模式")

mode = st.sidebar.radio(
    "选择模式",
    ["📖 按模块学习", "🎲 随机刷题", "🔍 知识点搜索", "📊 学习统计"]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 设置")
difficulty = st.sidebar.selectbox("题目难度", ["全部", "基础", "中档", "进阶"])

# ==================== 按模块学习 ====================
if mode == "📖 按模块学习":
    st.subheader("📖 按模块学习")
    
    # 选择模块
    modules = kg.get_modules()
    selected_module = st.selectbox("选择模块", modules, format_func=lambda x: x['name'])
    
    # 获取该模块的知识点
    kps = kg.get_knowledge_by_module(selected_module['name'])
    
    # 根据难度筛选
    if difficulty != "全部":
        kps = [kp for kp in kps if kp['difficulty'] == difficulty]
    
    st.write(f"共 {len(kps)} 个知识点")
    
    # 选择知识点
    kp_names = [kp['name'][:60] for kp in kps]
    if kp_names:
        selected_idx = st.selectbox("选择知识点", range(len(kp_names)), format_func=lambda x: kp_names[x])
        selected_kp = kps[selected_idx]
        
        st.markdown("---")
        st.markdown(f"### 📝 {selected_kp['name']}")
        st.markdown(f"**难度**: `{selected_kp['difficulty']}`")
        
        # 显示知识点内容
        with st.expander("📖 查看详细内容", expanded=True):
            st.markdown(selected_kp['content'])
        
        # 显示考点
        if selected_kp.get('exam_focus'):
            with st.expander("🎯 重点考点"):
                for focus in selected_kp['exam_focus']:
                    st.markdown(f"- {focus}")
        
        # 显示关键数据
        if selected_kp.get('key_data'):
            with st.expander("📊 关键数据"):
                for data in selected_kp['key_data']:
                    st.markdown(f"- {data}")
        
        # 生成练习题按钮
        if st.button("✏️ 生成练习题", type="primary", key="gen_btn"):
            with st.spinner("🤖 AI正在出题..."):
                generator = QuestionGenerator()
                question = generator.generate_question(selected_kp)
                st.session_state['current_question'] = question
                st.session_state['show_answer'] = False

        # 显示题目
        if st.session_state.get('current_question'):
            q = st.session_state['current_question']
            
            st.markdown("---")
            st.markdown("### 📝 练习题")
            
            if q.get('success'):
                st.markdown(f"**{q['question_text']}**")
                
                options = q.get('options', {})
                for letter in ['A', 'B', 'C', 'D']:
                    if letter in options:
                        st.markdown(f"{letter}. {options[letter]}")
                
                if st.button("🔍 查看答案", key="show_ans_btn"):
                    st.session_state['show_answer'] = True
                
                if st.session_state.get('show_answer', False):
                    st.success(f"✅ 答案: {q.get('answer', '未知')}")
                    if q.get('explanation'):
                        st.info(f"📖 解析: {q['explanation']}")
            else:
                st.error(f"出题失败: {q.get('error', '未知错误')}")

# ==================== 随机刷题 ====================
elif mode == "🎲 随机刷题":
    st.subheader("🎲 随机刷题")
    
    # 设置选项
    col1, col2, col3 = st.columns(3)
    with col1:
        n = st.number_input("题目数量", min_value=1, max_value=10, value=3)
    with col2:
        diff_filter = st.selectbox("难度筛选", ["全部", "基础", "中档", "进阶"])
    with col3:
        if st.button("🎲 生成随机题目", type="primary", use_container_width=True):
            # 获取知识点
            if diff_filter != "全部":
                kps = kg.get_knowledge_by_difficulty(diff_filter)
            else:
                kps = kg.get_all_knowledge_points()
            
            if len(kps) < n:
                st.warning(f"该难度下只有 {len(kps)} 个知识点，已调整为 {len(kps)} 题")
                n = len(kps)
            
            if n > 0:
                selected_kps = random.sample(kps, n)
                with st.spinner(f"🤖 AI正在生成 {n} 道题目..."):
                    generator = QuestionGenerator()
                    questions = generator.generate_batch(selected_kps, n)
                st.session_state['random_questions'] = questions
                st.session_state['random_answers'] = {}
                st.session_state['show_random_answers'] = False
    
    # 显示题目
    if st.session_state.get('random_questions'):
        questions = st.session_state['random_questions']
        
        st.markdown("---")
        st.subheader(f"📝 共 {len(questions)} 道题目")
        
        user_answers = {}
        
        for i, q in enumerate(questions):
            with st.container():
                st.markdown(f"### 第 {i+1} 题")
                
                if q.get('success'):
                    st.markdown(f"**{q['question_text']}**")
                    st.caption(f"来源: {q['knowledge_point'][:50]} | 难度: {q['difficulty']}")
                    
                    options = q.get('options', {})
                    if options:
                        option_text = ""
                        for letter in ['A', 'B', 'C', 'D']:
                            if letter in options:
                                option_text += f"\n{letter}. {options[letter]}"
                        st.markdown(option_text)
                        
                        user_answers[i] = st.radio(
                            "选择答案",
                            ['A', 'B', 'C', 'D'],
                            key=f"random_q_{i}",
                            label_visibility="collapsed",
                            horizontal=True
                        )
                    else:
                        st.info(q.get('raw_text', '题目格式解析中...'))
                else:
                    st.error(f"题目生成失败: {q.get('error', '未知错误')}")
                
                st.markdown("---")
        
        # 批改按钮
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ 提交批改", type="primary", use_container_width=True):
                st.session_state['show_random_answers'] = True
                # 计算得分
                score = 0
                for i, q in enumerate(questions):
                    if q.get('success') and q.get('answer') == user_answers.get(i):
                        score += 1
                st.session_state['random_score'] = score
        
        with col_btn2:
            if st.button("🔄 重新生成", use_container_width=True):
                st.session_state['random_questions'] = None
                st.session_state['random_answers'] = {}
                st.session_state['show_random_answers'] = False
                st.rerun()
        
        # 显示答案
        if st.session_state.get('show_random_answers', False):
            st.markdown("---")
            st.subheader("📋 答案与解析")
            
            score = st.session_state.get('random_score', 0)
            st.success(f"🎉 得分: {score}/{len(questions)}")
            
            for i, q in enumerate(questions):
                with st.expander(f"第 {i+1} 题 - {'✅ 正确' if q.get('answer') == user_answers.get(i) else '❌ 错误'}"):
                    st.markdown(f"**你的答案**: {user_answers.get(i, '未选择')}")
                    st.markdown(f"**正确答案**: {q.get('answer', '无')}")
                    st.markdown(f"**解析**: {q.get('explanation', '无')}")

# ==================== 知识点搜索 ====================
elif mode == "🔍 知识点搜索":
    st.subheader("🔍 知识点搜索")
    
    keyword = st.text_input("输入关键词搜索", placeholder="例如: DNA, 光合作用, 遗传...")
    
    if keyword:
        results = kg.get_knowledge_by_keyword(keyword)
        st.write(f"找到 {len(results)} 个相关知识点")
        
        for kp in results[:10]:
            with st.container():
                st.markdown(f"**{kp['name']}**")
                st.caption(f"模块: {kp['module_name']} | 难度: {kp['difficulty']}")
                st.markdown(f"考点: {', '.join(kp.get('exam_focus', [])[:3])}")
                st.markdown("---")

# ==================== 学习统计 ====================
elif mode == "📊 学习统计":
    st.subheader("📊 知识图谱统计")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总知识点", stats['total'])
    with col2:
        st.metric("模块数", len(kg.get_modules()))
    with col3:
        avg_len = sum(len(kp['content']) for kp in kg.get_all_knowledge_points()) / stats['total']
        st.metric("平均内容长度", f"{avg_len:.0f} 字符")
    
    st.markdown("---")
    st.subheader("难度分布")
    st.bar_chart(stats['by_difficulty'])
    
    st.subheader("模块分布")
    st.bar_chart(stats['by_module'])

# 侧边栏底部
st.sidebar.markdown("---")
st.sidebar.caption("💡 基于156个沪教版生物核心知识点 | AI智能出题")