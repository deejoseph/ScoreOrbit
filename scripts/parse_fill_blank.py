"""
解析填空版docx文件
- 检测红色文字（RGB 255,0,0）作为填空位置
- 将红色文字替换为 ______
- 提取红色文字作为答案
"""
import os
import json
from docx import Document
from docx.shared import RGBColor
from typing import List, Dict, Tuple

class FillBlankParser:
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.questions = []
    
    def _is_red(self, run) -> bool:
        """检查run是否为红色"""
        if run.font.color and run.font.color.rgb:
            return run.font.color.rgb == RGBColor(255, 0, 0)
        return False
    
    def _extract_red_text(self, paragraph) -> Tuple[str, List[str]]:
        """
        提取段落中的红色文字
        返回: (替换红色为______后的文本, 红色文字列表)
        """
        result_parts = []
        red_texts = []
        
        for run in paragraph.runs:
            if self._is_red(run):
                # 红色文字：记录答案，替换为填空
                text = run.text.strip()
                if text:
                    red_texts.append(text)
                    result_parts.append("______")
                else:
                    result_parts.append(run.text)
            else:
                result_parts.append(run.text)
        
        # 如果没有红色，尝试检测下划线（兼容旧格式）
        if not red_texts:
            for run in paragraph.runs:
                if run.font.underline:
                    text = run.text.strip()
                    if text:
                        red_texts.append(text)
                        result_parts.append("______")
                    else:
                        result_parts.append(run.text)
                else:
                    result_parts.append(run.text)
        
        return ''.join(result_parts), red_texts
    
    def parse(self) -> List[Dict]:
        """解析所有填空题目"""
        
        current_kp = ""
        current_content = []
        
        for para in self.doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # 检测知识点标题（如"知识点1："）
            if '知识点' in text and ('：' in text or ':' in text):
                # 保存上一个知识点
                if current_kp and current_content:
                    self._save_knowledge_point(current_kp, current_content)
                
                # 开始新知识点
                current_kp = text
                current_content = []
            elif current_kp:
                # 处理段落中的红色填空
                processed_text, red_words = self._extract_red_text(para)
                if processed_text.strip():
                    current_content.append({
                        'original': text,
                        'processed': processed_text,
                        'answers': red_words
                    })
        
        # 保存最后一个知识点
        if current_kp and current_content:
            self._save_knowledge_point(current_kp, current_content)
        
        return self.questions
    
    def _save_knowledge_point(self, kp_title: str, content: List[Dict]):
        """保存一个知识点的所有填空"""
        full_text_parts = []
        all_answers = []
        
        for item in content:
            full_text_parts.append(item['processed'])
            if item['answers']:
                all_answers.extend(item['answers'])
        
        self.questions.append({
            'knowledge_point': kp_title,
            'text': '\n'.join(full_text_parts),
            'answers': all_answers,
            'answer_count': len(all_answers)
        })
    
    def save_questions(self, output_path: str):
        """保存题目到JSON"""
        questions = self.parse()
        
        result = {
            "source": os.path.basename(self.docx_path),
            "total_knowledge_points": len(questions),
            "total_fill_blanks": sum(q['answer_count'] for q in questions),
            "questions": []
        }
        
        for i, q in enumerate(questions, 1):
            result['questions'].append({
                "id": f"kp_{i:04d}",
                "title": q['knowledge_point'],
                "text": q['text'],
                "answers": q['answers'],
                "answer_count": q['answer_count']
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已解析 {len(questions)} 个知识点")
        print(f"   总填空数: {result['total_fill_blanks']} 个")
        print(f"   保存到: {output_path}")


if __name__ == "__main__":
    docx_path = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考\高中生物合格考知识点梳理填空（高中学业水平合格性考试）.docx"
    
    if os.path.exists(docx_path):
        parser = FillBlankParser(docx_path)
        output_path = r"D:\PixelSmile\ScoreOrbit\data\questions\fill_blank_questions.json"
        parser.save_questions(output_path)
    else:
        print(f"文件不存在: {docx_path}")