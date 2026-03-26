# VocabQuiz Backend

智能词汇出题系统 - Flask后端API

## 项目简介

VocabQuiz是一个在线英语词汇学习工具，用户可以上传包含加粗词汇的图片，系统自动识别词汇并生成针对性的英语练习题。

## 技术栈

- **Python 3.10+**
- **Flask** - Web框架
- **Flask-CORS** - 跨域支持
- **OpenAI SDK** - 调用Kimi API
- **Kimi Vision API** - 图片OCR识别

## 项目结构

```
/backend/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── config.py             # 配置文件
├── services/
│   ├── ocr_service.py    # 图片OCR服务
│   └── quiz_generator.py # 题目生成服务
└── utils/
    └── prompt_templates.py # Prompt模板
```

## 安装说明

### 1. 克隆项目并进入后端目录

```bash
cd /root/.openclaw/workspace/backend
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量（可选）

创建 `.env` 文件或在启动前设置环境变量：

```bash
# API配置
export KIMI_API_KEY="your-api-key-here"
export KIMI_BASE_URL="https://api.moonshot.cn/v1"

# Flask配置
export SECRET_KEY="your-secret-key"
export FLASK_ENV="development"
```

如果不设置，将使用 `config.py` 中的默认值。

## 运行说明

### 开发模式

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 生产模式（使用Gunicorn）

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API接口文档

### 1. 提取词汇

**POST** `/api/extract-vocab`

从上传的图片中提取加粗的英文词汇。

**请求参数：**
- `file` (multipart/form-data): 图片文件
  - 支持格式: png, jpg, jpeg, gif, webp, bmp
  - 最大大小: 16MB

**响应示例：**
```json
{
  "success": true,
  "vocab": ["intense", "foundation", "transform"],
  "count": 3
}
```

**错误响应：**
```json
{
  "success": false,
  "error": "未找到上传的文件",
  "vocab": []
}
```

### 2. 生成练习题

**POST** `/api/generate-quiz`

基于词汇列表生成英语练习题。

**请求体：**
```json
{
  "vocab": ["intense", "foundation", "transform", "significant"],
  "difficulty": "medium"
}
```

**参数说明：**
- `vocab` (array, required): 词汇列表
- `difficulty` (string, optional): 难度级别
  - `easy`: 基础水平（初中）
  - `medium`: 中等水平（高考）- 默认
  - `hard`: 较高水平（大学四级以上）

**响应示例：**
```json
{
  "success": true,
  "quiz": {
    "translation": [
      {"en": "intense", "cn": "强烈的"},
      {"en": "foundation", "cn": "基础"}
    ],
    "form_filling": [
      {
        "question": "This was the ______ (intense) storm I've ever seen.",
        "hint": "intense",
        "answer": "most intense"
      }
    ],
    "no_hint": [
      {
        "question": "We should take ______ account all the factors.",
        "answer": "into"
      }
    ],
    "stats": {
      "total_questions": 8,
      "translation_count": 3,
      "form_filling_count": 3,
      "no_hint_count": 2,
      "vocab_coverage": 4
    }
  },
  "difficulty": "medium",
  "vocab_count": 4
}
```

### 3. 健康检查

**GET** `/api/health`

检查服务健康状态。

**响应：**
```json
{
  "status": "healthy",
  "service": "VocabQuiz API"
}
```

## 题目类型说明

### 1. 翻译题 (translation)
- **英译中**: 给出英文，填写中文意思
- **中译英**: 给出中文，填写英文单词

### 2. 正确形式填空 (form_filling)
- 括号内为动词/形容词原形
- 考点包括：时态、语态、非谓语、比较级、最高级
- 示例：`This was the ______ (intense) storm...` → `most intense`

### 3. 无提示填空 (no_hint)
- 无括号提示
- 考查固定搭配和介词
- 示例：`depend ______` → `on`

## 注意事项

1. **API Key安全**: 生产环境请通过环境变量设置 `KIMI_API_KEY`，不要硬编码
2. **文件大小限制**: 默认最大16MB，可在 `config.py` 中调整
3. **词汇数量限制**: 单次请求最多处理50个词汇
4. **图片格式**: 建议使用清晰、对比度高的图片以获得更好的OCR效果

## 调试技巧

开启调试日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

查看原始API响应：
- 错误响应中包含 `raw_response` 字段，可用于调试Prompt输出

## 许可证

MIT License