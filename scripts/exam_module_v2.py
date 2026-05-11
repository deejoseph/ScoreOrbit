"""
模拟考试模块 V2 - 完整版
支持60套试卷管理、答案库、OCR批改
"""
import os
import json
import shutil
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from config import EXAMS_DIR
except ImportError:
    # 如果没有config.py，使用默认路径
    EXAMS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exams')


class ExamManagerV2:
    """试卷管理器 - 支持完整索引和答案库"""
    
    def __init__(self, exams_dir: str = None):
        if exams_dir is None:
            self.base_exam_dir = EXAMS_DIR
        else:
            self.base_exam_dir = exams_dir
        
        # 试卷子目录
        self.papers_dir = os.path.join(self.base_exam_dir, '试卷')
        self.answers_dir = os.path.join(self.base_exam_dir, '答案')
        self.print_dir = os.path.join(self.base_exam_dir, 'print_ready')
        
        # 创建必要的目录
        os.makedirs(self.papers_dir, exist_ok=True)
        os.makedirs(self.answers_dir, exist_ok=True)
        os.makedirs(self.print_dir, exist_ok=True)
        
        # 加载索引
        self.index_path = os.path.join(self.base_exam_dir, 'exam_index_full.json')
        self.exams = self._load_index()
    
    def _load_index(self) -> List[Dict]:
        """加载完整试卷索引"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('exams', [])
        return []
    
    def _save_index(self):
        """保存索引"""
        data = {
            "version": "1.0",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_exams": len(self.exams),
            "exams": self.exams
        }
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def scan_and_build_index(self, source_dir: str = None):
        """
        扫描试卷目录，重建索引
        source_dir: 外部源目录（首次导入时使用）
        """
        if source_dir and os.path.exists(source_dir):
            # 从外部目录复制并扫描
            self._copy_from_source(source_dir)
        
        # 扫描试卷目录
        self.exams = []
        exam_id = 1
        
        for root, dirs, files in os.walk(self.papers_dir):
            for file in files:
                if file.endswith(('.pdf', '.docx', '.doc')):
                    # 获取相对路径
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_exam_dir)
                    
                    # 判断类型
                    exam_type = "其他"
                    if '真题' in rel_path or '会考' in file or '学业水平' in file:
                        exam_type = "真题"
                    elif '模拟' in rel_path or '仿真' in file:
                        exam_type = "模拟卷"
                    elif '必修' in rel_path or '章节' in rel_path:
                        exam_type = "章节卷"
                    
                    # 提取年份
                    year = None
                    year_match = re.search(r'(201\d|202\d)', file)
                    if year_match:
                        year = year_match.group(1)
                    
                    # 检查是否有答案文件
                    exam_name = os.path.splitext(file)[0]
                    answer_file = os.path.join(self.answers_dir, f"{exam_name}_answers.json")
                    has_answer = os.path.exists(answer_file)
                    
                    self.exams.append({
                        "id": f"exam_{exam_id:04d}",
                        "name": exam_name,
                        "file": rel_path,
                        "type": exam_type,
                        "year": year,
                        "has_answer": has_answer,
                        "size_kb": round(os.path.getsize(os.path.join(root, file)) / 1024, 1)
                    })
                    exam_id += 1
        
        self._save_index()
        return self.exams
    
    def _copy_from_source(self, source_dir: str):
        """从外部源目录复制试卷文件"""
        # 排除答案文件的关键词
        EXCLUDE_PATTERNS = ['解析版', '答案', 'answer', '解析', 'Answer']
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith(('.pdf', '.docx', '.doc')):
                    # 检查是否排除
                    should_exclude = False
                    for pattern in EXCLUDE_PATTERNS:
                        if pattern in file:
                            should_exclude = True
                            break
                    
                    if should_exclude:
                        continue
                    
                    # 保持目录结构
                    rel_path = os.path.relpath(root, source_dir)
                    if rel_path == '.':
                        target_subdir = self.papers_dir
                    else:
                        target_subdir = os.path.join(self.papers_dir, rel_path)
                    
                    os.makedirs(target_subdir, exist_ok=True)
                    
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_subdir, file)
                    
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                        print(f"✅ 已复制: {rel_path}/{file}")
    
    def get_all_exams(self) -> List[Dict]:
        """获取所有试卷"""
        return self.exams
    
    def get_exams_by_type(self, exam_type: str) -> List[Dict]:
        """按类型获取试卷"""
        return [e for e in self.exams if e.get('type') == exam_type]
    
    def get_exams_by_year(self, year: str) -> List[Dict]:
        """按年份获取试卷"""
        return [e for e in self.exams if e.get('year') == year]
    
    def get_exam_by_id(self, exam_id: str) -> Optional[Dict]:
        """根据ID获取试卷"""
        for e in self.exams:
            if e['id'] == exam_id:
                return e
        return None
    
    def get_exam_file_path(self, exam_id: str) -> Optional[str]:
        """获取试卷文件路径"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None
        return os.path.join(self.base_exam_dir, exam['file'])
    
    def print_exam(self, exam_id: str) -> Tuple[bool, str, str]:
        """生成可打印的试卷文件"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return False, None, f"试卷不存在: {exam_id}"
        
        source_file = os.path.join(self.base_exam_dir, exam['file'])
        
        if not os.path.exists(source_file):
            return False, None, f"试卷文件不存在: {source_file}"
        
        # 生成打印文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(source_file)[1]
        dest_file = os.path.join(self.print_dir, f"{exam_id}_{exam['name']}_{timestamp}{ext}")
        
        shutil.copy2(source_file, dest_file)
        
        return True, dest_file, None
    
    def load_answers(self, exam_name: str) -> Optional[Dict]:
        """加载试卷答案"""
        # 尝试加载专用答案文件
        answer_path = os.path.join(self.answers_dir, f"{exam_name}_answers.json")
        
        if os.path.exists(answer_path):
            with open(answer_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 尝试加载手动答案库
        manual_path = os.path.join(self.answers_dir, 'manual_answers.json')
        if os.path.exists(manual_path):
            with open(manual_path, 'r', encoding='utf-8') as f:
                manual = json.load(f)
                if exam_name in manual:
                    return manual[exam_name]
        
        return None
    
    def save_answers(self, exam_name: str, answers: Dict):
        """保存答案"""
        answer_path = os.path.join(self.answers_dir, f"{exam_name}_answers.json")
        with open(answer_path, 'w', encoding='utf-8') as f:
            json.dump(answers, f, ensure_ascii=False, indent=2)
        
        # 更新索引中的has_answer状态
        for exam in self.exams:
            if exam['name'] == exam_name:
                exam['has_answer'] = True
                break
        self._save_index()
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'total': len(self.exams),
            'by_type': {},
            'by_year': {},
            'with_answers': 0
        }
        
        for e in self.exams:
            t = e.get('type', '其他')
            stats['by_type'][t] = stats['by_type'].get(t, 0) + 1
            
            y = e.get('year')
            if y:
                stats['by_year'][y] = stats['by_year'].get(y, 0) + 1
            
            if e.get('has_answer'):
                stats['with_answers'] += 1
        
        return stats


class AnswerGrader:
    """答案批改器（OCR识别+自动评分）"""
    
    def __init__(self):
        self.ocr = None
    
    def _init_ocr(self):
        """延迟初始化OCR"""
        if self.ocr is None:
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            except Exception as e:
                print(f"OCR初始化失败: {e}")
                self.ocr = None
    
    def grade_image(self, image_path: str, answers: Dict) -> Dict:
        """
        拍照批改
        image_path: 上传的答题卡图片路径
        answers: 答案字典 {题号: 正确答案}
        """
        self._init_ocr()
        
        if self.ocr is None:
            return {
                'success': False,
                'error': 'OCR引擎未就绪，请检查PaddleOCR安装'
            }
        
        # OCR识别
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return {
                'success': False,
                'error': '图片识别失败，请确保图片清晰、光线充足'
            }
        
        # 提取识别出的文字
        recognized_text = ""
        for line in result[0]:
            recognized_text += line[1][0] + "\n"
        
        # 批改
        score = 0
        total = len(answers)
        details = []
        
        for q_id, correct_answer in answers.items():
            user_answer = self._extract_answer(recognized_text, q_id)
            is_correct = (user_answer.upper() == correct_answer.upper()) if user_answer else False
            
            if is_correct:
                score += 1
            
            details.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct
            })
        
        return {
            'success': True,
            'score': score,
            'total': total,
            'percentage': round(score / total * 100, 1) if total > 0 else 0,
            'details': details,
            'recognized_text': recognized_text[:500]
        }
    
    def _extract_answer(self, text: str, q_id) -> str:
        """从识别文本中提取特定题目的答案"""
        # 匹配模式：题号+分隔符+答案字母
        patterns = [
            rf'{q_id}[\.、\s]*([A-D])',           # 1.A 或 1、A 或 1 A
            rf'第{q_id}[题问][\s]*([A-D])',        # 第1题 A
            rf'（{q_id}）[\s]*([A-D])',            # （1）A
            rf'\[{q_id}\][\s]*([A-D])',            # [1] A
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return ""
    
    def grade_by_selection(self, user_answers: Dict, answers: Dict) -> Dict:
        """根据用户选择的答案批改（在线答题模式）"""
        score = 0
        total = len(answers)
        details = []
        
        for q_id, correct in answers.items():
            user = user_answers.get(str(q_id), '')
            is_correct = user.upper() == correct.upper() if user else False
            
            if is_correct:
                score += 1
            
            details.append({
                'question_id': q_id,
                'user_answer': user,
                'correct_answer': correct,
                'is_correct': is_correct
            })
        
        return {
            'success': True,
            'score': score,
            'total': total,
            'percentage': round(score / total * 100, 1) if total > 0 else 0,
            'details': details
        }


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("模拟考试模块 V2 测试")
    print("=" * 60)
    
    manager = ExamManagerV2()
    stats = manager.get_statistics()
    
    print(f"\n📚 共加载 {stats['total']} 套试卷")
    print(f"✅ 已有答案: {stats['with_answers']} 套")
    print("\n按类型分布:")
    for t, count in stats['by_type'].items():
        print(f"   {t}: {count} 套")
    
    print("\n📄 试卷示例:")
    for exam in manager.get_all_exams()[:5]:
        answer_status = "✅有答案" if exam.get('has_answer') else "⏳待录入"
        print(f"   [{answer_status}] {exam['name'][:50]}...")
    
    print("\n✅ 模块加载成功")