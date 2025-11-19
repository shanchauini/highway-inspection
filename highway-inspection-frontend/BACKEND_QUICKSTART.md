# 后端开发快速启动指南

> 为后端开发同学准备的快速上手指南

## 📋 前置条件

在开始后端开发前，请确保：

1. ✅ 前端项目已成功运行（`npm run dev`）
2. ✅ 已阅读 [部署与使用手册](./DEPLOYMENT_GUIDE.md)
3. ✅ 已查看 [API 接口速查表](./API_REFERENCE.md)

## 🎯 开发优先级

建议按以下顺序实现后端接口：

### 第一阶段：核心认证（必需）

- [ ] `POST /api/auth/login` - 用户登录
- [ ] Token 生成与验证机制
- [ ] CORS 跨域配置

### 第二阶段：基础数据展示

- [ ] `GET /api/map/drones` - 无人机位置（地图总览需要）
- [ ] `GET /api/map/airspaces` - 空域列表（地图总览需要）
- [ ] `GET /api/users` - 用户列表（用户管理需要）

### 第三阶段：核心业务流程

- [ ] 飞行申请 CRUD（5个接口）
- [ ] 空域管理（4个接口）
- [ ] 告警管理（4个接口）

### 第四阶段：视频功能

- [ ] 视频上传（文件处理）
- [ ] 视频列表与分析
- [ ] 直播流接入

### 第五阶段：数据统计

- [ ] 统计接口（数据看板）
- [ ] WebSocket 实时推送（可选）

---

## 🔧 后端技术选型建议

### Node.js 技术栈

**推荐框架**: Express / Nest.js / Koa

```bash
# Express 示例
npm install express cors jsonwebtoken bcrypt multer
```

**基础结构**：

```javascript
// server.js
const express = require('express')
const cors = require('cors')
const app = express()

// CORS 配置
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}))

// 解析 JSON
app.use(express.json())

// 路由
app.use('/api/auth', authRoutes)
app.use('/api/users', userRoutes)
app.use('/api/flights', flightRoutes)
// ...

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000')
})
```

### Python 技术栈

**推荐框架**: FastAPI / Django REST Framework

```bash
# FastAPI 示例
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

**基础结构**：

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/login")
async def login(credentials: dict):
    # 登录逻辑
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
```

### Java 技术栈

**推荐框架**: Spring Boot

```xml
<!-- pom.xml 依赖 -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt</artifactId>
    </dependency>
</dependencies>
```

---

## 🔐 认证实现示例

### JWT Token 生成（Node.js）

```javascript
const jwt = require('jsonwebtoken')
const SECRET_KEY = 'your-secret-key'

// 登录接口
app.post('/api/auth/login', async (req, res) => {
  const { username, password } = req.body
  
  // 验证用户（从数据库查询）
  const user = await User.findOne({ username })
  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(401).json({
      code: 401,
      message: '用户名或密码错误'
    })
  }
  
  // 生成 token
  const token = jwt.sign(
    { userId: user.id, role: user.role },
    SECRET_KEY,
    { expiresIn: '7d' }
  )
  
  res.json({
    code: 200,
    data: {
      token,
      user: {
        id: user.id,
        username: user.username,
        name: user.name,
        role: user.role
      }
    }
  })
})

// Token 验证中间件
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未提供token' })
  }
  
  try {
    const decoded = jwt.verify(token, SECRET_KEY)
    req.user = decoded
    next()
  } catch (error) {
    return res.status(401).json({ code: 401, message: 'token无效' })
  }
}

// 使用中间件保护路由
app.get('/api/users', authMiddleware, (req, res) => {
  // 只有携带有效 token 才能访问
})
```

---

## 📦 数据库设计建议

### 核心表结构

#### 用户表 (users)

```sql
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(100) UNIQUE,
  phone VARCHAR(20),
  role ENUM('admin', 'operator') NOT NULL,
  status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
  department VARCHAR(100),
  avatar VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP,
  created_by VARCHAR(50)
);
```

#### 空域表 (airspaces)

```sql
CREATE TABLE airspaces (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  code VARCHAR(50) UNIQUE NOT NULL,
  type ENUM('flyable', 'restricted', 'prohibited') NOT NULL,
  status ENUM('available', 'occupied', 'unavailable') DEFAULT 'available',
  coordinates JSON NOT NULL,  -- [[lat, lng], ...]
  altitude_min INT DEFAULT 0,
  altitude_max INT DEFAULT 500,
  description TEXT,
  occupied_by VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 飞行申请表 (flight_applications)

```sql
CREATE TABLE flight_applications (
  id VARCHAR(50) PRIMARY KEY,
  applicant_id VARCHAR(50) NOT NULL,
  drone_id VARCHAR(50) NOT NULL,
  mission VARCHAR(100),
  purpose TEXT,
  airspace_id VARCHAR(50) NOT NULL,
  planned_altitude INT,
  planned_duration INT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status ENUM('draft', 'pending', 'approved', 'rejected', 'expired') DEFAULT 'draft',
  reviewer_id VARCHAR(50),
  review_time TIMESTAMP,
  review_notes TEXT,
  launch_requested BOOLEAN DEFAULT FALSE,
  launch_approved BOOLEAN DEFAULT FALSE,
  launch_approved_by VARCHAR(50),
  launch_approved_time TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (applicant_id) REFERENCES users(id),
  FOREIGN KEY (airspace_id) REFERENCES airspaces(id)
);
```

#### 告警表 (alerts)

```sql
CREATE TABLE alerts (
  id VARCHAR(50) PRIMARY KEY,
  type ENUM('collision', 'intrusion', 'status_abnormal', 'weather', 
            'road_anomaly', 'traffic_accident', 'facility_abnormal'),
  level ENUM('critical', 'high', 'medium', 'low') NOT NULL,
  status ENUM('new', 'confirmed', 'processing', 'resolved', 'closed') DEFAULT 'new',
  title VARCHAR(200) NOT NULL,
  description TEXT,
  location_lat DECIMAL(10, 6),
  location_lng DECIMAL(10, 6),
  location_address VARCHAR(255),
  flight_id VARCHAR(50),
  drone_id VARCHAR(50),
  video_id VARCHAR(50),
  video_url VARCHAR(255),
  image_url VARCHAR(255),
  confidence INT,
  confirmed_by VARCHAR(50),
  confirmed_at TIMESTAMP,
  assigned_to VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 🧪 测试接口

### 使用 Postman / cURL

**登录测试**：

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**获取用户列表**（需要 token）：

```bash
curl -X GET http://localhost:3000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 前端联调

1. 确保后端运行在 `http://localhost:3000`
2. 前端配置 `.env.development`：
   ```env
   VITE_API_BASE_URL=http://localhost:3000/api
   ```
3. 启动前端：`npm run dev`
4. 访问 `http://localhost:5173/login`

---

## 🐛 常见问题

### 1. CORS 错误

**现象**：浏览器控制台报跨域错误

**解决**：

```javascript
// Express
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}))

// FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
)
```

### 2. Token 验证失败

**现象**：前端请求返回 401

**检查**：
- 后端是否正确解析 `Authorization` 头
- Token 格式是否为 `Bearer {token}`
- Token 是否过期

### 3. 文件上传失败

**解决**：

```javascript
// Express - 使用 multer
const multer = require('multer')
const upload = multer({ dest: 'uploads/' })

app.post('/api/video/upload', upload.single('file'), (req, res) => {
  const file = req.file
  const metadata = JSON.parse(req.body.metadata)
  // 处理文件
})
```

### 4. 时间格式问题

**要求**：所有时间使用 ISO 8601 格式

```javascript
// JavaScript
new Date().toISOString()  // "2025-10-28T10:00:00.000Z"

// Python
from datetime import datetime
datetime.utcnow().isoformat() + 'Z'
```

---

## 📊 Mock 数据参考

前端当前使用 Store 内的 Mock 数据，可以参考：

- `src/stores/users.ts` - 用户数据示例
- `src/stores/flight.ts` - 飞行申请数据示例
- `src/stores/airspace.ts` - 空域数据示例
- `src/stores/alert.ts` - 告警数据示例

---

## 🔗 相关资源

### 官方文档

- **Express**: https://expressjs.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Spring Boot**: https://spring.io/projects/spring-boot

### 工具推荐

- **API 测试**: Postman / Insomnia
- **数据库管理**: DBeaver / Navicat
- **API 文档**: Swagger / Apifox

---

## ✅ 开发检查清单

### 基础功能

- [ ] CORS 跨域配置
- [ ] 统一响应格式 `{ code, message, data }`
- [ ] 统一错误处理
- [ ] Token 认证中间件
- [ ] 请求日志记录

### 安全性

- [ ] 密码加密存储（bcrypt）
- [ ] Token 签名与验证（JWT）
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] 文件上传限制（大小、类型）

### 性能

- [ ] 数据库索引优化
- [ ] 分页查询
- [ ] 接口响应缓存（如适用）
- [ ] 文件上传进度反馈

### 数据完整性

- [ ] 必填字段验证
- [ ] 数据格式验证（邮箱、手机号等）
- [ ] 唯一性约束（用户名、邮箱等）
- [ ] 外键关联检查

---

## 💡 开发建议

1. **优先实现登录接口**，确保前端能够正常登录
2. **使用统一的响应格式**，方便前端统一处理
3. **及时同步接口变更**，避免前后端不一致
4. **提供清晰的错误信息**，帮助前端定位问题
5. **实现分页**，避免一次性返回大量数据
6. **记录操作日志**，方便问题追踪

---

## 📞 联系方式

如有疑问，请联系前端开发团队或查看完整文档：

- [部署与使用手册](./DEPLOYMENT_GUIDE.md)
- [API 接口速查表](./API_REFERENCE.md)

---

**祝开发顺利！** 🎉

