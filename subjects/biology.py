"""
生物学科模块
"""
import streamlit as st
import sys
import os

# 添加公共模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.knowledge_graph_loader import KnowledgeGraph
from common.exam_module import ExamManager, show_paper_list

SUBJECT = "biology"
SUBJECT_ICON = "🧬"
SUBJECT_NAME = "生物"


def show_biology():
    """显示生物学界面"""
    
    st.header(f"{SUBJECT_ICON} 沪教版高中{SUBJECT_NAME}")
    st.caption("合格考复习 | 知识点学习 | 历年真题 | 模拟试卷")
    
    # 初始化
    kg = KnowledgeGraph(SUBJECT)
    exam_mgr = ExamManager(SUBJECT)
    
    # 获取统计
    kg_stats = kg.get_statistics()
    exam_stats = exam_mgr.get_statistics()
    
    # 侧边栏显示统计
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 📊 {SUBJECT_NAME}学科统计")
        st.metric("📚 知识点", kg_stats['total'])
        st.metric("📂 模块数", kg_stats['modules'])
        st.metric("📖 章节数", kg_stats['chapters'])
        st.markdown("---")
        st.metric("📝 真题套数", exam_stats['真题'])
        st.metric("📄 模拟卷套数", exam_stats['模拟卷'])
    
    # 检查数据是否存在
    if kg_stats['total'] == 0:
        st.warning(f"""
        ⚠️ 未找到{SUBJECT_NAME}学科数据
        
        请确保以下目录存在并包含知识图谱文件：
        - `data/{SUBJECT}/knowledge_graph/knowledge.json`
        
        试卷目录（可选）：
        - `data/{SUBJECT}/exams/试卷/真题/`
        - `data/{SUBJECT}/exams/试卷/模拟卷/`
        """)
        return
    
    # 功能选择
    mode = st.radio(
        "选择功能",
        ["📖 知识点学习", "📝 历年真题", "📄 模拟试卷", "🔍 知识点搜索"],
        horizontal=True
    )
    
    # ========== 知识点学习 ==========
    if mode == "📖 知识点学习":
        st.subheader("📖 知识点学习")
        
        # 选择模块
        modules = kg.get_modules()
        module_names = [m.get('name', f'模块{i}') for i, m in enumerate(modules)]
        selected_module_idx = st.selectbox("选择模块", range(len(modules)), format_func=lambda x: module_names[x])
        selected_module = modules[selected_module_idx]
        
        # 选择章节
        chapters = selected_module.get('chapters', [])
        if not chapters:
            st.info("该模块暂无章节数据")
            return
        
        chapter_names = [c.get('name', f'第{i+1}章') for i, c in enumerate(chapters)]
        selected_chapter_idx = st.selectbox("选择章节", range(len(chapters)), format_func=lambda x: chapter_names[x])
        selected_chapter = chapters[selected_chapter_idx]
        
        # 显示知识点列表
        key_points = selected_chapter.get('key_points', [])
        st.write(f"共 {len(key_points)} 个知识点")
        
        # 显示每个知识点
        for i, kp in enumerate(key_points):
            with st.expander(f"📌 {i+1}. {kp.get('name', '知识点')} (难度: {kp.get('level', '基础')})"):
                st.markdown(kp.get('content', '暂无详细内容'))
                
                # 显示考点
                exam_focus = kp.get('exam_focus', [])
                if exam_focus:
                    st.markdown("**🎯 重点考点:**")
                    for focus in exam_focus:
                        st.markdown(f"- {focus}")
        
        # 如果知识点为空，显示提示
        if not key_points:
            st.info("该章节暂无知识点数据，请补充 knowledge.json")
    
    # ========== 历年真题 ==========
    elif mode == "📝 历年真题":
        papers = exam_mgr.get_all_papers()
        show_paper_list(papers['真题'], "📝 历年真题（带答案）", exam_mgr)
    
    # ========== 模拟试卷 ==========
    elif mode == "📄 模拟试卷":
        papers = exam_mgr.get_all_papers()
        show_paper_list(papers['模拟卷'], "📄 模拟试卷（带答案）", exam_mgr)
    
    # ========== 知识点搜索 ==========
    elif mode == "🔍 知识点搜索":
        st.subheader("🔍 知识点搜索")
        
        keyword = st.text_input("输入关键词搜索", placeholder="例如: DNA, 光合作用, 细胞...")
        
        if keyword:
            results = kg.search(keyword)
            st.write(f"找到 {len(results)} 个相关知识点")
            
            for kp in results[:20]:
                with st.expander(f"📌 {kp.get('name', '知识点')} ({kp.get('module', '')} - {kp.get('chapter', '')})"):
                    st.markdown(f"**难度**: {kp.get('level', '基础')}")
                    st.markdown(kp.get('content', '暂无详细内容'))
                    
                    exam_focus = kp.get('exam_focus', [])
                    if exam_focus:
                        st.markdown("**🎯 考点:**")
                        for focus in exam_focus[:3]:
                            st.markdown(f"- {focus}")