from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.models import Mission, User
from app.utils import success_response, error_response, paginate_response, login_required

missions_bp = Blueprint('missions', __name__)


@missions_bp.route('', methods=['GET'])
@login_required
def get_missions():
    """获取任务列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status', None)

        query = Mission.query

        # 操作员只能查看自己的任务
        if not user.is_admin():
            query = query.filter_by(operator_id=user_id)

        if status:
            query = query.filter_by(status=status)

        total = query.count()
        missions = query.order_by(Mission.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return paginate_response(
            items=[mission.to_dict(include_relations=True) for mission in missions],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        return error_response(f'获取任务列表失败: {str(e)}', 500)


@missions_bp.route('/<int:mission_id>', methods=['GET'])
@login_required
def get_mission(mission_id):
    """获取任务详情"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        mission = Mission.query.get(mission_id)
        if not mission:
            return error_response('任务不存在', 404)

        # 操作员只能查看自己的任务
        if not user.is_admin() and mission.operator_id != user_id:
            return error_response('无权限查看此任务', 403)

        return success_response(data=mission.to_dict(include_relations=True))

    except Exception as e:
        return error_response(f'获取任务详情失败: {str(e)}', 500)


@missions_bp.route('/active', methods=['GET'])
@login_required
def get_active_missions():
    """获取进行中的任务（用于地图显示）"""
    try:
        from datetime import datetime, timezone
        from app.models import db, Airspace
        
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        query = Mission.query.filter_by(status='executing')

        # 操作员只能查看自己的任务
        if not user.is_admin():
            query = query.filter_by(operator_id=user_id)

        missions = query.all()
        
        # 检查并自动结束超时的任务
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        completed_count = 0
        for mission in missions[:]:  # 使用切片创建副本遍历
            if mission.end_time and now >= mission.end_time:
                print(f"[INFO] 自动结束超时任务 #{mission.id}: 计划结束时间 {mission.end_time}, 当前时间 {now}")
                mission.status = 'completed'
                # 释放空域
                if mission.flight_application:
                    airspace = Airspace.query.get(mission.flight_application.planned_airspace_id)
                    if airspace and airspace.status == 'occupied':
                        airspace.status = 'available'
                        print(f"[INFO] 释放空域 #{airspace.id}")
                missions.remove(mission)  # 从列表移除
                completed_count += 1
        
        if completed_count > 0:
            db.session.commit()
            print(f"[INFO] 自动结束了 {completed_count} 个超时任务")

        return success_response(
            data=[mission.to_dict(include_relations=True) for mission in missions]
        )

    except Exception as e:
        return error_response(f'获取活跃任务失败: {str(e)}', 500)


@missions_bp.route('/<int:mission_id>/complete', methods=['POST'])
@login_required
def complete_mission(mission_id):
    """完成任务"""
    try:
        from datetime import datetime, timezone
        from app.models import db, Airspace

        user_id = int(get_jwt_identity())

        mission = Mission.query.get(mission_id)
        if not mission:
            return error_response('任务不存在', 404)

        if mission.operator_id != user_id:
            return error_response('无权限操作此任务', 403)

        if mission.status != 'executing':
            return error_response('任务状态不允许完成', 400)

        # 更新任务状态
        mission.status = 'completed'
        mission.end_time = datetime.now(timezone.utc).replace(tzinfo=None)

        # 释放空域
        if mission.flight_application:
            airspace = Airspace.query.get(mission.flight_application.planned_airspace_id)
            if airspace:
                airspace.status = 'available'

        db.session.commit()

        return success_response(
            data=mission.to_dict(include_relations=True),
            message='任务已完成'
        )

    except Exception as e:
        return error_response(f'完成任务失败: {str(e)}', 500)

    #airspaceusage是否要更新状态
    #任务应该是到实际开始时间+总时间后了自动完成

