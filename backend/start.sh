#!/bin/bash
# 启动 VocabQuiz 后端服务

cd /root/.openclaw/workspace/backend

# 设置环境变量
export KIMI_API_KEY="a751ed82-4346-4dd1-9ee6-ea58fca04bbf"
export KIMI_MODEL="doubao-1-5-lite-32k-250115"
export KIMI_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
export FLASK_ENV="development"
export FLASK_DEBUG="0"

# 启动服务
exec python3 app.py
