# 部署指南

## 开发环境部署

参见 `INSTALL.md` 文件。

## 生产环境部署

### 方案一：使用 Gunicorn（推荐）

#### 1. 安装 Gunicorn
```bash
pip install gunicorn
```

#### 2. 修改生产环境配置

编辑 `.env` 文件：
```
FLASK_ENV=production
SECRET_KEY=生成一个强随机密钥
JWT_SECRET_KEY=生成另一个强随机密钥
```

生成密钥方法：
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### 3. 启动服务
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

参数说明：
- `-w 4`: 4个工作进程
- `-b 0.0.0.0:5000`: 绑定地址和端口
- `run:app`: 模块名:应用对象

#### 4. 使用配置文件（推荐）

创建 `gunicorn_config.py`：
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
```

启动：
```bash
gunicorn -c gunicorn_config.py run:app
```

### 方案二：使用 Systemd 守护进程

#### 1. 创建服务文件

创建 `/etc/systemd/system/highway-inspection.service`：
```ini
[Unit]
Description=Highway Inspection Backend
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/highway-inspection-backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 2. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl start highway-inspection
sudo systemctl enable highway-inspection
sudo systemctl status highway-inspection
```

### 方案三：使用 Nginx + Gunicorn

#### 1. 安装 Nginx
```bash
sudo apt update
sudo apt install nginx
```

#### 2. 配置 Nginx

创建 `/etc/nginx/sites-available/highway-inspection`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/highway-inspection-backend/static;
    }

    location /uploads {
        alias /path/to/highway-inspection-backend/uploads;
    }
}
```

#### 3. 启用站点
```bash
sudo ln -s /etc/nginx/sites-available/highway-inspection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. 启动后端
```bash
gunicorn -w 4 -b 127.0.0.1:5000 run:app
```

### 方案四：使用 Docker（推荐用于容器化部署）

#### 1. 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads/videos

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASSWORD=your_password
      - DB_NAME=highway_inspection_system
    depends_on:
      - mysql
    volumes:
      - ./uploads:/app/uploads

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=your_password
      - MYSQL_DATABASE=highway_inspection_system
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

#### 3. 构建和运行
```bash
docker-compose up -d
```

## 数据库迁移

### 生产环境首次部署
```bash
# 导入数据库结构
mysql -u root -p highway_inspection_system < database.sql

# 或使用 Flask-Migrate
flask db upgrade
```

### 后续更新
```bash
# 备份数据库
mysqldump -u root -p highway_inspection_system > backup.sql

# 执行迁移
flask db upgrade
```

## 性能优化

### 1. 数据库优化
- 添加必要的索引
- 使用连接池
- 定期清理日志表

### 2. 应用优化
- 增加 Gunicorn worker 数量
- 使用 Redis 缓存热点数据
- 开启 gzip 压缩

### 3. 系统优化
- 增加系统文件描述符限制
- 调整数据库连接数
- 配置 Nginx 缓存

## 监控和日志

### 1. 应用日志
配置日志文件：
```python
import logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
```

### 2. 监控指标
- CPU 使用率
- 内存使用率
- 数据库连接数
- API 响应时间

### 3. 错误追踪
推荐使用：
- Sentry（错误追踪）
- Prometheus + Grafana（性能监控）

## 备份策略

### 数据库备份
```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
mysqldump -u root -p highway_inspection_system > backup_$DATE.sql
```

### 文件备份
- 定期备份 uploads/ 目录
- 定期备份配置文件

## 安全加固

### 1. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL/TLS 配置
使用 Let's Encrypt 获取免费证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 环境变量安全
- 不要将 .env 文件提交到版本控制
- 使用强随机密钥
- 定期更换密钥

### 4. 限流和防护
- 使用 Nginx 限制请求频率
- 配置 fail2ban 防止暴力破解
- 使用 WAF（Web应用防火墙）

## 故障排查

### 1. 服务无法启动
- 检查端口是否被占用
- 查看日志文件
- 验证配置文件

### 2. 数据库连接失败
- 检查数据库服务状态
- 验证连接信息
- 检查防火墙规则

### 3. 性能问题
- 查看系统资源使用
- 分析慢查询日志
- 检查数据库索引

## 更新部署

### 零停机更新（使用 Gunicorn）
```bash
# 拉取最新代码
git pull

# 安装新依赖
pip install -r requirements.txt

# 执行数据库迁移
flask db upgrade

# 平滑重启 Gunicorn
pkill -HUP gunicorn
```

### 使用 systemd 重启
```bash
sudo systemctl restart highway-inspection
```

## 回滚方案

### 代码回滚
```bash
git checkout <previous-commit>
pip install -r requirements.txt
sudo systemctl restart highway-inspection
```

### 数据库回滚
```bash
# 恢复备份
mysql -u root -p highway_inspection_system < backup.sql

# 或使用 Flask-Migrate
flask db downgrade
```

