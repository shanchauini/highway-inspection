# 公路巡检飞行管理系统 - 后端

## 项目简介

这是公路巡检飞行管理系统的后端服务，采用 Flask 框架开发，提供 RESTful API 接口。

## 技术栈

- **框架**: Flask 3.0
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **认证**: JWT (Flask-JWT-Extended)
- **数据验证**: Marshmallow
- **跨域**: Flask-CORS
- **数据库迁移**: Flask-Migrate

## 项目结构

```
highway-inspection-backend/
├── app/
│   ├── __init__.py              # Flask应用初始化
│   ├── models/                  # 数据模型
│   │   ├── user.py              # 用户模型
│   │   ├── airspace.py          # 空域模型
│   │   ├── flight_application.py # 飞行申请模型
│   │   ├── mission.py           # 飞行任务模型
│   │   ├── video.py             # 视频模型
│   │   ├── analysis_result.py   # 分析结果模型
│   │   └── alert.py             # 告警模型
│   ├── routes/                  # 路由（API接口）
│   │   ├── auth.py              # 认证接口
│   │   ├── users.py             # 用户管理
│   │   ├── airspaces.py         # 空域管理
│   │   ├── flights.py           # 飞行申请
│   │   ├── missions.py          # 飞行任务
│   │   ├── videos.py            # 视频管理
│   │   ├── alerts.py            # 告警管理
│   │   └── dashboard.py         # 数据看板
│   ├── services/                # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── airspace_service.py
│   │   ├── flight_service.py
│   │   └── dashboard_service.py
│   ├── schemas/                 # 数据验证
│   └── utils/                   # 工具函数
├── config.py                    # 配置文件
├── run.py                       # 启动文件
├── requirements.txt             # 依赖清单
└── README.md                    # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- pip

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

1. 创建数据库：
```sql
CREATE DATABASE highway_inspection_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 导入数据库结构（执行提供的 SQL 文件）

3. 复制环境变量配置文件：
```bash
copy env.example .env  # Windows
cp env.example .env    # Linux/Mac
```

4. 编辑 `.env` 文件，修改数据库连接信息：
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=highway_inspection_system
```

### 4. 初始化数据库迁移

```bash
# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

### 5. 运行服务

```bash
python run.py
```

服务将在 `http://localhost:5000` 启动。

## API 文档

### 认证接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/login` | 用户登录 | 公开 |
| GET | `/api/auth/current` | 获取当前用户 | 登录 |
| POST | `/api/auth/logout` | 登出 | 登录 |

### 用户管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/users` | 获取用户列表 | 管理员 |
| GET | `/api/users/:id` | 获取用户详情 | 登录 |
| PUT | `/api/users/:id` | 更新用户信息 | 登录 |
| DELETE | `/api/users/:id` | 删除用户 | 管理员 |

### 空域管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/airspaces` | 获取空域列表 | 登录 |
| GET | `/api/airspaces/:id` | 获取空域详情 | 登录 |
| POST | `/api/airspaces` | 创建空域 | 管理员 |
| PUT | `/api/airspaces/:id` | 更新空域 | 管理员 |
| DELETE | `/api/airspaces/:id` | 删除空域 | 管理员 |
| GET | `/api/airspaces/available` | 获取可用空域 | 登录 |

### 飞行申请

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/flights` | 获取申请列表 | 登录 |
| GET | `/api/flights/:id` | 获取申请详情 | 登录 |
| POST | `/api/flights` | 创建申请 | 登录 |
| PUT | `/api/flights/:id` | 更新申请 | 操作员 |
| POST | `/api/flights/:id/submit` | 提交申请 | 操作员 |
| POST | `/api/flights/:id/approve` | 批准申请 | 管理员 |
| POST | `/api/flights/:id/reject` | 驳回申请 | 管理员 |
| POST | `/api/flights/:id/launch` | 放飞 | 操作员 |
| GET | `/api/flights/pending` | 待审批列表 | 管理员 |

### 飞行任务

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/missions` | 获取任务列表 | 登录 |
| GET | `/api/missions/:id` | 获取任务详情 | 登录 |
| GET | `/api/missions/active` | 获取进行中任务 | 登录 |
| POST | `/api/missions/:id/complete` | 完成任务 | 操作员 |

### 视频管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/videos` | 获取视频列表 | 登录 |
| GET | `/api/videos/:id` | 获取视频详情 | 登录 |
| POST | `/api/videos` | 上传视频 | 操作员 |
| GET | `/api/videos/:id/analysis-results` | 获取分析结果 | 登录 |

### 告警管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/alerts` | 获取告警列表 | 登录 |
| GET | `/api/alerts/:id` | 获取告警详情 | 登录 |
| POST | `/api/alerts` | 创建告警 | AI模块 |
| PUT | `/api/alerts/:id` | 更新告警状态 | 登录 |
| GET | `/api/alerts/active` | 获取活跃告警 | 登录 |

### 数据看板

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/dashboard/stats` | 获取总览统计 | 登录 |
| GET | `/api/dashboard/flight-stats` | 飞行统计 | 登录 |
| GET | `/api/dashboard/airspace-usage` | 空域使用统计 | 登录 |
| GET | `/api/dashboard/alert-stats` | 告警统计 | 登录 |
| GET | `/api/dashboard/alert-trend` | 告警趋势 | 登录 |

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "error message",
  "errors": {...}
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 开发指南

### 数据库迁移

```bash
# 生成迁移文件
flask db migrate -m "description"

# 执行迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 测试

使用 Postman、Apifox 或 curl 测试 API 接口。

示例：
```bash
# 注册用户
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"1234"}'

# 登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"1234"}'
```

## 常见问题

### 1. 数据库连接失败
- 检查 `.env` 文件中的数据库配置
- 确认 MySQL 服务已启动
- 确认数据库已创建

### 2. 导入错误
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查 Python 版本是否为 3.8+

### 3. 跨域问题
- 检查 `config.py` 中的 `CORS_ORIGINS` 配置
- 确保前端地址已添加到允许列表

## 与前端对接

前端项目位于 `highway-inspection-frontend/`，需要配置前端的 API 基础 URL：

在前端 `src/api/index.ts` 中：
```typescript
const baseURL = 'http://localhost:5000/api'
```

## 与 AI 模块对接

AI 模块需要调用以下接口：

1. **提交分析结果**: `POST /api/analysis/results`
2. **创建告警**: `POST /api/alerts`

这些接口无需认证，供内部 AI 服务调用。

## 部署

### 生产环境配置

1. 修改 `.env` 文件：
```
FLASK_ENV=production
SECRET_KEY=强随机密钥
JWT_SECRET_KEY=强随机密钥
```

2. 使用 Gunicorn 运行：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 作者

软件工程课程设计小组

## 许可

MIT License

