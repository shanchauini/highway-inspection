from datetime import datetime
from app.models import db, Airspace, AirspaceUsage
from sqlalchemy import and_, or_


class AirspaceService:
    """空域服务"""

    @staticmethod
    def create_airspace(name, number, type, area, remark=None, status='available'):
        """创建空域"""
        # 检查编号是否已存在
        if Airspace.query.filter_by(number=number).first():
            raise ValueError('空域编号已存在')

        airspace = Airspace(
            name=name,
            number=number,
            type=type,
            area=area,
            remark=remark,
            status=status
        )

        db.session.add(airspace)
        db.session.commit()

        return airspace

    @staticmethod
    def update_airspace(airspace_id, **kwargs):
        """更新空域"""
        airspace = Airspace.query.get(airspace_id)
        if not airspace:
            raise ValueError('空域不存在')

        # 如果更新编号，需要检查唯一性
        if 'number' in kwargs and kwargs['number'] != airspace.number:
            if Airspace.query.filter_by(number=kwargs['number']).first():
                raise ValueError('空域编号已存在')

        # 限制：管理员不能直接设置占用状态，占用状态只能由任务控制
        if 'status' in kwargs:
            if kwargs['status'] == 'occupied':
                raise ValueError('不能手动设置空域为占用状态，占用状态由飞行任务自动管理')
            # 如果当前状态是占用，且要改为其他状态，需要检查是否有正在执行的任务
            if airspace.status == 'occupied' and kwargs['status'] != 'occupied':
                from app.models import Mission
                # 检查是否有正在执行的任务使用此空域
                active_mission = Mission.query.join(
                    'flight_application'
                ).filter(
                    Mission.status == 'executing',
                    Mission.flight_application.has(planned_airspace_id=airspace_id)
                ).first()
                if active_mission:
                    raise ValueError('该空域有正在执行的任务，无法修改状态')

        for key, value in kwargs.items():
            if hasattr(airspace, key):
                setattr(airspace, key, value)

        db.session.commit()
        return airspace

    @staticmethod
    def delete_airspace(airspace_id):
        """删除空域"""
        airspace = Airspace.query.get(airspace_id)
        if not airspace:
            raise ValueError('空域不存在')

        # 检查是否有关联的飞行申请
        if airspace.flight_applications.count() > 0:
            raise ValueError('该空域存在关联的飞行申请，无法删除')

        db.session.delete(airspace)
        db.session.commit()

    @staticmethod
    def get_airspace_list(page=1, page_size=20, type=None, status=None):
        """获取空域列表"""
        query = Airspace.query

        if type:
            query = query.filter_by(type=type)
        if status:
            query = query.filter_by(status=status)

        total = query.count()
        airspaces = query.order_by(Airspace.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': [airspace.to_dict() for airspace in airspaces],
            'total': total,
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def get_airspace_by_id(airspace_id):
        """根据ID获取空域"""
        return Airspace.query.get(airspace_id)

    @staticmethod
    def check_airspace_conflict(airspace_id, start_time, end_time, exclude_application_id=None):
        """检查空域时间冲突"""
        query = AirspaceUsage.query.filter(
            AirspaceUsage.airspace_id == airspace_id,
            AirspaceUsage.status.in_(['approved', 'active']),
            or_(
                and_(AirspaceUsage.start_time <= start_time, AirspaceUsage.end_time > start_time),
                and_(AirspaceUsage.start_time < end_time, AirspaceUsage.end_time >= end_time),
                and_(AirspaceUsage.start_time >= start_time, AirspaceUsage.end_time <= end_time)
            )
        )

        if exclude_application_id:
            query = query.filter(AirspaceUsage.flight_application_id != exclude_application_id)

        return query.first() is not None

    @staticmethod
    def update_airspace_status(airspace_id, status):
        """更新空域状态"""
        airspace = Airspace.query.get(airspace_id)
        if not airspace:
            raise ValueError('空域不存在')

        #这里要考虑是否要检查占用状态人工变更
        airspace.status = status
        db.session.commit()
        return airspace

    @staticmethod
    def get_available_airspaces():
        """获取所有可用空域"""
        return Airspace.query.filter(
            Airspace.type != 'no_fly',
            Airspace.status == 'available'
        ).all()

