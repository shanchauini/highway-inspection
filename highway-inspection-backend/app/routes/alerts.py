
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.models import db, AlertEvent, Mission, User
from app.schemas.alert_schema import AlertCreateSchema, AlertUpdateSchema
from app.utils import success_response, error_response, paginate_response, login_required

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('', methods=['GET'])
@login_required
def get_alerts():
    """获取告警列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status', None)
        severity = request.args.get('severity', None)
        mission_id = request.args.get('mission_id', None, type=int)

        query = AlertEvent.query

        # 操作员只能查看自己任务的告警
        if not user.is_admin():
            mission_ids = [m.id for m in Mission.query.filter_by(operator_id=user_id).all()]
            query = query.filter(AlertEvent.mission_id.in_(mission_ids))

        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        if mission_id:
            query = query.filter_by(mission_id=mission_id)

        total = query.count()
        alerts = query.order_by(AlertEvent.occurred_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return paginate_response(
            items=[alert.to_dict(include_relations=True) for alert in alerts],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        return error_response(f'获取告警列表失败: {str(e)}', 500)


@alerts_bp.route('/<int:alert_id>', methods=['GET'])
@login_required
def get_alert(alert_id):
    """获取告警详情"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        alert = AlertEvent.query.get(alert_id)
        if not alert:
            return error_response('告警不存在', 404)

        # 操作员只能查看自己任务的告警
        if not user.is_admin() and alert.mission.operator_id != user_id:
            return error_response('无权限查看此告警', 403)

        return success_response(data=alert.to_dict(include_relations=True))

    except Exception as e:
        return error_response(f'获取告警详情失败: {str(e)}', 500)


@alerts_bp.route('', methods=['POST'])
def create_alert():
    """创建告警（由AI模块调用，无需认证）"""
    try:
        # 验证请求数据
        schema = AlertCreateSchema()
        data = schema.load(request.get_json())

        # 创建告警
        alert = AlertEvent(**data)
        db.session.add(alert)
        db.session.commit()

        return success_response(
            data=alert.to_dict(include_relations=True),
            message='告警创建成功',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except Exception as e:
        return error_response(f'创建告警失败: {str(e)}', 500)


@alerts_bp.route('/<int:alert_id>', methods=['PUT'])
@login_required
def update_alert(alert_id):
    """更新告警状态"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        alert = AlertEvent.query.get(alert_id)
        if not alert:
            return error_response('告警不存在', 404)

        # 操作员只能更新自己任务的告警
        if not user.is_admin() and alert.mission.operator_id != user_id:
            return error_response('无权限更新此告警', 403)

        # 验证请求数据
        schema = AlertUpdateSchema()
        data = schema.load(request.get_json())

        alert.status = data['status']
        db.session.commit()

        return success_response(
            data=alert.to_dict(include_relations=True),
            message='更新成功'
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except Exception as e:
        return error_response(f'更新告警失败: {str(e)}', 500)


@alerts_bp.route('/active', methods=['GET'])
@login_required
def get_active_alerts():
    """获取活跃告警"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        query = AlertEvent.query.filter(AlertEvent.status.in_(['new', 'confirmed', 'processing']))

        # 操作员只能查看自己任务的告警
        if not user.is_admin():
            mission_ids = [m.id for m in Mission.query.filter_by(operator_id=user_id).all()]
            query = query.filter(AlertEvent.mission_id.in_(mission_ids))

        alerts = query.order_by(AlertEvent.occurred_time.desc()).all()

        return success_response(
            data=[alert.to_dict(include_relations=True) for alert in alerts]
        )

    except Exception as e:
        return error_response(f'获取活跃告警失败: {str(e)}', 500)

