import { defineStore } from 'pinia'
import { ref } from 'vue'
import { flightApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

// 后端飞行申请模型
export interface FlightApplication {
  id: number
  user_id: number
  drone_model: string
  task_purpose: string
  planned_airspace_id: number
  planned_start_time: string
  planned_end_time: string
  total_time: number // 分钟
  route: any // GeoJSON格式
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'expired' | 'terminated'
  is_long_term: boolean
  long_term_start?: string
  long_term_end?: string
  rejection_reason?: string
  created_at: string
  updated_at: string
  applicant?: any
  airspace?: any
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

interface PaginatedResponse {
  items: FlightApplication[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useFlightStore = defineStore('flight', () => {
  const applications = ref<FlightApplication[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 从后端获取飞行申请列表
  const fetchFlights = async (page: number = 1, page_size: number = 20, status?: string) => {
    loading.value = true
    try {
      const params: any = { page, page_size }
      if (status) params.status = status
      
      const response = await flightApi.getFlights(params) as ApiResponse<PaginatedResponse>
      
      if (response.code === 200 && response.data) {
        applications.value = response.data.items
        total.value = response.data.total
        currentPage.value = response.data.page
        pageSize.value = response.data.page_size
      } else {
        ElMessage.error(response.message || '获取申请列表失败')
      }
    } catch (error: any) {
      console.error('获取申请列表失败:', error)
      ElMessage.error(error.response?.data?.message || '获取申请列表失败')
    } finally {
      loading.value = false
    }
  }

  // 初始化数据（兼容旧接口）
  const initData = async (page: number = 1, page_size: number = 20, status?: string) => {
    await fetchFlights(page, page_size, status)
  }

  // 获取飞行申请详情
  const getFlightById = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.getFlightById(id) as ApiResponse<FlightApplication>
      
      if (response.code === 200 && response.data) {
        return response.data
      } else {
        throw new Error(response.message || '获取申请详情失败')
      }
    } catch (error: any) {
      console.error('获取申请详情失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '获取申请详情失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建飞行申请
  const createFlight = async (data: {
    drone_model: string
    task_purpose: string
    planned_airspace_id: number
    planned_start_time: string
    planned_end_time: string
    total_time: number
    route: any
    is_long_term?: boolean
    long_term_start?: string
    long_term_end?: string
  }) => {
    loading.value = true
    try {
      const response = await flightApi.createFlight(data) as ApiResponse<FlightApplication>
      
      if (response.code === 200 || response.code === 201) {
        if (response.data) {
          ElMessage.success('申请创建成功')
          await fetchFlights(currentPage.value, pageSize.value)
          return response.data
        }
      } else {
        throw new Error(response.message || '创建申请失败')
      }
    } catch (error: any) {
      console.error('创建申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '创建申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新飞行申请
  const updateFlight = async (id: number, data: Partial<FlightApplication>) => {
    loading.value = true
    try {
      const response = await flightApi.updateFlight(id, data) as ApiResponse<FlightApplication>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('申请更新成功')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '更新申请失败')
      }
    } catch (error: any) {
      console.error('更新申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '更新申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 提交飞行申请
  const submitFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.submitFlight(id) as ApiResponse<FlightApplication>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('申请提交成功')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '提交申请失败')
      }
    } catch (error: any) {
      console.error('提交申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '提交申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 批准飞行申请
  const approveFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.approveFlight(id) as ApiResponse<FlightApplication>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('申请批准成功')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '批准申请失败')
      }
    } catch (error: any) {
      console.error('批准申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '批准申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 驳回飞行申请
  const rejectFlight = async (id: number, rejection_reason: string) => {
    loading.value = true
    try {
      const response = await flightApi.rejectFlight(id, { rejection_reason }) as ApiResponse<FlightApplication>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('申请已驳回')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '驳回申请失败')
      }
    } catch (error: any) {
      console.error('驳回申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '驳回申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除草稿申请
  const deleteFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.deleteFlight(id) as ApiResponse

      if (response.code === 200) {
        ElMessage.success(response.message || '申请已删除')
        applications.value = applications.value.filter(a => a.id !== id)
        total.value = Math.max(0, total.value - 1)
        return true
      } else {
        throw new Error(response.message || '删除申请失败')
      }
    } catch (error: any) {
      console.error('删除申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '删除申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 撤回待审批申请
  const withdrawFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.withdrawFlight(id) as ApiResponse<FlightApplication>

      if (response.code === 200 && response.data) {
        ElMessage.success(response.message || '申请已撤回')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '撤回申请失败')
      }
    } catch (error: any) {
      console.error('撤回申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '撤回申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 终止已批准申请
  const terminateFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.terminateFlight(id) as ApiResponse<FlightApplication>

      if (response.code === 200 && response.data) {
        ElMessage.success(response.message || '计划已终止')
        const index = applications.value.findIndex(a => a.id === id)
        if (index !== -1) {
          applications.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '终止申请失败')
      }
    } catch (error: any) {
      console.error('终止申请失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '终止申请失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 放飞申请
  const launchFlight = async (id: number) => {
    loading.value = true
    try {
      const response = await flightApi.launchFlight(id) as ApiResponse<any>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('放飞成功')
        await fetchFlights(currentPage.value, pageSize.value)
        return response.data
      } else {
        throw new Error(response.message || '放飞失败')
      }
    } catch (error: any) {
      console.error('放飞失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '放飞失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取待审批申请列表
  const fetchPendingFlights = async () => {
    loading.value = true
    try {
      const response = await flightApi.getPendingFlights() as ApiResponse<FlightApplication[]>
      
      if (response.code === 200 && response.data) {
        return response.data
      }
      return []
    } catch (error: any) {
      console.error('获取待审批列表失败:', error)
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    applications,
    loading,
    total,
    currentPage,
    pageSize,
    initData,
    fetchFlights,
    getFlightById,
    createFlight,
    updateFlight,
    deleteFlight,
    submitFlight,
    approveFlight,
    rejectFlight,
    withdrawFlight,
    terminateFlight,
    launchFlight,
    fetchPendingFlights
  }
})
