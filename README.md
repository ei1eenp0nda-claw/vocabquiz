# VocabQuiz

智能词汇出题系统 - 基于 OCR + AI 的英语词汇学习工具

## 项目简介

VocabQuiz 是一个在线英语词汇学习工具，用户可以上传包含加粗词汇的图片（如教材截图），系统自动识别词汇并生成针对性的英语练习题。

## 技术栈

- **前端**: Vue 3 + Element Plus + Vite
- **后端**: Flask + Python 3.10+
- **OCR**: 豆包 Vision API (doubao-seed-1-6-vision-250815)
- **题目生成**: 豆包 Lite 32K (doubao-1-5-lite-32k-250115)

## 项目结构

```
vocabquiz/
├── backend/          # Flask 后端 API
│   ├── app.py       # 主应用
│   ├── services/    # 业务服务
│   ├── utils/       # 工具函数
│   └── requirements.txt
├── frontend/        # Vue 前端
│   ├── src/        # 源代码
│   ├── public/     # 静态资源
│   └── package.json
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

服务将在 `http://localhost:5000` 启动

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

服务将在 `http://localhost:5173` 启动

## 功能特性

- 📷 图片 OCR 识别加粗词汇
- 📝 自动生成三类题目：
  - 翻译题（英译中/中译英）
  - 正确形式填空（时态、语态、比较级等）
  - 无提示填空（固定搭配、介词）
- 🎯 支持三种难度级别（初中/高考/四级）
- 📊 答题统计与解析

## 许可证

MIT License
