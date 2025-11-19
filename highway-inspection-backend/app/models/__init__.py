from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型
from app.models.user import User
from app.models.airspace import Airspace, AirspaceUsage
from app.models.flight_application import FlightApplication
from app.models.mission import Mission
from app.models.video import Video
from app.models.analysis_result import AnalysisResult
from app.models.alert import AlertEvent

__all__ = [
    'db',
    'User',
    'Airspace',
    'AirspaceUsage',
    'FlightApplication',
    'Mission',
    'Video',
    'AnalysisResult',
    'AlertEvent'
]

