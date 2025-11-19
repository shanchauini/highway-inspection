from datetime import datetime
from app.models import db


class AlertEvent(db.Model):
    """告警事件模型"""
    __tablename__ = 'alert_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Enum('low', 'medium', 'high'), nullable=False)
    road_section = db.Column(db.String(200), nullable=False)
    occurred_time = db.Column(db.DateTime, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    status = db.Column(db.Enum('new', 'confirmed', 'processing', 'closed'), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        db.Index('idx_status_time', 'status', 'occurred_time'),
    )

    def is_active(self):
        """判断告警是否活跃"""
        return self.status in ['new', 'confirmed', 'processing']

    def to_dict(self, include_relations=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'event_type': self.event_type,
            'severity': self.severity,
            'road_section': self.road_section,
            'occurred_time': self.occurred_time.isoformat() if self.occurred_time else None,
            'video_id': self.video_id,
            'mission_id': self.mission_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_relations:
            data['video'] = self.video.to_dict() if self.video else None
            data['mission'] = self.mission.to_dict() if self.mission else None

        return data

    def __repr__(self):
        return f'<AlertEvent {self.id} - {self.title}>'

