"""加载和管理知识图谱 - 适配新版JSON结构"""
import json
import os
from typing import Dict, List, Optional

class BiologyKnowledgeGraph:
    def __init__(self, json_path: str = None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            json_path = os.path.join(base_dir, "data", "knowledge_graph", "biology_knowledge.json")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 建立快速索引
        self.kp_index = {}  # 知识点ID -> 知识点信息
        self.module_index = {}  # 模块ID -> 模块信息
        
        for module in self.data['modules']:
            self.module_index[module['id']] = module
            for kp in module['knowledge_points']:
                self.kp_index[kp['id']] = {
                    **kp,
                    'module_id': module['id'],
                    'module_name': module['name']
                }
    
    def get_all_knowledge_points(self) -> List[Dict]:
        """获取所有知识点"""
        return list(self.kp_index.values())
    
    def get_modules(self) -> List[Dict]:
        """获取所有模块"""
        return [{'id': m['id'], 'name': m['name']} for m in self.data['modules']]
    
    def get_knowledge_by_module(self, module_name: str) -> List[Dict]:
        """按模块获取知识点"""
        for module in self.data['modules']:
            if module['name'] == module_name:
                return module['knowledge_points']
        return []
    
    def get_knowledge_by_difficulty(self, difficulty: str) -> List[Dict]:
        """按难度获取知识点"""
        return [kp for kp in self.kp_index.values() if kp['difficulty'] == difficulty]
    
    def get_knowledge_by_keyword(self, keyword: str) -> List[Dict]:
        """按关键词搜索知识点"""
        results = []
        for kp in self.kp_index.values():
            if keyword in kp['name'] or keyword in str(kp.get('exam_focus', [])):
                results.append(kp)
        return results
    
    def get_random_knowledge(self, n: int = 5) -> List[Dict]:
        """随机获取n个知识点"""
        import random
        kps = list(self.kp_index.values())
        return random.sample(kps, min(n, len(kps)))
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'total': len(self.kp_index),
            'by_difficulty': {},
            'by_module': {}
        }
        
        for kp in self.kp_index.values():
            # 按难度统计
            diff = kp['difficulty']
            stats['by_difficulty'][diff] = stats['by_difficulty'].get(diff, 0) + 1
            
            # 按模块统计
            mod = kp['module_name']
            stats['by_module'][mod] = stats['by_module'].get(mod, 0) + 1
        
        return stats

# 测试
if __name__ == "__main__":
    kg = BiologyKnowledgeGraph()
    
    print("=" * 50)
    print("知识图谱加载器测试")
    print("=" * 50)
    
    stats = kg.get_statistics()
    print(f"总知识点数: {stats['total']}")
    print(f"\n按难度分布:")
    for diff, count in stats['by_difficulty'].items():
        print(f"  {diff}: {count} 个")
    
    print(f"\n按模块分布:")
    for mod, count in stats['by_module'].items():
        print(f"  {mod}: {count} 个")
    
    print(f"\n随机获取3个知识点:")
    for kp in kg.get_random_knowledge(3):
        print(f"  - {kp['name'][:50]}... ({kp['difficulty']})")
    
    print("\n✅ 加载器测试完成！")