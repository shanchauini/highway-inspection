from datetime import datetime
from app.models import db
import json


class AnalysisResult(db.Model):
    """视频分析结果模型"""
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    occurred_time = db.Column(db.DateTime, nullable=False)
    bounding_box = db.Column(db.JSON)  # 目标框坐标
    confidence = db.Column(db.Numeric(4, 3))  # 置信度
    result_image = db.Column(db.String(500))  # 检测结果图片路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 索引
    __table_args__ = (
        db.Index('idx_video_time', 'video_id', 'occurred_time'),
    )

    def get_bounding_box(self):
        """获取目标框坐标"""
        if isinstance(self.bounding_box, str):
            return json.loads(self.bounding_box)
        return self.bounding_box

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'video_id': self.video_id,
            'target_type': self.target_type,
            'occurred_time': self.occurred_time.isoformat() if self.occurred_time else None,
            'bounding_box': self.get_bounding_box(),
            'confidence': float(self.confidence) if self.confidence else None,
            'result_image': self.result_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AnalysisResult {self.id} - {self.target_type}>'

