import { defineStore } from 'pinia'
import { ref } from 'vue'
import { airspaceApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

// 后端空域模型
export interface Airspace {
  id: number
  name: string
  number: string
  type: 'suitable' | 'restricted' | 'no_fly'
  area: {
    type: 'Polygon'
    coordinates: number[][][] // [[[lng, lat], [lng, lat], ...]]
  }
  remark?: string
  status: 'available' | 'occupied' | 'unavailable'
  created_at: string
  updated_at: string
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

interface PaginatedResponse {
  items: Airspace[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useAirspaceStore = defineStore('airspace', () => {
  const airspaces = ref<Airspace[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 从后端获取空域列表
  const fetchAirspaces = async (page: number = 1, page_size: number = 20, type?: string, status?: string) => {
    loading.value = true
    try {
      const params: any = { page, page_size }
      if (type) params.type = type
      if (status) params.status = status
      
      const response = await airspaceApi.getAirspaces(params) as ApiResponse<PaginatedResponse>
      
      if (response.code === 200 && response.data) {
        airspaces.value = response.data.items
        total.value = response.data.total
        currentPage.value = response.data.page
        pageSize.value = response.data.page_size
      } else {
        ElMessage.error(response.message || '获取空域列表失败')
      }
    } catch (error: any) {
      console.error('获取空域列表失败:', error)
      ElMessage.error(error.response?.data?.message || '获取空域列表失败')
    } finally {
      loading.value = false
    }
  }

  // 初始化数据（兼容旧接口）
  const initData = async (page: number = 1, page_size: number = 20, type?: string, status?: string) => {
    await fetchAirspaces(page, page_size, type, status)
  }

  // 创建空域
  const createAirspace = async (data: {
    name: string
    number: string
    type: 'suitable' | 'restricted' | 'no_fly'
    area: any
    remark?: string
    status?: 'available' | 'occupied' | 'unavailable'
  }) => {
    loading.value = true
    try {
      const response = await airspaceApi.createAirspace(data) as ApiResponse<Airspace>
      
      if (response.code === 200 || response.code === 201) {
        if (response.data) {
          ElMessage.success('空域创建成功')
          await fetchAirspaces(currentPage.value, pageSize.value)
          return response.data
        }
      } else {
        throw new Error(response.message || '创建空域失败')
      }
    } catch (error: any) {
      console.error('创建空域失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '创建空域失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新空域
  const updateAirspace = async (id: number, data: Partial<Airspace>) => {
    loading.value = true
    try {
      const response = await airspaceApi.updateAirspace(id, data) as ApiResponse<Airspace>
      
      if (response.code === 200 && response.data) {
        ElMessage.success('空域更新成功')
        // 更新本地数据
        const index = airspaces.value.findIndex(a => a.id === id)
        if (index !== -1) {
          airspaces.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '更新空域失败')
      }
    } catch (error: any) {
      console.error('更新空域失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '更新空域失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除空域
  const deleteAirspace = async (id: number) => {
    loading.value = true
    try {
      const response = await airspaceApi.deleteAirspace(id) as ApiResponse
      
      if (response.code === 200) {
        ElMessage.success('空域删除成功')
        // 从列表中移除
        const index = airspaces.value.findIndex(a => a.id === id)
        if (index !== -1) {
          airspaces.value.splice(index, 1)
          total.value--
        }
        return true
      } else {
        throw new Error(response.message || '删除空域失败')
      }
    } catch (error: any) {
      console.error('删除空域失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '删除空域失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取可用空域
  const getAvailableAirspaces = async () => {
    try {
      const response = await airspaceApi.getAvailableAirspaces() as ApiResponse<Airspace[]>
      if (response.code === 200 && response.data) {
        return response.data
      }
      return []
    } catch (error: any) {
      console.error('获取可用空域失败:', error)
      return []
    }
  }

  // 检查空域冲突
  const checkConflict = async (id: number, startTime: string, endTime: string) => {
    try {
      const response = await airspaceApi.checkConflict(id, { start_time: startTime, end_time: endTime }) as ApiResponse<{ has_conflict: boolean }>
      if (response.code === 200 && response.data) {
        return response.data.has_conflict
      }
      return false
    } catch (error: any) {
      console.error('检查空域冲突失败:', error)
      return false
    }
  }

  // 统计数据
  const getStatistics = () => {
    return {
      total: total.value || airspaces.value.length,
      available: airspaces.value.filter(a => a.status === 'available').length,
      occupied: airspaces.value.filter(a => a.status === 'occupied').length,
      unavailable: airspaces.value.filter(a => a.status === 'unavailable').length,
      suitable: airspaces.value.filter(a => a.type === 'suitable').length,
      restricted: airspaces.value.filter(a => a.type === 'restricted').length,
      no_fly: airspaces.value.filter(a => a.type === 'no_fly').length
    }
  }

  return {
    airspaces,
    loading,
    total,
    currentPage,
    pageSize,
    initData,
    fetchAirspaces,
    createAirspace,
    updateAirspace,
    deleteAirspace,
    getAvailableAirspaces,
    checkConflict,
    getStatistics
  }
})
