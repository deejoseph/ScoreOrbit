import json
import os

# 读取JSON文件
json_path = r'D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("修复前:")
print(f"  模块1: {data['modules'][0]['name']}")
print(f"  模块2: {data['modules'][1]['name']}")

# 修复模块名
if data['modules'][1]['name'] == '' or data['modules'][1]['name'] == ':':
    data['modules'][1]['name'] = '必修2 遗传与进化'

# 保存修复后的JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n修复后:")
print(f"  模块1: {data['modules'][0]['name']}")
print(f"  模块2: {data['modules'][1]['name']}")
print(f"  总知识点数: {data['total_knowledge_points']}")

print("\n✅ 修复完成！")