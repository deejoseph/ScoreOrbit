"""加载和管理知识图谱"""
import json
import os
from typing import Dict, List, Optional

class BiologyKnowledgeGraph:
    def __init__(self, json_path: str = None):
        if json_path is None:
            # 自动查找路径
            base_dir = os.path.dirname(os.path.dirname(__file__))
            json_path = os.path.join(base_dir, "data", "knowledge_graph", "biology_knowledge.json")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 建立快速索引
        self.kp_index = {}  # 知识点ID -> 知识点信息
        self.chapter_index = {}  # 章节ID -> 章节信息
        
        for module in self.data['modules']:
            for chapter in module['chapters']:
                self.chapter_index[chapter['id']] = {
                    **chapter,
                    'module_id': module['id'],
                    'module_name': module['name']
                }
                for kp in chapter['key_points']:
                    self.kp_index[kp['id']] = {
                        **kp,
                        'chapter_id': chapter['id'],
                        'chapter_name': chapter['name'],
                        'module_id': module['id'],
                        'module_name': module['name']
                    }
    
    def get_all_chapters(self) -> List[Dict]:
        """获取所有章节"""
        chapters = []
        for module in self.data['modules']:
            for chapter in module['chapters']:
                chapters.append({
                    'id': chapter['id'],
                    'name': chapter['name'],
                    'module': module['name']
                })
        return chapters
    
    def get_chapter_knowledge(self, chapter_id: str) -> List[Dict]:
        """获取章节下的所有知识点"""
        if chapter_id in self.chapter_index:
            return self.chapter_index[chapter_id]['key_points']
        return []
    
    def get_knowledge_by_level(self, level: str) -> List[Dict]:
        """按难度层级获取知识点"""
        return [kp for kp in self.kp_index.values() if kp['level'] == level]
    
    def get_related_topics(self, kp_id: str) -> List[str]:
        """获取相关主题（基于关系）"""
        related = []
        for rel in self.data.get('relationships', []):
            if rel['from'] == kp_id:
                related.append(rel['to'])
            if rel['to'] == kp_id and rel['type'] == '前置':
                related.append(rel['from'])
        return related
    
    def get_chapter_by_id(self, chapter_id: str) -> Optional[Dict]:
        """通过ID获取章节信息"""
        return self.chapter_index.get(chapter_id)

# 测试
if __name__ == "__main__":
    kg = BiologyKnowledgeGraph()
    print(f"✅ 加载完成，共 {len(kg.kp_index)} 个知识点")
    print(f"📚 共 {len(kg.get_all_chapters())} 个章节")
    print("\n所有章节：")
    for ch in kg.get_all_chapters():
        print(f"  - {ch['name']} ({ch['module']})")