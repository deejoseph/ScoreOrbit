"""
模拟考试页面 - 试卷浏览（新页面打开）
"""
import streamlit as st
import sys
import os
import webbrowser
import tempfile
import base64

st.set_page_config(
    page_title="ScoreOrbit · 模拟考试",
    page_icon="📝",
    layout="wide"
)

st.title("📝 ScoreOrbit · 模拟考试")
st.caption("历年真题 | 仿真模拟卷 | 带答案直接查看")

# 试卷目录
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
EXAMS_BASE = os.path.join(ROOT_DIR, 'data', 'exams', '试卷')

def get_all_papers():
    """递归扫描所有试卷文件"""
    papers = {'真题': [], '模拟卷': [], '其他': []}
    
    if not os.path.exists(EXAMS_BASE):
        st.error(f"试卷目录不存在: {EXAMS_BASE}")
        return papers
    
    for root, dirs, files in os.walk(EXAMS_BASE):
        for f in files:
            if not f.endswith(('.pdf', '.docx', '.doc')):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(root, EXAMS_BASE)
            name = f.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
            
            path_lower = rel_path.lower() + f.lower()
            
            if '模拟' in path_lower or '仿真' in path_lower:
                papers['模拟卷'].append({'name': name, 'path': full_path, 'display': rel_path})
            elif '真题' in path_lower or '会考' in path_lower or '学业水平' in path_lower:
                papers['真题'].append({'name': name, 'path': full_path, 'display': rel_path})
            else:
                papers['其他'].append({'name': name, 'path': full_path, 'display': rel_path})
    
    return papers

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

papers = get_all_papers()

# 侧边栏筛选
st.sidebar.header("🔍 筛选试卷")
exam_type = st.sidebar.selectbox("试卷类型", ["全部", "真题", "模拟卷", "其他"])

# 获取显示列表
if exam_type == "真题":
    display_papers = papers['真题']
    title = "📚 历年真题（带答案）"
elif exam_type == "模拟卷":
    display_papers = papers['模拟卷']
    title = "📚 模拟试卷（带答案）"
elif exam_type == "其他":
    display_papers = papers['其他']
    title = "📚 其他学习资料"
else:
    display_papers = papers['真题'] + papers['模拟卷'] + papers['其他']
    title = "📚 全部试卷"

st.subheader(title)
st.info("💡 点击「打开」用默认PDF阅读器查看试卷，点击「下载」保存到本地")

if not display_papers:
    st.warning(f"暂无{exam_type}文件")
else:
    st.write(f"共 {len(display_papers)} 个文件")
    
    for paper in display_papers:
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

# 侧边栏统计
st.sidebar.markdown("---")
st.sidebar.subheader("📊 统计")
st.sidebar.metric("真题", len(papers['真题']))
st.sidebar.metric("模拟卷", len(papers['模拟卷']))
st.sidebar.metric("其他", len(papers['其他']))

st.sidebar.markdown("---")
st.sidebar.caption("💡 使用说明:\n1. 点击「打开」用默认阅读器查看\n2. 点击「下载」保存到本地")