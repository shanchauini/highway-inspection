import { defineStore } from 'pinia'
import { ref } from 'vue'
import { missionApi, videoApi, alertApi } from '@/api/modules'

export interface Mission {
  id: number
  flight_application_id: number
  operator_id: number
  route: number[][] | { coordinates?: number[][] } | any
  start_time?: string | null
  end_time?: string | null
  status: 'executing' | 'completed'
  created_at?: string
  updated_at?: string
  route_distance?: number // 航线距离（公里）
  flight_speed?: number // 飞行速度（公里/小时）
  operator?: any
  flight_application?: any
}

export const useMissionStore = defineStore('mission', () => {
  const missions = ref<Mission[]>([])
  const activeMissions = ref<Mission[]>([])
  const missionDetail = ref<Mission | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)

  async function fetchMissions(params?: { status?: 'executing' | 'completed'; page?: number; page_size?: number }) {
    try {
      loading.value = true
      const query = {
        page: params?.page ?? currentPage.value,
        page_size: params?.page_size ?? pageSize.value,
        status: params?.status
      }
      const res = await missionApi.getMissions(query)
      if (res.data?.items) {
        missions.value = res.data.items
        total.value = res.data.total ?? 0
        currentPage.value = res.data.page ?? query.page
        pageSize.value = res.data.page_size ?? query.page_size
      } else if (Array.isArray(res.data)) {
        // 兼容非分页返回
        missions.value = res.data
        total.value = res.data.length
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchActiveMissions() {
    try {
      loading.value = true
      const res = await missionApi.getActiveMissions()
      activeMissions.value = res.data || []
    } finally {
      loading.value = false
    }
  }

  async function getMissionById(id: number) {
    const res = await missionApi.getMissionById(id)
    missionDetail.value = res.data
    return res.data as Mission
  }

  async function completeMission(id: number) {
    const res = await missionApi.completeMission(id)
    return res.data
  }

  // 辅助：根据任务ID加载相关视频与告警（后端支持 mission_id 作为查询参数时可用）
  async function fetchMissionVideos(id: number) {
    const res = await videoApi.getVideos({ mission_id: id })
    return res.data?.items ?? res.data ?? []
  }

  async function fetchMissionAlerts(id: number) {
    const res = await alertApi.getAlerts({ mission_id: id })
    return res.data?.items ?? res.data ?? []
  }

  return {
    missions,
    activeMissions,
    missionDetail,
    total,
    currentPage,
    pageSize,
    loading,
    fetchMissions,
    fetchActiveMissions,
    getMissionById,
    completeMission,
    fetchMissionVideos,
    fetchMissionAlerts
  }
})
