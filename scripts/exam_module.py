"""模拟考试模块 - 试卷管理、打印、批改"""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional

class ExamManager:
    def __init__(self, exam_dir: str = None):
        if exam_dir is None:
            self.exam_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exams')
        else:
            self.exam_dir = exam_dir
        
        self.index_path = os.path.join(self.exam_dir, 'exam_index.json')
        self.exams = self._load_index()
    
    def _load_index(self) -> List[Dict]:
        """加载试卷索引"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('exams', [])
        return []
    
    def get_all_exams(self) -> List[Dict]:
        """获取所有试卷"""
        return self.exams
    
    def get_exams_by_type(self, exam_type: str) -> List[Dict]:
        """按类型筛选试卷"""
        return [e for e in self.exams if e.get('type') == exam_type]
    
    def print_exam(self, exam_id: str, output_dir: str = None) -> str:
        """生成可打印的PDF"""
        exam = self._find_exam(exam_id)
        if not exam:
            return None
        
        source_file = os.path.join(self.exam_dir, exam['file'])
        
        if output_dir is None:
            output_dir = os.path.join(self.exam_dir, 'print_ready')
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 复制文件到打印目录
        dest_file = os.path.join(output_dir, f"{exam_id}_{exam['name']}.pdf")
        shutil.copy2(source_file, dest_file)
        
        return dest_file
    
    def _find_exam(self, exam_id: str) -> Optional[Dict]:
        for e in self.exams:
            if e['id'] == exam_id:
                return e
        return None


class AnswerGrader:
    """答案批改器"""
    
    def __init__(self):
        self.ocr = None  # 延迟初始化PaddleOCR
    
    def _init_ocr(self):
        if self.ocr is None:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
    
    def grade_by_ocr(self, image_path: str, answer_key: Dict) -> Dict:
        """通过OCR识别批改"""
        self._init_ocr()
        
        # 识别图片中的文字
        result = self.ocr.ocr(image_path, cls=True)
        
        recognized_text = ""
        for line in result[0]:
            recognized_text += line[1][0] + "\n"
        
        # 比对答案
        score = 0
        total = len(answer_key)
        details = []
        
        for q_id, correct_answer in answer_key.items():
            is_correct = correct_answer in recognized_text
            if is_correct:
                score += 1
            details.append({
                'question_id': q_id,
                'correct_answer': correct_answer,
                'user_answer': self._extract_answer(recognized_text, q_id),
                'is_correct': is_correct
            })
        
        return {
            'score': score,
            'total': total,
            'percentage': score / total * 100,
            'details': details,
            'recognized_text': recognized_text
        }
    
    def _extract_answer(self, text: str, q_id: int) -> str:
        """从识别文本中提取特定题目的答案"""
        # 简化版实现
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if str(q_id) in line:
                return line
        return "未识别"