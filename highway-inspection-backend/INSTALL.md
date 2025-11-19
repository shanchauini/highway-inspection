# 后端安装与运行指南

## 一、环境准备

### 1. 安装 Python
确保已安装 Python 3.8 或更高版本。

检查版本：
```bash
python --version
```

### 2. 安装 MySQL
确保已安装 MySQL 8.0 或更高版本，并启动服务。

## 二、项目设置

### 1. 进入项目目录
```bash
cd highway-inspection-backend
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
```

### 3. 激活虚拟环境

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

如果安装速度较慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 三、数据库配置

### 1. 创建数据库

在 MySQL 中执行以下命令：
```sql
CREATE DATABASE highway_inspection_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 导入数据库结构

执行项目提供的 SQL 文件（假设文件名为 `database.sql`）：

**方法1：使用命令行**
```bash
mysql -u root -p highway_inspection_system < database.sql
```

**方法2：使用 MySQL Workbench 或其他GUI工具**
- 打开 SQL 文件
- 连接到数据库
- 执行 SQL 脚本

### 3. 配置环境变量

复制环境变量模板文件：
```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

编辑 `.env` 文件，修改以下配置：
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=highway_inspection_system

SECRET_KEY=请修改为随机字符串
JWT_SECRET_KEY=请修改为随机字符串
```

## 四、初始化数据库迁移（可选）

如果需要使用数据库迁移功能：

```bash
# 设置Flask应用
set FLASK_APP=run.py  # Windows CMD
$env:FLASK_APP="run.py"  # Windows PowerShell
export FLASK_APP=run.py  # Linux/Mac

# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

## 五、运行服务

### 开发模式运行

```bash
python run.py
```

服务将在 `http://localhost:5000` 启动。

### 查看服务状态

浏览器访问：
- `http://localhost:5000/` - 查看API信息
- `http://localhost:5000/health` - 健康检查

## 六、测试接口

### 使用 curl 测试

**1. 注册用户：**
```bash
curl -X POST http://localhost:5000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"test\",\"password\":\"1234\"}"
```

**2. 登录：**
```bash
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"test\",\"password\":\"1234\"}"
```

返回的 `access_token` 用于后续请求。

**3. 获取当前用户（需要 token）：**
```bash
curl -X GET http://localhost:5000/api/auth/current ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 使用 Postman 或 Apifox 测试

推荐使用图形化工具测试 API：
1. 导入 API 文档（参考 README.md）
2. 设置 Base URL 为 `http://localhost:5000`
3. 登录后获取 token
4. 在请求头中添加 `Authorization: Bearer <token>`

## 七、常见问题

### 1. ModuleNotFoundError

**问题：** 找不到某个模块

**解决：**
```bash
# 确保虚拟环境已激活
# 重新安装依赖
pip install -r requirements.txt
```

### 2. 数据库连接失败

**问题：** `Access denied for user` 或 `Can't connect to MySQL server`

**解决：**
- 检查 `.env` 文件中的数据库配置
- 确认 MySQL 服务已启动
- 确认用户名和密码正确
- 确认数据库已创建

### 3. 端口被占用

**问题：** `Address already in use`

**解决：**
- 修改 `.env` 文件中的 `PORT` 配置
- 或关闭占用 5000 端口的其他程序

### 4. CORS 错误

**问题：** 前端请求被拦截

**解决：**
- 检查 `config.py` 中的 `CORS_ORIGINS` 配置
- 添加前端地址到允许列表

### 5. JWT 认证失败

**问题：** `Token has expired` 或 `Invalid token`

**解决：**
- 重新登录获取新 token
- 检查 token 是否正确携带在请求头中

## 八、PyCharm 配置

### 1. 打开项目
- File → Open → 选择 `highway-inspection-backend` 目录

### 2. 配置解释器
- File → Settings → Project → Python Interpreter
- 点击齿轮图标 → Add
- 选择 Existing environment
- 选择虚拟环境中的 python.exe

### 3. 配置运行
- Run → Edit Configurations
- 点击 + → Python
- Script path: 选择 `run.py`
- 确保 Python interpreter 选择正确

### 4. 运行项目
- 点击绿色运行按钮
- 或按 Shift + F10

## 九、下一步

安装完成后，可以：
1. 阅读 `README.md` 了解详细的 API 文档
2. 配置前端项目连接后端
3. 开始开发和测试

## 十、联系与支持

如有问题，请联系项目组成员。

