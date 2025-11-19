from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.models import User
from app.services import FlightService
from app.schemas.flight_schema import FlightApplicationCreateSchema, FlightApplicationUpdateSchema, FlightApprovalSchema
from app.utils import success_response, error_response, paginate_response, admin_required, login_required

flights_bp = Blueprint('flights', __name__)


@flights_bp.route('', methods=['GET'])
@login_required
def get_flights():
    """获取飞行申请列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status', None)

        result = FlightService.get_application_list(
            user_id=user_id,
            is_admin=user.is_admin(),
            status=status,
            page=page,
            page_size=page_size
        )

        return paginate_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size']
        )

    except Exception as e:
        return error_response(f'获取申请列表失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>', methods=['GET'])
@login_required
def get_flight(flight_id):
    """获取飞行申请详情"""
    try:
        from app.models import FlightApplication
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        flight = FlightApplication.query.get(flight_id)
        if not flight:
            return error_response('申请不存在', 404)

        # 操作员只能查看自己的申请
        if not user.is_admin() and flight.user_id != int(user_id):
            return error_response('无权限查看此申请', 403)

        return success_response(data=flight.to_dict(include_relations=True))

    except Exception as e:
        return error_response(f'获取申请详情失败: {str(e)}', 500)


@flights_bp.route('', methods=['POST'])
@login_required
def create_flight():
    """创建飞行申请"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        

        
        schema = FlightApplicationCreateSchema()
        validated_data = schema.load(data)
        

        if validated_data.get('planned_start_time'):
            print(f"  start_time tzinfo: {validated_data.get('planned_start_time').tzinfo}")
        if validated_data.get('planned_end_time'):
            print(f"  end_time tzinfo: {validated_data.get('planned_end_time').tzinfo}")
        
        application = FlightService.create_application(int(user_id), **validated_data)
        


        return success_response(
            data=application.to_dict(include_relations=True),
            message='申请创建成功',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:

        import traceback
        traceback.print_exc()
        return error_response(f'创建申请失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>', methods=['PUT'])
@login_required
def update_flight(flight_id):
    """更新飞行申请（仅草稿状态）"""
    try:
        user_id = int(get_jwt_identity())

        # 验证请求数据
        schema = FlightApplicationUpdateSchema()
        data = schema.load(request.get_json())

        # 更新申请
        application = FlightService.update_application(flight_id, user_id, **data)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='更新成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'更新申请失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>/submit', methods=['POST'])
@login_required
def submit_flight(flight_id):
    """提交飞行申请"""
    try:
        user_id = int(get_jwt_identity())

        application = FlightService.submit_application(flight_id, user_id)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='提交成功'
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'提交申请失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>/approve', methods=['POST'])
@admin_required
def approve_flight(flight_id):
    """批准飞行申请（仅管理员）"""
    try:
        application = FlightService.approve_application(flight_id)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='批准成功'
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'批准申请失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>/reject', methods=['POST'])
@admin_required
def reject_flight(flight_id):
    """驳回飞行申请（仅管理员）"""
    try:
        data = request.get_json()
        rejection_reason = data.get('rejection_reason', '')

        if not rejection_reason:
            return error_response('请填写驳回理由', 400)

        application = FlightService.reject_application(flight_id, rejection_reason)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='驳回成功'
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'驳回申请失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>/launch', methods=['POST'])
@login_required
def launch_flight(flight_id):
    """放飞申请"""
    try:
        user_id = int(get_jwt_identity())

        mission = FlightService.launch_flight(flight_id, user_id)

        return success_response(
            data=mission.to_dict(include_relations=True),
            message='放飞成功'
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'放飞失败: {str(e)}', 500)


@flights_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_flights():
    """获取待审批申请列表（仅管理员）"""
    try:
        applications = FlightService.get_pending_applications()

        return success_response(
            data=[app.to_dict(include_relations=True) for app in applications]
        )

    except Exception as e:
        return error_response(f'获取待审批列表失败: {str(e)}', 500)


@flights_bp.route('/<int:flight_id>/terminate',methods=['POST'])
@admin_required
def terminate_flights(flight_id):
    """ 取消已通过的飞行申请"""
    try:
        application = FlightService.terminate_flights(flight_id)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='终止飞行计划成功'
        )

    except ValueError as e:
        return error_response(str(e),400)
    except Exception as e:
        return error_response(f'终止飞行申请失败:{str(e)}',500)

@flights_bp.route('/<int:flight_id>/withdraw',methods=['POST'])
@login_required
def withdraw_flights(flight_id):
    """ 撤回飞行申请"""
    try:
        application = FlightService.withdraw_application(flight_id)

        return success_response(
            data=application.to_dict(include_relations=True),
            message='撤回申请成功'
        )

    except ValueError as e:
        return error_response(str(e),400)
    except Exception as e:
        return error_response(f'撤回飞行申请失败:{str(e)}',500)


@flights_bp.route('/<int:flight_id>', methods=['DELETE'])
@login_required
def delete_flights(flight_id):
    """ 删除飞行申请"""
    try:
        application = FlightService.delete_application(flight_id)

        return success_response(
            message='删除飞行申请成功'
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'删除飞行申请失败:{str(e)}', 500)
