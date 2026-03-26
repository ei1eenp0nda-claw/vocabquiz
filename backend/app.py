# app.py - Flask主应用
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from services.ocr_service import OCRService
from services.quiz_generator import QuizGenerator

app = Flask(__name__)
app.config.from_object(Config)

# 启用CORS，允许前端跨域访问
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # 生产环境应限制具体域名
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化服务
ocr_service = OCRService()
quiz_generator = QuizGenerator()


@app.route('/')
def index():
    """根路径 - API信息"""
    return jsonify({
        "name": "VocabQuiz API",
        "version": "1.0.0",
        "endpoints": {
            "/api/extract-vocab": "POST - 从图片提取加粗词汇",
            "/api/generate-quiz": "POST - 基于词汇生成练习题",
            "/api/health": "GET - 健康检查"
        }
    })


@app.route('/api/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "VocabQuiz API"
    })


@app.route('/api/extract-vocab', methods=['POST'])
def extract_vocab():
    """
    从上传的图片中提取加粗词汇
    
    Request:
        - file: 图片文件 (multipart/form-data)
    
    Response:
        {
            "success": true,
            "vocab": ["word1", "word2", ...],
            "count": 2
        }
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "未找到上传的文件",
                "vocab": []
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "未选择文件",
                "vocab": []
            }), 400
        
        # 验证文件类型
        if not Config.allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"不支持的文件格式。支持的格式: {', '.join(Config.ALLOWED_EXTENSIONS)}",
                "vocab": []
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # 调用OCR服务提取词汇
            result = ocr_service.extract_vocab_from_image(filepath)
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "vocab": result["vocab"],
                    "count": len(result["vocab"])
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "提取词汇失败"),
                    "vocab": [],
                    "raw_response": result.get("raw_response")
                }), 500
                
        finally:
            # 清理上传的文件
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}",
            "vocab": []
        }), 500


@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    """
    基于词汇列表生成练习题
    
    Request:
        {
            "vocab": ["word1", "word2", ...],
            "difficulty": "medium"  // optional: easy/medium/hard
        }
    
    Response:
        {
            "success": true,
            "quiz": {
                "translation": [...],
                "form_filling": [...],
                "no_hint": [...],
                "stats": {...}
            }
        }
    """
    try:
        # 获取JSON数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体必须是JSON格式"
            }), 400
        
        # 验证词汇列表
        vocab = data.get('vocab', [])
        if not vocab or not isinstance(vocab, list):
            return jsonify({
                "success": False,
                "error": "请提供有效的词汇列表（vocab字段）"
            }), 400
        
        # 清理词汇列表
        vocab = [str(v).strip() for v in vocab if str(v).strip()]
        
        if len(vocab) == 0:
            return jsonify({
                "success": False,
                "error": "词汇列表不能为空"
            }), 400
        
        # 限制词汇数量（避免超出token限制）
        if len(vocab) > 50:
            vocab = vocab[:50]
        
        # 获取难度级别
        difficulty = data.get('difficulty', 'medium')
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'medium'
        
        # 调用题目生成服务
        result = quiz_generator.generate_quiz(vocab, difficulty)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "quiz": result["quiz"],
                "difficulty": difficulty,
                "vocab_count": len(vocab)
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "生成题目失败"),
                "raw_response": result.get("raw_response")
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "error": "接口不存在"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500


if __name__ == '__main__':
    # 开发模式运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )