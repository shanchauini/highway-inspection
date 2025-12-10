# 公路巡检飞行管理系统 - 后端

## 📋 项目简介

公路巡检飞行管理系统的后端服务，采用 Flask 框架开发，提供 RESTful API 接口。

## 🛠️ 技术栈

- **框架**: Flask 3.0
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **认证**: JWT (Flask-JWT-Extended)
- **数据验证**: Marshmallow
- **AI 模块**: Ultralytics YOLOv8

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- pip

### 2. 安装步骤

```bash
# 进入项目目录
cd highway-inspection-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE highway_inspection_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 复制环境变量文件：
```bash
copy env.example .env  # Windows
cp env.example .env    # Linux/Mac
```

3. 编辑 `.env` 文件，配置数据库连接：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=highway_inspection_system
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

### 4. 运行服务

```bash
python run.py
```

服务将在 `http://localhost:3000` 启动。

## 📁 项目结构

```
highway-inspection-backend/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # API 路由
│   ├── services/        # 业务逻辑
│   ├── schemas/         # 数据验证
│   └── utils/           # 工具函数
├── ai/                  # AI 模块
│   ├── models/          # 模型文件
│   ├── scripts/         # 训练和推理脚本
│   └── data/            # 数据文件
├── config.py            # 配置文件
├── run.py               # 启动文件
└── requirements.txt     # 依赖清单
```

详细结构说明请参考 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 📡 API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/current` - 获取当前用户

### 核心功能
- **用户管理**: `/api/users`
- **空域管理**: `/api/airspaces`
- **飞行申请**: `/api/flights`
- **飞行任务**: `/api/missions`
- **视频管理**: `/api/videos`
- **告警管理**: `/api/alerts`
- **数据看板**: `/api/dashboard`
- **AI 接口**: `/api/ai`

完整 API 文档请参考前端项目的 `API_REFERENCE.md`

## 🤖 AI 模块

项目集成了 YOLOv8 图像分类功能，用于视频分析。

- **模型位置**: `ai/models/`
- **训练脚本**: `ai/scripts/train.py`
- **推理脚本**: `ai/scripts/inference.py`

详细说明请参考 [ai/README.md](./ai/README.md) 和 [AI_MODULE_MIGRATION.md](./AI_MODULE_MIGRATION.md)

## 🔧 开发指南

### 数据库迁移

```bash
flask db init
flask db migrate -m "description"
flask db upgrade
```

### 测试 API

```bash
# 登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## ❓ 常见问题

1. **数据库连接失败**: 检查 `.env` 配置和 MySQL 服务状态
2. **依赖安装失败**: 使用国内镜像 `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. **CORS 错误**: 检查 `config.py` 中的 `CORS_ORIGINS` 配置

## 📚 相关文档

- [项目结构说明](./PROJECT_STRUCTURE.md)
- [AI 模块迁移指南](./AI_MODULE_MIGRATION.md)
- [AI 模块使用说明](./ai/README.md)

## 📝 License

MIT License
