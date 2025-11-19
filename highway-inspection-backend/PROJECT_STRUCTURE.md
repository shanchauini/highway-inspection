# 项目结构说明

## 目录树

```
highway-inspection-backend/
│
├── app/                          # 应用主目录
│   ├── __init__.py              # Flask应用工厂函数
│   │
│   ├── models/                  # 数据模型层（ORM）
│   │   ├── __init__.py         # 模型初始化，导出所有模型
│   │   ├── user.py             # 用户模型（认证、角色管理）
│   │   ├── airspace.py         # 空域模型、空域使用记录
│   │   ├── flight_application.py # 飞行申请模型
│   │   ├── mission.py          # 飞行任务模型
│   │   ├── video.py            # 视频模型
│   │   ├── analysis_result.py  # AI分析结果模型
│   │   └── alert.py            # 告警事件模型
│   │
│   ├── routes/                  # 路由层（API接口定义）
│   │   ├── __init__.py         # 路由注册
│   │   ├── auth.py             # 认证接口（登录、注册）
│   │   ├── users.py            # 用户管理接口
│   │   ├── airspaces.py        # 空域管理接口
│   │   ├── flights.py          # 飞行申请接口
│   │   ├── missions.py         # 飞行任务接口
│   │   ├── videos.py           # 视频管理接口
│   │   ├── alerts.py           # 告警管理接口
│   │   ├── dashboard.py        # 数据看板接口
│   │   └── ai_interface.py     # AI模块对接接口
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证业务逻辑
│   │   ├── airspace_service.py # 空域业务逻辑（冲突检测等）
│   │   ├── flight_service.py   # 飞行申请业务逻辑
│   │   └── dashboard_service.py # 数据统计业务逻辑
│   │
│   ├── schemas/                 # 数据验证和序列化
│   │   ├── __init__.py
│   │   ├── user_schema.py      # 用户数据验证
│   │   ├── airspace_schema.py  # 空域数据验证
│   │   ├── flight_schema.py    # 飞行申请数据验证
│   │   ├── video_schema.py     # 视频数据验证
│   │   └── alert_schema.py     # 告警数据验证
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── response.py         # 统一响应格式
│       └── decorators.py       # 权限装饰器
│
├── migrations/                  # 数据库迁移文件（Flask-Migrate生成）
│
├── uploads/                     # 文件上传目录
│   └── videos/                 # 视频文件存储
│
├── config.py                    # 配置文件（多环境配置）
├── run.py                       # 应用启动入口
├── requirements.txt             # Python依赖清单
│
├── .env                        # 环境变量（数据库密码等敏感信息）
├── .env.example / env.example  # 环境变量模板
├── .flaskenv                   # Flask环境配置
├── .gitignore                  # Git忽略文件
│
├── start.bat                   # Windows启动脚本
├── start.sh                    # Linux/Mac启动脚本
│
├── README.md                   # 项目说明文档
├── INSTALL.md                  # 安装指南
└── PROJECT_STRUCTURE.md        # 本文件（项目结构说明）
```

## 分层架构说明

本项目采用经典的 **MVC + Service** 分层架构：

### 1. Models 层（数据模型）
- **职责**: 定义数据库表结构，提供数据操作的基础方法
- **技术**: SQLAlchemy ORM
- **文件位置**: `app/models/`

### 2. Routes 层（路由/控制器）
- **职责**: 接收HTTP请求，验证参数，调用Service层，返回响应
- **技术**: Flask Blueprint
- **文件位置**: `app/routes/`

### 3. Services 层（业务逻辑）
- **职责**: 实现核心业务逻辑，处理复杂的数据操作
- **技术**: 纯Python类和函数
- **文件位置**: `app/services/`

### 4. Schemas 层（数据验证）
- **职责**: 定义数据验证规则，序列化和反序列化
- **技术**: Marshmallow
- **文件位置**: `app/schemas/`

### 5. Utils 层（工具函数）
- **职责**: 提供通用的辅助函数和装饰器
- **技术**: Python函数和装饰器
- **文件位置**: `app/utils/`

## 数据流向

```
客户端请求
    ↓
Routes（接收请求，参数验证）
    ↓
Services（业务逻辑处理）
    ↓
Models（数据库操作）
    ↓
数据库
    ↓
Models（返回数据）
    ↓
Services（数据处理）
    ↓
Routes（响应格式化）
    ↓
客户端响应
```

## 主要模块说明

### 认证模块 (auth)
- **登录**: 验证用户名密码，返回JWT token
- **注册**: 创建新用户（操作员可自行注册）
- **权限控制**: 通过装饰器实现角色权限验证

### 空域管理模块 (airspaces)
- **CRUD操作**: 创建、读取、更新、删除空域
- **冲突检测**: 检查时间和空间上的空域冲突
- **状态管理**: 跟踪空域占用状态

### 飞行申请模块 (flights)
- **申请流程**: 草稿 → 提交 → 审批 → 批准/驳回
- **放飞检查**: 验证时间、空域、设备等条件
- **状态跟踪**: 记录申请的完整生命周期

### 任务管理模块 (missions)
- **任务执行**: 记录飞行任务的实时状态
- **地图显示**: 提供活跃任务数据供前端展示
- **任务完成**: 更新任务状态，释放空域

### 视频管理模块 (videos)
- **视频上传**: 记录视频元数据
- **分析结果**: 关联AI分析结果
- **查询检索**: 按任务、时间等条件查询

### 告警管理模块 (alerts)
- **告警创建**: 由AI模块自动创建
- **状态管理**: 新发现 → 已确认 → 处理中 → 已关闭
- **实时监控**: 提供活跃告警列表

### 数据看板模块 (dashboard)
- **飞行统计**: 任务次数、总时长等
- **空域使用**: 各空域使用频率和时长
- **告警统计**: 告警类型、严重程度分布
- **趋势分析**: 告警趋势图表

### AI接口模块 (ai_interface)
- **分析结果接收**: 接收AI模块推送的分析结果
- **批量提交**: 支持批量提交分析结果
- **无需认证**: 供内部AI服务调用

## 数据库关系

```
users (用户)
  ├─→ flight_applications (飞行申请)
  │     ├─→ airspace_usage (空域使用记录)
  │     └─→ missions (飞行任务)
  │           ├─→ videos (视频)
  │           │     ├─→ analysis_results (分析结果)
  │           │     └─→ alert_events (告警事件)
  │           ├─→ analysis_results
  │           └─→ alert_events
  └─→ missions

airspaces (空域)
  ├─→ flight_applications
  └─→ airspace_usage
```

## 配置说明

### config.py
- **DevelopmentConfig**: 开发环境配置（调试开启）
- **ProductionConfig**: 生产环境配置（优化性能）
- **TestingConfig**: 测试环境配置（内存数据库）

### .env
存储敏感信息：
- 数据库连接信息
- JWT密钥
- 其他密钥和配置

## API设计原则

1. **RESTful风格**: 使用标准HTTP方法（GET、POST、PUT、DELETE）
2. **统一响应格式**: 成功/错误响应格式一致
3. **JWT认证**: 无状态认证，支持前后端分离
4. **权限控制**: 基于角色的访问控制（RBAC）
5. **分页支持**: 列表接口支持分页查询

## 扩展指南

### 添加新模块
1. 在 `models/` 创建模型
2. 在 `schemas/` 创建验证规则
3. 在 `services/` 创建业务逻辑
4. 在 `routes/` 创建API接口
5. 在 `routes/__init__.py` 注册蓝图

### 添加新接口
1. 在对应的 `routes/*.py` 文件中添加路由函数
2. 使用装饰器控制权限（@login_required, @admin_required）
3. 调用 Service 层处理业务逻辑
4. 返回统一格式的响应

## 开发建议

1. **遵循分层**: 不要跨层调用（如Route直接操作Model）
2. **错误处理**: 使用try-except捕获异常
3. **日志记录**: 记录关键操作和错误信息
4. **代码注释**: 为复杂逻辑添加注释
5. **测试**: 编写单元测试和集成测试

## 性能优化

1. **数据库索引**: 已在关键字段添加索引
2. **查询优化**: 使用 `lazy='dynamic'` 延迟加载
3. **分页查询**: 避免一次性加载大量数据
4. **缓存**: 可考虑添加Redis缓存热点数据
5. **异步任务**: 使用定时任务处理后台作业

## 安全考虑

1. **密码加密**: 使用 werkzeug 的密码哈希
2. **JWT认证**: 有时效的token认证
3. **SQL注入防护**: 使用ORM自动参数化
4. **XSS防护**: 输入验证和输出转义
5. **CORS配置**: 仅允许可信域名跨域访问

