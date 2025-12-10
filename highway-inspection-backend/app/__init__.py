import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import config
from app.models import db


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    JWTManager(app)
    Migrate(app, db)

    # 注册蓝图
    from app.routes import register_blueprints
    register_blueprints(app)

    # 创建上传目录
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 注册错误处理
    register_error_handlers(app)

    # 注册定时任务
    register_scheduled_tasks(app)

    # 健康检查路由
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Highway Inspection Backend is running'}

    @app.route('/')
    def index():
        return {
            'name': 'Highway Inspection System API',
            'version': '1.0.0',
            'status': 'running'
        }

    # 静态文件路由 - 访问上传的文件
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        """提供上传文件的访问"""
        # 使用 uploads 根目录，支持所有子目录
        uploads_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        return send_from_directory(uploads_base, filename)

    return app


def register_error_handlers(app):
    """注册错误处理器"""
    from app.utils import error_response

    @app.errorhandler(404)
    def not_found(error):
        return error_response('资源不存在', 404)

    @app.errorhandler(500)
    def internal_error(error):
        return error_response('服务器内部错误', 500)

    @app.errorhandler(400)
    def bad_request(error):
        return error_response('请求参数错误', 400)


def register_scheduled_tasks(app):
    """注册定时任务"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services import FlightService

    scheduler = BackgroundScheduler()

    # 每小时检查一次过期的飞行申请
    def check_expired_applications():
        with app.app_context():
            try:
                count = FlightService.check_expired_applications()
                if count > 0:
                    print(f'已更新 {count} 个过期申请')
            except Exception as e:
                print(f'检查过期申请失败: {str(e)}')

    scheduler.add_job(
        func=check_expired_applications,
        trigger='interval',
        hours=1,
        id='check_expired_applications'
    )

    scheduler.start()

