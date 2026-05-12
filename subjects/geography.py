"""
地理学科模块
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.knowledge_graph_loader import KnowledgeGraph
from common.exam_module import ExamManager, show_paper_list

SUBJECT = "geography"
SUBJECT_ICON = "🌍"
SUBJECT_NAME = "地理"


def show_geography():
    """显示地理学科界面"""
    
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
        if kg_stats['total'] > 0:
            st.metric("📚 知识点", kg_stats['total'])
            st.metric("📂 模块数", kg_stats['modules'])
            st.metric("📖 章节数", kg_stats['chapters'])
        else:
            st.info("📚 知识点数据待添加")
        st.markdown("---")
        st.metric("📝 真题套数", exam_stats.get('真题', 0))
        st.metric("📄 模拟卷套数", exam_stats.get('模拟卷', 0))
    
    # 如果知识图谱为空，显示提示
    if kg_stats['total'] == 0:
        st.info("""
        🌍 地理学科正在开发中，敬请期待！
        
        预计包含内容：
        - 自然地理：宇宙中的地球、大气、水、地貌
        - 人文地理：人口、城市、农业、工业、交通
        - 区域地理：区域发展、资源环境
        - 历年真题 + 模拟试卷
        
        🚀 开发中，近期上线！
        """)
        
        # 仍然显示试卷（如果有）
        if exam_stats.get('真题', 0) > 0 or exam_stats.get('模拟卷', 0) > 0:
            st.markdown("---")
            st.subheader("📁 试卷资源")
            
            mode = st.radio("选择类型", ["📝 历年真题", "📄 模拟试卷"], horizontal=True)
            
            papers = exam_mgr.get_all_papers()
            if mode == "📝 历年真题":
                show_paper_list(papers.get('真题', []), "历年真题", exam_mgr)
            else:
                show_paper_list(papers.get('模拟卷', []), "模拟试卷", exam_mgr)
        return
    
    # 功能选择
    mode = st.radio(
        "选择功能",
        ["📖 知识点学习", "📝 历年真题", "📄 模拟试卷", "🔍 知识点搜索"],
        horizontal=True
    )
    
    if mode == "📖 知识点学习":
        st.subheader("📖 地理知识点学习")
        
        modules = kg.get_modules()
        if not modules:
            st.warning("暂无知识点数据")
            return
        
        # 选择模块
        module_names = [m.get('name', f'模块{i}') for i, m in enumerate(modules)]
        selected_module_idx = st.selectbox("选择模块", range(len(modules)), format_func=lambda x: module_names[x])
        selected_module = modules[selected_module_idx]
        
        # 选择章节
        chapters = selected_module.get('chapters', [])
        if not chapters:
            st.info("该模块暂无章节")
            return
        
        chapter_names = [c.get('name', f'章节{i}') for i, c in enumerate(chapters)]
        selected_chapter_idx = st.selectbox("选择章节", range(len(chapters)), format_func=lambda x: chapter_names[x])
        selected_chapter = chapters[selected_chapter_idx]
        
        # 显示知识点
        key_points = selected_chapter.get('key_points', [])
        if not key_points:
            st.info("该章节暂无知识点")
            return
        
        st.write(f"共 {len(key_points)} 个知识点")
        
        for i, kp in enumerate(key_points):
            with st.expander(f"📌 {i+1}. {kp.get('name', '知识点')} (难度: {kp.get('difficulty', '基础')})"):
                st.markdown(kp.get('content', '暂无详细内容'))
                
                exam_focus = kp.get('exam_focus', [])
                if exam_focus:
                    st.markdown("**🎯 重点考点:**")
                    for focus in exam_focus:
                        st.markdown(f"- {focus}")
    
    elif mode == "📝 历年真题":
        papers = exam_mgr.get_all_papers()
        show_paper_list(papers.get('真题', []), "历年真题", exam_mgr)
    
    elif mode == "📄 模拟试卷":
        papers = exam_mgr.get_all_papers()
        show_paper_list(papers.get('模拟卷', []), "模拟试卷", exam_mgr)
    
    elif mode == "🔍 知识点搜索":
        st.subheader("🔍 知识点搜索")
        
        keyword = st.text_input("输入关键词搜索", placeholder="例如: 大气环流, 城市化, 板块运动...")
        
        if keyword:
            results = kg.search(keyword)
            st.write(f"找到 {len(results)} 个相关知识点")
            
            for kp in results[:20]:
                with st.expander(f"📌 {kp.get('name', '知识点')}"):
                    st.markdown(f"**难度**: {kp.get('difficulty', '基础')}")
                    st.markdown(kp.get('content', '暂无详细内容'))


if __name__ == "__main__":
    show_geography()