import { defineStore } from 'pinia'
import { ref } from 'vue'
import { videoApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

// 后端视频模型
export interface Video {
  id: number
  mission_id: number
  video_path: string
  collected_time: string
  road_section: string
  file_format: string
  file_size?: number
  duration?: number
  created_at: string
  mission?: any
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

interface PaginatedResponse {
  items: Video[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useVideoStore = defineStore('video', () => {
  const videos = ref<Video[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 从后端获取视频列表
  const fetchVideos = async (page: number = 1, page_size: number = 20, mission_id?: number) => {
    loading.value = true
    try {
      const params: any = { page, page_size }
      if (mission_id) params.mission_id = mission_id
      
      const response = await videoApi.getVideos(params) as ApiResponse<PaginatedResponse>
      
      if (response.code === 200 && response.data) {
        videos.value = response.data.items
        total.value = response.data.total
        currentPage.value = response.data.page
        pageSize.value = response.data.page_size
      } else {
        ElMessage.error(response.message || '获取视频列表失败')
      }
    } catch (error: any) {
      console.error('获取视频列表失败:', error)
      ElMessage.error(error.response?.data?.message || '获取视频列表失败')
    } finally {
      loading.value = false
    }
  }

  // 初始化数据（兼容旧接口）
  const initData = async (page: number = 1, page_size: number = 20, mission_id?: number) => {
    await fetchVideos(page, page_size, mission_id)
  }

  // 创建视频记录
  const createVideo = async (data: {
    mission_id: number
    video_path: string
    collected_time: string
    road_section: string
    file_format?: string
    file_size?: number
    duration?: number
  }) => {
    loading.value = true
    try {
      const response = await videoApi.uploadVideo(data) as ApiResponse<Video>
      
      if (response.code === 200 || response.code === 201) {
        if (response.data) {
          ElMessage.success('视频记录创建成功')
          await fetchVideos(currentPage.value, pageSize.value)
          return response.data
        }
      } else {
        throw new Error(response.message || '创建视频记录失败')
      }
    } catch (error: any) {
      console.error('创建视频记录失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '创建视频记录失败'
      ElMessage.error(errorMsg)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取视频分析结果
  const fetchAnalysisResults = async (id: number) => {
    try {
      const response = await videoApi.getAnalysisResults(id) as ApiResponse<any[]>
      if (response.code === 200 && response.data) {
        return response.data
      }
      return []
    } catch (error: any) {
      console.error('获取分析结果失败:', error)
      return []
    }
  }

  return {
    videos,
    loading,
    total,
    currentPage,
    pageSize,
    initData,
    fetchVideos,
    createVideo,
    fetchAnalysisResults
  }
})

