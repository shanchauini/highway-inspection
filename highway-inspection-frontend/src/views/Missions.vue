<template>
  <div class="missions-overview">
    <el-card class="left-panel cosmic-card" shadow="never">
      <template #header>
        <div class="panel-header">
          <span class="cosmic-title-small">进行中任务</span>
          <div>
            <button class="cosmic-button" @click="refresh" :disabled="missionStore.loading" style="padding: 6px 12px; font-size: 12px;">
              刷新
            </button>
          </div>
        </div>
      </template>

      <el-empty v-if="missionStore.activeMissions.length === 0" description="暂无进行中任务" />
      <el-scrollbar v-else class="mission-list">
        <div
          v-for="m in missionStore.activeMissions"
          :key="m.id"
          :class="['mission-item', { active: selectedMission?.id === m.id }]"
          @click="selectMission(m)"
        >
          <div class="title">
            <el-tag type="success" size="small">执行中</el-tag>
            <span class="id">#{{ m.id }}</span>
          </div>
          <div class="row"><span class="label">操作员：</span><span class="val">{{ m.operator?.username || m.operator_id }}</span></div>
          <div class="row"><span class="label">申请ID：</span><span class="val">{{ m.flight_application_id }}</span></div>
          <div class="row"><span class="label">开始时间：</span><span class="val">{{ formatTime(m.start_time) }}</span></div>
        </div>
      </el-scrollbar>
    </el-card>

    <el-card class="map-panel cosmic-card" shadow="never">
      <template #header>
        <div class="panel-header">
          <span class="cosmic-title-small">任务地图</span>
          <div>
            <button v-if="selectedMission" class="cosmic-button" @click="viewDetail" style="padding: 6px 12px; font-size: 12px;">查看详情</button>
          </div>
        </div>
      </template>
      <div id="mission-map" class="map"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ElMessage } from 'element-plus'
import { useMissionStore, type Mission } from '@/stores/mission'

const missionStore = useMissionStore()
const selectedMission = ref<Mission | null>(null)

let map: L.Map | null = null
let routeLayers = new Map<number, L.Polyline<any>>() // 存储所有航线图层
let droneMarkers = new Map<number, L.Marker<any>>() // 存储所有无人机标记
let droneAnimations = new Map<number, {
  positions: [number, number][],
  currentIndex: number,
  intervalId: number | null
}>()

// 生成随机颜色
const getRandomColor = () => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

const initMap = () => {
  map = L.map('mission-map', {
    center: [39.9, 116.4],
    zoom: 11,
    zoomControl: true
  })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)
}

// 渲染所有任务
const renderMissions = (missions: Mission[]) => {
  if (!map) return
  
  // 清除现有的图层
  routeLayers.forEach(layer => map?.removeLayer(layer))
  droneMarkers.forEach(marker => map?.removeLayer(marker))
  
  // 清除动画定时器
  droneAnimations.forEach(anim => {
    if (anim.intervalId) clearInterval(anim.intervalId)
  })
  
  // 清空存储
  routeLayers.clear()
  droneMarkers.clear()
  droneAnimations.clear()
  
  // 为每个任务创建图层
  missions.forEach(mission => {
    const latlngs = coordsFromRoute(mission.route)
    if (latlngs.length === 0) return
    
    // 生成随机颜色
    const routeColor = getRandomColor()
    
    // 创建航线图层
    const routeLayer = L.polyline(latlngs, { 
      color: routeColor, 
      weight: 3
    }).addTo(map)
    routeLayers.set(mission.id, routeLayer)
    
    // 创建无人机图标
    const droneIcon = L.divIcon({
      className: 'drone-icon',
      html: '🛩️',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    })
    
    // 创建无人机标记
    const droneMarker = L.marker(latlngs[0], { icon: droneIcon }).addTo(map)
    droneMarkers.set(mission.id, droneMarker)
    
    // 初始化动画数据
    droneAnimations.set(mission.id, {
      positions: latlngs,
      currentIndex: 0,
      intervalId: null
    })
    
    // 启动无人机移动动画
    startDroneAnimation(mission.id)
  })
  
  // 调整地图视野
  if (missions.length > 0) {
    const allBounds = L.latLngBounds()
    missions.forEach(mission => {
      const latlngs = coordsFromRoute(mission.route)
      if (latlngs.length > 0) {
        const bounds = L.latLngBounds(latlngs)
        allBounds.extend(bounds)
      }
    })
    map.fitBounds(allBounds, { padding: [20, 20] })
  }
}

// 启动无人机动画
const startDroneAnimation = (missionId: number) => {
  const animation = droneAnimations.get(missionId)
  const droneMarker = droneMarkers.get(missionId)
  
  if (!animation || !droneMarker || animation.positions.length < 2) return
  
  // 清除已有的定时器
  if (animation.intervalId) {
    clearInterval(animation.intervalId)
  }
  
  // 启动新的动画循环
  animation.intervalId = window.setInterval(() => {
    animation.currentIndex = (animation.currentIndex + 1) % animation.positions.length
    droneMarker.setLatLng(animation.positions[animation.currentIndex])
  }, 1000) // 每秒移动到下一个点
}

// 突出显示选中的任务航线
const highlightMissionRoute = (missionId: number | null) => {
  routeLayers.forEach((layer, id) => {
    if (id === missionId) {
      // 突出显示选中的航线
      layer.setStyle({
        weight: 5,
        shadowBlur: 10
      })
    } else {
      // 恢复其他航线的样式
      layer.setStyle({
        weight: 3,
        shadowBlur: 0
      })
    }
  })
}

const coordsFromRoute = (route: any): Array<[number, number]> => {
  if (!route) return []
  // 兼容两种格式：直接数组[[lng,lat], ...] 或 GeoJSON {coordinates: [[lng,lat], ...]}
  const raw = Array.isArray(route) ? route : (route.coordinates || [])
  // 转换为 [lat, lng]
  return raw.map((c: number[]) => [c[1], c[0]] as [number, number]).filter((p: any) => Array.isArray(p) && p.length === 2)
}

const selectMission = (m: Mission) => {
  selectedMission.value = m
  highlightMissionRoute(m.id)
}

const refresh = async () => {
  try {
    await missionStore.fetchActiveMissions()
    renderMissions(missionStore.activeMissions)
    
    // 如果有任务，选择第一个作为默认选中
    if (missionStore.activeMissions.length > 0 && !selectedMission.value) {
      selectedMission.value = missionStore.activeMissions[0]
      highlightMissionRoute(selectedMission.value.id)
    }
  } catch (e) {
    ElMessage.error('刷新任务失败')
  }
}

const viewDetail = () => {
  if (!selectedMission.value) return
  window.open(`#/_mission/${selectedMission.value.id}`, '_blank')
}

onMounted(async () => {
  await missionStore.fetchActiveMissions()
  await nextTick()
  initMap()
  renderMissions(missionStore.activeMissions)
  
  // 如果有任务，选择第一个作为默认选中
  if (missionStore.activeMissions.length > 0 && !selectedMission.value) {
    selectedMission.value = missionStore.activeMissions[0]
    highlightMissionRoute(selectedMission.value.id)
  }
})

onBeforeUnmount(() => {
  // 清除动画定时器
  droneAnimations.forEach(anim => {
    if (anim.intervalId) {
      clearInterval(anim.intervalId)
    }
  })
  
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => missionStore.activeMissions, () => {
  renderMissions(missionStore.activeMissions)
  
  if (selectedMission.value) {
    const found = missionStore.activeMissions.find(x => x.id === selectedMission.value?.id)
    if (!found) {
      selectedMission.value = missionStore.activeMissions[0] || null
    }
    // 更新突出显示
    if (selectedMission.value) {
      highlightMissionRoute(selectedMission.value.id)
    }
  }
}, { deep: true })
</script>

<style scoped>
.missions-overview {
  height: 100%;
  display: flex;
  gap: 16px;
}
.left-panel {
  width: 360px;
  flex-shrink: 0;
}
.map-panel {
  flex: 1;
  min-width: 400px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.mission-list {
  max-height: 600px;
}
.mission-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}
.mission-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}
.mission-item .title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.mission-item .id {
  font-weight: 600;
}
.row {
  display: flex;
  font-size: 13px;
  margin: 2px 0;
}
.label {
  color: #909399;
  width: 70px;
}
.val {
  color: #606266;
  flex: 1;
}
.map {
  height: 600px;
  border-radius: 8px;
  overflow: hidden;
}
.drone-icon {
  font-size: 20px;
  line-height: 24px;
}
</style>


