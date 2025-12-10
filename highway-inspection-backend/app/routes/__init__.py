from flask import Blueprint

# 导入所有路由蓝图
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.airspaces import airspaces_bp
from app.routes.flights import flights_bp
from app.routes.missions import missions_bp
from app.routes.videos import videos_bp
from app.routes.alerts import alerts_bp
from app.routes.inspection_results import inspection_results_bp
from app.routes.dashboard import dashboard_bp
from app.routes.ai_interface import ai_bp


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(airspaces_bp, url_prefix='/api/airspaces')
    app.register_blueprint(flights_bp, url_prefix='/api/flights')
    app.register_blueprint(missions_bp, url_prefix='/api/missions')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(inspection_results_bp, url_prefix='/api/inspection-results')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

