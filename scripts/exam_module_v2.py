"""
模拟考试模块 V2 - 支持60套试卷的完整管理
"""
import os
import json
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ExamManagerV2:
    """试卷管理器 - 支持完整索引"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exams')
        else:
            self.data_dir = data_dir
        
        self.base_exam_dir = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考"
        self.index_path = os.path.join(self.data_dir, 'exam_index_full.json')
        self.exams = self._load_index()
    
    def _load_index(self) -> List[Dict]:
        """加载完整试卷索引"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('exams', [])
        return []
    
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
    
    def print_exam(self, exam_id: str) -> Tuple[bool, str, str]:
        """
        生成可打印的试卷文件
        返回: (成功, 文件路径, 错误信息)
        """
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return False, None, f"试卷不存在: {exam_id}"
        
        source_file = os.path.join(self.base_exam_dir, exam['file'])
        
        if not os.path.exists(source_file):
            return False, None, f"试卷文件不存在: {source_file}"
        
        # 创建打印目录
        print_dir = os.path.join(self.data_dir, 'print_ready')
        os.makedirs(print_dir, exist_ok=True)
        
        # 生成打印文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(source_file)[1]
        dest_file = os.path.join(print_dir, f"{exam_id}_{exam['name']}_{timestamp}{ext}")
        
        # 复制文件
        shutil.copy2(source_file, dest_file)
        
        return True, dest_file, None
    
    def get_answer_file(self, exam_id: str) -> Optional[str]:
        """获取答案文件路径"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        if exam.get('answer_file'):
            answer_path = os.path.join(self.base_exam_dir, 
                                       os.path.dirname(exam['file']), 
                                       exam['answer_file'])
            if os.path.exists(answer_path):
                return answer_path
        
        # 如果原文件本身就包含答案
        if '答案' in exam['file'] or '解析' in exam['file']:
            return os.path.join(self.base_exam_dir, exam['file'])
        
        return None
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'total': len(self.exams),
            'by_type': {},
            'by_year': {}
        }
        
        for e in self.exams:
            t = e.get('type', '其他')
            stats['by_type'][t] = stats['by_type'].get(t, 0) + 1
            
            y = e.get('year')
            if y:
                stats['by_year'][y] = stats['by_year'].get(y, 0) + 1
        
        return stats


class SimpleGrader:
    """简单批改器（用于模拟考试）"""
    
    def __init__(self):
        self.ocr = None
    
    def _init_ocr(self):
        """延迟初始化OCR"""
        if self.ocr is None:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
    
    def grade_image(self, image_path: str, answer_key: Dict) -> Dict:
        """拍照批改"""
        self._init_ocr()
        
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return {'success': False, 'error': '图片识别失败'}
        
        recognized_text = ""
        for line in result[0]:
            recognized_text += line[1][0] + "\n"
        
        # 简单批改逻辑（实际使用时需要根据具体试卷配置答案）
        return {
            'success': True,
            'recognized_text': recognized_text[:500],
            'message': '识别完成，请配置答案后批改'
        }


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("模拟考试模块 V2 测试")
    print("=" * 60)
    
    manager = ExamManagerV2()
    stats = manager.get_statistics()
    
    print(f"\n📚 共加载 {stats['total']} 套试卷")
    print("\n按类型分布:")
    for t, count in stats['by_type'].items():
        print(f"   {t}: {count} 套")
    
    print("\n📅 按年份分布（真题）:")
    for year in sorted(stats['by_year'].keys()):
        print(f"   {year}: {stats['by_year'][year]} 套")
    
    print("\n📄 试卷示例:")
    for exam in manager.get_all_exams()[:5]:
        print(f"   [{exam['type']}] {exam['name'][:40]}...")
    
    print("\n✅ 模块加载成功")