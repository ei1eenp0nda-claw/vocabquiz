# utils/prompt_templates.py - Prompt模板

# 词汇提取Prompt
VOCAB_EXTRACTION_PROMPT = """你是一个专业的OCR识别专家。请仔细分析这张图片，找出其中所有**加粗**的英文单词和词组。

要求：
1. 只识别加粗（bold）的文本
2. 识别英文单词和常见词组
3. 返回纯净的JSON数组格式，不要包含任何其他文字

输出格式（必须严格遵循）：
["word1", "word2", "phrase one", "word3"]

如果图片中没有加粗的词汇，返回空数组：
[]
"""

# 题目生成Prompt模板
def get_quiz_generation_prompt(vocab_list, difficulty="medium"):
    """
    生成题目生成Prompt
    
    Args:
        vocab_list: 词汇列表
        difficulty: 难度级别 (easy/medium/hard)
    
    Returns:
        完整的Prompt字符串
    """
    vocab_str = ", ".join(vocab_list)
    
    difficulty_desc = {
        "easy": "初中水平，简单",
        "medium": "高中水平，高考难度",
        "hard": "四级以上，较难"
    }.get(difficulty, "高中水平")
    
    return f"""基于以下词汇出英语练习题：{vocab_str}
难度：{difficulty_desc}

题型要求：
1. 英译中3题 + 中译英2题
2. 形式填空4题（必须用括号词的变形，如过去式/比较级/被动语态）
3. 无提示填空1题（固定搭配）

重要规则：
- 形式填空不能直接填原形（如will后填原形是禁止的）
- 必须考察变形：时态变化、比较级、被动语态等

输出JSON格式：
{{
  "quiz": {{
    "translation": [{{"num": 1, "question": "英文", "type": "英译中"}}],
    "form_filling": [{{"num": 6, "question": "句子______填空（提示词）", "type": "形式填空"}}],
    "no_hint": [{{"num": 10, "question": "句子______填空", "type": "无提示填空"}}]
  }},
  "answer": {{
    "translation": [{{"num": 1, "answer": "中文"}}],
    "form_filling": [{{"num": 6, "answer": "变形后答案", "explanation": "解析"}}],
    "no_hint": [{{"num": 10, "answer": "答案", "explanation": "解析"}}]
  }},
  "stats": {{"total": 10, "translation_count": 5, "form_filling_count": 4, "no_hint_count": 1}}
}}

只返回JSON，不要其他文字。"""

# 图片分析Prompt（带详细说明）
IMAGE_ANALYSIS_PROMPT = """请分析这张图片中的文本内容。

任务：识别所有**加粗显示**的英文单词和词组。

识别规则：
1. 只识别视觉上加粗（字体更粗）的文本
2. 忽略普通字体的文本
3. 识别完整的单词和常见词组
4. 如果加粗文本是中文，请忽略

请返回JSON数组格式：
["word1", "word2", "phrase one", ...]

如无加粗词汇，返回空数组：[]
"""
