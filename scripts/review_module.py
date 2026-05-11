"""知识点复习和出题模块"""
import ollama
from typing import List, Dict
import os

class KnowledgeReviewer:
    def __init__(self, knowledge_graph, model_name: str = 'qwen2.5-coder:7b'):
        self.kg = knowledge_graph
        self.model = model_name
    
    def review_topic(self, chapter_id: str, topic_name: str) -> str:
        """针对具体知识点生成复习讲解"""
        
        # 获取该章节的知识点
        chapter = self.kg.get_chapter_by_id(chapter_id)
        
        if not chapter:
            return f"未找到章节: {chapter_id}"
        
        # 构建Prompt
        prompt = f"""
你是一位沪教版高中生物老师，正在帮助学生复习【{topic_name}】这个知识点。

请用简洁的方式讲解，包含：
1. 核心概念（1-2句话）
2. 重要考点（2-3个，点出常考方向）
3. 记忆口诀或关键对比（如果有）
4. 一个典型例题（选择题形式，带答案和简析）

要求：语言精炼，直击考点，不讲废话。总字数控制在300字以内。
"""
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': '你是沪教版高中生物老师，回答要简洁、考点明确。'},
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"❌ 生成失败: {str(e)}\n\n请确保Ollama服务正在运行。"
    
    def generate_question(self, chapter_id: str, difficulty: str = "基础") -> Dict:
        """生成一道练习题"""
        
        chapter = self.kg.get_chapter_by_id(chapter_id)
        
        if not chapter:
            return {'error': f'未找到章节: {chapter_id}'}
        
        prompt = f"""
根据沪教版高中生物【{chapter['name']}】章节，生成一道{difficulty}难度的题目。

要求：
- 题型：选择题（4个选项，标注正确答案）
- 考察核心知识点，贴近合格考/等级考真题风格
- 不需要额外说明，直接输出题目

输出格式：
【题目】xxxx
A. xxx
B. xxx
C. xxx
D. xxx
【答案】X
【解析】xxx
"""
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return {
                'chapter': chapter['name'],
                'difficulty': difficulty,
                'question_text': response['message']['content'],
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

# 测试
if __name__ == "__main__":
    from knowledge_graph_loader import BiologyKnowledgeGraph
    
    print("加载知识图谱...")
    kg = BiologyKnowledgeGraph()
    reviewer = KnowledgeReviewer(kg)
    
    print("\n=== 测试复习 ===")
    review = reviewer.review_topic("1_2", "蛋白质的结构与功能")
    print(review)
    
    print("\n=== 测试出题 ===")
    question = reviewer.generate_question("1_2", "基础")
    if question.get('success'):
        print(question['question_text'])
    else:
        print(f"错误: {question.get('error')}")