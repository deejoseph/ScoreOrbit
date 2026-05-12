"""
通用试卷管理模块
支持多学科试卷浏览和下载
"""
import os
import base64
import webbrowser
from typing import Dict, List


class ExamManager:
    """试卷管理器"""
    
    def __init__(self, subject: str):
        """
        初始化试卷管理器
        
        Args:
            subject: 学科名称 (biology, physics, chemistry)
        """
        self.subject = subject
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.exams_dir = os.path.join(self.root_dir, 'data', subject, 'exams', '试卷')
    
    def get_all_papers(self, recursive: bool = True) -> Dict[str, List]:
        """
        获取所有试卷文件
        
        Returns:
            {'真题': [{'name':, 'path':, 'display':}], '模拟卷': [], '其他': []}
        """
        papers = {'真题': [], '模拟卷': [], '其他': []}
        
        if not os.path.exists(self.exams_dir):
            return papers
        
        for root, dirs, files in os.walk(self.exams_dir):
            for f in files:
                if not f.endswith(('.pdf', '.docx', '.doc')):
                    continue
                
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(root, self.exams_dir)
                name = f.replace('.pdf', '').replace('.docx', '').replace('.doc', '')
                
                # 限制名称长度
                if len(name) > 50:
                    name = name[:47] + '...'
                
                path_lower = (rel_path + f).lower()
                
                if '模拟' in path_lower or '仿真' in path_lower:
                    papers['模拟卷'].append({
                        'name': name,
                        'path': full_path,
                        'display': rel_path if rel_path != '.' else ''
                    })
                elif '真题' in path_lower or '会考' in path_lower or '学业水平' in path_lower:
                    papers['真题'].append({
                        'name': name,
                        'path': full_path,
                        'display': rel_path if rel_path != '.' else ''
                    })
                else:
                    papers['其他'].append({
                        'name': name,
                        'path': full_path,
                        'display': rel_path if rel_path != '.' else ''
                    })
        
        return papers
    
    def get_statistics(self) -> Dict:
        """获取试卷统计"""
        papers = self.get_all_papers()
        return {
            '真题': len(papers['真题']),
            '模拟卷': len(papers['模拟卷']),
            '其他': len(papers['其他'])
        }
    
    def open_paper(self, path: str) -> bool:
        """用系统默认程序打开文件"""
        try:
            os.startfile(path)
            return True
        except:
            try:
                webbrowser.open(f'file://{path}')
                return True
            except:
                return False


def show_paper_list(paper_list: List[Dict], title: str, exam_mgr: ExamManager):
    """
    显示试卷列表（用于Streamlit页面）
    
    Args:
        paper_list: 试卷列表
        title: 标题
        exam_mgr: ExamManager实例
    """
    import streamlit as st
    
    st.subheader(title)
    st.info("💡 点击「打开」用默认阅读器查看，点击「下载」保存到本地")
    
    if not paper_list:
        st.warning(f"暂无{title}文件\n\n请将试卷文件放入: data/{exam_mgr.subject}/exams/试卷/ 目录")
        return
    
    st.write(f"共 {len(paper_list)} 个文件")
    
    for paper in paper_list:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**📄 {paper['name']}**")
            if paper['display']:
                st.caption(f"📁 {paper['display']}")
        with col2:
            if st.button("📖 打开", key=f"open_{paper['name']}_{hash(paper['path'])}"):
                if exam_mgr.open_paper(paper['path']):
                    st.toast(f"已打开: {paper['name']}", icon="✅")
                else:
                    st.error("无法打开文件")
        with col3:
            with open(paper['path'], 'rb') as f:
                file_data = f.read()
                st.download_button(
                    label="📥 下载",
                    data=file_data,
                    file_name=os.path.basename(paper['path']),
                    key=f"down_{paper['name']}_{hash(paper['path'])}"
                )
        st.divider()