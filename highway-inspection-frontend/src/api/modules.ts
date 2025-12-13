import api from './index'

// 认证相关API
export const authApi = {
  // 用户登录
  login: (username: string, password: string) => {
    return api.post('/auth/login', { username, password })
  },

  // 用户注册
  register: (username: string, password: string, role?: string) => {
    return api.post('/auth/register', { username, password, role })
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return api.get('/auth/current')
  },

  // 登出
  logout: () => {
    return api.post('/auth/logout')
  }
}

// 视频相关API
export const videoApi = {
  // 获取视频列表
  getVideos: (params?: any) => {
    return api.get('/videos', { params })
  },

  // 获取视频详情
  getVideoById: (id: string | number) => {
    return api.get(`/videos/${id}`)
  },

  // 上传视频（创建视频记录）
  uploadVideo: (data: any) => {
    return api.post('/videos', data)
  },

  // 上传媒体文件（图片或视频）
  uploadMediaFile: (formData: FormData) => {
    return api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取视频分析结果（支持分页）
  getAnalysisResults: (id: string | number, params?: any) => {
    return api.get(`/videos/${id}/analysis-results`, { params })
  },

  // 触发AI分析
  analyzeVideo: (id: string | number, detectionType: string = 'traffic_congestion') => {
    return api.post(`/videos/${id}/analyze`, { detection_type: detectionType })
  }
}

// 地图相关API（使用airspaceApi和missionApi）
export const mapApi = {
  // 获取可用空域（用于地图显示）
  getAvailableAirspaces: () => {
    return airspaceApi.getAvailableAirspaces()
  },

  // 获取活跃任务（用于地图显示无人机位置）
  getActiveMissions: () => {
    return missionApi.getActiveMissions()
  }
}


// 用户管理API
export const userApi = {
  // 获取用户列表
  getUsers: (params?: any) => {
    return api.get('/users', { params })
  },

  // 获取用户详情
  getUserById: (id: string | number) => {
    return api.get(`/users/${id}`)
  },

  // 更新用户
  updateUser: (id: string | number, data: any) => {
    return api.put(`/users/${id}`, data)
  },

  // 删除用户
  deleteUser: (id: string | number) => {
    return api.delete(`/users/${id}`)
  }
}

// 空域管理API
export const airspaceApi = {
  // 获取空域列表
  getAirspaces: (params?: any) => {
    return api.get('/airspaces', { params })
  },

  // 获取空域详情
  getAirspaceById: (id: string | number) => {
    return api.get(`/airspaces/${id}`)
  },

  // 创建空域
  createAirspace: (data: any) => {
    return api.post('/airspaces', data)
  },

  // 更新空域
  updateAirspace: (id: string | number, data: any) => {
    return api.put(`/airspaces/${id}`, data)
  },

  // 删除空域
  deleteAirspace: (id: string | number) => {
    return api.delete(`/airspaces/${id}`)
  },

  // 获取可用空域
  getAvailableAirspaces: () => {
    return api.get('/airspaces/available')
  },

  // 检查空域冲突
  checkConflict: (id: string | number, data: any) => {
    return api.post(`/airspaces/${id}/check-conflict`, data)
  }
}

// 飞行申请API
export const flightApi = {
  // 获取飞行申请列表
  getFlights: (params?: any) => {
    return api.get('/flights', { params })
  },

  // 获取飞行申请详情
  getFlightById: (id: string | number) => {
    return api.get(`/flights/${id}`)
  },

  // 创建飞行申请
  createFlight: (data: any) => {
    return api.post('/flights', data)
  },

  // 更新飞行申请
  updateFlight: (id: string | number, data: any) => {
    return api.put(`/flights/${id}`, data)
  },

  // 删除飞行申请
  deleteFlight: (id: string | number) => {
    return api.delete(`/flights/${id}`)
  },

  // 提交飞行申请
  submitFlight: (id: string | number) => {
    return api.post(`/flights/${id}/submit`)
  },

  // 撤回待审批申请
  withdrawFlight: (id: string | number) => {
    return api.post(`/flights/${id}/withdraw`)
  },

  // 批准飞行申请
  approveFlight: (id: string | number) => {
    return api.post(`/flights/${id}/approve`)
  },

  // 驳回飞行申请
  rejectFlight: (id: string | number, data: any) => {
    return api.post(`/flights/${id}/reject`, data)
  },

  // 放飞申请
  launchFlight: (id: string | number) => {
    return api.post(`/flights/${id}/launch`)
  },

  // 终止已批准申请
  terminateFlight: (id: string | number) => {
    return api.post(`/flights/${id}/terminate`)
  },

  // 获取待审批申请列表
  getPendingFlights: () => {
    return api.get('/flights/pending')
  }
}

// 告警API
export const alertApi = {
  // 获取告警列表
  getAlerts: (params?: any) => {
    return api.get('/alerts', { params })
  },

  // 获取告警详情
  getAlertById: (id: string | number) => {
    return api.get(`/alerts/${id}`)
  },

  // 更新告警状态
  updateAlert: (id: string | number, data: any) => {
    return api.put(`/alerts/${id}`, data)
  },

  // 获取活跃告警
  getActiveAlerts: () => {
    return api.get('/alerts/active')
  }
}

// 巡检结果API
export const inspectionResultApi = {
  // 获取巡检结果列表
  getInspectionResults: (params?: any) => {
    return api.get('/inspection-results', { params })
  },

  // 获取巡检结果详情
  getInspectionResultById: (id: string | number) => {
    return api.get(`/inspection-results/${id}`)
  },

  // 获取巡检结果统计
  getInspectionStatistics: (params?: any) => {
    return api.get('/inspection-results/statistics', { params })
  },

  // 获取巡检结果趋势
  getInspectionTrend: (params?: any) => {
    return api.get('/inspection-results/trend', { params })
  }
}

// 任务API
export const missionApi = {
  // 获取任务列表
  getMissions: (params?: any) => {
    return api.get('/missions', { params })
  },

  // 获取任务详情
  getMissionById: (id: string | number) => {
    return api.get(`/missions/${id}`)
  },

  // 获取活跃任务
  getActiveMissions: () => {
    return api.get('/missions/active')
  },

  // 完成任务
  completeMission: (id: string | number) => {
    return api.post(`/missions/${id}/complete`)
  }
}

// 数据看板API
export const dashboardApi = {
  // 获取看板统计
  getStats: (params?: any) => {
    return api.get('/dashboard/stats', { params })
  },

  // 获取飞行统计
  getFlightStats: (params?: any) => {
    return api.get('/dashboard/flight-stats', { params })
  },

  // 获取空域使用统计
  getAirspaceUsage: (params?: any) => {
    return api.get('/dashboard/airspace-usage', { params })
  },

  // 获取告警统计
  getAlertStats: (params?: any) => {
    return api.get('/dashboard/alert-stats', { params })
  },

  // 获取告警趋势
  getAlertTrend: (params?: any) => {
    return api.get('/dashboard/alert-trend', { params })
  },

  // 获取飞行任务趋势
  getFlightTrend: (params?: any) => {
    return api.get('/dashboard/flight-trend', { params })
  },
  
  // 获取巡检成果统计
  getInspectionResults: (params?: any) => {
    return api.get('/dashboard/inspection-results', { params })
  },
  
  // 获取巡检结果趋势
  getInspectionTrend: (params?: any) => {
    return api.get('/dashboard/inspection-trend', { params })
  },
  
  // 获取巡检结果类型分布
  getInspectionTypeDistribution: (params?: any) => {
    return api.get('/dashboard/inspection-type-distribution', { params })
  }
}

// AI 相关API
export const aiApi = {
  // AI 健康检查
  healthCheck: () => {
    return api.get('/ai/health')
  },

  // 提交单个分析结果
  submitAnalysisResult: (data: {
    mission_id: number
    video_id: number
    target_type: string
    occurred_time: string
    bounding_box?: any
    confidence?: number
  }) => {
    return api.post('/ai/analysis/results', data)
  },

  // 批量提交分析结果
  submitAnalysisResultsBatch: (results: Array<{
    mission_id: number
    video_id: number
    target_type: string
    occurred_time: string
    bounding_box?: any
    confidence?: number
  }>) => {
    return api.post('/ai/analysis/results/batch', { results })
  }
}
