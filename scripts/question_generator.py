"""智能出题模块 - 基于知识点内容生成练习题"""
import ollama
import json
import re
from typing import Dict, List, Optional

class QuestionGenerator:
    def __init__(self, model_name: str = 'qwen2.5-coder:7b'):
        self.model = model_name
    
    def generate_question(self, knowledge_point: Dict, difficulty: str = None) -> Dict:
        """根据知识点生成练习题"""
        
        # 使用知识点本身的难度，如果没有则用传入的
        if not difficulty:
            difficulty = knowledge_point.get('difficulty', '基础')
        
        # 构建prompt
        prompt = f"""
你是一位沪教版高中生物老师，需要根据以下知识点生成一道{difficulty}难度的题目。

【知识点名称】
{knowledge_point['name']}

【知识点内容】
{knowledge_point['content'][:500]}

【重点考点】
{', '.join(knowledge_point.get('exam_focus', ['无']))}

要求：
1. 题型：选择题（4个选项，A、B、C、D）
2. 题目要贴合合格考/等级考风格
3. 难度要符合{difficulty}级别
4. 输出格式：
   题目：[题目内容]
   A. [选项1]
   B. [选项2]
   C. [选项3]
   D. [选项4]
   答案：[正确选项字母]
   解析：[为什么选这个答案]

请直接输出，不要有其他说明。
"""
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': '你是沪教版高中生物老师，擅长出题。输出要简洁规范。'},
                {'role': 'user', 'content': prompt}
            ])
            
            result_text = response['message']['content']
            return self._parse_question(result_text, knowledge_point, difficulty)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'knowledge_point': knowledge_point['name']
            }
    
    def _parse_question(self, text: str, kp: Dict, difficulty: str) -> Dict:
        """解析LLM返回的题目文本"""
        
        question = {
            'success': True,
            'knowledge_point': kp['name'],
            'module': kp.get('module_name', ''),
            'difficulty': difficulty,
            'raw_text': text
        }
        
        # 提取题目
        match = re.search(r'题目[：:]\s*(.+?)(?=A\.|答案[：:])', text, re.DOTALL)
        if match:
            question['question_text'] = match.group(1).strip()
        else:
            question['question_text'] = text[:200]
        
        # 提取选项
        options = {}
        for letter in ['A', 'B', 'C', 'D']:
            pattern = rf'{letter}[\.、]\s*(.+?)(?={chr(ord(letter)+1)}[\.、]|答案[：:]|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                options[letter] = match.group(1).strip()
        
        question['options'] = options
        
        # 提取答案
        match = re.search(r'答案[：:]\s*([A-D])', text)
        if match:
            question['answer'] = match.group(1)
        
        # 提取解析
        match = re.search(r'解析[：:]\s*(.+?)(?=$)', text, re.DOTALL)
        if match:
            question['explanation'] = match.group(1).strip()
        
        return question
    
    def generate_batch(self, knowledge_points: List[Dict], max_count: int = 5) -> List[Dict]:
        """批量生成题目"""
        questions = []
        for i, kp in enumerate(knowledge_points[:max_count]):
            print(f"  生成第 {i+1}/{min(max_count, len(knowledge_points))} 题: {kp['name'][:40]}...")
            q = self.generate_question(kp)
            questions.append(q)
        return questions


# 测试
if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from knowledge_graph_loader_v2 import BiologyKnowledgeGraph
    
    print("加载知识图谱...")
    kg = BiologyKnowledgeGraph()
    generator = QuestionGenerator()
    
    # 获取几个知识点进行测试
    kps = kg.get_all_knowledge_points()
    test_kp = kps[0]
    
    print(f"\n测试知识点: {test_kp['name']}")
    print(f"难度: {test_kp['difficulty']}")
    print("\n正在生成题目...")
    
    question = generator.generate_question(test_kp)
    
    if question['success']:
        print("\n" + "="*50)
        print("生成的题目:")
        print("="*50)
        print(f"题目: {question.get('question_text', '')}")
        print("\n选项:")
        for k, v in question.get('options', {}).items():
            print(f"  {k}. {v}")
        print(f"\n答案: {question.get('answer', '')}")
        print(f"\n解析: {question.get('explanation', '')}")
    else:
        print(f"生成失败: {question.get('error', '')}")