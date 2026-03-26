# utils/prompt_templates.py - Prompt模板

# ==================== OCR Prompt ====================
# 实际使用：ocr_service.py 内联的简化版本
# 这里保留完整版供参考

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

# ==================== 题目生成 Prompt ====================

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

【题型要求】
1. 翻译题5题（英译中3题 + 中译英2题）
2. 形式填空4题（用括号词的变形填空）
3. 无提示填空1题（固定搭配，无括号提示）

【形式填空 - 好示例】
✓ The weather is getting ______ (bad). → worse（比较级变形）
✓ She ______ (go) to school yesterday. → went（过去式变形）
✓ The book ______ (write) by Lu Xun. → was written（被动语态）
✓ I look forward to ______ (hear) from you. → hearing（固定搭配）
✓ He insisted that we ______ (leave) early. → (should) leave（虚拟语气）

【形式填空 - 坏示例】
✗ I will ______ (go) home. → go（原形，过于简单，尽量避免）
✗ She can ______ (swim). → swim（原形，情态动词后原形是常规考点，但最多放1个）

【规则说明】
- 4题形式填空中，最多1题可以填原形（如情态动词后、不定式等）
- 其他3题必须考察变形：时态/语态/比较级/非谓语/虚拟语气等
- 如果给的词汇不适合变形，允许用其派生词（如 success → successful → successfully）

【兜底策略】
如果词汇列表太短（少于4个）或不适合出题：
1. 优先使用词汇的派生形式出题
2. 允许少量重复用词，但要换题型
3. 如果实在出不够，在 stats 里如实标注实际题数

【输出格式】
{format_json}

只返回JSON，不要其他文字。"""

    format_json = """{
  "quiz": {
    "translation": [
      {"num": 1, "question": "英文单词", "type": "英译中"},
      {"num": 2, "question": "英文单词", "type": "英译中"},
      {"num": 3, "question": "英文单词", "type": "英译中"},
      {"num": 4, "question": "中文意思", "type": "中译英"},
      {"num": 5, "question": "中文意思", "type": "中译英"}
    ],
    "form_filling": [
      {"num": 6, "question": "句子______填空（提示词）", "type": "形式填空"},
      {"num": 7, "question": "句子______填空（提示词）", "type": "形式填空"},
      {"num": 8, "question": "句子______填空（提示词）", "type": "形式填空"},
      {"num": 9, "question": "句子______填空（提示词）", "type": "形式填空"}
    ],
    "no_hint": [
      {"num": 10, "question": "句子______填空", "type": "无提示填空"}
    ]
  },
  "answer": {
    "translation": [
      {"num": 1, "answer": "中文意思"},
      {"num": 2, "answer": "中文意思"},
      {"num": 3, "answer": "中文意思"},
      {"num": 4, "answer": "英文单词"},
      {"num": 5, "answer": "英文单词"}
    ],
    "form_filling": [
      {"num": 6, "answer": "变形后答案", "explanation": "解析：如过去式变化规则"},
      {"num": 7, "answer": "变形后答案", "explanation": "解析"},
      {"num": 8, "answer": "变形后答案", "explanation": "解析"},
      {"num": 9, "answer": "变形后答案", "explanation": "解析"}
    ],
    "no_hint": [
      {"num": 10, "answer": "答案", "explanation": "解析：固定搭配说明"}
    ]
  },
  "stats": {"total": 10, "translation_count": 5, "form_filling_count": 4, "no_hint_count": 1}
}"""
    
    # 重新构建，把 format_json 提前
    return f"""基于以下词汇出英语练习题：{vocab_str}
难度：{difficulty_desc}

【题型要求】
1. 翻译题5题（英译中3题 + 中译英2题）
2. 形式填空4题（用括号词的变形填空）
3. 无提示填空1题（固定搭配，无括号提示）

【形式填空 - 好示例】
✓ The weather is getting ______ (bad). → worse（比较级变形）
✓ She ______ (go) to school yesterday. → went（过去式变形）
✓ The book ______ (write) by Lu Xun. → was written（被动语态）
✓ I look forward to ______ (hear) from you. → hearing（固定搭配）
✓ He insisted that we ______ (leave) early. → (should) leave（虚拟语气）

【形式填空 - 坏示例】
✗ I will ______ (go) home. → go（原形，过于简单，尽量避免）
✗ She can ______ (swim). → swim（原形，情态动词后原形是常规考点，但最多放1个）

【规则说明】
- 4题形式填空中，最多1题可以填原形（如情态动词后、不定式等）
- 其他3题必须考察变形：时态/语态/比较级/非谓语/虚拟语气等
- 如果给的词汇不适合变形，允许用其派生词（如 success → successful → successfully）

【兜底策略】
如果词汇列表太短（少于4个）或不适合出题：
1. 优先使用词汇的派生形式出题
2. 允许少量重复用词，但要换题型
3. 如果实在出不够，在 stats 里如实标注实际题数

【输出格式】
{format_json}

只返回JSON，不要其他文字。"""


# ==================== 保留的备用 Prompt ====================

# 图片分析Prompt（备用）
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
