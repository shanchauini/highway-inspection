from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.services import AuthService
from app.schemas.user_schema import UserLoginSchema, UserRegisterSchema
from app.utils import success_response, error_response, login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册（仅操作员可以自行注册）"""
    try:
        # 验证请求数据
        schema = UserRegisterSchema()
        data = schema.load(request.get_json())

        # 注册用户
        user = AuthService.register(
            username=data['username'],
            password=data['password'],
            role=data.get('role', 'operator')
        )

        return success_response(
            data=user.to_dict(),
            message='注册成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'注册失败: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 验证请求数据
        schema = UserLoginSchema()
        data = schema.load(request.get_json())

        # 登录
        result = AuthService.login(
            username=data['username'],
            password=data['password']
        )

        return success_response(
            data=result,
            message='登录成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 401)
    except Exception as e:
        return error_response(f'登录失败: {str(e)}', 500)


@auth_bp.route('/current', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(int(user_id))

        if not user:
            return error_response('用户不存在', 404)

        return success_response(
            data=user.to_dict(),
            message='获取成功'
        )

    except Exception as e:
        return error_response(f'获取用户信息失败: {str(e)}', 500)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出（前端删除token即可）"""
    return success_response(message='登出成功')

