# VocabQuiz 智能词汇出题系统 - 前端

基于 Vue3 + Element Plus 的在线词汇练习题生成工具。

## 功能特性

- 📤 **图片上传**: 支持拖拽上传 JPG、PNG、PDF 格式文件
- 🔍 **词汇提取**: 自动识别图片中的加粗词汇
- ✅ **词汇确认**: 灵活选择和编辑词汇列表
- 📝 **智能出题**: 生成翻译题、填空题等多种题型
- 📋 **一键复制**: 方便复制题目用于打印或分享
- 📱 **响应式设计**: 支持桌面和移动设备

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - 桌面端组件库
- **Vue Router** - 官方路由管理器
- **Axios** - HTTP 客户端

## 快速开始

### 环境要求

- Node.js 16.0+
- npm 7.0+ 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

服务默认运行在 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建后的文件位于 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── assets/         # 样式、图片等资源
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── utils/          # 工具函数
│   ├── views/          # 页面视图
│   │   ├── UploadView.vue    # 上传页
│   │   ├── VocabView.vue     # 词汇确认页
│   │   └── ResultView.vue    # 结果展示页
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML 模板
├── package.json        # 依赖配置
├── vite.config.js      # Vite 配置
└── README.md           # 项目说明
```

## 页面说明

### 1. 首页/上传页 (`/`)

- 大文件上传区域，支持拖拽
- 文件类型验证 (jpg, png, pdf)
- 上传后显示预览
- 调用 `/api/extract-vocab` 提取词汇

### 2. 词汇确认页 (`/vocab`)

- 展示提取的候选词汇列表
- 支持勾选/取消选择
- 支持手动添加新词汇
- 难度选择 (简单/中等/困难)
- 调用 `/api/generate-quiz` 生成题目

### 3. 结果展示页 (`/result`)

- 按题型分类展示
  - 翻译题
  - 填空题
  - 无提示填空
- 一键复制全部题目
- 复制成功提示

## API 接口

### 提取词汇

```http
POST /api/extract-vocab
Content-Type: multipart/form-data

{
  "image": File
}
```

响应：
```json
{
  "vocab": ["word1", "phrase1", "word2"]
}
```

### 生成题目

```http
POST /api/generate-quiz
Content-Type: application/json

{
  "vocab": ["word1", "phrase1"],
  "difficulty": "medium"
}
```

响应：
```json
{
  "translation": [...],
  "form_filling": [...],
  "no_hint": [...]
}
```

## 配置说明

### 代理配置

在 `vite.config.js` 中配置后端 API 代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 环境变量

创建 `.env` 文件配置环境变量：

```bash
# API 基础地址
VITE_API_BASE_URL=/api
```

## 浏览器支持

- Chrome >= 88
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 开发计划

- [ ] 词汇编辑功能（修改已提取的词汇）
- [ ] 题目预览打印样式优化
- [ ] 支持导出 PDF/Word 格式
- [ ] 题目答案显示切换
- [ ] 历史记录功能

## License

MIT
