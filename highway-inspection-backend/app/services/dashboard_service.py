from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.models import db, Mission, AlertEvent, AirspaceUsage, Airspace


class DashboardService:
    """数据看板服务"""

    @staticmethod
    def get_flight_statistics(start_date=None, end_date=None):
        """获取飞行统计"""
        query = Mission.query.filter_by(status='completed')

        if start_date:
            query = query.filter(Mission.start_time >= start_date)
        if end_date:
            query = query.filter(Mission.end_time <= end_date)

        missions = query.all()

        # 统计总次数
        total_missions = len(missions)

        # 统计总时长（小时）
        total_duration = 0
        for mission in missions:
            if mission.start_time and mission.end_time:
                duration = (mission.end_time - mission.start_time).total_seconds() / 3600
                total_duration += duration

        return {
            'total_missions': total_missions,
            'total_duration': round(total_duration, 2),
            'average_duration': round(total_duration / total_missions, 2) if total_missions > 0 else 0
        }

    @staticmethod
    def get_airspace_usage_statistics(start_date=None, end_date=None):
        """获取空域使用统计"""
        query = AirspaceUsage.query.filter(AirspaceUsage.status.in_(['approved', 'active', 'released']))

        if start_date:
            query = query.filter(AirspaceUsage.start_time >= start_date)
        if end_date:
            query = query.filter(AirspaceUsage.end_time <= end_date)

        usage_records = query.all()

        # 按空域统计
        airspace_stats = {}
        for record in usage_records:
            airspace_id = record.airspace_id
            if airspace_id not in airspace_stats:
                airspace = Airspace.query.get(airspace_id)
                airspace_stats[airspace_id] = {
                    'airspace_id': airspace_id,
                    'airspace_name': airspace.name if airspace else '未知',
                    'usage_count': 0,
                    'total_duration': 0
                }

            airspace_stats[airspace_id]['usage_count'] += 1

            # 计算使用时长（小时）
            if record.start_time and record.end_time:
                duration = (record.end_time - record.start_time).total_seconds() / 3600
                airspace_stats[airspace_id]['total_duration'] += duration

        # 转换为列表并排序
        result = list(airspace_stats.values())
        for item in result:
            item['total_duration'] = round(item['total_duration'], 2)

        result.sort(key=lambda x: x['usage_count'], reverse=True)

        return result

    @staticmethod
    def get_alert_statistics(start_date=None, end_date=None):
        """获取告警统计"""
        query = AlertEvent.query

        if start_date:
            query = query.filter(AlertEvent.occurred_time >= start_date)
        if end_date:
            query = query.filter(AlertEvent.occurred_time <= end_date)

        alerts = query.all()

        # 总告警数
        total_alerts = len(alerts)

        # 按类型统计
        type_stats = {}
        for alert in alerts:
            event_type = alert.event_type
            if event_type not in type_stats:
                type_stats[event_type] = 0
            type_stats[event_type] += 1

        # 按严重程度统计
        severity_stats = {
            'low': 0,
            'medium': 0,
            'high': 0
        }
        for alert in alerts:
            severity_stats[alert.severity] += 1

        # 按状态统计
        status_stats = {
            'new': 0,
            'confirmed': 0,
            'processing': 0,
            'closed': 0
        }
        for alert in alerts:
            status_stats[alert.status] += 1

        return {
            'total_alerts': total_alerts,
            'type_stats': type_stats,
            'severity_stats': severity_stats,
            'status_stats': status_stats
        }

    @staticmethod
    def get_alert_trend(days=7):
        """获取告警趋势（最近N天）"""
        end_date = datetime.now(timezone.utc).replace(tzinfo=None)
        start_date = end_date - timedelta(days=days)

        # 按天分组统计
        results = db.session.query(
            func.date(AlertEvent.occurred_time).label('date'),
            func.count(AlertEvent.id).label('count')
        ).filter(
            AlertEvent.occurred_time >= start_date,
            AlertEvent.occurred_time <= end_date
        ).group_by(func.date(AlertEvent.occurred_time)).all()

        # 构建完整的日期序列
        trend = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).date()
            count = 0
            for result in results:
                if result.date == date:
                    count = result.count
                    break
            trend.append({
                'date': date.isoformat(),
                'count': count
            })

        return trend

    @staticmethod
    def get_dashboard_overview(start_date=None, end_date=None):
        """获取看板总览"""
        flight_stats = DashboardService.get_flight_statistics(start_date, end_date)
        airspace_stats = DashboardService.get_airspace_usage_statistics(start_date, end_date)
        alert_stats = DashboardService.get_alert_statistics(start_date, end_date)
        alert_trend = DashboardService.get_alert_trend()

        return {
            'flight_statistics': flight_stats,
            'airspace_usage': airspace_stats,
            'alert_statistics': alert_stats,
            'alert_trend': alert_trend
        }

