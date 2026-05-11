import json

# 读取当前的JSON
json_path = r'D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("修复前统计:")
for mod in data['modules']:
    print(f"  {mod['name']}: {len(mod['knowledge_points'])} 个知识点")

# 重新读取原始数据（你需要重新运行解析脚本）
# 或者手动检查是否有必修1的内容丢失

print("\n⚠️ 必修1的知识点数量不对（应该是88个，现在只有22个）")
print("需要重新运行解析脚本，并修复合并逻辑。")

# 临时方案：从原始数据重建
# 如果你有备份的原始JSON，可以在这里恢复