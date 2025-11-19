import os
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  Highway Inspection System Backend                      ║
    ║  公路巡检飞行管理系统 - 后端服务                          ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Server running on: http://{host}:{port}              ║
    ║  Environment: {os.getenv('FLASK_ENV', 'development')}                                      ║
    ║  Press CTRL+C to quit                                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)

