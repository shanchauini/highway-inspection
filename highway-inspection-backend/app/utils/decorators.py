from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
from app.utils.response import error_response


def login_required(fn):
    """登录验证装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            # JWT identity是字符串，需要转换为整数
            user = User.query.get(int(user_id))
            
            if not user:
                return error_response('用户不存在', 401)
            
            return fn(*args, **kwargs)
        except Exception as e:
            return error_response(f'身份验证失败: {str(e)}', 401)
    
    return wrapper


def admin_required(fn):
    """管理员权限验证装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            # JWT identity是字符串，需要转换为整数
            user = User.query.get(int(user_id))
            
            if not user:
                return error_response('用户不存在', 401)
            
            if not user.is_admin():
                return error_response('需要管理员权限', 403)
            
            return fn(*args, **kwargs)
        except Exception as e:
            return error_response(f'权限验证失败: {str(e)}', 403)
    
    return wrapper


def get_current_user():
    """获取当前登录用户"""
    try:
        user_id = get_jwt_identity()
        # JWT identity是字符串，需要转换为整数
        return User.query.get(int(user_id))
    except:
        return None

