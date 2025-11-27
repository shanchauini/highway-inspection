from datetime import datetime, timezone, timedelta
from app.models import db, FlightApplication, AirspaceUsage, Mission, Airspace
from app.services.airspace_service import AirspaceService


class FlightService:
    """飞行申请服务"""

    LOCAL_TZ = timezone(timedelta(hours=8))  # 假定前端表单均使用北京时间

    @staticmethod
    def _normalize_time_fields(data):
        """将时间字段统一转换为UTC的无时区datetime"""
        if not data:
            return data

        def to_utc(dt):
            if not isinstance(dt, datetime):
                return dt
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=FlightService.LOCAL_TZ)
            return dt.astimezone(timezone.utc).replace(tzinfo=None)

        for field in ['planned_start_time', 'planned_end_time', 'long_term_start', 'long_term_end']:
            if field in data and data[field]:
                data[field] = to_utc(data[field])
        return data

    @staticmethod
    def create_application(user_id, **kwargs):
        """创建飞行申请"""
        # 过滤掉不应该由前端传递的字段
        forbidden_fields = ['status', 'user_id', 'rejection_reason', 'created_at', 'updated_at', 'id']
        for field in forbidden_fields:
            kwargs.pop(field, None)
        
        # 确保is_long_term有默认值
        if 'is_long_term' not in kwargs:
            kwargs['is_long_term'] = False
        
        FlightService._normalize_time_fields(kwargs)
        
        # 验证飞行时长
        if 'planned_start_time' in kwargs and 'planned_end_time' in kwargs and 'total_time' in kwargs:
            start_time = kwargs['planned_start_time']
            end_time = kwargs['planned_end_time']
            total_time = kwargs['total_time']
            
            # 计算时间窗口（分钟）
            time_window = (end_time - start_time).total_seconds() / 60
            
            if total_time > time_window:
                raise ValueError(f'飞行时长（{total_time}分钟）不能超过计划时间窗口（{int(time_window)}分钟）')

        application = FlightApplication(
            user_id=user_id,
            status='draft',  # 强制设置为draft
            **kwargs
        )

        db.session.add(application)
        db.session.commit()

        return application

    @staticmethod
    def update_application(application_id, user_id, **kwargs):
        """更新飞行申请（仅草稿状态）"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if application.user_id != user_id:
            raise ValueError('无权限修改此申请')

        if application.status != 'draft':
            raise ValueError('只能修改草稿状态的申请')

        # 过滤掉不应该由前端传递的字段
        forbidden_fields = ['status', 'user_id', 'rejection_reason', 'created_at', 'updated_at', 'id']
        for field in forbidden_fields:
            kwargs.pop(field, None)

        FlightService._normalize_time_fields(kwargs)
        
        # 验证飞行时长（考虑更新和原有值）
        start_time = kwargs.get('planned_start_time', application.planned_start_time)
        end_time = kwargs.get('planned_end_time', application.planned_end_time)
        total_time = kwargs.get('total_time', application.total_time)
        
        if start_time and end_time and total_time:
            time_window = (end_time - start_time).total_seconds() / 60
            if total_time > time_window:
                raise ValueError(f'飞行时长（{total_time}分钟）不能超过计划时间窗口（{int(time_window)}分钟）')

        for key, value in kwargs.items():
            if hasattr(application, key):
                setattr(application, key, value)

        db.session.commit()
        return application

    @staticmethod
    def submit_application(application_id, user_id):
        """提交飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if application.user_id != user_id:
            raise ValueError('无权限提交此申请')

        if not application.can_be_submitted():
            raise ValueError('申请状态不允许提交')

        # 检查空域冲突
        if AirspaceService.check_airspace_conflict(
            application.planned_airspace_id,
            application.planned_start_time,
            application.planned_end_time
        ):
            raise ValueError('申请的时间段内空域已被占用')

        application.status = 'pending'
        db.session.commit()

        # 创建空域使用记录
        usage = AirspaceUsage(
            flight_application_id=application.id,
            airspace_id=application.planned_airspace_id,
            start_time=application.planned_start_time,
            end_time=application.planned_end_time,
            status='applied'
        )
        db.session.add(usage)
        db.session.commit()

        return application

    #此处应该添加一个函数，用于检测当前所有申请的冲突情况，并返回具体冲突对象编号

    @staticmethod
    def approve_application(application_id):
        """批准飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if not application.can_be_approved():
            raise ValueError('申请状态不允许审批')

        # 检查是否已过期
        if application.is_expired():
            application.status = 'expired'
            db.session.commit()
            raise ValueError('申请已过期')

        # 再次检查空域冲突
        if AirspaceService.check_airspace_conflict(
            application.planned_airspace_id,
            application.planned_start_time,
            application.planned_end_time,
            exclude_application_id=application.id
        ):
            raise ValueError('申请的时间段内空域已被占用')

        application.status = 'approved'
        application.rejection_reason = None
        db.session.commit()

        # 更新空域使用记录状态
        usage = AirspaceUsage.query.filter_by(flight_application_id=application.id).first()
        if usage:
            usage.status = 'approved'
            db.session.commit()

        return application

    @staticmethod
    def reject_application(application_id, rejection_reason):
        """驳回飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if not application.can_be_approved():
            raise ValueError('申请状态不允许审批')

        application.status = 'rejected'
        application.rejection_reason = rejection_reason
        db.session.commit()

        return application

    @staticmethod
    def withdraw_application(application_id):
        """撤回飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if not application.can_be_approved():
            raise ValueError('申请状态不允许审批')

        application.status = 'draft'
        db.session.commit()

        return application

    @staticmethod
    def terminate_flights(application_id):
        """终止已审批通过的飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')
        if not application.can_be_terminate():
            raise ValueError("申请状态不允许终止")

        application.status = 'rejected' #终止状态等价于驳回状态
        application.rejection_reason = "管理员误操作通过申请，现已终止该计划"
        db.session.commit()

        #更新空域使用情况

        usage = AirspaceUsage.query.filter_by(flight_application_id=application.id).first()
        if usage:
            usage.status = 'released'
            db.session.commit()

        return application

    @staticmethod
    def delete_application(application_id):
        """删除草稿状态的飞行申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')
        if not application.can_be_submitted():
            raise ValueError("申请状态不允许删除")


        db.session.delete(application)
        db.session.commit()

        # 由于只有申请提交成功后才有空域占用，所有此处不需要更新空域使用情况
        return application

    @staticmethod
    def launch_flight(application_id, user_id):
        """放飞申请"""
        application = FlightApplication.query.get(application_id)
        if not application:
            raise ValueError('申请不存在')

        if application.user_id != user_id:
            raise ValueError('无权限执行此操作')

        if not application.can_be_launched():
            raise ValueError('申请状态不允许放飞')

        # 检查时间是否在申请范围内
        # 使用timezone-aware的UTC时间，确保正确性
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        
        if now < application.planned_start_time or now > application.planned_end_time:
            error_msg = f'当前时间不在申请的飞行时间范围内 (当前UTC: {now}, 申请时间: {application.planned_start_time} ~ {application.planned_end_time})'
            raise ValueError(error_msg)
        
        # 验证预计结束时间
        estimated_finish_time = now + timedelta(minutes=application.total_time)

        if estimated_finish_time > application.planned_end_time:
            time_shortage = (estimated_finish_time - application.planned_end_time).total_seconds() / 60
            error_msg = (
                f'预计结束时间（{estimated_finish_time.strftime("%H:%M:%S")}）'
                f'超出计划结束时间（{application.planned_end_time.strftime("%H:%M:%S")}）约{int(time_shortage)}分钟，'
                f'无法在计划时间内完成飞行任务，不得放飞'
            )
            raise ValueError(error_msg)

        # 检查空域是否可用
        airspace = Airspace.query.get(application.planned_airspace_id)
        if not airspace:
            raise ValueError('空域不存在')

        if airspace.type == 'no_fly':
            raise ValueError('该空域为禁飞区，无法放飞')

        if airspace.status == 'occupied':
            raise ValueError('空域当前被占用，无法放飞')

        # 创建任务，计算预计结束时间
        estimated_end_time = now + timedelta(minutes=application.total_time)
        mission = Mission(
            flight_application_id=application.id,
            operator_id=user_id,
            route=application.route,
            start_time=now,
            end_time=estimated_end_time,  # 设置预计结束时间
            status='executing'
        )
        db.session.add(mission)

        # 更新空域状态
        airspace.status = 'occupied'

        # 更新空域使用记录
        usage = AirspaceUsage.query.filter_by(flight_application_id=application.id).first()
        if usage:
            usage.status = 'active'

        db.session.commit()

        return mission

    @staticmethod
    def get_application_list(user_id=None, is_admin=False, status=None, page=1, page_size=20):
        """获取申请列表"""
        query = FlightApplication.query

        # 操作员只能看到自己的申请
        if not is_admin and user_id:
            query = query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        total = query.count()
        applications = query.order_by(FlightApplication.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': [app.to_dict(include_relations=True) for app in applications],
            'total': total,
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def get_pending_applications():
        """获取待审批的申请"""
        return FlightApplication.query.filter_by(status='pending').order_by(FlightApplication.created_at.asc()).all()

    @staticmethod
    def check_expired_applications():
        """检查并更新过期的申请"""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expired_apps = FlightApplication.query.filter(
            FlightApplication.status.in_([ 'pending','approved']),
            FlightApplication.planned_end_time < now
        ).all()    #此处应该是超过计划结束时间，已修改

        for app in expired_apps:
            app.status = 'expired'

        db.session.commit()
        return len(expired_apps)

