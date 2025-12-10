from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.models import db, Video, Mission, User, AnalysisResult
from app.schemas.video_schema import VideoUploadSchema
from app.utils import success_response, error_response, paginate_response, login_required

# 导入AI模块
AI_MODULES = {
    'traffic_congestion': False,
    'road_damage': False
}

# 交通拥堵检测模块
try:
    from ai.traffic_congestion import YOLOv8Classifier
    AI_MODULES['traffic_congestion'] = True
    print("✅ 交通拥堵检测模块加载成功")
except Exception as e:
    print(f"⚠️ 交通拥堵检测模块加载失败 - {e}")

# 地面破损检测模块
try:
    from ai.road_damage import RoadDamageDetector
    AI_MODULES['road_damage'] = True
    print("✅ 地面破损检测模块加载成功")
except Exception as e:
    print(f"⚠️ 地面破损检测模块加载失败 - {e}")

# 向后兼容
AI_AVAILABLE = AI_MODULES['traffic_congestion']

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
        user_id = int(get_jwt_identity())  # 转换为int类型
        user = User.query.get(user_id)

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


@videos_bp.route('/upload', methods=['POST'])
@login_required
def upload_media_file():
    """上传媒体文件（图片或视频）并进行AI分析"""
    try:
        user_id = int(get_jwt_identity())
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response('未找到文件', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('未选择文件', 400)
        
        # 获取表单数据
        mission_id = request.form.get('mission_id', type=int)
        detection_type = request.form.get('detection_type', 'traffic_congestion')
        collected_time = request.form.get('collected_time')
        road_section = request.form.get('road_section', '')
        file_format = request.form.get('file_format', '')
        file_size = request.form.get('file_size', type=int)
        media_type = request.form.get('media_type', 'video')
        
        if not mission_id:
            return error_response('任务ID不能为空', 400)
        
        # 检查任务是否存在且有权限
        mission = Mission.query.get(mission_id)
        if not mission:
            return error_response('任务不存在', 404)
        
        # 获取当前用户
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 404)
        
        # 管理员或任务操作员可以上传文件
        if not user.is_admin() and mission.operator_id != user_id:
            return error_response('无权限为此任务上传文件', 403)
        
        # 保存文件
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('uploads', str(mission_id))
        os.makedirs(upload_folder, exist_ok=True)
        
        # 添加时间戳避免文件名冲突
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_with_timestamp = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_folder, filename_with_timestamp)
        file.save(file_path)
        
        # 创建视频记录
        video = Video(
            mission_id=mission_id,
            video_path=file_path,
            collected_time=datetime.fromisoformat(collected_time.replace('Z', '+00:00')) if collected_time else datetime.now(),
            road_section=road_section,
            file_format=file_format or filename.split('.')[-1],
            file_size=file_size,
            duration=0
        )
        
        db.session.add(video)
        db.session.commit()
        
        # 如果是图片，根据检测类型进行AI分析
        detection_type = request.form.get('detection_type', 'traffic_congestion')
        ai_result_data = None
        ai_analyzed = False
        
        if media_type == 'image':
            if detection_type == 'traffic_congestion' and AI_MODULES['traffic_congestion']:
                # 交通拥堵检测
                try:
                    print(f"🔍 开始交通拥堵检测: {file_path}")
                    classifier = YOLOv8Classifier()
                    result = classifier.predict(file_path)
                    
                    print(f"📊 交通检测结果: class_name={result['class_name']}, confidence={result['confidence']:.4f}")
                    
                    analysis_result = AnalysisResult(
                        mission_id=mission_id,
                        video_id=video.id,
                        target_type=result['class_name'],
                        occurred_time=datetime.now(),
                        confidence=result['confidence']
                    )
                    
                    db.session.add(analysis_result)
                    db.session.commit()
                    
                    ai_result_data = analysis_result.to_dict()
                    ai_analyzed = True
                    print(f"✅ 交通拥堵检测完成: ID={analysis_result.id}")
                    
                except Exception as ai_error:
                    import traceback
                    print(f"⚠️ 交通拥堵检测失败: {ai_error}")
                    print(traceback.format_exc())
                    
            elif detection_type == 'road_damage' and AI_MODULES['road_damage']:
                # 地面破损检测
                try:
                    print(f"🔍 开始地面破损检测: {file_path}")
                    detector = RoadDamageDetector(model_type='pt')
                    result = detector.predict(file_path, save_result=True)
                    
                    detections = result['detections']
                    result_image = result['result_image']
                    
                    print(f"📊 地面破损检测结果: 检测到 {len(detections)} 个目标")
                    
                    # 为每个检测目标创建分析结果记录
                    for det in detections:
                        analysis_result = AnalysisResult(
                            mission_id=mission_id,
                            video_id=video.id,
                            target_type=det['class_name'],
                            occurred_time=datetime.now(),
                            confidence=det['confidence'],
                            bounding_box=det['bbox'],
                            result_image=result_image  # 保存结果图片路径
                        )
                        db.session.add(analysis_result)
                    
                    # 如果没有检测到目标，也创建一条记录表示已分析
                    if not detections:
                        analysis_result = AnalysisResult(
                            mission_id=mission_id,
                            video_id=video.id,
                            target_type='无破损',
                            occurred_time=datetime.now(),
                            confidence=1.0,
                            result_image=result_image
                        )
                        db.session.add(analysis_result)
                    
                    db.session.commit()
                    ai_analyzed = True
                    print(f"✅ 地面破损检测完成，结果图片: {result_image}")
                    
                except Exception as ai_error:
                    import traceback
                    print(f"⚠️ 地面破损检测失败: {ai_error}")
                    print(traceback.format_exc())
            else:
                print(f"⚠️ 检测类型 {detection_type} 的AI模块不可用")
        
        return success_response(
            data=video.to_dict(include_relations=True),
            message=f'{"图片" if media_type == "image" else "视频"}上传成功{"并已完成AI分析" if ai_analyzed else ""}',
            code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'文件上传失败: {str(e)}', 500)

