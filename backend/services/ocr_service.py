# services/ocr_service.py - OCR服务（图片解析）
import base64
import json
import re
import http.client
from config import Config

class OCRService:
    """OCR服务 - 使用豆包 Vision API识别图片中的加粗词汇"""
    
    def __init__(self):
        self.api_key = Config.KIMI_API_KEY
        self.base_url = "ark.cn-beijing.volces.com"
        self.model = getattr(Config, 'KIMI_VISION_MODEL', "doubao-seed-1-6-vision-250815")
    
    def encode_image(self, image_path):
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_vocab_from_image(self, image_path):
        """
        从图片中提取加粗词汇
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: {"success": bool, "vocab": list, "error": str}
        """
        try:
            # 编码图片
            base64_image = self.encode_image(image_path)
            
            # 构建请求
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个OCR识别专家，专门识别图片中加粗的英文词汇。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "找出图片中所有加粗的英文单词和词组，返回JSON数组格式：[\"word1\", \"word2\", ...]。只返回JSON数组，不要有其他文字。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1
            })
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 发送请求
            conn = http.client.HTTPSConnection(self.base_url)
            conn.request("POST", "/api/v3/chat/completions", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))
            
            if res.status != 200:
                return {
                    "success": False,
                    "vocab": [],
                    "error": f"API错误: {data.get('error', {}).get('message', 'Unknown error')}",
                    "raw_response": data
                }
            
            # 解析响应
            content = data["choices"][0]["message"]["content"].strip()
            
            # 清理可能的Markdown代码块
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            # 查找JSON数组
            match = re.search(r'\[.*?\]', content, re.DOTALL)
            if match:
                vocab_list = json.loads(match.group())
                # 清理词汇（去除空白）
                vocab_list = [v.strip() for v in vocab_list if v.strip()]
                return {
                    "success": True,
                    "vocab": vocab_list,
                    "raw_response": content
                }
            else:
                return {
                    "success": False,
                    "vocab": [],
                    "error": "无法从响应中解析JSON数组",
                    "raw_response": content
                }
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "vocab": [],
                "error": f"JSON解析错误: {str(e)}",
                "raw_response": content if 'content' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "vocab": [],
                "error": f"处理错误: {str(e)}"
            }
