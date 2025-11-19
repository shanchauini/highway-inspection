from flask import Blueprint, request
from marshmallow import ValidationError

from app.services import AirspaceService
from app.schemas.airspace_schema import AirspaceCreateSchema, AirspaceUpdateSchema
from app.utils import success_response, error_response, paginate_response, admin_required, login_required

airspaces_bp = Blueprint('airspaces', __name__)


@airspaces_bp.route('', methods=['GET'])
@login_required
def get_airspaces():
    """获取空域列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        type = request.args.get('type', None)
        status = request.args.get('status', None)

        result = AirspaceService.get_airspace_list(
            page=page,
            page_size=page_size,
            type=type,
            status=status
        )

        return paginate_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )

    except Exception as e:
        return error_response(f'获取空域列表失败: {str(e)}', 500)


@airspaces_bp.route('/<int:airspace_id>', methods=['GET'])
@login_required
def get_airspace(airspace_id):
    """获取空域详情"""
    try:
        airspace = AirspaceService.get_airspace_by_id(airspace_id)

        if not airspace:
            return error_response('空域不存在', 404)

        return success_response(data=airspace.to_dict())

    except Exception as e:
        return error_response(f'获取空域详情失败: {str(e)}', 500)


@airspaces_bp.route('', methods=['POST'])
@admin_required
def create_airspace():
    """创建空域（仅管理员）"""
    try:
        # 验证请求数据
        schema = AirspaceCreateSchema()
        data = schema.load(request.get_json())

        # 创建空域
        airspace = AirspaceService.create_airspace(**data)

        return success_response(
            data=airspace.to_dict(),
            message='创建成功',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'创建空域失败: {str(e)}', 500)


@airspaces_bp.route('/<int:airspace_id>', methods=['PUT'])
@admin_required
def update_airspace(airspace_id):
    """更新空域（仅管理员）"""
    try:
        # 验证请求数据
        schema = AirspaceUpdateSchema()
        data = schema.load(request.get_json())

        # 更新空域
        airspace = AirspaceService.update_airspace(airspace_id, **data)

        return success_response(
            data=airspace.to_dict(),
            message='更新成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'更新空域失败: {str(e)}', 500)


@airspaces_bp.route('/<int:airspace_id>', methods=['DELETE'])
@admin_required
def delete_airspace(airspace_id):
    """删除空域（仅管理员）"""
    try:
        AirspaceService.delete_airspace(airspace_id)

        return success_response(message='删除成功')

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'删除空域失败: {str(e)}', 500)


@airspaces_bp.route('/available', methods=['GET'])
@login_required
def get_available_airspaces():
    """获取所有可用空域"""
    try:
        airspaces = AirspaceService.get_available_airspaces()

        return success_response(
            data=[airspace.to_dict() for airspace in airspaces]
        )

    except Exception as e:
        return error_response(f'获取可用空域失败: {str(e)}', 500)


@airspaces_bp.route('/<int:airspace_id>/check-conflict', methods=['POST'])
@login_required
def check_airspace_conflict(airspace_id):
    """检查空域时间冲突"""
    try:
        data = request.get_json()
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not start_time or not end_time:
            return error_response('缺少必要参数', 400)

        from datetime import datetime
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        has_conflict = AirspaceService.check_airspace_conflict(
            airspace_id,
            start_time,
            end_time
        )

        return success_response(
            data={'has_conflict': has_conflict}
        )

    except Exception as e:
        return error_response(f'检查冲突失败: {str(e)}', 500)

