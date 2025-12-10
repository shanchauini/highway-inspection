# 公路巡检系统前端 - 部署与使用手册

## 目录

1. [系统概述](#系统概述)
2. [技术栈](#技术栈)
3. [环境要求](#环境要求)
4. [安装部署](#安装部署)
5. [项目结构](#项目结构)
6. [API 接口规范](#api-接口规范)
7. [模块详解](#模块详解)
8. [数据模型](#数据模型)
9. [开发调试](#开发调试)
10. [生产构建](#生产构建)
11. [常见问题](#常见问题)

---

## 系统概述

公路巡检系统前端是一个基于 Vue 3 + TypeScript 的现代化 Web 应用，为无人机公路巡检业务提供可视化操作界面。

### 核心功能模块

- **地图总览**：实时显示无人机位置、空域状态
- **视频巡检**：视频上传、实时直播、智能分析
- **飞行申请**：飞行任务申请、审批、放飞管理
- **空域管理**：空域划设、状态管理、冲突检测
- **巡检结果**：巡检结果展示、处理、统计分析
- **数据看板**：多维度数据可视化展示
- **用户管理**：用户 CRUD、角色权限、设备分配

---

## 技术栈

### 核心框架
- **Vue 3.4+** - 渐进式 JavaScript 框架
- **TypeScript 5.0+** - 类型安全
- **Vite 5.0+** - 快速构建工具

### 状态管理与路由
- **Pinia** - Vue 3 官方状态管理
- **Vue Router 4** - 路由管理

### UI 与可视化
- **Element Plus** - UI 组件库
- **Leaflet** - 地图引擎
- **ECharts 5** - 数据可视化

### HTTP 与通信
- **Axios** - HTTP 客户端
- **Socket.IO Client** - WebSocket 实时通信（预留）

### 其他工具
- **Day.js** - 日期时间处理
- **Turf.js** - 地理空间分析
- **XGPlayer** - 视频播放器

---

## 环境要求

### 开发环境
- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0 或 **pnpm**: >= 8.0.0
- **操作系统**: Windows 10+, macOS 10.15+, Linux

### 浏览器支持
- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

---

## 安装部署

### 1. 克隆项目（如适用）

```bash
git clone <repository-url>
cd highway-inspection-frontend
```

### 2. 安装依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm（推荐）
pnpm install
```

### 3. 配置环境变量

创建 `.env.development` 文件（开发环境）：

```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:3000/api

# WebSocket 地址
VITE_WS_URL=ws://localhost:3000

# 是否启用 Mock 数据
VITE_USE_MOCK=false
```

创建 `.env.production` 文件（生产环境）：

```env
# API 基础地址
VITE_API_BASE_URL=https://api.example.com/api

# WebSocket 地址
VITE_WS_URL=wss://api.example.com

# 是否启用 Mock 数据
VITE_USE_MOCK=false
```

### 4. 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:5173`

### 5. 生产构建

```bash
npm run build
```

构建产物在 `dist` 目录

### 6. 预览生产构建

```bash
npm run preview
```

---

## 项目结构

```
highway-inspection-frontend/
├── public/                    # 静态资源
├── src/
│   ├── api/                   # API 接口层
│   │   ├── index.ts          # Axios 实例配置
│   │   └── modules.ts        # API 模块定义
│   ├── assets/               # 资源文件
│   │   └── styles/
│   │       └── global.css    # 全局样式
│   ├── layouts/              # 布局组件
│   │   └── MainLayout.vue    # 主布局
│   ├── plugins/              # 插件配置
│   │   └── element.ts        # Element Plus 配置
│   ├── router/               # 路由配置
│   │   └── index.ts          # 路由定义
│   ├── stores/               # Pinia 状态管理
│   │   ├── index.ts          # Store 入口
│   │   ├── user.ts           # 用户状态
│   │   ├── users.ts          # 用户管理
│   │   ├── map.ts            # 地图状态
│   │   ├── flight.ts         # 飞行申请
│   │   ├── airspace.ts       # 空域管理
│   │   └── alert.ts          # 告警中心
│   ├── views/                # 页面组件
│   │   ├── Login.vue         # 登录页
│   │   ├── Map.vue           # 地图总览
│   │   ├── Video.vue         # 视频巡检
│   │   ├── Flights.vue       # 飞行申请
│   │   ├── Airspace.vue      # 空域管理
│   │   ├── Alerts.vue        # 告警中心
│   │   ├── Dashboard.vue     # 数据看板
│   │   └── Users.vue         # 用户管理
│   ├── App.vue               # 根组件
│   └── main.ts               # 入口文件
├── .env.development          # 开发环境变量
├── .env.production           # 生产环境变量
├── index.html                # HTML 模板
├── package.json              # 项目配置
├── tsconfig.json             # TypeScript 配置
├── vite.config.ts            # Vite 配置
└── README.md                 # 项目说明
```

---

## API 接口规范

### 基础配置

**文件位置**: `src/api/index.ts`

```typescript
// 所有请求自动携带 Authorization 头
headers: {
  'Authorization': `Bearer ${token}`
}

// 请求拦截器：添加 token
// 响应拦截器：统一错误处理
```

### API 模块

**文件位置**: `src/api/modules.ts`

前端已按功能模块组织 API，后端需实现对应接口。

---

### 1. 视频管理 API (`videoApi`)

#### 1.1 上传视频文件

```
POST /api/video/upload
Content-Type: multipart/form-data

Request Body:
  - file: File (视频文件)
  - metadata: JSON String {
      taskId: string,           // 任务ID
      collectionTime: string,   // 采集时间 ISO8601
      collectionSection: string, // 采集路段
      droneNumber: string       // 无人机编号
    }

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "videoId": "string",        // 视频ID
    "uploadTime": "string",     // 上传时间
    "status": "uploaded"        // 状态
  }
}
```

#### 1.2 获取视频列表

```
GET /api/video/list?page=1&size=10&status=uploaded

Response:
{
  "code": 200,
  "data": {
    "total": 100,
    "list": [
      {
        "videoId": "string",
        "taskId": "string",
        "fileName": "string",
        "fileSize": 123456,
        "duration": 120,          // 秒
        "collectionTime": "string",
        "collectionSection": "string",
        "droneNumber": "string",
        "status": "uploaded|analyzing|completed",
        "uploadTime": "string"
      }
    ]
  }
}
```

#### 1.3 启动视频分析

```
POST /api/video/:videoId/analyze

Response:
{
  "code": 200,
  "message": "分析任务已启动",
  "data": {
    "analysisId": "string",
    "status": "analyzing"
  }
}
```

#### 1.4 获取分析结果

```
GET /api/video/:videoId/results

Response:
{
  "code": 200,
  "data": {
    "videoId": "string",
    "status": "completed",
    "events": [
      {
        "eventId": "string",
        "type": "road_anomaly|traffic_accident|facility_abnormal",
        "title": "string",
        "description": "string",
        "location": {
          "lat": 39.9042,
          "lng": 116.4074
        },
        "timestamp": "string",     // 视频时间戳（秒）
        "confidence": 95,          // 置信度 0-100
        "imageUrl": "string"       // 截图URL
      }
    ],
    "targets": [
      {
        "targetId": "string",
        "type": "vehicle|person|animal",
        "count": 10,
        "locations": [...]
      }
    ]
  }
}
```

#### 1.5 获取直播流地址

```
GET /api/video/live/:droneId

Response:
{
  "code": 200,
  "data": {
    "streamUrl": "rtmp://example.com/live/stream",
    "protocol": "rtmp|rtsp|flv|hls",
    "status": "online|offline"
  }
}
```

---

### 2. 地图管理 API (`mapApi`)

#### 2.1 获取地图配置

```
GET /api/map/config

Response:
{
  "code": 200,
  "data": {
    "center": [39.9042, 116.4074],  // [lat, lng]
    "zoom": 10,
    "minZoom": 3,
    "maxZoom": 18,
    "tileLayerUrl": "string"
  }
}
```

#### 2.2 获取空域列表

```
GET /api/map/airspaces

Response:
{
  "code": 200,
  "data": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "type": "flyable|restricted|prohibited",
      "status": "available|occupied|unavailable",
      "coordinates": [[lat, lng], ...],  // 多边形顶点
      "altitude": {
        "min": 0,
        "max": 500
      },
      "description": "string",
      "occupiedBy": "string",           // 占用者用户ID
      "occupiedByName": "string"
    }
  ]
}
```

#### 2.3 获取无人机位置

```
GET /api/map/drones

Response:
{
  "code": 200,
  "data": [
    {
      "droneId": "string",
      "serialNumber": "string",
      "model": "string",
      "position": {
        "lat": 39.9042,
        "lng": 116.4074,
        "altitude": 120
      },
      "status": "flying|idle|maintenance",
      "speed": 15.5,                    // km/h
      "battery": 85,                    // 百分比
      "operator": "string",             // 操作员姓名
      "lastUpdate": "string"            // ISO8601
    }
  ]
}
```

#### 2.4 创建空域

```
POST /api/map/airspaces

Request Body:
{
  "name": "string",
  "code": "string",
  "type": "flyable|restricted|prohibited",
  "status": "available",
  "coordinates": [[lat, lng], ...],
  "altitude": {
    "min": 0,
    "max": 500
  },
  "description": "string"
}

Response:
{
  "code": 200,
  "data": {
    "id": "string",
    ...
  }
}
```

#### 2.5 更新空域状态

```
PUT /api/map/airspaces/:id/status

Request Body:
{
  "status": "available|occupied|unavailable",
  "occupiedBy": "string"  // 占用者ID（可选）
}

Response:
{
  "code": 200,
  "message": "状态更新成功"
}
```

---

### 3. 飞行申请 API (`flightApi`)

#### 3.1 获取飞行申请列表

```
GET /api/flights/applications?status=pending&page=1&size=10

Query Params:
  - status: draft|pending|approved|rejected|expired
  - applicant: string (申请人ID)
  - startDate: string (开始日期)
  - endDate: string (结束日期)
  - page: number
  - size: number

Response:
{
  "code": 200,
  "data": {
    "total": 50,
    "list": [
      {
        "id": "string",
        "applicantId": "string",
        "applicantName": "string",
        "droneId": "string",
        "droneModel": "string",
        "serialNumber": "string",
        "mission": "string",             // 任务类型
        "purpose": "string",             // 任务目的
        "airspaceId": "string",
        "airspaceName": "string",
        "plannedAltitude": 120,          // 米
        "plannedDuration": 60,           // 分钟
        "startTime": "string",           // ISO8601
        "endTime": "string",
        "status": "draft|pending|approved|rejected|expired",
        "reviewerId": "string",
        "reviewerName": "string",
        "reviewTime": "string",
        "reviewNotes": "string",
        "launchRequested": false,
        "launchApproved": false,
        "launchApprovedBy": "string",
        "launchApprovedTime": "string",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ]
  }
}
```

#### 3.2 创建飞行申请

```
POST /api/flights/applications

Request Body:
{
  "droneId": "string",
  "mission": "string",
  "purpose": "string",
  "airspaceId": "string",
  "plannedAltitude": 120,
  "plannedDuration": 60,
  "startTime": "string",
  "endTime": "string",
  "status": "draft|pending"  // draft=草稿, pending=提交审批
}

Response:
{
  "code": 200,
  "data": {
    "id": "string",
    ...
  }
}
```

#### 3.3 审批飞行申请

```
PUT /api/flights/applications/:id/approve

Request Body:
{
  "decision": "approve|reject",
  "reason": "string"  // 审批意见
}

Response:
{
  "code": 200,
  "message": "审批成功"
}
```

#### 3.4 提交放飞申请

```
POST /api/flights/applications/:applicationId/launch

Response:
{
  "code": 200,
  "message": "放飞申请已提交"
}
```

#### 3.5 批准放飞

```
PUT /api/flights/applications/:applicationId/launch/approve

Response:
{
  "code": 200,
  "message": "已批准放飞"
}
```

---

### 4. 告警管理 API (`alertApi`)

#### 4.1 获取告警列表

```
GET /api/alerts?type=collision&level=high&status=new&page=1&size=10

Query Params:
  - type: collision|intrusion|status_abnormal|weather|road_anomaly|traffic_accident|facility_abnormal
  - level: critical|high|medium|low
  - status: new|confirmed|processing|resolved|closed
  - startDate: string
  - endDate: string
  - page: number
  - size: number

Response:
{
  "code": 200,
  "data": {
    "total": 100,
    "list": [
      {
        "id": "string",
        "type": "string",
        "level": "string",
        "status": "string",
        "title": "string",
        "description": "string",
        "location": {
          "lat": 39.9042,
          "lng": 116.4074,
          "address": "string"
        },
        "flightId": "string",
        "flightName": "string",
        "droneId": "string",
        "droneName": "string",
        "videoId": "string",
        "videoUrl": "string",
        "imageUrl": "string",
        "confidence": 95,
        "confirmedBy": "string",
        "confirmedByName": "string",
        "confirmedAt": "string",
        "assignedTo": "string",
        "assignedToName": "string",
        "notes": "string",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ]
  }
}
```

#### 4.2 确认告警

```
PUT /api/alerts/:id/confirm

Response:
{
  "code": 200,
  "message": "告警已确认"
}
```

#### 4.3 处理告警

```
PUT /api/alerts/:id/handle

Request Body:
{
  "action": "assign|resolve|close",
  "assignTo": "string",      // action=assign 时必填
  "note": "string"           // 处理备注
}

Response:
{
  "code": 200,
  "message": "处理成功"
}
```

#### 4.4 删除告警

```
DELETE /api/alerts/:id

Response:
{
  "code": 200,
  "message": "删除成功"
}
```

---

### 5. 用户管理 API (`userApi`)

#### 5.1 用户登录

```
POST /api/auth/login

Request Body:
{
  "username": "string",
  "password": "string"
}

Response:
{
  "code": 200,
  "data": {
    "token": "string",
    "user": {
      "id": "string",
      "username": "string",
      "name": "string",
      "email": "string",
      "role": "admin|operator",
      "avatar": "string"
    }
  }
}
```

#### 5.2 获取用户列表

```
GET /api/users?role=operator&status=active&page=1&size=10

Query Params:
  - username: string (搜索)
  - role: admin|operator
  - status: active|inactive|locked
  - page: number
  - size: number

Response:
{
  "code": 200,
  "data": {
    "total": 50,
    "list": [
      {
        "id": "string",
        "username": "string",
        "name": "string",
        "email": "string",
        "phone": "string",
        "role": "admin|operator",
        "status": "active|inactive|locked",
        "department": "string",
        "assignedDrones": ["droneId1", "droneId2"],
        "avatar": "string",
        "createdAt": "string",
        "updatedAt": "string",
        "lastLoginAt": "string",
        "createdBy": "string",
        "createdByName": "string"
      }
    ]
  }
}
```

#### 5.3 创建用户

```
POST /api/users

Request Body:
{
  "username": "string",        // 3-20字符，唯一
  "password": "string",        // 6-20字符
  "name": "string",
  "email": "string",           // 可选，唯一
  "phone": "string",           // 可选
  "role": "admin|operator",
  "status": "active|inactive|locked",
  "department": "string"
}

Response:
{
  "code": 200,
  "data": {
    "id": "string",
    ...
  }
}
```

#### 5.4 更新用户

```
PUT /api/users/:id

Request Body:
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "role": "string",
  "status": "string",
  "department": "string"
}

Response:
{
  "code": 200,
  "message": "更新成功"
}
```

#### 5.5 删除用户

```
DELETE /api/users/:id

Response:
{
  "code": 200,
  "message": "删除成功"
}
```

#### 5.6 重置密码

```
PUT /api/users/:id/password/reset

Request Body:
{
  "newPassword": "string"
}

Response:
{
  "code": 200,
  "message": "密码重置成功"
}
```

#### 5.7 分配设备

```
PUT /api/users/:id/drones

Request Body:
{
  "droneIds": ["droneId1", "droneId2"]
}

Response:
{
  "code": 200,
  "message": "分配成功"
}
```

---

### 6. 统一错误响应格式

```json
{
  "code": 400|401|403|404|500,
  "message": "错误描述",
  "error": {
    "field": "字段名",
    "detail": "详细错误信息"
  }
}
```

**常用错误码**：
- `400` - 请求参数错误
- `401` - 未授权（token 失效或未提供）
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 数据模型

### 用户角色权限

| 角色 | 代码 | 权限 |
|------|------|------|
| 管理员 | `admin` | 所有权限，包括用户管理、空域管理、飞行审批、告警处理 |
| 操作员 | `operator` | 飞行申请、视频上传、查看数据 |

### 状态枚举

**飞行申请状态**：
- `draft` - 草稿
- `pending` - 待审批
- `approved` - 已批准
- `rejected` - 已驳回
- `expired` - 已过期

**空域状态**：
- `available` - 可用
- `occupied` - 占用中
- `unavailable` - 不可用

**告警状态**：
- `new` - 新发现
- `confirmed` - 已确认
- `processing` - 处理中
- `resolved` - 已解决
- `closed` - 已关闭

**用户状态**：
- `active` - 活跃
- `inactive` - 停用
- `locked` - 锁定

---

## 模块详解

### 1. 地图总览 (`Map.vue`)

**功能**：
- 显示基础地图（OpenStreetMap / 卫星图）
- 实时显示无人机位置和状态
- 显示空域范围和状态
- 点击无人机查看详细信息
- 提供定位和导航功能

**数据来源**：
- `mapApi.getDronePositions()` - 获取无人机位置
- `mapApi.getAirspaces()` - 获取空域数据

**刷新频率**：建议每 5-10 秒更新一次无人机位置

---

### 2. 视频巡检 (`Video.vue`)

**功能**：
- 上传视频文件（MP4, AVI 等）
- 连接无人机实时直播流
- 显示视频分析结果（实时事件、目标识别）
- 视频播放控制

**支持的视频格式**：
- 上传：MP4, AVI, MOV
- 直播：RTMP, RTSP, FLV, HLS

**分析结果类型**：
- 路况异常（掉落物、积水、积雪）
- 交通事件（拥堵、事故、违章）
- 设施状态（标志牌、边坡）
- 其他目标（行人、动物）

---

### 3. 飞行申请 (`Flights.vue`)

**工作流程**：

1. **操作员创建申请**：
   - 选择无人机
   - 填写任务信息
   - 选择空域
   - 设置飞行参数
   - 保存草稿或提交审批

2. **管理员审批**：
   - 查看申请详情
   - 检查空域冲突
   - 批准或驳回

3. **操作员申请放飞**：
   - 审批通过后，在飞行时间前申请放飞

4. **管理员批准放飞**：
   - 最终确认，无人机可以起飞

**空域冲突检测**：
- 前端仅做基础展示
- 后端需实现：时间重叠检测、空间重叠检测

---

### 4. 空域管理 (`Airspace.vue`)

**功能**：
- 创建空域（绘制多边形或输入坐标）
- 编辑空域属性
- 修改空域状态（可用/占用/不可用）
- 地图可视化显示

**空域类型**：
- `flyable` - 适飞区（绿色）
- `restricted` - 限制区（黄色）
- `prohibited` - 禁飞区（红色）

**数据验证**：
- 多边形至少 3 个顶点
- 最小/最大高度合理性（0-500米）

---

### 5. 巡检结果 (`InspectionResults.vue`)

**告警来源**：
- 视频分析识别
- 无人机状态监测
- 空域侵入检测
- 碰撞风险预警
- 气象预警

**处理流程**：
1. 新发现（`new`）
2. 确认（`confirmed`）
3. 分派给处理人（`processing`）
4. 解决（`resolved`）
5. 关闭（`closed`）

**优先级**：
- `critical` - 严重（红色）
- `high` - 高级（橙色）
- `medium` - 中级（黄色）
- `low` - 低级（蓝色）

---

### 6. 数据看板 (`Dashboard.vue`)

**图表类型**：
- 飞行统计（柱状图）
- 空域利用率（饼图）
- 告警统计（饼图/折线图）
- 巡检成果（饼图）

**数据聚合**：
- 支持日期范围筛选
- 后端需提供聚合统计接口

---

### 7. 用户管理 (`Users.vue`)

**功能**：
- 用户 CRUD
- 密码重置
- 状态管理（激活/停用/锁定）
- 设备分配（仅操作员）
- 角色权限控制

**权限**：仅 `admin` 角色可访问

---

## 开发调试

### 启动开发服务器

```bash
npm run dev
```

### Mock 数据

前端当前使用 Store 内的 `initData()` 方法初始化 Mock 数据。

**后端开发建议**：
1. 优先实现登录接口
2. 然后按模块逐步替换 Mock 数据
3. 前端通过环境变量切换 Mock/真实 API

### 调试工具

- **Vue DevTools**: 浏览器扩展，查看组件状态
- **Network**: 浏览器开发工具，查看 API 请求
- **Console**: 查看错误日志

### 常用命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码格式化
npm run format

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

## 生产构建

### 构建命令

```bash
npm run build
```

### 构建产物

```
dist/
├── assets/          # JS/CSS 资源
├── index.html       # 入口 HTML
└── ...
```

### 部署建议

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/highway-inspection;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend-server:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 常见问题

### 1. CORS 跨域问题

**现象**：前端调用后端 API 时报 CORS 错误

**解决方案**：

后端需配置 CORS 头：

```javascript
// Express 示例
app.use(cors({
  origin: 'http://localhost:5173',  // 开发环境
  credentials: true
}))
```

### 2. Token 过期处理

**前端处理逻辑**：

```typescript
// src/api/index.ts 响应拦截器
if (error.response?.status === 401) {
  // 清除 token
  localStorage.removeItem('token')
  // 跳转登录页
  router.push('/login')
}
```

**后端建议**：
- Token 有效期：7天
- 返回 401 状态码表示 token 失效

### 3. 文件上传大小限制

**前端限制**：视频文件建议不超过 500MB

**后端需配置**：
```javascript
// Express 示例
app.use(express.json({ limit: '500mb' }))
app.use(express.urlencoded({ limit: '500mb', extended: true }))
```

### 4. WebSocket 实时通信（预留）

**使用场景**：
- 实时无人机位置更新
- 实时告警推送
- 视频分析进度通知

**前端集成**：
```typescript
import io from 'socket.io-client'
const socket = io('ws://backend-url')
```

### 5. 地图不显示

**可能原因**：
- Leaflet CSS 未加载
- 地图容器高度为 0
- 瓦片地图服务不可用

**解决方案**：
- 检查 `leaflet/dist/leaflet.css` 引入
- 确保 `.map-container` 有固定高度
- 使用可访问的瓦片服务（如 OpenStreetMap）

---

## 联系与支持

### 文档更新

本文档会随项目迭代持续更新，请关注最新版本。

### 技术支持

如有问题，请联系前端开发团队或提交 Issue。

---

## 附录：完整接口清单

| 模块 | 接口路径 | 方法 | 说明 |
|------|----------|------|------|
| **认证** | `/api/auth/login` | POST | 用户登录 |
| **视频** | `/api/video/upload` | POST | 上传视频 |
| | `/api/video/list` | GET | 视频列表 |
| | `/api/video/:id/analyze` | POST | 启动分析 |
| | `/api/video/:id/results` | GET | 分析结果 |
| | `/api/video/live/:droneId` | GET | 直播流 |
| **地图** | `/api/map/config` | GET | 地图配置 |
| | `/api/map/airspaces` | GET | 空域列表 |
| | `/api/map/airspaces` | POST | 创建空域 |
| | `/api/map/airspaces/:id/status` | PUT | 更新状态 |
| | `/api/map/drones` | GET | 无人机位置 |
| **飞行** | `/api/flights/applications` | GET | 申请列表 |
| | `/api/flights/applications` | POST | 创建申请 |
| | `/api/flights/applications/:id/approve` | PUT | 审批 |
| | `/api/flights/applications/:id/launch` | POST | 申请放飞 |
| | `/api/flights/applications/:id/launch/approve` | PUT | 批准放飞 |
| **告警** | `/api/alerts` | GET | 告警列表 |
| | `/api/alerts/:id/confirm` | PUT | 确认告警 |
| | `/api/alerts/:id/handle` | PUT | 处理告警 |
| | `/api/alerts/:id` | DELETE | 删除告警 |
| **用户** | `/api/users` | GET | 用户列表 |
| | `/api/users` | POST | 创建用户 |
| | `/api/users/:id` | PUT | 更新用户 |
| | `/api/users/:id` | DELETE | 删除用户 |
| | `/api/users/:id/password/reset` | PUT | 重置密码 |
| | `/api/users/:id/drones` | PUT | 分配设备 |

---

**版本**: 1.0.0  
**最后更新**: 2025-10-28  
**维护者**: 前端开发团队

