"""
将高中生物合格考知识点docx文件转换为知识图谱JSON
"""
import os
import re
import json
from docx import Document
from typing import List, Dict, Any
from tqdm import tqdm

class DocxToKnowledgeGraph:
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.knowledge_points = []
        self.current_module = "必修一 分子与细胞"
        self.current_chapter = ""
        
    def parse(self) -> Dict[str, Any]:
        """解析docx文件，提取知识点"""
        
        paragraphs = self.doc.paragraphs
        i = 0
        total = len(paragraphs)
        
        kp_id = 1
        
        with tqdm(total=total, desc="解析知识点") as pbar:
            while i < total:
                text = paragraphs[i].text.strip()
                
                if not text:
                    i += 1
                    pbar.update(1)
                    continue
                
                # 检测知识点标题（如"知识点7：C、H、O、N、P、S 等元素组成复杂的生物分子"）
                if re.match(r'知识点\d+[：:]', text):
                    # 保存上一个知识点
                    if self.current_chapter:
                        self._save_current_kp()
                    
                    # 开始新知识点
                    self.current_chapter = text
                    self.current_content = []
                    kp_id += 1
                    
                # 检测章节分割（必修一/必修二）
                elif '必修一' in text or '必修二' in text:
                    if '必修二' in text:
                        self.current_module = "必修二 遗传与进化"
                    else:
                        self.current_module = "必修一 分子与细胞"
                    self.current_content = []
                    
                # 收集当前知识点的内容
                elif self.current_chapter:
                    self.current_content.append(text)
                    
                i += 1
                pbar.update(1)
        
        # 保存最后一个知识点
        if self.current_chapter:
            self._save_current_kp()
            
        return self._build_json()
    
    def _save_current_kp(self):
        """保存当前知识点"""
        content = "\n".join(self.current_content)
        
        # 提取考点（Exam Focus）
        exam_focus = self._extract_exam_focus(content)
        
        # 提取关键细节
        key_details = self._extract_key_details(content)
        
        # 生成题目（基于内容）
        questions = self._generate_questions_from_content(content)
        
        # 确定难度等级
        difficulty = self._determine_difficulty(content)
        
        self.knowledge_points.append({
            "id": f"kp_{len(self.knowledge_points) + 1:04d}",
            "name": self._extract_kp_name(self.current_chapter),
            "full_title": self.current_chapter,
            "module": self.current_module,
            "content": content[:500],  # 限制长度
            "key_details": key_details,
            "exam_focus": exam_focus,
            "difficulty": difficulty,
            "questions": questions
        })
    
    def _extract_kp_name(self, title: str) -> str:
        """从标题中提取知识点名称"""
        # 去掉"知识点X："前缀
        match = re.search(r'知识点\d+[：:]\s*(.+)', title)
        if match:
            return match.group(1)[:30]  # 限制长度
        return title[:30]
    
    def _extract_exam_focus(self, content: str) -> List[str]:
        """提取考点（基于填空和重复出现的内容）"""
        focuses = []
        
        # 查找【深入思考】部分
        if '【深入思考】' in content:
            thinking_part = content.split('【深入思考】')[1]
            # 提取问句作为考点
            questions = re.findall(r'(\d+[、.].*?)\n', thinking_part)
            for q in questions[:3]:
                focuses.append(q.strip())
        
        # 如果没有深入思考，则提取带下划线填空的内容
        if not focuses:
            underlines = re.findall(r'\[(.*?)\]{.underline}', content)
            unique_underlines = list(set(underlines))[:5]
            focuses.extend(unique_underlines)
            
        return focuses[:5]  # 最多5个考点
    
    def _extract_key_details(self, content: str) -> List[str]:
        """提取关键细节"""
        details = []
        
        # 提取带编号的内容
        numbered_items = re.findall(r'（\d+）(.*?)[\n。]', content)
        for item in numbered_items[:5]:
            cleaned = item.strip()
            if cleaned and len(cleaned) > 5:
                details.append(cleaned)
                
        # 提取表格中的内容
        if '---' in content or '|' in content:
            lines = content.split('\n')
            for line in lines:
                if '|' in line and '---' not in line:
                    cells = [c.strip() for c in line.split('|') if c.strip()]
                    if cells:
                        details.append(' | '.join(cells[:3]))
                        
        return details[:5]
    
    def _determine_difficulty(self, content: str) -> str:
        """根据内容判断难度"""
        # 包含计算、遗传等进阶内容
        if any(word in content for word in ['计算', '推导', '概率', '定律', '公式']):
            return "进阶"
        # 包含深入思考、原理等中档内容
        elif any(word in content for word in ['原理', '机制', '过程', '比较']):
            return "中档"
        else:
            return "基础"
    
    def _generate_questions_from_content(self, content: str) -> List[Dict]:
        """基于内容生成题目"""
        questions = []
        
        # 查找已有的填空题
        fill_blanks = re.findall(r'([^。]*?\[(.*?)\]{.underline}[^。]*?)', content)
        for i, fb in enumerate(fill_blanks[:3]):
            questions.append({
                "text": fb[0].replace(fb[1], "______"),
                "answer": fb[1],
                "type": "填空题",
                "difficulty": "基础"
            })
            
        # 查找带答案的题目
        if '答案' in content.lower() or '解析' in content:
            # 提取可能的题目区域
            lines = content.split('\n')
            current_question = ""
            for line in lines:
                if re.match(r'^\d+[、.]', line):
                    if current_question:
                        questions.append({
                            "text": current_question,
                            "answer": "参考教材",
                            "type": "简答题",
                            "difficulty": "中档"
                        })
                    current_question = line
                elif 'A.' in line or 'B.' in line:
                    current_question += " " + line
        
        return questions[:3]  # 最多3个题目
    
    def _build_json(self) -> Dict[str, Any]:
        """构建最终JSON结构"""
        # 按模块分组
        modules = {}
        for kp in self.knowledge_points:
            module = kp['module']
            if module not in modules:
                modules[module] = []
            modules[module].append(kp)
        
        result = {
            "version": "1.0",
            "grade": "高中",
            "edition": "沪教版",
            "subject": "生物",
            "total_knowledge_points": len(self.knowledge_points),
            "modules": [
                {
                    "id": "必修1",
                    "name": "必修一 分子与细胞",
                    "knowledge_points": modules.get("必修一 分子与细胞", [])
                },
                {
                    "id": "必修2",
                    "name": "必修二 遗传与进化",
                    "knowledge_points": modules.get("必修二 遗传与进化", [])
                }
            ]
        }
        
        return result
    
    def save_json(self, output_path: str):
        """保存为JSON文件"""
        data = self.parse()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存 {len(data['modules'][0]['knowledge_points'])} 个知识点到 {output_path}")
        print(f"   - {data['modules'][0]['name']}: {len(data['modules'][0]['knowledge_points'])} 个")
        print(f"   - {data['modules'][1]['name']}: {len(data['modules'][1]['knowledge_points'])} 个")


# 运行转换
if __name__ == "__main__":
    # 请修改为你的docx文件实际路径
    docx_path = r"D:\PixelSmile\ScoreOrbit\data\textbooks\高中生物合格考知识点梳理填空.docx"
    
    # 如果文件不存在，尝试查找
    if not os.path.exists(docx_path):
        print(f"❌ 找不到文件: {docx_path}")
        print("请将docx文件放到正确位置，或修改上面的路径")
        
        # 列出可能的文件
        data_dir = r"D:\PixelSmile\ScoreOrbit\data\textbooks"
        if os.path.exists(data_dir):
            print(f"\n📁 {data_dir} 目录下的文件:")
            for f in os.listdir(data_dir):
                print(f"   - {f}")
    else:
        converter = DocxToKnowledgeGraph(docx_path)
        output_path = r"D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json"
        converter.save_json(output_path)