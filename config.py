"""
ScoreOrbit 配置文件
统一管理所有路径，方便打包和迁移
"""
import os

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(ROOT_DIR, 'data')
KNOWLEDGE_GRAPH_DIR = os.path.join(DATA_DIR, 'knowledge_graph')
QUESTIONS_DIR = os.path.join(DATA_DIR, 'questions')
EXAMS_DIR = os.path.join(DATA_DIR, 'exams')

# 试卷子目录
EXAMS_PAPERS_DIR = os.path.join(EXAMS_DIR, '试卷')
EXAMS_ANSWERS_DIR = os.path.join(EXAMS_DIR, '答案')
EXAMS_PRINT_DIR = os.path.join(EXAMS_DIR, 'print_ready')

# 知识图谱文件路径
KNOWLEDGE_GRAPH_PATH = os.path.join(KNOWLEDGE_GRAPH_DIR, 'biology_knowledge.json')
FILL_BLANK_QUESTIONS_PATH = os.path.join(QUESTIONS_DIR, 'fill_blank_questions.json')

# 试卷索引路径
EXAM_INDEX_PATH = os.path.join(EXAMS_DIR, 'exam_index_full.json')

# 创建必要的目录
os.makedirs(EXAMS_PAPERS_DIR, exist_ok=True)
os.makedirs(EXAMS_ANSWERS_DIR, exist_ok=True)
os.makedirs(EXAMS_PRINT_DIR, exist_ok=True)