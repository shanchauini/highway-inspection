"""
AI模块接口
供AI分析模块调用的接口，用于提交分析结果
"""
from flask import Blueprint, request
from marshmallow import ValidationError, Schema, fields

from app.models import db, AnalysisResult
from app.utils import success_response, error_response

ai_bp = Blueprint('ai', __name__)


class AnalysisResultSubmitSchema(Schema):
    """分析结果提交Schema"""
    mission_id = fields.Int(required=True)
    video_id = fields.Int(required=True)
    target_type = fields.Str(required=True)
    occurred_time = fields.DateTime(required=True, format='iso')
    bounding_box = fields.Dict(allow_none=True)
    confidence = fields.Float(allow_none=True)


@ai_bp.route('/analysis/results', methods=['POST'])
def submit_analysis_result():
    """
    提交视频分析结果
    由AI模块调用，无需认证
    """
    try:
        # 验证请求数据
        schema = AnalysisResultSubmitSchema()
        data = schema.load(request.get_json())

        # 创建分析结果
        result = AnalysisResult(
            mission_id=data['mission_id'],
            video_id=data['video_id'],
            target_type=data['target_type'],
            occurred_time=data['occurred_time'],
            bounding_box=data.get('bounding_box'),
            confidence=data.get('confidence')
        )

        db.session.add(result)
        db.session.commit()

        return success_response(
            data=result.to_dict(),
            message='分析结果提交成功',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except Exception as e:
        return error_response(f'提交分析结果失败: {str(e)}', 500)


@ai_bp.route('/analysis/results/batch', methods=['POST'])
def submit_analysis_results_batch():
    """
    批量提交视频分析结果
    由AI模块调用，无需认证
    """
    try:
        data = request.get_json()
        results_data = data.get('results', [])

        if not results_data:
            return error_response('结果列表不能为空', 400)

        # 批量创建分析结果
        results = []
        schema = AnalysisResultSubmitSchema()

        for item in results_data:
            validated_data = schema.load(item)
            result = AnalysisResult(
                mission_id=validated_data['mission_id'],
                video_id=validated_data['video_id'],
                target_type=validated_data['target_type'],
                occurred_time=validated_data['occurred_time'],
                bounding_box=validated_data.get('bounding_box'),
                confidence=validated_data.get('confidence')
            )
            results.append(result)

        db.session.bulk_save_objects(results)
        db.session.commit()

        return success_response(
            data={'count': len(results)},
            message=f'成功提交 {len(results)} 条分析结果',
            code=201
        )

    except ValidationError as e:
        return error_response('数据验证失败', 400, e.messages)
    except Exception as e:
        return error_response(f'批量提交分析结果失败: {str(e)}', 500)


@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """
    AI模块健康检查接口
    """
    return success_response(
        data={'status': 'ok'},
        message='AI接口服务正常'
    )

