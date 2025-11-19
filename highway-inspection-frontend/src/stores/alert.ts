import { defineStore } from 'pinia'
import { ref } from 'vue'
import { alertApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

// 后端告警模型
export interface Alert {
  id: number
  title: string
  event_type: string
  severity: 'low' | 'medium' | 'high'
  road_section: string
  occurred_time: string
  video_id: number
  mission_id: number
  status: 'new' | 'confirmed' | 'processing' | 'closed'
  created_at: string
  updated_at: string
  video?: any
  mission?: any
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

interface PaginatedResponse {
  items: Alert[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<Alert[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 从后端获取告警列表
  const fetchAlerts = async (page: number = 1, page_size: number = 20, status?: string, severity?: string, mission_id?: number) => {
    loading.value = true
    try {
      const params: any = { page, page_size }
      if (status) params.status = status
      if (severity) params.severity = severity
      if (mission_id) params.mission_id = mission_id
      
      const response = await alertApi.getAlerts(params) as ApiResponse<PaginatedResponse>
      
      if (response.code === 200 && response.data) {
        alerts.value = response.data.items
        total.value = response.data.total
        currentPage.value = response.data.page
        pageSize.value = response.data.page_size
      } else {
        // 后端返回了错误响应，应该显示给用户
        ElMessage.error(response.message || '获取告警列表失败')
        // 确保有默认值，避免页面崩溃
        alerts.value = []
        total.value = 0
      }
    } catch (error: any) {
      console.error('获取告警列表失败:', error)
      
      // 区分网络错误和后端返回的错误
      const isNetworkError = !error.response // 没有 response 说明是网络错误（无法连接后端）
      const isBackendError = error.response // 有 response 说明后端返回了错误响应
      
      // 只在网络错误时静默处理（前端单独开发场景）
      // 后端返回的错误应该显示给用户
      if (isBackendError) {
        ElMessage.error(error.response?.data?.message || '获取告警列表失败')
      } else if (!import.meta.env.DEV) {
        // 生产环境的网络错误也显示
        ElMessage.error('网络连接失败，请检查后端服务')
      }
      // 开发环境的网络错误静默处理，不干扰前端开发
      
      // 确保有默认值，避免页面崩溃
      alerts.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 初始化数据（兼容旧接口）
  const initData = async (page: number = 1, page_size: number = 20, status?: string, severity?: string, mission_id?: number) => {
    await fetchAlerts(page, page_size, status, severity, mission_id)
  }

  // 更新告警状态
  const updateAlert = async (id: number, data: { status?: 'new' | 'confirmed' | 'processing' | 'closed', notes?: string }) => {
    loading.value = true
    try {
      const response = await alertApi.updateAlert(id, data) as ApiResponse<Alert>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('告警状态更新成功')
        const index = alerts.value.findIndex(a => a.id === id)
        if (index !== -1) {
          alerts.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '更新告警失败')
      }
    } catch (error: any) {
      console.error('更新告警失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '更新告警失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取活跃告警
  const fetchActiveAlerts = async () => {
    try {
      const response = await alertApi.getActiveAlerts() as ApiResponse<Alert[]>
      if (response.code === 200 && response.data) {
        return response.data
      }
      return []
    } catch (error: any) {
      console.error('获取活跃告警失败:', error)
      return []
    }
  }

  // 统计数据
  const getStatistics = () => {
    return {
      total: total.value || alerts.value.length,
      byStatus: {
        new: alerts.value.filter(a => a.status === 'new').length,
        confirmed: alerts.value.filter(a => a.status === 'confirmed').length,
        processing: alerts.value.filter(a => a.status === 'processing').length,
        closed: alerts.value.filter(a => a.status === 'closed').length
      },
      bySeverity: {
        low: alerts.value.filter(a => a.severity === 'low').length,
        medium: alerts.value.filter(a => a.severity === 'medium').length,
        high: alerts.value.filter(a => a.severity === 'high').length
      }
    }
  }

  return {
    alerts,
    loading,
    total,
    currentPage,
    pageSize,
    initData,
    fetchAlerts,
    updateAlert,
    fetchActiveAlerts,
    getStatistics
  }
})
