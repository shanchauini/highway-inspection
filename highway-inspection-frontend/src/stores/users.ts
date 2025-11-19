import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi, authApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

// 后端用户模型：id, username, role, created_at, updated_at
export interface User {
  id: number
  username: string
  role: 'admin' | 'operator'
  created_at: string
  updated_at: string
}

export interface UserStatistics {
  total: number
  byRole: {
    admin: number
    operator: number
  }
}

// 后端API响应格式
interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

interface PaginatedResponse {
  items: User[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 从后端获取用户列表
  const fetchUsers = async (page: number = 1, page_size: number = 20, role?: string) => {
    loading.value = true
    try {
      const params: any = { page, page_size }
      if (role) {
        params.role = role
      }
      
      const response = await userApi.getUsers(params) as ApiResponse<PaginatedResponse>
      
      if (response.code === 200 && response.data) {
        users.value = response.data.items
        total.value = response.data.total
        currentPage.value = response.data.page
        pageSize.value = response.data.page_size
      } else {
        ElMessage.error(response.message || '获取用户列表失败')
      }
    } catch (error: any) {
      console.error('获取用户列表失败:', error)
      ElMessage.error(error.response?.data?.message || '获取用户列表失败')
    } finally {
      loading.value = false
    }
  }

  // 初始化数据（兼容旧接口）
  const initData = async (page: number = 1, page_size: number = 20, role?: string) => {
    await fetchUsers(page, page_size, role)
  }

  // 创建用户（通过注册接口）
  const createUser = async (username: string, password: string, role: 'admin' | 'operator' = 'operator') => {
    loading.value = true
    try {
      const response = await authApi.register(username, password, role) as ApiResponse<User>
      
      if (response.code === 200 && response.data) {
        // 刷新列表
        await fetchUsers(currentPage.value, pageSize.value)
        return response.data
      } else {
        throw new Error(response.message || '创建用户失败')
      }
    } catch (error: any) {
      console.error('创建用户失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '创建用户失败'
      ElMessage.error(errorMessage)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新用户
  const updateUser = async (id: number, updates: { password?: string; role?: 'admin' | 'operator' }) => {
    loading.value = true
    try {
      const response = await userApi.updateUser(id.toString(), updates) as ApiResponse<User>
      
      if (response.code === 200 && response.data) {
        // 更新本地数据
        const index = users.value.findIndex(u => u.id === id)
        if (index !== -1) {
          users.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '更新用户失败')
      }
    } catch (error: any) {
      console.error('更新用户失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '更新用户失败'
      ElMessage.error(errorMessage)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除用户
  const deleteUser = async (id: number) => {
    loading.value = true
    try {
      const response = await userApi.deleteUser(id.toString()) as ApiResponse
      
      if (response.code === 200) {
        // 从列表中移除
        const index = users.value.findIndex(u => u.id === id)
        if (index !== -1) {
          users.value.splice(index, 1)
          total.value--
        }
        return true
      } else {
        throw new Error(response.message || '删除用户失败')
      }
    } catch (error: any) {
      console.error('删除用户失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '删除用户失败'
      ElMessage.error(errorMessage)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置密码
  const resetPassword = async (id: number, newPassword: string) => {
    try {
      await updateUser(id, { password: newPassword })
      return true
    } catch (error) {
      throw error
    }
  }

  // 获取用户详情
  const getUserById = async (id: number) => {
    loading.value = true
    try {
      const response = await userApi.getUserById(id) as ApiResponse<User>
      if (response.code === 200 && response.data) {
        return response.data
      }
      return null
    } catch (error: any) {
      console.error('获取用户详情失败:', error)
      // 如果API失败，尝试从列表中查找
      const user = users.value.find(u => u.id === id)
      return user || null
    } finally {
      loading.value = false
    }
  }

  // 获取统计数据
  const getStatistics = (): UserStatistics => {
    const stats: UserStatistics = {
      total: total.value || users.value.length,
      byRole: {
        admin: 0,
        operator: 0
      }
    }

    users.value.forEach(user => {
      // 按角色统计
      if (user.role === 'admin') {
        stats.byRole.admin++
      } else if (user.role === 'operator') {
        stats.byRole.operator++
      }
    })

    return stats
  }

  // 检查用户名是否存在
  const isUsernameExists = (username: string, excludeId?: number) => {
    return users.value.some(u => 
      u.username === username && u.id !== excludeId
    )
  }

  return {
    users,
    loading,
    total,
    currentPage,
    pageSize,
    initData,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    resetPassword,
    getUserById,
    getStatistics,
    isUsernameExists
  }
})
