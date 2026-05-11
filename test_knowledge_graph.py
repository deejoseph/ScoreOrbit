import json
with open('data/knowledge_graph/biology_knowledge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'版本: {data["version"]}')
    print(f'学科: {data["subject"]}')
    print(f'教材: {data["edition"]}')
    print(f'总知识点数: {data["total_knowledge_points"]}')
    print(f'\n模块数: {len(data["modules"])}')
    for mod in data['modules']:
        print(f'  - {mod["name"]}: {len(mod["knowledge_points"])} 个知识点')
    print(f'\n第一个知识点示例:')
    kp = data['modules'][0]['knowledge_points'][0]
    print(f'  名称: {kp["name"]}')
    print(f'  难度: {kp["difficulty"]}')
    print(f'  考点: {kp["exam_focus"][:3]}')