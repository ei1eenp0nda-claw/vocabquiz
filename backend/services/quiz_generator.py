# services/quiz_generator.py - 题目生成服务
import json
import re
import http.client
from config import Config
from utils.prompt_templates import get_quiz_generation_prompt

class QuizGenerator:
    """题目生成器 - 基于词汇生成英语练习题"""
    
    def __init__(self):
        self.api_key = Config.KIMI_API_KEY
        self.base_url = "ark.cn-beijing.volces.com"
        self.model = Config.KIMI_MODEL
    
    def generate_quiz(self, vocab_list, difficulty="medium"):
        """
        基于词汇列表生成练习题
        
        Args:
            vocab_list: 词汇列表
            difficulty: 难度级别 (easy/medium/hard)
            
        Returns:
            dict: {"success": bool, "quiz": dict, "error": str}
        """
        if not vocab_list or len(vocab_list) == 0:
            return {
                "success": False,
                "quiz": None,
                "error": "词汇列表为空"
            }
        
        try:
            # 获取Prompt
            prompt = get_quiz_generation_prompt(vocab_list, difficulty)
            
            # 构建请求
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的高考英语命题专家，擅长设计高质量的英语练习题。你必须严格按照要求的JSON格式输出，不要包含任何其他文字。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            })
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 发送请求
            conn = http.client.HTTPSConnection(self.base_url, timeout=60)
            conn.request("POST", "/api/v3/chat/completions", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))
            
            if res.status != 200:
                return {
                    "success": False,
                    "quiz": None,
                    "error": f"API错误: {data.get('error', {}).get('message', 'Unknown error')}",
                    "raw_response": data
                }
            
            # 解析响应
            content = data["choices"][0]["message"]["content"].strip()
            
            # 清理Markdown代码块
            content = self._clean_json_response(content)
            
            # 解析JSON
            quiz_data = json.loads(content)
            
            # 验证数据结构
            validated_data = self._validate_quiz_data(quiz_data, vocab_list)
            
            # 检查变形题比例
            quality_report = self._ensure_transformation_ratio(validated_data, min_transformation_ratio=0.5)
            validated_data["quality_report"] = quality_report
            
            return {
                "success": True,
                "quiz": validated_data,
                "quality_passed": quality_report["passed"],
                "raw_response": content
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "quiz": None,
                "error": f"JSON解析错误: {str(e)}",
                "raw_response": content if 'content' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "quiz": None,
                "error": f"生成题目时出错: {str(e)}"
            }
    
    def generate_quiz_with_retry(self, vocab_list, difficulty="medium", max_retries=2, min_transformation_ratio=0.5):
        """
        智能生成题目，自动重试直到质量达标
        
        Args:
            vocab_list: 词汇列表
            difficulty: 难度级别
            max_retries: 最大重试次数
            min_transformation_ratio: 最小变形题比例
            
        Returns:
            dict: 包含最佳结果和质量报告
        """
        attempts = []
        best_result = None
        
        for attempt in range(max_retries + 1):
            result = self.generate_quiz(vocab_list, difficulty)
            
            if result.get("success"):
                quality_report = result.get("quiz", {}).get("quality_report", {})
                attempts.append({
                    "attempt": attempt + 1,
                    "passed": quality_report.get("passed", False),
                    "ratio": quality_report.get("transformation_ratio", 0),
                    "result": result
                })
                
                # 保存最佳结果（优先选通过的，否则选比例最高的）
                if best_result is None:
                    best_result = result
                elif quality_report.get("passed") and not best_result.get("quiz", {}).get("quality_report", {}).get("passed"):
                    best_result = result
                elif quality_report.get("transformation_ratio", 0) > best_result.get("quiz", {}).get("quality_report", {}).get("transformation_ratio", 0):
                    best_result = result
                
                # 如果通过了，直接返回
                if quality_report.get("passed"):
                    break
        
        # 组装最终返回
        if best_result:
            best_result["generation_attempts"] = len(attempts)
            best_result["all_attempts"] = attempts
            
            # 添加建议
            quality_report = best_result.get("quiz", {}).get("quality_report", {})
            if not quality_report.get("passed"):
                best_result["recommendation"] = "变形题比例偏低，建议人工审核或增加变形词汇"
        
        return best_result if best_result else result
    
    def _clean_json_response(self, content):
        """清理API响应中的JSON内容"""
        # 移除Markdown代码块标记
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # 查找JSON对象
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return match.group()
        
        return content.strip()
    
    def _validate_quiz_data(self, data, original_vocab):
        """验证并规范化题目数据"""
        validated = {
            "quiz": {
                "translation": [],
                "form_filling": [],
                "no_hint": []
            },
            "answer": {
                "translation": [],
                "form_filling": [],
                "no_hint": []
            },
            "stats": {},
            "quality_issues": []  # 新增：质量问题记录
        }
        
        # 处理新格式（包含quiz和answer）
        if "quiz" in data and "answer" in data:
            quiz_section = data["quiz"]
            answer_section = data["answer"]
            
            # 处理题目部分
            if "translation" in quiz_section:
                validated["quiz"]["translation"] = quiz_section["translation"]
            if "form_filling" in quiz_section:
                validated["quiz"]["form_filling"] = quiz_section["form_filling"]
            if "no_hint" in quiz_section:
                validated["quiz"]["no_hint"] = quiz_section["no_hint"]
            
            # 处理答案部分 - 同时检测原形填空
            if "translation" in answer_section:
                validated["answer"]["translation"] = answer_section["translation"]
            if "form_filling" in answer_section:
                validated["answer"]["form_filling"] = answer_section["form_filling"]
                # 检测原形填空
                for ans in answer_section["form_filling"]:
                    question = next((q for q in quiz_section.get("form_filling", []) 
                                   if q.get("num") == ans.get("num")), {})
                    self._check_base_form_issue(validated, question, ans)
            if "no_hint" in answer_section:
                validated["answer"]["no_hint"] = answer_section["no_hint"]
        else:
            # 兼容旧格式
            if "translation" in data and isinstance(data["translation"], list):
                for item in data["translation"]:
                    if isinstance(item, dict):
                        if "en" in item and "cn" in item:
                            num = len(validated["quiz"]["translation"]) + 1
                            validated["quiz"]["translation"].append({
                                "num": num,
                                "question": item["en"],
                                "type": "英译中"
                            })
                            validated["answer"]["translation"].append({
                                "num": num,
                                "answer": item["cn"]
                            })
                        elif "num" in item:
                            validated["quiz"]["translation"].append(item)
            
            if "form_filling" in data and isinstance(data["form_filling"], list):
                for item in data["form_filling"]:
                    if isinstance(item, dict) and "question" in item:
                        num = len(validated["quiz"]["form_filling"]) + 1
                        question_data = {
                            "num": num,
                            "question": str(item["question"]).strip(),
                            "type": "形式填空"
                        }
                        if "hint" in item and item["hint"]:
                            question_data["hint"] = str(item["hint"]).strip()
                        validated["quiz"]["form_filling"].append(question_data)
                        validated["answer"]["form_filling"].append({
                            "num": num,
                            "answer": str(item.get("answer", "")).strip(),
                            "explanation": str(item.get("explanation", "")).strip()
                        })
            
            if "no_hint" in data and isinstance(data["no_hint"], list):
                for item in data["no_hint"]:
                    if isinstance(item, dict) and "question" in item:
                        num = len(validated["quiz"]["no_hint"]) + 1
                        validated["quiz"]["no_hint"].append({
                            "num": num,
                            "question": str(item["question"]).strip(),
                            "type": "无提示填空"
                        })
                        validated["answer"]["no_hint"].append({
                            "num": num,
                            "answer": str(item.get("answer", "")).strip(),
                            "explanation": str(item.get("explanation", "")).strip()
                        })
        
        # 添加统计信息
        stats = data.get("stats", {})
        validated["stats"] = {
            "total": stats.get("total", 0),
            "translation_count": stats.get("translation_count", len(validated["quiz"]["translation"])),
            "form_filling_count": stats.get("form_filling_count", len(validated["quiz"]["form_filling"])),
            "no_hint_count": stats.get("no_hint_count", len(validated["quiz"]["no_hint"])),
            "vocab_coverage": len(original_vocab)
        }
        
        return validated
    
    def _check_base_form_issue(self, validated, question, answer):
        """检测原形填空问题"""
        import re
        
        question_text = question.get("question", "")
        answer_text = answer.get("answer", "")
        
        # 从题干中提取括号内的提示词
        match = re.search(r'\(([^)]+)\)', question_text)
        if match:
            hint_word = match.group(1).strip().lower()
            # 检查答案是否等于提示词（原形填空）
            if answer_text.lower() == hint_word:
                validated["quality_issues"].append({
                    "type": "base_form_filling",
                    "num": answer.get("num"),
                    "question": question_text,
                    "answer": answer_text,
                    "issue": "答案等于提示词原形，没有考察变形能力"
                })
    
    def _ensure_transformation_ratio(self, validated, min_transformation_ratio=0.5):
        """
        确保变形题比例达标
        
        Args:
            validated: 验证后的数据
            min_transformation_ratio: 最小变形题比例（默认50%）
            
        Returns:
            dict: 质量报告
        """
        form_filling = validated.get("quiz", {}).get("form_filling", [])
        answers = validated.get("answer", {}).get("form_filling", [])
        issues = validated.get("quality_issues", [])
        
        total = len(form_filling)
        base_form_count = len(issues)
        transformation_count = total - base_form_count
        
        ratio = transformation_count / total if total > 0 else 0
        
        quality_report = {
            "total_form_filling": total,
            "base_form_count": base_form_count,
            "transformation_count": transformation_count,
            "transformation_ratio": round(ratio, 2),
            "min_required_ratio": min_transformation_ratio,
            "passed": ratio >= min_transformation_ratio,
            "suggestion": None
        }
        
        if not quality_report["passed"]:
            quality_report["suggestion"] = f"变形题比例{ratio:.0%}低于要求{min_transformation_ratio:.0%}，建议增加变形题"
        
        validated["quality_report"] = quality_report
        return quality_report
    
    def generate_sample_quiz(self):
        """生成示例题目（用于测试）"""
        sample_vocab = ["intense", "foundation", "transform", "significant", "challenge"]
        return self.generate_quiz(sample_vocab, "medium")
