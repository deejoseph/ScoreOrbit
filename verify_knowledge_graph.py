import json

json_path = r'D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 50)
print("知识图谱验证")
print("=" * 50)
print(f"版本: {data['version']}")
print(f"学科: {data['subject']}")
print(f"教材: {data['edition']}")
print(f"总知识点数: {data['total_knowledge_points']}")
print(f"\n模块分布:")
for mod in data['modules']:
    print(f"  📚 {mod['name']}: {len(mod['knowledge_points'])} 个知识点")

print(f"\n前5个知识点示例:")
for i, kp in enumerate(data['modules'][0]['knowledge_points'][:5]):
    print(f"  {i+1}. {kp['name'][:60]}")
    print(f"     难度: {kp['difficulty']}")
    print(f"     考点: {', '.join(kp['exam_focus'][:2])}")
    print()

print("✅ 验证完成！")