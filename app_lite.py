"""
ScoreOrbit 简化版 - 知识点学习 + 试卷浏览
"""
import streamlit as st
import sys
import os
import base64

# 添加scripts目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from knowledge_graph_loader_v2 import BiologyKnowledgeGraph

st.set_page_config(page_title="ScoreOrbit · 生物合格考助手", page_icon="🧬", layout="wide")

st.title("🧬 ScoreOrbit · 生物合格考助手")
st.caption("沪教版高中生物 | 156个核心知识点 | 历年真题+模拟卷")

# ==================== 初始化 ====================
@st.cache_resource
def init_system():
    kg = BiologyKnowledgeGraph()
    return kg

try:
    kg = init_system()
    stats = kg.get_statistics()
    st.sidebar.success(f"✅ 共 {stats['total']} 个核心知识点")
except Exception as e:
    st.error(f"❌ 系统初始化失败: {str(e)}")
    st.stop()

# 试卷目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMS_BASE = os.path.join(ROOT_DIR, 'data', 'exams', '试卷')

def get_all_papers():
    """递归扫描所有试卷文件"""
    papers = {'真题': [], '模拟卷': [], '其他': []}
    
    if not os.path.exists(EXAMS_BASE):
        return papers
    
    # 递归遍历所有文件
    for root, dirs, files in os.walk(EXAMS_BASE):
        for f in files:
            if not f.endswith(('.pdf', '.docx', '.doc')):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(root, EXAMS_BASE)
            name = f.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
            
            # 判断类型（根据路径或文件名）
            path_lower = rel_path.lower() + f.lower()
            
            if '模拟' in path_lower or '仿真' in path_lower:
                papers['模拟卷'].append({'name': name, 'path': full_path, 'display': rel_path})
            elif '真题' in path_lower or '会考' in path_lower or '学业水平' in path_lower:
                papers['真题'].append({'name': name, 'path': full_path, 'display': rel_path})
            else:
                papers['其他'].append({'name': name, 'path': full_path, 'display': rel_path})
    
    return papers

# 加载试卷
papers = get_all_papers()

# 侧边栏导航
st.sidebar.title("📚 导航")
page = st.sidebar.radio(
    "选择功能",
    ["📖 知识点学习", "📝 历年真题", "📄 模拟试卷", "📊 学习统计"]
)

# 预览状态
if 'current_paper' not in st.session_state:
    st.session_state.current_paper = None

def open_with_default_app(file_path):
    """用系统默认程序打开文件"""
    try:
        os.startfile(file_path)  # Windows
        return True
    except:
        try:
            webbrowser.open(f'file://{file_path}')
            return True
        except:
            return False

def show_paper_list(paper_list, title):
    """显示试卷列表"""
    st.subheader(title)
    st.info("💡 点击「打开」用默认PDF阅读器查看试卷，点击「下载」保存到本地")
    
    if not paper_list:
        st.warning(f"暂无{title}文件")
        return
    
    st.write(f"共 {len(paper_list)} 个文件")
    
    for paper in paper_list:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**📄 {paper['name']}**")
            if paper['display'] and paper['display'] != '.':
                st.caption(f"📁 {paper['display']}")
        with col2:
            if st.button("📖 打开", key=f"open_{paper['name']}_{hash(paper['path'])}"):
                success = open_with_default_app(paper['path'])
                if success:
                    st.toast(f"已打开: {paper['name']}", icon="✅")
                else:
                    st.error("无法打开文件，请手动下载后查看")
        with col3:
            with open(paper['path'], 'rb') as f:
                file_data = f.read()
                st.download_button(
                    label="📥 下载",
                    data=file_data,
                    file_name=os.path.basename(paper['path']),
                    key=f"download_{paper['name']}_{hash(paper['path'])}"
                )
        st.divider()

# ==================== 知识点学习 ====================
if page == "📖 知识点学习":
    st.subheader("📖 沪教版高中生物知识图谱")
    
    modules = kg.get_modules()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_module = st.selectbox("选择模块", modules, format_func=lambda x: x['name'])
    
    kps = kg.get_knowledge_by_module(selected_module['name'])
    
    difficulty_filter = st.selectbox("难度筛选", ["全部", "基础", "中档", "进阶"])
    if difficulty_filter != "全部":
        kps = [kp for kp in kps if kp['difficulty'] == difficulty_filter]
    
    st.write(f"共 {len(kps)} 个知识点")
    
    if kps:
        kp_names = [f"{kp['name'][:60]} ({kp['difficulty']})" for kp in kps]
        selected_idx = st.selectbox("选择知识点", range(len(kp_names)), format_func=lambda x: kp_names[x])
        selected_kp = kps[selected_idx]
        
        st.markdown("---")
        st.markdown(f"### 📝 {selected_kp['name']}")
        st.markdown(f"**难度**: `{selected_kp['difficulty']}`")
        
        with st.expander("📖 详细内容", expanded=True):
            st.markdown(selected_kp['content'])
        
        if selected_kp.get('exam_focus'):
            with st.expander("🎯 重点考点"):
                for focus in selected_kp['exam_focus']:
                    st.markdown(f"- {focus}")

# ==================== 历年真题 ====================
elif page == "📝 历年真题":
    show_paper_list(papers['真题'], "📝 历年真题（带答案）")

# ==================== 模拟试卷 ====================
elif page == "📄 模拟试卷":
    show_paper_list(papers['模拟卷'], "📄 模拟试卷（带答案）")

# ==================== 学习统计 ====================
elif page == "📊 学习统计":
    st.subheader("📊 学习统计")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 总知识点", stats['total'])
    with col2:
        st.metric("📂 模块数", len(kg.get_modules()))
    with col3:
        avg_len = sum(len(kp['content']) for kp in kg.get_all_knowledge_points()) / stats['total']
        st.metric("平均内容", f"{avg_len:.0f} 字符")
    
    st.markdown("---")
    st.subheader("难度分布")
    st.bar_chart(stats['by_difficulty'])
    
    st.subheader("模块分布")
    st.bar_chart(stats['by_module'])
    
    st.markdown("---")
    st.subheader("📁 试卷统计")
    st.metric("历年真题", len(papers['真题']))
    st.metric("模拟试卷", len(papers['模拟卷']))
    st.metric("其他资料", len(papers['其他']))

# 预览
if st.session_state.current_paper:
    preview_paper(st.session_state.current_paper)

# 侧边栏底部
st.sidebar.markdown("---")
st.sidebar.caption("💡 基于沪教版高中生物教材 | 156个核心知识点 | 历年真题+模拟卷")