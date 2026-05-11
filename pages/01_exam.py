"""
模拟考试页面 - 试卷预览、打印、批改
"""
import streamlit as st
import sys
import os
import json
import base64
from datetime import datetime

# 添加scripts目录
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from exam_module_v2 import ExamManagerV2, SimpleGrader

st.set_page_config(
    page_title="ScoreOrbit · 模拟考试",
    page_icon="📝",
    layout="wide"
)

st.title("📝 ScoreOrbit · 模拟考试")
st.caption("历年真题 | 仿真模拟卷 | 章节专项训练 | 一键打印")

# 初始化
@st.cache_resource
def init_exam_manager():
    return ExamManagerV2()

manager = init_exam_manager()
stats = manager.get_statistics()

# 侧边栏筛选
st.sidebar.header("🔍 筛选试卷")
exam_type = st.sidebar.selectbox("试卷类型", ["全部", "真题", "模拟卷", "章节卷", "精品解析"])

# 获取试卷列表
if exam_type == "全部":
    exams = manager.get_all_exams()
else:
    exams = manager.get_exams_by_type(exam_type)

st.sidebar.markdown(f"📊 共 {len(exams)} 套试卷")

# 初始化预览状态
if 'expanded_exams' not in st.session_state:
    st.session_state['expanded_exams'] = {}

# 主界面 - 试卷列表
st.subheader("📚 试卷库")

# 搜索框
search = st.text_input("🔍 搜索试卷", placeholder="输入试卷名称关键词...")
if search:
    exams = [e for e in exams if search.lower() in e['name'].lower()]

# 显示试卷
for exam in exams:
    with st.container():
        # 试卷卡片头部
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        
        with col1:
            st.markdown(f"**📄 {exam['name']}**")
            st.caption(f"类型: {exam['type']} | 年份: {exam.get('year', '未知')}")
        
        with col2:
            is_expanded = st.session_state['expanded_exams'].get(exam['id'], False)
            btn_label = "📖 收起" if is_expanded else "📖 预览"
            if st.button(btn_label, key=f"preview_{exam['id']}"):
                st.session_state['expanded_exams'][exam['id']] = not is_expanded
                st.rerun()
        
        with col3:
            if st.button("🖨️ 打印", key=f"print_{exam['id']}"):
                success, file_path, error = manager.print_exam(exam['id'])
                if success:
                    st.toast(f"✅ 打印文件已生成", icon="✅")
                else:
                    st.toast(f"❌ 失败: {error}", icon="❌")
        
        with col4:
            if exam.get('has_answer'):
                st.caption("✅ 有答案")
            else:
                st.caption("⏳ 待补充")
        
        # 如果展开，显示该试卷的预览
        if st.session_state['expanded_exams'].get(exam['id'], False):
            file_path = os.path.join(manager.base_exam_dir, exam['file'])
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024
                st.caption(f"📁 文件大小: {file_size:.1f} KB")
                
                # 操作按钮行
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    # 下载按钮
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        file_ext = os.path.splitext(file_path)[1]
                        mime_type = "application/pdf" if file_ext == '.pdf' else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        st.download_button(
                            label="📥 下载试卷",
                            data=file_data,
                            file_name=os.path.basename(file_path),
                            mime=mime_type,
                            key=f"download_{exam['id']}"
                        )
                
                with col_btn2:
                    # 用系统程序打开按钮
                    import platform
                    import subprocess
                    
                    def open_with_default_app(file_path):
                        """用系统默认程序打开文件"""
                        try:
                            if platform.system() == "Windows":
                                os.startfile(file_path)
                            elif platform.system() == "Darwin":  # macOS
                                subprocess.run(["open", file_path])
                            else:  # Linux
                                subprocess.run(["xdg-open", file_path])
                            return True, "已打开"
                        except Exception as e:
                            return False, str(e)
                    
                    if st.button("📂 打开文件", key=f"open_{exam['id']}"):
                        success, msg = open_with_default_app(file_path)
                        if success:
                            st.toast(f"✅ 已用系统程序打开", icon="✅")
                        else:
                            st.toast(f"❌ 打开失败: {msg}", icon="❌")
                
                with col_btn3:
                    # 提示信息
                    st.caption("💡 下载后也可直接打开")
                
                # PDF预览提示
                if file_path.endswith('.pdf'):
                    st.info("📄 **PDF试卷** - 下载后双击即可用系统阅读器打开并打印")
                else:
                    st.info("📝 **Word试卷** - 下载后可用 Microsoft Word 或 WPS 打开并打印")
                
                # 显示文件信息（可选）
                with st.expander("📋 文件详情"):
                    st.json({
                        "文件名": os.path.basename(file_path),
                        "文件大小": f"{file_size:.1f} KB",
                        "文件类型": "PDF" if file_path.endswith('.pdf') else "Word文档",
                        "存储路径": file_path,
                        "是否有答案": exam.get('has_answer', False)
                    })
            else:
                st.error(f"❌ 文件不存在: {file_path}")
                st.info("请检查试卷文件是否在以下目录:\n" + manager.base_exam_dir)
        
        st.markdown("---")

# 侧边栏统计
st.sidebar.markdown("---")
st.sidebar.subheader("📊 统计")
st.sidebar.metric("总试卷数", stats['total'])
st.sidebar.metric("真题套数", stats['by_type'].get('真题', 0))
st.sidebar.metric("模拟卷套数", stats['by_type'].get('模拟卷', 0))

st.sidebar.markdown("---")
st.sidebar.info("💡 使用说明:\n1. 点击「预览」展开试卷\n2. 点击「下载试卷」保存到本地\n3. 用本地PDF阅读器打开打印")