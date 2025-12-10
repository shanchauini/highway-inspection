from datetime import datetime, timezone
from app.models import db
import json
import math


def utcnow():
    """返回真正的UTC时间（无时区）"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Mission(db.Model):
    """飞行任务模型"""
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_application_id = db.Column(db.Integer, db.ForeignKey('flight_applications.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route = db.Column(db.JSON, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('executing', 'completed'), default='executing')
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    # 关系
    videos = db.relationship('Video', backref='mission', lazy='dynamic')
    analysis_results = db.relationship('AnalysisResult', backref='mission', lazy='dynamic')
    alert_events = db.relationship('AlertEvent', backref='mission', lazy='dynamic')

    def get_route_coordinates(self):
        """获取航线坐标"""
        if isinstance(self.route, str):
            return json.loads(self.route)
        return self.route

    def is_active(self):
        """判断任务是否进行中"""
        return self.status == 'executing'

    def calculate_route_distance(self):
        """计算航线总长度（公里）- 使用Haversine公式"""
        coords = self.get_route_coordinates()
        if not coords:
            return 0.0
        
        # 处理GeoJSON格式：可能是直接数组或包含coordinates的对象
        if isinstance(coords, dict) and 'coordinates' in coords:
            # GeoJSON LineString格式: {"type": "LineString", "coordinates": [[lng, lat], ...]}
            coord_list = coords['coordinates']
        elif isinstance(coords, list):
            # 直接数组格式: [[lng, lat], ...]
            coord_list = coords
        else:
            return 0.0
        
        if len(coord_list) < 2:
            return 0.0
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """计算两点间距离（公里）"""
            R = 6371  # 地球半径（公里）
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2) ** 2 + \
                math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
                math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        
        total_distance = 0.0
        for i in range(len(coord_list) - 1):
            # GeoJSON格式是[lng, lat]，需要转换为[lat, lng]用于计算
            lon1, lat1 = coord_list[i]
            lon2, lat2 = coord_list[i + 1]
            total_distance += haversine_distance(lat1, lon1, lat2, lon2)
        
        return total_distance

    def calculate_flight_speed(self):
        """计算飞行速度（公里/小时）
        使用飞行申请中的total_time（分钟）和航线距离
        """
        if not self.flight_application or not self.flight_application.total_time:
            return None
        
        route_distance = self.calculate_route_distance()
        if route_distance == 0:
            return None
        
        # total_time是分钟，转换为小时
        flight_time_hours = self.flight_application.total_time / 60.0
        if flight_time_hours <= 0:
            return None
        
        speed = route_distance / flight_time_hours
        return round(speed, 2)

    def to_dict(self, include_relations=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'flight_application_id': self.flight_application_id,
            'operator_id': self.operator_id,
            'route': self.get_route_coordinates(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'route_distance': round(self.calculate_route_distance(), 2),  # 航线距离（公里）
            'flight_speed': self.calculate_flight_speed(),  # 飞行速度（公里/小时）
            'analysis_results_count': self.analysis_results.count()  # AI分析结果数量
        }

        if include_relations:
            data['operator'] = self.operator.to_dict() if self.operator else None
            data['flight_application'] = self.flight_application.to_dict() if self.flight_application else None

        return data

    def __repr__(self):
        return f'<Mission {self.id} - {self.status}>'

