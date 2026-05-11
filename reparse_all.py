"""
重新解析必修1和必修2，正确合并知识点
"""
import json
import os
import re
from docx import Document

def parse_docx_to_knowledge_points(docx_path, module_name):
    """解析单个docx文件，返回知识点列表"""
    doc = Document(docx_path)
    knowledge_points = []
    
    current_topic = ""
    current_content = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        # 跳过说明性文字
        if text.startswith('【') and text.endswith('】'):
            continue
        
        # 检测知识点标题（数字开头或中文数字开头）
        is_topic = False
        if re.match(r'^\d+[、.]', text):
            is_topic = True
        elif re.match(r'^[一二三四五六七八九十]+[、.]', text):
            is_topic = True
        elif re.match(r'^\d+\.\d+', text):  # 如 1.1
            is_topic = True
        
        if is_topic:
            # 保存上一个知识点
            if current_topic and current_content:
                content = '\n'.join(current_content)
                knowledge_points.append({
                    "name": current_topic,
                    "content": content[:800],
                    "difficulty": determine_difficulty(content),
                    "exam_focus": extract_key_terms(content)
                })
            
            # 开始新知识点
            current_topic = text
            current_content = []
        elif current_topic:
            current_content.append(text)
    
    # 保存最后一个知识点
    if current_topic and current_content:
        content = '\n'.join(current_content)
        knowledge_points.append({
            "name": current_topic,
            "content": content[:800],
            "difficulty": determine_difficulty(content),
            "exam_focus": extract_key_terms(content)
        })
    
    print(f"  {module_name}: 解析出 {len(knowledge_points)} 个知识点")
    return knowledge_points

def determine_difficulty(content):
    """判断难度"""
    hard_keywords = ['计算', '推导', '定律', '概率', '遗传', '变异', '进化']
    mid_keywords = ['原理', '机制', '过程', '比较', '区别']
    
    for kw in hard_keywords:
        if kw in content:
            return "进阶"
    for kw in mid_keywords:
        if kw in content:
            return "中档"
    return "基础"

def extract_key_terms(content):
    """提取关键术语"""
    terms = []
    # 提取引号内容
    quoted = re.findall(r'[「『《](.*?)[」』》]', content)
    terms.extend(quoted[:3])
    # 提取大写缩写
    acronyms = re.findall(r'\b[A-Z]{2,}\b', content)
    terms.extend(acronyms[:2])
    return list(set(terms))[:5]

# 文件路径
base_path = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考"
docx1_path = os.path.join(base_path, "生物合格考知识点总结【必修1】-2023年高中生物合格考得分秘籍（上海专用）.docx")
docx2_path = os.path.join(base_path, "生物合格考知识点总结【必修2】-2023年高中生物合格考得分秘籍（上海专用）.docx")

print("开始重新解析知识点...")
print("=" * 50)

# 解析必修1
kps1 = parse_docx_to_knowledge_points(docx1_path, "必修1分子与细胞")
# 解析必修2
kps2 = parse_docx_to_knowledge_points(docx2_path, "必修2遗传与进化")

# 构建JSON
result = {
    "version": "1.0",
    "grade": "高中",
    "edition": "沪教版",
    "subject": "生物",
    "total_knowledge_points": len(kps1) + len(kps2),
    "modules": [
        {
            "id": "mod_1",
            "name": "必修1分子与细胞",
            "knowledge_points": []
        },
        {
            "id": "mod_2",
            "name": "必修2遗传与进化",
            "knowledge_points": []
        }
    ]
}

# 添加知识点ID
for i, kp in enumerate(kps1, 1):
    result['modules'][0]['knowledge_points'].append({
        "id": f"kp_{i:04d}",
        **kp
    })

for i, kp in enumerate(kps2, 1):
    result['modules'][1]['knowledge_points'].append({
        "id": f"kp_{len(kps1)+i:04d}",
        **kp
    })

# 保存
output_path = r"D:\PixelSmile\ScoreOrbit\data\knowledge_graph\biology_knowledge.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=" * 50)
print(f"✅ 合并完成！")
print(f"   总知识点数: {result['total_knowledge_points']}")
print(f"   必修1: {len(kps1)} 个")
print(f"   必修2: {len(kps2)} 个")
print(f"   保存到: {output_path}")