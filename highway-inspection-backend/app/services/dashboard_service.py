from datetime import datetime, timedelta, timezone
from sqlalchemy import func, text
from app.models import db, Mission, AirspaceUsage, Airspace, AnalysisResult, AlertEvent, Video


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
        # 统计总飞行距离（公里）
        total_distance = 0
        for mission in missions:
            if mission.start_time and mission.end_time:
                duration = (mission.end_time - mission.start_time).total_seconds() / 3600
                total_duration += duration
            
            # 累加每个任务的飞行距离
            total_distance += mission.calculate_route_distance()

        return {
            'total_missions': total_missions,
            'total_duration': round(total_duration, 2),
            'total_distance': round(total_distance, 2),
            #'average_duration': round(total_duration / total_missions, 2) if total_missions > 0 else 0
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

    #ai检测结果现存储在analysis_results表中，此功能暂不需用
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
        """获取巡检成果统计（按类型分组）"""

        # 查询交通拥堵类型的结果
        traffic_query = db.session.query(
            AnalysisResult.target_type,
            func.count(AnalysisResult.id).label('total_count')
        ).filter(AnalysisResult.target_type.contains('('))  # 交通拥堵类型包含括号

        # 查询道路破损类型的结果
        damage_query = db.session.query(
            AnalysisResult.target_type,
            func.count(AnalysisResult.id).label('total_count')
        ).filter(~AnalysisResult.target_type.contains('('))  # 道路破损类型不包含括号

        if start_date:
            traffic_query = traffic_query.filter(AnalysisResult.occurred_time >= start_date)
            damage_query = damage_query.filter(AnalysisResult.occurred_time >= start_date)
        if end_date:
            traffic_query = traffic_query.filter(AnalysisResult.occurred_time <= end_date)
            damage_query = damage_query.filter(AnalysisResult.occurred_time <= end_date)

        # 按类型分组统计总数
        traffic_results = traffic_query.group_by(AnalysisResult.target_type).all()
        damage_results = damage_query.group_by(AnalysisResult.target_type).all()

        # 构建返回数据
        categories = []
        found = []

        # 添加交通拥堵类型统计
        for target_type, count in traffic_results:
            categories.append(f'交通拥堵-{target_type}')
            found.append(count)

        # 添加道路破损类型统计
        for target_type, count in damage_results:
            categories.append(f'道路破损-{target_type}')
            found.append(count)

        return {
            'categories': categories,
            'found': found,
            'resolved': [0] * len(categories)  # 简化处理，暂不区分已处理和未处理
        }

    @staticmethod
    def get_inspection_results_statistics(start_date=None, end_date=None):
        """获取巡检结果统计"""
        query = AnalysisResult.query

        if start_date:
            query = query.filter(AnalysisResult.occurred_time >= start_date)
        if end_date:
            query = query.filter(AnalysisResult.occurred_time <= end_date)

        results = query.all()

        # 总巡检结果数
        total_results = len(results)

        # 按事件类型统计
        traffic_congestion_count = 0
        road_damage_count = 0
        
        # 拥堵程度统计
        congestion_stats = {
            '轻度 (light)': 0,
            '中度 (medium)': 0,
            '重度 (heavy)': 0
        }
        
        # 破损程度统计
        damage_stats = {
            '无破损': 0,
            '轻度破损': 0,
            '中度破损': 0,
            '严重破损': 0
        }

        for result in results:
            # 根据target_type判断事件类型
            if '(' in result.target_type:
                traffic_congestion_count += 1
                # 统计拥堵程度
                if result.target_type in congestion_stats:
                    congestion_stats[result.target_type] += 1
            else:
                road_damage_count += 1
                # 统计破损程度
                if result.target_type in damage_stats:
                    damage_stats[result.target_type] += 1

        return {
            'total_results': total_results,
            'traffic_congestion_count': traffic_congestion_count,
            'road_damage_count': road_damage_count,
            'congestion_stats': congestion_stats,
            'damage_stats': damage_stats
        }

    @staticmethod
    def get_inspection_results_trend(start_date=None, end_date=None):
        """获取巡检结果趋势"""
        # 默认显示最近30天
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=29)  # 30天包括今天
            
        days = (end_date - start_date).days + 1

        # 按天分组统计
        results = db.session.query(
            func.date(AnalysisResult.occurred_time).label('date'),
            func.count(AnalysisResult.id).label('count')
        ).filter(
            AnalysisResult.occurred_time >= start_date,
            AnalysisResult.occurred_time <= end_date
        ).group_by(func.date(AnalysisResult.occurred_time)).all()

        # 构建完整的日期序列
        trend = []
        result_dict = {result.date: result.count for result in results}
        
        for i in range(days):
            date = (start_date + timedelta(days=i)).date()
            count = result_dict.get(date, 0)
            trend.append({
                'date': date.isoformat(),
                'count': count
            })

        return trend

    @staticmethod
    def get_problem_sections(start_date=None, end_date=None):
        """获取高频问题路段统计"""
        # 按路段分组并统计数量
        query = db.session.query(
            Video.road_section,
            func.count(AnalysisResult.id).label('count')
        ).join(
            AnalysisResult, Video.id == AnalysisResult.video_id
        )
        
        if start_date:
            query = query.filter(AnalysisResult.occurred_time >= start_date)
        if end_date:
            query = query.filter(AnalysisResult.occurred_time <= end_date)
            
        query = query.group_by(Video.road_section).order_by(func.count(AnalysisResult.id).desc()).limit(10)
        
        section_results = query.all()
        
        # 提取路段和数量
        sections = [row.road_section for row in section_results]
        counts = [int(row.count) for row in section_results]
        
        return {
            'sections': sections,
            'counts': counts
        }

    @staticmethod
    def get_inspection_type_distribution(start_date=None, end_date=None):
        """获取巡检结果类型分布"""
        query = AnalysisResult.query

        if start_date:
            query = query.filter(AnalysisResult.occurred_time >= start_date)
        if end_date:
            query = query.filter(AnalysisResult.occurred_time <= end_date)

        results = query.all()

        # 拥堵程度统计
        congestion_stats = {
            '轻度 (light)': 0,
            '中度 (medium)': 0,
            '重度 (heavy)': 0
        }
        
        # 破损程度统计
        damage_stats = {
            '无破损': 0,
            '轻度破损': 0,
            '中度破损': 0,
            '严重破损': 0
        }

        for result in results:
            # 根据target_type判断事件类型并统计
            if '(' in result.target_type:
                # 交通拥堵类型
                if result.target_type in congestion_stats:
                    congestion_stats[result.target_type] += 1
            else:
                # 道路破损类型
                if result.target_type in damage_stats:
                    damage_stats[result.target_type] += 1

        # 合并统计数据
        type_distribution = {}
        # 添加交通拥堵统计
        for level, count in congestion_stats.items():
            if count > 0:  # 只添加有数据的项
                type_distribution[f'交通拥堵-{level}'] = count
        
        # 添加道路破损统计
        for level, count in damage_stats.items():
            if count > 0:  # 只添加有数据的项
                type_distribution[f'道路破损-{level}'] = count

        return type_distribution

    @staticmethod
    def get_dashboard_overview(start_date=None, end_date=None):
        """获取看板总览"""
        flight_stats = DashboardService.get_flight_statistics(start_date, end_date)
        airspace_stats = DashboardService.get_airspace_usage_statistics(start_date, end_date)
        # 使用新的巡检结果统计替代告警统计
        inspection_stats = DashboardService.get_inspection_results_statistics(start_date, end_date)
        inspection_trend = DashboardService.get_inspection_results_trend(start_date=start_date, end_date=end_date)
        inspection_results = DashboardService.get_inspection_results(start_date, end_date)
        problem_sections = DashboardService.get_problem_sections(start_date, end_date)

        return {
            'flight_statistics': flight_stats,
            'airspace_usage': airspace_stats,
            'inspection_statistics': inspection_stats,  
            'inspection_trend': inspection_trend,
            'inspection_results': inspection_results,
            'problem_sections': problem_sections
        }