from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.models import db, Video, Mission, User, AnalysisResult
from app.schemas.video_schema import VideoUploadSchema
from app.utils import success_response, error_response, paginate_response, login_required

# 导入AI服务
from app.services import ai_service

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
    """获取视频分析结果（支持分页）"""
    try:
        user_id = int(get_jwt_identity())  # 转换为int类型
        user = User.query.get(user_id)

        video = Video.query.get(video_id)
        if not video:
            return error_response('视频不存在', 404)

        # 操作员只能查看自己任务的视频
        if not user.is_admin() and video.mission.operator_id != user_id:
            return error_response('无权限查看此视频分析结果', 403)

        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 查询结果
        query = video.analysis_results
        total = query.count()
        results = query.order_by(AnalysisResult.occurred_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return paginate_response(
            items=[result.to_dict() for result in results],
            total=total,
            page=page,
            page_size=page_size
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
        
        print(f"📥 接收到上传请求: mission_id={mission_id}, detection_type={detection_type}, media_type={media_type}")
        
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
        
        print(f"📁 文件已保存: {file_path}")
        
        # 如果是视频文件，检查是否需要格式转换
        original_file_path = file_path
        if media_type == 'video':
            # 检查文件扩展名是否为 avi，如果是则转换为 mp4
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.avi':
                # 使用 opencv-python 转换 avi 到 mp4（不需要 ffmpeg 命令）
                mp4_filename = f"{os.path.splitext(filename_with_timestamp)[0]}.mp4"
                mp4_file_path = os.path.join(upload_folder, mp4_filename)
                
                try:
                    import cv2
                    print(f"🔄 开始使用 OpenCV 转换 AVI 到 MP4: {file_path}")
                    
                    # 打开原始视频
                    cap = cv2.VideoCapture(file_path)
                    if not cap.isOpened():
                        raise ValueError(f"无法打开视频文件: {file_path}")
                    
                    # 获取视频属性
                    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25  # 默认25fps
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    print(f"📹 视频信息: {width}x{height}, {fps}fps, {total_frames}帧")
                    
                    # 尝试多种编码器，按优先级顺序
                    # 注意：不同系统支持的编码器可能不同
                    codecs_to_try = [
                        ('avc1', 'H.264/AVC'),  # 最佳浏览器兼容性
                        ('mp4v', 'MPEG-4'),     # 通用MPEG-4
                        ('XVID', 'Xvid'),        # Xvid编码
                        ('MJPG', 'Motion JPEG') # Motion JPEG（备用）
                    ]
                    
                    out = None
                    used_codec = None
                    for fourcc_str, codec_name in codecs_to_try:
                        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
                        out = cv2.VideoWriter(mp4_file_path, fourcc, fps, (width, height))
                        if out.isOpened():
                            used_codec = codec_name
                            print(f"✅ 使用编码器: {codec_name} ({fourcc_str})")
                            break
                        else:
                            out.release()
                            out = None
                    
                    if out is None or not out.isOpened():
                        raise ValueError("无法创建输出视频文件，所有编码器都不可用")
                    
                    # 逐帧读取并写入
                    frame_count = 0
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        out.write(frame)
                        frame_count += 1
                        
                        # 每处理100帧打印一次进度
                        if frame_count % 100 == 0:
                            progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
                            print(f"🔄 转换进度: {frame_count}/{total_frames} ({progress:.1f}%)")
                    
                    # 释放资源
                    cap.release()
                    out.release()
                    
                    print(f"✅ 视频格式转换完成: {mp4_file_path} ({frame_count}帧)")
                    
                    # 转换成功后更新文件路径
                    file_path = mp4_file_path
                    # 删除原始 avi 文件
                    try:
                        os.remove(original_file_path)
                        print(f"🗑️ 已删除原始 AVI 文件: {original_file_path}")
                    except Exception as e:
                        print(f"⚠️ 删除原始文件失败（可忽略）: {e}")
                        
                except ImportError:
                    print("⚠️ OpenCV 未安装，无法转换视频格式")
                    print("💡 提示: 请安装 opencv-python: pip install opencv-python")
                except Exception as e:
                    import traceback
                    print(f"⚠️ 视频格式转换失败: {e}")
                    print(traceback.format_exc())
                    # 即使转换失败，我们也继续使用原始文件
        
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
        
        print(f"📹 视频记录已创建: ID={video.id}")
        
        # 不再在上传时进行AI分析，用户需要单独触发分析
        # 保存检测类型到视频记录中，以便后续分析时使用
        # 注意：Video模型可能需要添加detection_type字段，这里先不保存
        
        return success_response(
            data=video.to_dict(include_relations=True),
            message=f'{"图片" if media_type == "image" else "视频"}上传成功，请点击"开始分析"按钮进行AI分析',
            code=201
        )
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = f'文件上传失败: {str(e)}'
        print(f"🚨 错误详情: {error_msg}")
        print(traceback.format_exc())
        return error_response(error_msg, 500)


@videos_bp.route('/<int:video_id>/analyze', methods=['POST'])
@login_required
def analyze_video(video_id):
    """对视频或图片进行AI分析"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # 获取视频记录
        video = Video.query.get(video_id)
        if not video:
            return error_response('视频不存在', 404)
        
        # 检查权限
        if not user.is_admin() and video.mission.operator_id != user_id:
            return error_response('无权限分析此视频', 403)
        
        # 获取检测类型（从请求参数或表单数据）
        detection_type = request.json.get('detection_type') if request.is_json else request.form.get('detection_type', 'traffic_congestion')
        
        file_path = video.video_path
        if not file_path or not os.path.exists(file_path):
            return error_response('视频文件不存在', 404)
        
        # 判断是图片还是视频
        file_ext = os.path.splitext(file_path)[1].lower()
        is_image = file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        
        if not (is_image or is_video):
            return error_response('不支持的文件格式', 400)
        
        print(f"🔍 开始AI分析: video_id={video_id}, detection_type={detection_type}, file_type={'image' if is_image else 'video'}")
        
        # 图片分析
        if is_image:
            if detection_type == 'traffic_congestion' and ai_service.is_traffic_congestion_available():
                try:
                    print(f"🔍 开始交通拥堵检测（图片）: {file_path}")
                    result = ai_service.predict_traffic_congestion(file_path)
                    
                    if result:
                        print(f"📊 交通检测结果: class_name={result['class_name']}, confidence={result['confidence']:.4f}")
                        
                        analysis_result = AnalysisResult(
                            mission_id=video.mission_id,
                            video_id=video.id,
                            target_type=result['class_name'],
                            occurred_time=datetime.now(),
                            confidence=result['confidence'],
                            result_image=file_path
                        )
                        
                        db.session.add(analysis_result)
                        db.session.commit()
                        print(f"✅ 交通拥堵检测完成: ID={analysis_result.id}")
                        
                        return success_response(
                            data=analysis_result.to_dict(),
                            message='图片分析完成'
                        )
                    
                except Exception as ai_error:
                    import traceback
                    print(f"⚠️ 交通拥堵检测失败: {ai_error}")
                    print(traceback.format_exc())
                    return error_response(f'AI分析失败: {str(ai_error)}', 500)
                    
            elif detection_type == 'road_damage' and ai_service.is_road_damage_available():
                try:
                    print(f"🔍 开始地面破损检测（图片）: {file_path}")
                    result = ai_service.predict_road_damage(file_path, save_result=True)
                    
                    if result:
                        detections = result['detections']
                        result_image = result['result_image']
                        
                        print(f"📊 地面破损检测结果: 检测到 {len(detections)} 个目标")
                        
                        # 为每个检测目标创建分析结果记录
                        for det in detections:
                            analysis_result = AnalysisResult(
                                mission_id=video.mission_id,
                                video_id=video.id,
                                target_type=det['class_name'],
                                occurred_time=datetime.now(),
                                confidence=det['confidence'],
                                bounding_box=det['bbox'],
                                result_image=result_image
                            )
                            db.session.add(analysis_result)
                        
                        # 如果没有检测到目标，也创建一条记录表示已分析
                        if not detections:
                            analysis_result = AnalysisResult(
                                mission_id=video.mission_id,
                                video_id=video.id,
                                target_type='无破损',
                                occurred_time=datetime.now(),
                                confidence=1.0,
                                result_image=result_image
                            )
                            db.session.add(analysis_result)
                        
                        db.session.commit()
                        print(f"✅ 地面破损检测完成，结果图片: {result_image}")
                        
                        return success_response(
                            message=f'图片分析完成，检测到 {len(detections)} 个目标'
                        )
                    
                except Exception as ai_error:
                    import traceback
                    print(f"⚠️ 地面破损检测失败: {ai_error}")
                    print(traceback.format_exc())
                    return error_response(f'AI分析失败: {str(ai_error)}', 500)
            else:
                return error_response(f'检测类型 {detection_type} 的AI模块不可用', 400)
        
        # 视频分析
        elif is_video:
            if detection_type == 'traffic_congestion' and ai_service.is_traffic_congestion_available():
                try:
                    print(f"🔍 开始交通拥堵视频检测: {file_path}")
                    
                    # 定义回调函数，每处理一帧时保存结果到数据库
                    def process_frame_callback(frame_idx, timestamp_ms, result, frame_image_path=None):
                        """处理每一帧的回调函数"""
                        print(f"📊 处理帧 #{frame_idx}: {result['class_name']} ({result['confidence']:.2f})")
                        analysis_result = AnalysisResult(
                            mission_id=video.mission_id,
                            video_id=video.id,
                            target_type=result['class_name'],
                            occurred_time=datetime.now(),
                            confidence=result['confidence'],
                            result_image=frame_image_path
                        )
                        db.session.add(analysis_result)
                        # 每10帧提交一次，避免数据库操作过多
                        if frame_idx % 10 == 0:
                            db.session.commit()
                            print(f"💾 已提交前 {frame_idx} 帧的分析结果到数据库")
                    
                    # 执行视频检测（每5帧处理一次，减少数据库操作）
                    results = ai_service.predict_traffic_congestion_video(
                        file_path,
                        frame_interval=5,
                        callback=process_frame_callback,
                        save_result=False,
                        save_frames=True,
                        frames_output_dir=None
                    )
                    
                    # 提交剩余的结果
                    db.session.commit()
                    
                    if results:
                        print(f"✅ 交通拥堵视频检测完成，共处理 {len(results)} 帧")
                        return success_response(
                            message=f'视频分析完成，共处理 {len(results)} 帧'
                        )
                    else:
                        return error_response('视频分析未返回结果', 500)
                    
                except Exception as ai_error:
                    import traceback
                    print(f"⚠️ 交通拥堵视频检测失败: {ai_error}")
                    print(traceback.format_exc())
                    return error_response(f'AI分析失败: {str(ai_error)}', 500)
            else:
                return error_response(f'视频检测类型 {detection_type} 暂不支持或AI模块不可用', 400)
        
        return error_response('不支持的文件类型', 400)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = f'AI分析失败: {str(e)}'
        print(f"🚨 错误详情: {error_msg}")
        print(traceback.format_exc())
        return error_response(error_msg, 500)

