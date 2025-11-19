from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.models import User
from app.services import AuthService
from app.schemas.user_schema import UserUpdateSchema
from app.utils import success_response, error_response, paginate_response, admin_required, login_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表（仅管理员）"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        role = request.args.get('role', None)

        query = User.query

        if role:
            query = query.filter_by(role=role)

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return paginate_response(
            items=[user.to_dict() for user in users],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        return error_response(f'获取用户列表失败: {str(e)}', 500)


@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        # 普通用户只能查看自己，管理员可以查看所有用户
        if not current_user.is_admin() and int(current_user_id) != user_id:
            return error_response('无权限查看其他用户信息', 403)

        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 404)

        return success_response(data=user.to_dict())

    except Exception as e:
        return error_response(f'获取用户详情失败: {str(e)}', 500)


@users_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        # 普通用户只能修改自己，管理员可以修改所有用户
        if not current_user.is_admin() and current_user_id != user_id:
            return error_response('无权限修改其他用户信息', 403)

        # 验证请求数据
        schema = UserUpdateSchema()
        data = schema.load(request.get_json())

        # 普通用户不能修改角色
        if not current_user.is_admin() and 'role' in data:
            return error_response('无权限修改用户角色', 403)

        user = AuthService.update_user(user_id, **data)

        return success_response(
            data=user.to_dict(),
            message='更新成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'更新用户失败: {str(e)}', 500)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户（仅管理员）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 404)

        # 不能删除自己
        current_user_id = get_jwt_identity()
        if int(current_user_id) == user_id:
            return error_response('不能删除自己', 400)

        from app.models import db
        db.session.delete(user)
        db.session.commit()

        return success_response(message='删除成功')

    except Exception as e:
        return error_response(f'删除用户失败: {str(e)}', 500)

