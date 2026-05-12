"""
通用知识图谱加载器
支持多学科：biology, physics, chemistry
支持新旧两种JSON格式
"""
import json
import os
from typing import Dict, List, Optional


class KnowledgeGraph:
    """知识图谱加载和管理"""
    
    def __init__(self, subject: str):
        """
        初始化知识图谱
        
        Args:
            subject: 学科名称 (biology, physics, chemistry)
        """
        self.subject = subject
        
        # 获取项目根目录
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, 'data', subject)
        self.knowledge_path = os.path.join(self.data_dir, 'knowledge_graph', 'knowledge.json')
        
        self.data = self._load()
        self._adapt_format()  # 适配新旧格式
    
    def _load(self) -> Dict:
        """加载知识图谱JSON文件"""
        if os.path.exists(self.knowledge_path):
            with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0", "subject": self.subject, "modules": []}
    
    def _adapt_format(self):
        """适配新旧两种JSON格式"""
        modules = self.data.get('modules', [])
        
        for module in modules:
            # 检查是否是旧版格式（直接有 knowledge_points）
            if 'knowledge_points' in module:
                # 旧版格式：将 knowledge_points 转换为 chapters
                old_points = module.pop('knowledge_points', [])
                if old_points:
                    module['chapters'] = [{
                        'id': 'all',
                        'name': '全部知识点',
                        'key_points': old_points
                    }]
            # 检查是否已经是新版格式
            elif 'chapters' not in module:
                module['chapters'] = []
        
        self.data['modules'] = modules
    
    def get_subject_info(self) -> Dict:
        """获取学科基本信息"""
        return {
            "name": self.data.get("name", self.subject),
            "version": self.data.get("version", "1.0"),
            "grade": self.data.get("grade", "高中"),
            "edition": self.data.get("edition", "沪教版")
        }
    
    def get_modules(self) -> List[Dict]:
        """获取所有模块"""
        return self.data.get('modules', [])
    
    def get_chapters(self, module_id: str = None) -> List[Dict]:
        """获取章节列表"""
        if module_id:
            for module in self.data['modules']:
                if module.get('id') == module_id:
                    return module.get('chapters', [])
            return []
        
        # 返回所有章节
        chapters = []
        for module in self.data['modules']:
            chapters.extend(module.get('chapters', []))
        return chapters
    
    def get_knowledge_points(self, chapter_id: str = None) -> List[Dict]:
        """获取知识点列表"""
        if chapter_id:
            for module in self.data['modules']:
                for chapter in module.get('chapters', []):
                    if chapter.get('id') == chapter_id:
                        return chapter.get('key_points', [])
            return []
        
        # 返回所有知识点
        points = []
        for module in self.data['modules']:
            for chapter in module.get('chapters', []):
                for kp in chapter.get('key_points', []):
                    kp['chapter'] = chapter.get('name')
                    kp['module'] = module.get('name')
                    points.append(kp)
        return points
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索知识点"""
        results = []
        keyword_lower = keyword.lower()
        
        for module in self.data['modules']:
            for chapter in module.get('chapters', []):
                for kp in chapter.get('key_points', []):
                    name = kp.get('name', '')
                    content = kp.get('content', '')
                    if keyword_lower in name.lower() or keyword_lower in content.lower():
                        results.append({
                            **kp,
                            'chapter': chapter.get('name'),
                            'module': module.get('name')
                        })
        return results
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_points = 0
        total_chapters = 0
        total_modules = len(self.data.get('modules', []))
        
        difficulty_count = {'基础': 0, '中档': 0, '进阶': 0}
        
        for module in self.data.get('modules', []):
            chapters = module.get('chapters', [])
            total_chapters += len(chapters)
            for chapter in chapters:
                points = chapter.get('key_points', [])
                total_points += len(points)
                for kp in points:
                    level = kp.get('difficulty', '基础')
                    difficulty_count[level] = difficulty_count.get(level, 0) + 1
        
        return {
            'total': total_points,
            'modules': total_modules,
            'chapters': total_chapters,
            'by_difficulty': difficulty_count
        }
    
    def get_chapter_by_id(self, chapter_id: str) -> Optional[Dict]:
        """根据ID获取章节"""
        for module in self.data['modules']:
            for chapter in module.get('chapters', []):
                if chapter.get('id') == chapter_id:
                    return {
                        **chapter,
                        'module_id': module.get('id'),
                        'module_name': module.get('name')
                    }
        return None
    
    def get_kp_by_id(self, kp_id: str) -> Optional[Dict]:
        """根据ID获取知识点"""
        for module in self.data['modules']:
            for chapter in module.get('chapters', []):
                for kp in chapter.get('key_points', []):
                    if kp.get('id') == kp_id:
                        return {
                            **kp,
                            'chapter_id': chapter.get('id'),
                            'chapter_name': chapter.get('name'),
                            'module_id': module.get('id'),
                            'module_name': module.get('name')
                        }
        return None