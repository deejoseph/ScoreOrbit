"""
自动扫描所有试卷文件，生成完整索引
"""
import os
import json
import re
from pathlib import Path

def scan_exams(base_path: str) -> dict:
    """扫描所有试卷文件"""
    
    exams = []
    exam_id = 1
    
    # 递归遍历所有文件
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_path)
            
            # 识别试卷文件
            is_exam = False
            exam_type = "其他"
            year = None
            
            # 真题PDF
            if file.endswith('.pdf') and ('会考' in file or '学业水平' in file or '合格考' in file):
                is_exam = True
                exam_type = "真题"
                # 提取年份
                year_match = re.search(r'(201\d|202\d)', file)
                if year_match:
                    year = year_match.group(1)
            
            # 模拟卷
            elif '模拟卷' in file or '模拟检测' in file:
                is_exam = True
                exam_type = "模拟卷"
            
            # 章节卷（原卷版）
            elif '原卷版' in file or '必刷考点' in file:
                is_exam = True
                exam_type = "章节卷"
            
            # 精品解析
            elif '精品解析' in rel_path:
                is_exam = True
                exam_type = "精品解析"
            
            if is_exam:
                # 查找对应的解析版
                answer_file = None
                if '原卷版' in file:
                    answer_file = file.replace('原卷版', '解析版')
                    # 检查解析版是否存在
                    answer_path = os.path.join(root, answer_file)
                    if not os.path.exists(answer_path):
                        answer_file = None
                
                exams.append({
                    "id": f"exam_{exam_id:04d}",
                    "name": file.replace('.pdf', '').replace('.docx', '').replace('.doc', ''),
                    "file": rel_path,
                    "type": exam_type,
                    "year": year,
                    "has_answer": answer_file is not None,
                    "answer_file": answer_file
                })
                exam_id += 1
    
    return {
        "version": "1.0",
        "base_path": base_path,
        "total_exams": len(exams),
        "exams": exams
    }

if __name__ == "__main__":
    base_path = r"D:\BaiduNetdiskDownload\生物（2011-2019）\2011-2019上海生物合格考"
    
    print("正在扫描试卷文件...")
    result = scan_exams(base_path)
    
    print(f"\n✅ 共找到 {result['total_exams']} 套试卷")
    
    # 按类型统计
    type_count = {}
    for e in result['exams']:
        t = e['type']
        type_count[t] = type_count.get(t, 0) + 1
    
    print("\n按类型分布:")
    for t, count in type_count.items():
        print(f"  {t}: {count} 套")
    
    # 保存索引
    output_path = r"D:\PixelSmile\ScoreOrbit\data\exams\exam_index_full.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 索引已保存: {output_path}")