# config.py - 配置文件
import os

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB最大文件大小
    
    # AI API配置 - 使用豆包 (Doubao/火山引擎)
    # 强制使用豆包API Key，忽略环境变量
    KIMI_API_KEY = 'a751ed82-4346-4dd1-9ee6-ea58fca04bbf'
    KIMI_BASE_URL = 'https://ark.cn-beijing.volces.com/api/v3'
    # Vision模型用于OCR，文本模型用于生成题目
    KIMI_VISION_MODEL = 'doubao-seed-1-6-vision-250815'
    KIMI_MODEL = 'doubao-1-5-lite-32k-250115'
    
    # 支持的图片格式
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
