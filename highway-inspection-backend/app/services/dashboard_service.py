from datetime import datetime, timedelta, timezone
from sqlalchemy import func, text
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
    def get_flight_trend(days=30, start_date=None, end_date=None):
        """获取飞行任务趋势"""

        if start_date and end_date:
            days_count = (end_date - start_date).days + 1
        else:
            end_date = datetime.now().date()  # 结束日期是今天
            start_date = end_date - timedelta(days=29)  # 开始日期是30天前
            days_count = 30


        sql_query = text("""
                SELECT 
                    DATE(start_time) as flight_date,
                    COUNT(id) as mission_count,
                    SUM(TIMESTAMPDIFF(SECOND, start_time, end_time)) / 3600 as flight_hours
                FROM missions 
                WHERE status = 'completed' 
                  AND DATE(start_time) >= :start_date 
                  AND DATE(start_time) <= :end_date 
                GROUP BY DATE(start_time)
                ORDER BY flight_date
            """)



        result = db.session.execute(sql_query, {
            'start_date': start_date,
            'end_date': end_date
        })


        database_rows = result.fetchall()


        dates_list = []  # 存储日期
        counts_list = []  # 存储任务数量
        hours_list = []  # 存储飞行时长

        # 将数据库结果按日期存储
        database_data = {}
        for row in database_rows:
            date_str = row.flight_date.isoformat()
            database_data[date_str] = {
                'count': row.mission_count,
                'hours': row.flight_hours if row.flight_hours else 0.0
            }


        # 循环处理每一天，填充三个列表
        for day_index in range(days_count):
            # 计算当前要处理的日期
            current_date = start_date + timedelta(days=day_index)
            date_str = current_date.strftime("%Y-%m-%d")  #注意格式！此时字典里的key是date字符串而不是datetime


            if date_str in database_data:
                # 如果有数据，使用数据库中的数据
                day_data = database_data[date_str]
                day_mission_count = day_data['count']
                day_flight_hours = day_data['hours']
            else:
                # 如果没有数据，使用默认值
                day_mission_count = 0
                day_flight_hours = 0.0


            dates_list.append(date_str)
            counts_list.append(day_mission_count)
            hours_list.append(round(day_flight_hours, 2))

        data = {
            'dates': dates_list,
            'counts': counts_list,
            'hours': hours_list
        }

        return data



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
        #因视频处理未完成，此功能暂未完善
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
    def get_alert_trend(days=None, start_date=None, end_date=None):
        """获取告警趋势（最近N天）"""
        # 如果提供了开始和结束日期，则使用它们而不是天数
        if start_date and end_date:
            # 计算天数
            days = (end_date - start_date).days + 1
        elif days:
            #基于天数计算
            end_date = datetime.now(timezone.utc).replace(tzinfo=None)
            start_date = end_date - timedelta(days=days)
        else:
            # 默认显示最近30天
            days = 30
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
    def get_inspection_results(start_date=None, end_date=None):
        """获取巡检成果统计"""

        query = db.session.query(
            AlertEvent.event_type,
            func.count(AlertEvent.id).label('total_count')
        )

        if start_date:
            query = query.filter(AlertEvent.occurred_time >= start_date)
        if end_date:
            query = query.filter(AlertEvent.occurred_time <= end_date)

        # 按类型分组统计总数
        type_results = query.group_by(AlertEvent.event_type).all()

        # 按类型分组统计已解决的数量
        resolved_results = query.filter(
            AlertEvent.status == 'processing'  #或者是closed状态的告警
        ).group_by(AlertEvent.event_type).all()

        # 转换为字典便于查找
        type_dict = {event_type: count for event_type, count in type_results}
        resolved_dict = {event_type: count for event_type, count in resolved_results}

        # 构建返回数据
        categories = []
        found = []
        resolved = []

        for event_type, count in type_results:
            categories.append(event_type)
            found.append(count)
            resolved.append(resolved_dict.get(event_type, 0))

        return {
            'categories': categories,
            'found': found,
            'resolved': resolved
        }

    @staticmethod
    def get_problem_sections(start_date=None, end_date=None):
        """获取高频问题路段"""
        # 查询告警事件中的路段统计数据
        query = db.session.query(
            AlertEvent.road_section,
            func.count(AlertEvent.id).label('event_count')
        )
        

        if start_date:
            query = query.filter(AlertEvent.occurred_time >= start_date)
        if end_date:
            query = query.filter(AlertEvent.occurred_time <= end_date)
            
        # 按路段分组并统计事件数量
        query = query.group_by(AlertEvent.road_section).order_by(func.count(AlertEvent.id).desc()) .limit(10)  # 获取前10个高频路段
        
        results = query.all()
        
        # 提取路段名称和事件数量
        sections = [row.road_section for row in results]
        counts = [row.event_count for row in results]
        
        return {
            'sections': sections,
            'counts': counts
        }

    @staticmethod
    def get_dashboard_overview(start_date=None, end_date=None):
        """获取看板总览"""
        flight_stats = DashboardService.get_flight_statistics(start_date, end_date)
        airspace_stats = DashboardService.get_airspace_usage_statistics(start_date, end_date)
        alert_stats = DashboardService.get_alert_statistics(start_date, end_date)
        alert_trend = DashboardService.get_alert_trend(start_date=start_date, end_date=end_date)
        inspection_results = DashboardService.get_inspection_results(start_date, end_date)
        problem_sections = DashboardService.get_problem_sections(start_date, end_date)

        return {
            'flight_statistics': flight_stats,
            'airspace_usage': airspace_stats,
            'alert_statistics': alert_stats,
            'alert_trend': alert_trend,
            'inspection_results': inspection_results,
            'problem_sections': problem_sections
        }