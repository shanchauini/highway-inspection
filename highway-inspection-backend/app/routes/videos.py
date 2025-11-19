from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import os

from app.models import db, Video, Mission, User
from app.schemas.video_schema import VideoUploadSchema
from app.utils import success_response, error_response, paginate_response, login_required

videos_bp = Blueprint('videos', __name__)


@videos_bp.route('', methods=['GET'])
@login_required
def get_videos():
    """获取视频列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        mission_id = request.args.get('mission_id', None, type=int)

        query = Video.query

        if mission_id:
            query = query.filter_by(mission_id=mission_id)
        else:
            # 操作员只能查看自己任务的视频
            if not user.is_admin():
                mission_ids = [m.id for m in Mission.query.filter_by(operator_id=user_id).all()]
                query = query.filter(Video.mission_id.in_(mission_ids))

        total = query.count()
        videos = query.order_by(Video.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return paginate_response(
            items=[video.to_dict(include_relations=True) for video in videos],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        return error_response(f'获取视频列表失败: {str(e)}', 500)


@videos_bp.route('/<int:video_id>', methods=['GET'])
@login_required
def get_video(video_id):
    """获取视频详情"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        video = Video.query.get(video_id)
        if not video:
            return error_response('视频不存在', 404)

        # 操作员只能查看自己任务的视频
        if not user.is_admin() and video.mission.operator_id != user_id:
            return error_response('无权限查看此视频', 403)

        return success_response(data=video.to_dict(include_relations=True))

    except Exception as e:
        return error_response(f'获取视频详情失败: {str(e)}', 500)


@videos_bp.route('', methods=['POST'])
@login_required
def upload_video():
    """上传视频（创建视频记录）"""
    try:
        user_id = int(get_jwt_identity())

        # 验证请求数据
        schema = VideoUploadSchema()
        data = schema.load(request.get_json())

        # 检查任务是否存在且有权限
        mission = Mission.query.get(data['mission_id'])
        if not mission:
            return error_response('任务不存在', 404)

        if mission.operator_id != user_id:
            return error_response('无权限为此任务上传视频', 403)

        # 创建视频记录
        video = Video(
            mission_id=data['mission_id'],
            video_path=data.get('video_path', ''),  # 实际文件上传后更新
            collected_time=data['collected_time'],
            road_section=data['road_section'],
            file_format=data.get('file_format', 'mp4'),
            file_size=data.get('file_size'),
            duration=data.get('duration')
        )

        db.session.add(video)
        db.session.commit()

        return success_response(
            data=video.to_dict(include_relations=True),
            message='视频记录创建成功',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except Exception as e:
        return error_response(f'上传视频失败: {str(e)}', 500)


@videos_bp.route('/<int:video_id>/analysis-results', methods=['GET'])
@login_required
def get_video_analysis_results(video_id):
    """获取视频分析结果"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        video = Video.query.get(video_id)
        if not video:
            return error_response('视频不存在', 404)

        # 操作员只能查看自己任务的视频
        if not user.is_admin() and video.mission.operator_id != user_id:
            return error_response('无权限查看此视频分析结果', 403)

        results = video.analysis_results.all()

        return success_response(
            data=[result.to_dict() for result in results]
        )

    except Exception as e:
        return error_response(f'获取分析结果失败: {str(e)}', 500)

