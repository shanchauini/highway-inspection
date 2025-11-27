from datetime import datetime
from app.models import db
import json


class FlightApplication(db.Model):
    """飞行申请模型"""
    __tablename__ = 'flight_applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drone_model = db.Column(db.String(100), nullable=False)
    task_purpose = db.Column(db.Text, nullable=False)
    planned_airspace_id = db.Column(db.Integer, db.ForeignKey('airspaces.id'), nullable=False)
    planned_start_time = db.Column(db.DateTime, nullable=False)
    planned_end_time = db.Column(db.DateTime, nullable=False)
    total_time = db.Column(db.Integer, nullable=False)  # 总时长（分钟）
    route = db.Column(db.JSON, nullable=False)  # GeoJSON格式的航线
    status = db.Column(db.Enum('draft', 'pending', 'approved', 'rejected', 'expired'), default='draft')
    is_long_term = db.Column(db.Boolean, default=False)
    long_term_start = db.Column(db.DateTime)
    long_term_end = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    missions = db.relationship('Mission', backref='flight_application', lazy='dynamic')
    usage_records = db.relationship('AirspaceUsage', backref='flight_application', lazy='dynamic')

    def get_route_coordinates(self):
        """获取航线坐标"""
        if isinstance(self.route, str):
            return json.loads(self.route)
        return self.route

    def can_be_submitted(self):
        """判断是否可以提交"""
        return self.status == 'draft'

    def can_be_approved(self):
        """判断是否可以审批"""
        return self.status == 'pending'

    def can_be_launched(self):
        """判断是否可以放飞"""
        return self.status == 'approved'

    def is_expired(self):
        """判断是否过期"""
        return self.status in ['pending','approved'] and datetime.utcnow() > self.planned_end_time

    def can_be_terminate(self):
        """判断是否可以终止,目前暂定只有误操作审批通过后需要终止"""
        return self.status == 'approved'

    def to_dict(self, include_relations=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'drone_model': self.drone_model,
            'task_purpose': self.task_purpose,
            'planned_airspace_id': self.planned_airspace_id,
            'planned_start_time': self.planned_start_time.isoformat() if self.planned_start_time else None,
            'planned_end_time': self.planned_end_time.isoformat() if self.planned_end_time else None,
            'total_time': self.total_time,
            'route': self.get_route_coordinates(),
            'status': self.status,
            'is_long_term': self.is_long_term,
            'long_term_start': self.long_term_start.isoformat() if self.long_term_start else None,
            'long_term_end': self.long_term_end.isoformat() if self.long_term_end else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_relations:
            data['applicant'] = self.applicant.to_dict() if self.applicant else None
            data['airspace'] = self.planned_airspace.to_dict() if self.planned_airspace else None

        return data

    def __repr__(self):
        return f'<FlightApplication {self.id} - {self.status}>'

