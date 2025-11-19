"""
数据库初始化脚本
用于创建测试数据
"""
from datetime import datetime, timedelta
from app import create_app
from app.models import db, User, Airspace, FlightApplication, Mission, Video, AlertEvent

app = create_app()


def init_test_data():
    """初始化测试数据"""
    with app.app_context():
        print("正在初始化测试数据...")

        # 清空现有数据（谨慎使用！）
        # db.drop_all()
        # db.create_all()

        # 创建测试用户
        print("创建测试用户...")
        
        # 管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("  - 创建管理员: admin / admin123")

        # 操作员1
        op1 = User.query.filter_by(username='operator1').first()
        if not op1:
            op1 = User(username='operator1', role='operator')
            op1.set_password('op123')
            db.session.add(op1)
            print("  - 创建操作员1: operator1 / op123")

        # 操作员2
        op2 = User.query.filter_by(username='operator2').first()
        if not op2:
            op2 = User(username='operator2', role='operator')
            op2.set_password('op123')
            db.session.add(op2)
            print("  - 创建操作员2: operator2 / op123")

        db.session.commit()

        # 创建测试空域
        print("创建测试空域...")
        
        if Airspace.query.count() == 0:
            airspaces = [
                Airspace(
                    name='京港澳高速适飞区A',
                    number='AS001',
                    type='suitable',
                    area={
                        "type": "Polygon",
                        "coordinates": [[[116.39, 39.90], [116.41, 39.90], [116.41, 39.92], [116.39, 39.92], [116.39, 39.90]]]
                    },
                    remark='主要巡检区域A',
                    status='available'
                ),
                Airspace(
                    name='京港澳高速适飞区B',
                    number='AS002',
                    type='suitable',
                    area={
                        "type": "Polygon",
                        "coordinates": [[[116.42, 39.90], [116.44, 39.90], [116.44, 39.92], [116.42, 39.92], [116.42, 39.90]]]
                    },
                    remark='主要巡检区域B',
                    status='available'
                ),
                Airspace(
                    name='限制区域C',
                    number='AS003',
                    type='restricted',
                    area={
                        "type": "Polygon",
                        "coordinates": [[[116.45, 39.90], [116.47, 39.90], [116.47, 39.92], [116.45, 39.92], [116.45, 39.90]]]
                    },
                    remark='特殊时段限制',
                    status='available'
                ),
                Airspace(
                    name='军事禁飞区',
                    number='AS004',
                    type='no_fly',
                    area={
                        "type": "Polygon",
                        "coordinates": [[[116.48, 39.90], [116.50, 39.90], [116.50, 39.92], [116.48, 39.92], [116.48, 39.90]]]
                    },
                    remark='军事区域，禁止飞行',
                    status='unavailable'
                )
            ]
            
            for airspace in airspaces:
                db.session.add(airspace)
                print(f"  - 创建空域: {airspace.number} - {airspace.name}")
            
            db.session.commit()

        # 创建测试飞行申请
        print("创建测试飞行申请...")
        
        if FlightApplication.query.count() <= 1:  # 只保留SQL中的初始数据
            op1 = User.query.filter_by(username='operator1').first()
            airspace1 = Airspace.query.filter_by(number='AS001').first()
            
            if op1 and airspace1:
                # 已批准的申请
                app1 = FlightApplication(
                    user_id=op1.id,
                    drone_model='DJI Mavic 3 Pro',
                    task_purpose='G4高速K10-K20段日常巡检',
                    planned_airspace_id=airspace1.id,
                    planned_start_time=datetime.utcnow() + timedelta(hours=2),
                    planned_end_time=datetime.utcnow() + timedelta(hours=4),
                    total_time=120,
                    route={
                        "type": "LineString",
                        "coordinates": [[116.3974, 39.9093], [116.4074, 39.9193], [116.4174, 39.9293]]
                    },
                    status='approved',
                    is_long_term=False
                )
                db.session.add(app1)
                print("  - 创建已批准申请")

                # 待审批的申请
                app2 = FlightApplication(
                    user_id=op1.id,
                    drone_model='DJI Phantom 4 RTK',
                    task_purpose='G4高速K20-K30段应急巡检',
                    planned_airspace_id=airspace1.id,
                    planned_start_time=datetime.utcnow() + timedelta(days=1),
                    planned_end_time=datetime.utcnow() + timedelta(days=1, hours=2),
                    total_time=120,
                    route={
                        "type": "LineString",
                        "coordinates": [[116.4074, 39.9193], [116.4174, 39.9293], [116.4274, 39.9393]]
                    },
                    status='pending',
                    is_long_term=False
                )
                db.session.add(app2)
                print("  - 创建待审批申请")

                db.session.commit()

        print("测试数据初始化完成！")
        print("\n可用的测试账号：")
        print("  管理员: admin / admin123")
        print("  操作员1: operator1 / op123")
        print("  操作员2: operator2 / op123")


if __name__ == '__main__':
    init_test_data()

