from datetime import datetime
from app.models import db


class Video(db.Model):
    """视频模型"""
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    video_path = db.Column(db.String(500), nullable=False)
    collected_time = db.Column(db.DateTime, nullable=False)
    road_section = db.Column(db.String(200), nullable=False)
    file_format = db.Column(db.String(10), default='mp4')
    file_size = db.Column(db.BigInteger)  # 字节
    duration = db.Column(db.Integer)  # 秒
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    analysis_results = db.relationship('AnalysisResult', backref='video', lazy='dynamic')
    alert_events = db.relationship('AlertEvent', backref='video', lazy='dynamic')

    def to_dict(self, include_relations=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'mission_id': self.mission_id,
            'video_path': self.video_path,
            'collected_time': self.collected_time.isoformat() if self.collected_time else None,
            'road_section': self.road_section,
            'file_format': self.file_format,
            'file_size': self.file_size,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_relations:
            data['mission'] = self.mission.to_dict() if self.mission else None

        return data

    def __repr__(self):
        return f'<Video {self.id} - {self.road_section}>'

