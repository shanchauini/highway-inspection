from datetime import datetime
from app.models import db
import json


class Airspace(db.Model):
    """空域模型"""
    __tablename__ = 'airspaces'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    type = db.Column(db.Enum('suitable', 'restricted', 'no_fly'), nullable=False)
    area = db.Column(db.JSON, nullable=False)  # GeoJSON格式
    remark = db.Column(db.Text)
    status = db.Column(db.Enum('available', 'occupied', 'unavailable'), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    flight_applications = db.relationship('FlightApplication', backref='planned_airspace', lazy='dynamic')
    usage_records = db.relationship('AirspaceUsage', backref='airspace', lazy='dynamic')

    def get_area_coordinates(self):
        """获取空域坐标"""
        if isinstance(self.area, str):
            return json.loads(self.area)
        return self.area

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'type': self.type,
            'area': self.get_area_coordinates(),
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Airspace {self.number} - {self.name}>'


class AirspaceUsage(db.Model):
    """空域使用记录模型"""
    __tablename__ = 'airspace_usage'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_application_id = db.Column(db.Integer, db.ForeignKey('flight_applications.id'), nullable=False)
    airspace_id = db.Column(db.Integer, db.ForeignKey('airspaces.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('applied', 'approved', 'active', 'released'), default='applied')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 索引
    __table_args__ = (
        db.Index('idx_airspace_time', 'airspace_id', 'start_time', 'end_time'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'flight_application_id': self.flight_application_id,
            'airspace_id': self.airspace_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AirspaceUsage {self.id} - Airspace {self.airspace_id}>'

