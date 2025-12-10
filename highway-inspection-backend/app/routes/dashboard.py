from flask import Blueprint, request
from datetime import datetime
from flask_jwt_extended import get_jwt_identity

from app.services import DashboardService
from app.models import User
from app.utils import success_response, error_response, login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """获取数据看板统计（总览）"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # 获取查询参数
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        # 获取统计数据
        data = DashboardService.get_dashboard_overview(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取统计数据失败: {str(e)}', 500)


@dashboard_bp.route('/flight-stats', methods=['GET'])
@login_required
def get_flight_stats():
    """获取飞行统计"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_flight_statistics(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取飞行统计失败: {str(e)}', 500)


@dashboard_bp.route('/airspace-usage', methods=['GET'])
@login_required
def get_airspace_usage():
    """获取空域使用统计"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_airspace_usage_statistics(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取空域使用统计失败: {str(e)}', 500)


@dashboard_bp.route('/alert-stats', methods=['GET'])
@login_required
def get_alert_stats():
    """获取告警统计"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_alert_statistics(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取告警统计失败: {str(e)}', 500)


@dashboard_bp.route('/alert-trend', methods=['GET'])
@login_required
def get_alert_trend():
    """获取告警趋势"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        # 如果提供了开始和结束日期，则使用日期范围
        if start_date and end_date:
            data = DashboardService.get_alert_trend(start_date=start_date, end_date=end_date, user=user)
        else:
            # 否则使用默认的天数参数
            days = request.args.get('days', 7, type=int)
            data = DashboardService.get_alert_trend(days=days, user=user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取告警趋势失败: {str(e)}', 500)


@dashboard_bp.route('/flight-trend', methods=['GET'])
@login_required
def get_flight_trend():
    """获取飞行任务趋势"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_flight_trend(start_date=start_date, end_date=end_date, user=user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取飞行任务趋势失败: {str(e)}', 500)


@dashboard_bp.route('/inspection-results', methods=['GET'])
@login_required
def get_inspection_results():
    """获取巡检结果统计"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_inspection_results_statistics(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取巡检结果统计失败: {str(e)}', 500)


@dashboard_bp.route('/inspection-trend', methods=['GET'])
@login_required
def get_inspection_trend():
    """获取巡检结果趋势"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        # 如果提供了开始和结束日期，则使用日期范围
        if start_date and end_date:
            data = DashboardService.get_inspection_results_trend(start_date=start_date, end_date=end_date, user=user)
        else:
            # 否则使用默认的天数参数
            days = request.args.get('days', 30, type=int)
            data = DashboardService.get_inspection_results_trend(days=days, user=user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取巡检结果趋势失败: {str(e)}', 500)


@dashboard_bp.route('/inspection-type-distribution', methods=['GET'])
@login_required
def get_inspection_type_distribution():
    """获取巡检结果类型分布"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_inspection_type_distribution(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取巡检结果类型分布失败: {str(e)}', 500)


@dashboard_bp.route('/problem-sections', methods=['GET'])
@login_required
def get_problem_sections():
    """获取高频问题路段"""
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

        data = DashboardService.get_problem_sections(start_date, end_date, user)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取高频问题路段失败: {str(e)}', 500)