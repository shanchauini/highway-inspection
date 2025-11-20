from flask import Blueprint, request
from datetime import datetime

from app.services import DashboardService
from app.utils import success_response, error_response, login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """获取数据看板统计（总览）"""
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        # 获取统计数据
        data = DashboardService.get_dashboard_overview(start_date, end_date)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取统计数据失败: {str(e)}', 500)


@dashboard_bp.route('/flight-stats', methods=['GET'])
@login_required
def get_flight_stats():
    """获取飞行统计"""
    try:
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        data = DashboardService.get_flight_statistics(start_date, end_date)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取飞行统计失败: {str(e)}', 500)


@dashboard_bp.route('/airspace-usage', methods=['GET'])
@login_required
def get_airspace_usage():
    """获取空域使用统计"""
    try:
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        data = DashboardService.get_airspace_usage_statistics(start_date, end_date)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取空域使用统计失败: {str(e)}', 500)


@dashboard_bp.route('/alert-stats', methods=['GET'])
@login_required
def get_alert_stats():
    """获取告警统计"""
    try:
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        data = DashboardService.get_alert_statistics(start_date, end_date)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取告警统计失败: {str(e)}', 500)


@dashboard_bp.route('/alert-trend', methods=['GET'])
@login_required
def get_alert_trend():
    """获取告警趋势"""
    try:
        days = request.args.get('days', 7, type=int)

        data = DashboardService.get_alert_trend(days)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取告警趋势失败: {str(e)}', 500)


@dashboard_bp.route('/flight-trend', methods=['GET'])
@login_required
def get_flight_trend():
    """获取飞行任务趋势"""
    try:
        start_date_str = request.args.get('start_date', None)
        end_date_str = request.args.get('end_date', None)

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        data = DashboardService.get_flight_trend(start_date=start_date, end_date=end_date)

        return success_response(data=data)

    except Exception as e:
        return error_response(f'获取飞行任务趋势失败: {str(e)}', 500)
