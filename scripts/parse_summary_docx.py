"""
解析《生物合格考知识点总结》格式的docx文件
生成知识图谱JSON
"""
import os
import re
import json
from docx import Document
from typing import List, Dict, Any

class SummaryDocxParser:
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.knowledge_points = []
        
    def parse(self) -> Dict[str, Any]:
        """解析文档"""
        
        current_module = ""
        current_chapter = ""
        current_topic = ""
        current_content = []
        
        for para in self.doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # 检测模块标题（如"必修1分子与细胞"）
            if text.startswith('必修') and ('分子与细胞' in text or '遗传与进化' in text):
                if current_topic and current_content:
                    self._save_topic(current_module, current_chapter, 
                                    current_topic, current_content)
                current_module = text
                current_chapter = ""
                current_topic = ""
                current_content = []
                
            # 检测章节标题（如"第1章 走进生物学"）
            elif text.startswith('第') and '章' in text:
                if current_topic and current_content:
                    self._save_topic(current_module, current_chapter,
                                    current_topic, current_content)
                current_chapter = text
                current_topic = ""
                current_content = []
                
            # 检测知识点标题（如"一、生物学是与人类生活密切相关的自然科学"）
            elif re.match(r'[一二三四五六七八九十]+、', text) or re.match(r'\d+[、.]', text):
                if current_topic and current_content:
                    self._save_topic(current_module, current_chapter,
                                    current_topic, current_content)
                current_topic = text
                current_content = []
                
            # 普通内容，添加到当前知识点
            elif current_topic:
                current_content.append(text)
        
        # 保存最后一个知识点
        if current_topic and current_content:
            self._save_topic(current_module, current_chapter,
                            current_topic, current_content)
            
        return self._build_json()
    
    def _save_topic(self, module: str, chapter: str, topic: str, content: List[str]):
        """保存知识点"""
        full_content = '\n'.join(content)
        
        # 提取考点（关键术语）
        exam_focus = self._extract_key_terms(full_content)
        
        # 提取关键数据/公式
        key_data = self._extract_key_data(full_content)
        
        # 确定难度
        difficulty = self._determine_difficulty(topic, full_content)
        
        # 生成知识点ID
        kp_id = len(self.knowledge_points) + 1
        
        self.knowledge_points.append({
            "id": f"kp_{kp_id:04d}",
            "name": self._clean_topic_name(topic),
            "chapter": chapter,
            "module": module,
            "content": full_content[:800],  # 限制长度
            "exam_focus": exam_focus,
            "key_data": key_data,
            "difficulty": difficulty
        })
        
        print(f"  ✓ 解析: {topic[:40]}...")
    
    def _clean_topic_name(self, topic: str) -> str:
        """清理知识点名称"""
        # 去掉编号前缀
        cleaned = re.sub(r'^[一二三四五六七八九十]+、', '', topic)
        cleaned = re.sub(r'^\d+[、.]', '', cleaned)
        return cleaned[:50]
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """提取关键术语（潜在考点）"""
        terms = []
        
        # 提取带书名号或引号的内容
        quoted = re.findall(r'[「『《](.*?)[」』》]', content)
        terms.extend(quoted[:3])
        
        # 提取"称为"、"叫做"前面的术语
        called = re.findall(r'([^，,。]*?)称为', content)
        terms.extend([c.strip() for c in called[:2]])
        
        # 提取大写英文缩写
        acronyms = re.findall(r'\b[A-Z]{2,}\b', content)
        terms.extend(acronyms[:2])
        
        return list(set(terms))[:5]
    
    def _extract_key_data(self, content: str) -> List[str]:
        """提取关键数据/公式"""
        data = []
        
        # 提取数字+单位
        numbers = re.findall(r'\d+(?:\.\d+)?\s*[μμm]?m', content)
        data.extend(numbers[:3])
        
        # 提取公式
        formulas = re.findall(r'[A-Za-z]+\s*[=]\s*[A-Za-z0-9\s\+\-\*\/]+', content)
        data.extend(formulas[:2])
        
        return data[:3]
    
    def _determine_difficulty(self, topic: str, content: str) -> str:
        """判断难度等级"""
        hard_keywords = ['计算', '推导', '定律', '概率', '遗传', '变异', '进化']
        mid_keywords = ['原理', '机制', '过程', '比较', '区别', '联系']
        
        text = topic + content
        
        for kw in hard_keywords:
            if kw in text:
                return "进阶"
        
        for kw in mid_keywords:
            if kw in text:
                return "中档"
        
        return "基础"
    
    def _build_json(self) -> Dict[str, Any]:
        """构建JSON"""
        # 按模块分组
        modules_dict = {}
        for kp in self.knowledge_points:
            mod = kp['module']
            if mod not in modules_dict:
                modules_dict[mod] = []
            modules_dict[mod].append(kp)
        
        # 转换为列表
        modules_list = []
        for i, (mod_name, kps) in enumerate(modules_dict.items(), 1):
            modules_list.append({
                "id": f"mod_{i}",
                "name": mod_name,
                "knowledge_points": kps
            })
        
        return {
            "version": "1.0",
            "grade": "高中",
            "edition": "沪教版",
            "subject": "生物",
            "source": "生物合格考知识点总结",
            "total_knowledge_points": len(self.knowledge_points),
            "modules": modules_list
        }
    
    def save_json(self, output_path: str):
        """保存JSON"""
        data = self.parse()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已保存到: {output_path}")
        print(f"   总知识点数: {data['total_knowledge_points']}")


if __name__ == "__main__":
    # 必修1总结文件
    docx_path = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考\生物合格考知识点总结【必修1】-2023年高中生物合格考得分秘籍（上海专用）.docx"
    
    if not os.path.exists(docx_path):
        print(f"❌ 文件不存在: {docx_path}")
    else:
        print("正在解析必修1知识点总结...")
        parser = SummaryDocxParser(docx_path)
        output_path = r"D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json"
        parser.save_json(output_path)
        
        # 同时解析必修2
        docx_path2 = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考\生物合格考知识点总结【必修2】-2023年高中生物合格考得分秘籍（上海专用）.docx"
        if os.path.exists(docx_path2):
            print("\n正在解析必修2知识点总结...")
            parser2 = SummaryDocxParser(docx_path2)
            # 合并到同一个文件
            data2 = parser2.parse()
            with open(output_path, 'r', encoding='utf-8') as f:
                data1 = json.load(f)
            data1['modules'].extend(data2['modules'])
            data1['total_knowledge_points'] += data2['total_knowledge_points']
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data1, f, ensure_ascii=False, indent=2)
            print(f"   合并后总知识点数: {data1['total_knowledge_points']}")