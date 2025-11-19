# API 接口速查表

## 基础信息

**Base URL**: `/api`  
**认证方式**: Bearer Token (Header: `Authorization: Bearer {token}`)  
**响应格式**: JSON

---

## 快速索引

- [认证接口](#认证接口)
- [视频管理](#视频管理)
- [地图与空域](#地图与空域)
- [飞行申请](#飞行申请)
- [告警管理](#告警管理)
- [用户管理](#用户管理)

---

## 认证接口

### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}

→ 200 OK
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "user_1",
      "username": "admin",
      "name": "管理员",
      "role": "admin"
    }
  }
}
```

---

## 视频管理

### 上传视频
```http
POST /api/video/upload
Content-Type: multipart/form-data

file: <video-file>
metadata: {
  "taskId": "task_001",
  "collectionTime": "2025-10-28T10:00:00Z",
  "collectionSection": "G1京哈高速",
  "droneNumber": "UAV001"
}

→ 200 OK
{
  "code": 200,
  "data": {
    "videoId": "video_123",
    "uploadTime": "2025-10-28T10:05:00Z",
    "status": "uploaded"
  }
}
```

### 获取视频列表
```http
GET /api/video/list?page=1&size=10&status=uploaded

→ 200 OK
{
  "code": 200,
  "data": {
    "total": 50,
    "list": [
      {
        "videoId": "video_123",
        "fileName": "patrol_20251028.mp4",
        "duration": 300,
        "status": "uploaded"
      }
    ]
  }
}
```

### 启动视频分析
```http
POST /api/video/{videoId}/analyze

→ 200 OK
{
  "code": 200,
  "message": "分析任务已启动",
  "data": {
    "analysisId": "analysis_456",
    "status": "analyzing"
  }
}
```

### 获取分析结果
```http
GET /api/video/{videoId}/results

→ 200 OK
{
  "code": 200,
  "data": {
    "videoId": "video_123",
    "status": "completed",
    "events": [
      {
        "eventId": "event_1",
        "type": "road_anomaly",
        "title": "路面掉落物",
        "confidence": 95,
        "timestamp": "120.5",
        "location": { "lat": 39.9042, "lng": 116.4074 }
      }
    ]
  }
}
```

### 获取直播流
```http
GET /api/video/live/{droneId}

→ 200 OK
{
  "code": 200,
  "data": {
    "streamUrl": "rtmp://example.com/live/UAV001",
    "protocol": "rtmp",
    "status": "online"
  }
}
```

---

## 地图与空域

### 获取地图配置
```http
GET /api/map/config

→ 200 OK
{
  "code": 200,
  "data": {
    "center": [39.9042, 116.4074],
    "zoom": 10
  }
}
```

### 获取空域列表
```http
GET /api/map/airspaces

→ 200 OK
{
  "code": 200,
  "data": [
    {
      "id": "airspace_1",
      "name": "空域A1",
      "type": "flyable",
      "status": "available",
      "coordinates": [[39.9, 116.4], [39.91, 116.41], ...],
      "altitude": { "min": 0, "max": 500 }
    }
  ]
}
```

### 创建空域
```http
POST /api/map/airspaces
Content-Type: application/json

{
  "name": "空域B1",
  "code": "AS_B1",
  "type": "flyable",
  "status": "available",
  "coordinates": [[39.9, 116.4], [39.91, 116.41], [39.9, 116.42]],
  "altitude": { "min": 0, "max": 300 },
  "description": "适飞区B1"
}

→ 200 OK
{
  "code": 200,
  "data": {
    "id": "airspace_2",
    ...
  }
}
```

### 更新空域状态
```http
PUT /api/map/airspaces/{id}/status
Content-Type: application/json

{
  "status": "occupied",
  "occupiedBy": "user_123"
}

→ 200 OK
{
  "code": 200,
  "message": "状态更新成功"
}
```

### 获取无人机位置
```http
GET /api/map/drones

→ 200 OK
{
  "code": 200,
  "data": [
    {
      "droneId": "drone_1",
      "serialNumber": "DJI001",
      "model": "DJI Mavic 3",
      "position": {
        "lat": 39.9042,
        "lng": 116.4074,
        "altitude": 120
      },
      "status": "flying",
      "speed": 15.5,
      "battery": 85
    }
  ]
}
```

---

## 飞行申请

### 获取申请列表
```http
GET /api/flights/applications?status=pending&page=1&size=10

→ 200 OK
{
  "code": 200,
  "data": {
    "total": 20,
    "list": [
      {
        "id": "app_1",
        "applicantName": "操作员A",
        "droneModel": "DJI Mavic 3",
        "mission": "公路巡检",
        "airspaceName": "空域A1",
        "status": "pending",
        "startTime": "2025-10-29T08:00:00Z"
      }
    ]
  }
}
```

### 创建申请
```http
POST /api/flights/applications
Content-Type: application/json

{
  "droneId": "drone_1",
  "mission": "公路巡检",
  "purpose": "G1京哈高速日常巡检",
  "airspaceId": "airspace_1",
  "plannedAltitude": 120,
  "plannedDuration": 60,
  "startTime": "2025-10-29T08:00:00Z",
  "endTime": "2025-10-29T09:00:00Z",
  "status": "pending"
}

→ 200 OK
{
  "code": 200,
  "data": {
    "id": "app_2",
    ...
  }
}
```

### 审批申请
```http
PUT /api/flights/applications/{id}/approve
Content-Type: application/json

{
  "decision": "approve",
  "reason": "符合飞行条件，批准"
}

→ 200 OK
{
  "code": 200,
  "message": "审批成功"
}
```

### 提交放飞申请
```http
POST /api/flights/applications/{id}/launch

→ 200 OK
{
  "code": 200,
  "message": "放飞申请已提交"
}
```

### 批准放飞
```http
PUT /api/flights/applications/{id}/launch/approve

→ 200 OK
{
  "code": 200,
  "message": "已批准放飞"
}
```

---

## 告警管理

### 获取告警列表
```http
GET /api/alerts?type=collision&level=high&status=new&page=1&size=10

→ 200 OK
{
  "code": 200,
  "data": {
    "total": 15,
    "list": [
      {
        "id": "alert_1",
        "type": "collision",
        "level": "high",
        "status": "new",
        "title": "碰撞风险预警",
        "description": "无人机接近限制区域",
        "location": { "lat": 39.9, "lng": 116.4 },
        "confidence": 92,
        "createdAt": "2025-10-28T10:00:00Z"
      }
    ]
  }
}
```

### 确认告警
```http
PUT /api/alerts/{id}/confirm

→ 200 OK
{
  "code": 200,
  "message": "告警已确认"
}
```

### 处理告警
```http
PUT /api/alerts/{id}/handle
Content-Type: application/json

{
  "action": "assign",
  "assignTo": "user_123",
  "note": "分派给操作员A处理"
}

→ 200 OK
{
  "code": 200,
  "message": "处理成功"
}
```

### 删除告警
```http
DELETE /api/alerts/{id}

→ 200 OK
{
  "code": 200,
  "message": "删除成功"
}
```

---

## 用户管理

### 获取用户列表
```http
GET /api/users?role=operator&status=active&page=1&size=10

→ 200 OK
{
  "code": 200,
  "data": {
    "total": 10,
    "list": [
      {
        "id": "user_1",
        "username": "operator1",
        "name": "操作员A",
        "email": "operator1@example.com",
        "role": "operator",
        "status": "active",
        "department": "飞行作业部"
      }
    ]
  }
}
```

### 创建用户
```http
POST /api/users
Content-Type: application/json

{
  "username": "operator3",
  "password": "123456",
  "name": "操作员C",
  "email": "operator3@example.com",
  "phone": "13800138003",
  "role": "operator",
  "status": "active",
  "department": "飞行作业部"
}

→ 200 OK
{
  "code": 200,
  "data": {
    "id": "user_3",
    ...
  }
}
```

### 更新用户
```http
PUT /api/users/{id}
Content-Type: application/json

{
  "name": "操作员C（更新）",
  "email": "operator3_new@example.com",
  "department": "巡检作业部"
}

→ 200 OK
{
  "code": 200,
  "message": "更新成功"
}
```

### 删除用户
```http
DELETE /api/users/{id}

→ 200 OK
{
  "code": 200,
  "message": "删除成功"
}
```

### 重置密码
```http
PUT /api/users/{id}/password/reset
Content-Type: application/json

{
  "newPassword": "newpass123"
}

→ 200 OK
{
  "code": 200,
  "message": "密码重置成功"
}
```

### 分配设备
```http
PUT /api/users/{id}/drones
Content-Type: application/json

{
  "droneIds": ["drone_1", "drone_2"]
}

→ 200 OK
{
  "code": 200,
  "message": "分配成功"
}
```

---

## 错误响应格式

```json
{
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "field": "username",
    "detail": "用户名已存在"
  }
}
```

### 常用状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（token失效或未提供） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 枚举值参考

### 用户角色 (role)
- `admin` - 管理员
- `operator` - 操作员

### 用户状态 (user.status)
- `active` - 活跃
- `inactive` - 停用
- `locked` - 锁定

### 空域类型 (airspace.type)
- `flyable` - 适飞区
- `restricted` - 限制区
- `prohibited` - 禁飞区

### 空域状态 (airspace.status)
- `available` - 可用
- `occupied` - 占用中
- `unavailable` - 不可用

### 飞行申请状态 (flight.status)
- `draft` - 草稿
- `pending` - 待审批
- `approved` - 已批准
- `rejected` - 已驳回
- `expired` - 已过期

### 告警类型 (alert.type)
- `collision` - 碰撞风险
- `intrusion` - 空域侵入
- `status_abnormal` - 状态异常
- `weather` - 气象预警
- `road_anomaly` - 路况异常
- `traffic_accident` - 交通事故
- `facility_abnormal` - 设施异常

### 告警等级 (alert.level)
- `critical` - 严重
- `high` - 高级
- `medium` - 中级
- `low` - 低级

### 告警状态 (alert.status)
- `new` - 新发现
- `confirmed` - 已确认
- `processing` - 处理中
- `resolved` - 已解决
- `closed` - 已关闭

### 视频分析事件类型 (event.type)
- `road_anomaly` - 路况异常
- `traffic_accident` - 交通事故
- `facility_abnormal` - 设施异常
- `other` - 其他

---

## 注意事项

1. **所有时间字段**使用 ISO 8601 格式：`2025-10-28T10:00:00Z`
2. **坐标格式**：`[纬度(lat), 经度(lng)]`，例如 `[39.9042, 116.4074]`
3. **分页参数**：`page` 从 1 开始，`size` 默认 10
4. **Token 有效期**：建议 7 天
5. **文件上传**：最大 500MB

---

**版本**: 1.0.0  
**最后更新**: 2025-10-28

