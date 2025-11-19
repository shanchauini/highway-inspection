<template>
  <el-card class="page-card cosmic-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="cosmic-title-small">地图总览</span>
        <div class="tools">
          <button class="cosmic-button" @click="locate">定位</button>
          <button class="cosmic-button" @click="viewDroneVideo">查看无人机视频画面</button>
        </div>
      </div>
    </template>
    <div class="map-grid">
      <div class="grid-left">
        <div class="panel-title">
          <span class="panel-title-text" style="color: #fff;">进行中任务</span>
          <button class="cosmic-button cosmic-button-small" @click="refreshMissions" :disabled="missionStore.loading">刷新</button>
        </div>
        <el-empty v-if="missionStore.activeMissions.length === 0" description="暂无进行中任务" />
        <el-scrollbar v-else class="missions-list">
          <div 
            v-for="m in missionStore.activeMissions" 
            :key="m.id" 
            :class="['mission-item', {active: selectedMission?.id === m.id}]"
            @click="selectMission(m)"
          >
            <div class="line">
              <el-tag type="success" size="small">执行中</el-tag>
              <span class="mid">#{{ m.id }}</span>
            </div>
            <div class="kv"><span class="k">操作员</span><span class="v">{{ m.operator?.username || m.operator_id }}</span></div>
            <div class="kv"><span class="k">开始</span><span class="v">{{ formatTime(m.start_time) }}</span></div>
          </div>
        </el-scrollbar>
      </div>

      <div class="grid-center">
        <div id="map" class="map-container"></div>
      </div>

      <div class="grid-right">
        <div class="panel-title">
          <span class="panel-title-text" style="color: #fff;">任务详情</span>
          <button class="cosmic-button cosmic-button-small" @click="selectedMission = null" :disabled="!selectedMission">清空</button>
        </div>
        <el-empty v-if="!selectedMission" description="请选择左侧任务" />
        <el-scrollbar v-else class="detail-content">
          <div class="kv"><span class="k">任务ID</span><span class="v">#{{ selectedMission.id }}</span></div>
          <div class="kv"><span class="k">操作员</span><span class="v">{{ selectedMission.operator?.username || selectedMission.operator_id }}</span></div>
          <div class="kv" v-if="selectedMission.flight_application">
            <span class="k">无人机型号</span>
            <span class="v">{{ selectedMission.flight_application.drone_model || '-' }}</span>
          </div>
          <div class="kv" v-if="selectedMission.flight_application">
            <span class="k">任务目的</span>
            <span class="v">{{ selectedMission.flight_application.task_purpose || '-' }}</span>
          </div>
          <div class="kv" v-if="selectedMission.flight_application">
            <span class="k">计划开始时间</span>
            <span class="v">{{ formatTime(selectedMission.flight_application.planned_start_time) }}</span>
          </div>
          <div class="kv" v-if="selectedMission.flight_application">
            <span class="k">计划结束时间</span>
            <span class="v">{{ formatTime(selectedMission.flight_application.planned_end_time) }}</span>
          </div>
          <div class="kv" v-if="selectedMission.flight_application">
            <span class="k">飞行总时长</span>
            <span class="v">{{ selectedMission.flight_application.total_time || 0 }} 分钟</span>
          </div>
          <div class="kv">
            <span class="k">实际开始时间</span>
            <span class="v">{{ formatTime(selectedMission.start_time) }}</span>
          </div>
          <div class="kv" v-if="selectedMission.end_time">
            <span class="k">实际结束时间</span>
            <span class="v">{{ formatTime(selectedMission.end_time) }}</span>
          </div>
          <div class="kv">
            <span class="k">飞行速度</span>
            <span class="v">{{ selectedMission.flight_speed ? `${selectedMission.flight_speed} km/h` : '-' }}</span>
          </div>
          <div class="kv" v-if="selectedMission.route_distance">
            <span class="k">航线距离</span>
            <span class="v">{{ selectedMission.route_distance }} km</span>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </el-card>
  
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useMapStore } from '@/stores/map'
import { useMissionStore, type Mission } from '@/stores/mission'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'

dayjs.extend(utc)

const router = useRouter()
let map: L.Map | null = null
const mapStore = useMapStore()
const missionStore = useMissionStore()
const selectedMission = ref<Mission | null>(null)
let routeLayers = new Map<number, L.Polyline<any>>() // 存储所有航线图层
let droneMarkers = new Map<number, L.Marker<any>>() // 存储所有无人机标记
let droneAnimations = new Map<number, {
  positions: [number, number][],
  currentIndex: number,
  intervalId: number | null
}>()

const formatTime = (t?: string | null) => {
  if (!t) return '-'
  // UTC时间转换为本地时间显示
  return dayjs.utc(t).local().format('YYYY/MM/DD HH:mm:ss')
}

// 生成随机颜色
const getRandomColor = () => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

const coordsFromRoute = (route: any): Array<[number, number]> => {
  if (!route) return []
  const raw = Array.isArray(route) ? route : (route.coordinates || [])
  return raw.map((c: number[]) => [c[1], c[0]] as [number, number]).filter((p: any) => Array.isArray(p) && p.length === 2)
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
      iconSize: [24,24], 
      iconAnchor: [12,12] 
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
    map.fitBounds(allBounds, { padding: [24, 24] })
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

// 选择任务
const selectMission = (m: Mission) => {
  selectedMission.value = m
  highlightMissionRoute(m.id)
}

// 刷新任务
const refreshMissions = async () => {
  await missionStore.fetchActiveMissions()
  renderMissions(missionStore.activeMissions)
  
  // 如果有任务，选择第一个作为默认选中
  if (missionStore.activeMissions.length > 0 && !selectedMission.value) {
    selectedMission.value = missionStore.activeMissions[0]
    highlightMissionRoute(selectedMission.value.id)
  }
}

onMounted(async () => {
  await nextTick()
  
  // 延迟一下确保DOM完全渲染
  setTimeout(() => {
    try {
      const mapElement = document.getElementById('map')
      if (!mapElement) {
        console.error('地图容器未找到')
        return
      }
      
      // 创建地图实例
      map = L.map('map', {
        center: [39.9042, 116.4074], // 北京坐标
        zoom: 10,
        zoomControl: true
      })

      // 使用高德地图（国内访问快速稳定）
      L.tileLayer('https://wprd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', {
          maxZoom: 18,
          attribution: '© 高德地图',
          subdomains: ['1', '2', '3', '4']
      }).addTo(map)

      // 触发地图大小调整
      setTimeout(() => {
        map?.invalidateSize()
      }, 100)

      // 加载进行中任务并渲染
      refreshMissions()
    } catch (error) {
      console.error('地图初始化失败:', error)
    }
  }, 200)
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

const locate = () => {
  if (!map) return
  map.setView([39.9042, 116.4074], 10)
}

const viewDroneVideo = () => {
  router.push('/video')
}
</script>

<style scoped>
.map-grid {
  display: grid;
  grid-template-columns: 320px 1fr 360px;
  gap: 12px;
  height: calc(100vh - 200px);
  min-height: 600px;
}
.map-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.grid-left, .grid-right {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  overflow: hidden;
}
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.missions-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  min-height: 0;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  min-height: 0;
}

/* Element Plus el-scrollbar 宇宙主题滚动条样式 */
:deep(.missions-list .el-scrollbar__wrap) {
  overflow-x: hidden;
  padding-right: 8px;
}

:deep(.detail-content .el-scrollbar__wrap) {
  overflow-x: hidden;
  padding-right: 8px;
}

:deep(.missions-list .el-scrollbar__bar),
:deep(.detail-content .el-scrollbar__bar) {
  right: 2px;
}

:deep(.missions-list .el-scrollbar__thumb),
:deep(.detail-content .el-scrollbar__thumb) {
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%) !important;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(124, 77, 255, 0.5);
  transition: all 0.3s ease;
}

:deep(.missions-list .el-scrollbar__thumb:hover),
:deep(.detail-content .el-scrollbar__thumb:hover) {
  background: linear-gradient(135deg, #4fc3f7 0%, #7c4dff 100%) !important;
  box-shadow: 0 0 12px rgba(124, 77, 255, 0.8);
}

:deep(.missions-list .el-scrollbar__bar.is-vertical),
:deep(.detail-content .el-scrollbar__bar.is-vertical) {
  width: 6px;
  right: 2px;
}

:deep(.missions-list .el-scrollbar__bar.is-vertical .el-scrollbar__thumb),
:deep(.detail-content .el-scrollbar__bar.is-vertical .el-scrollbar__thumb) {
  width: 100%;
}
.mission-item {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}
.mission-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(124, 77, 255, 0.5);
}
.mission-item.active {
  border-color: #7c4dff;
  background: rgba(124, 77, 255, 0.2);
  box-shadow: 0 0 10px rgba(124, 77, 255, 0.3);
}
.mission-item .line {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}
.mission-item .mid { 
  font-weight: 600;
  color: #fff;
}
.kv { 
  display: flex; 
  font-size: 13px; 
  margin: 8px 0;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.k { 
  width: 100px; 
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  flex-shrink: 0;
}
.v { 
  flex: 1; 
  color: #fff;
  word-break: break-word;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tools {
  display: flex;
  gap: 8px;
}

/* 确保 Leaflet 地图容器样式正确 */
:deep(.leaflet-container) {
  height: 100% !important;
  width: 100% !important;
  z-index: 0;
}

/* 修复 Leaflet 默认图标路径问题 */
:deep(.leaflet-default-icon-path) {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCAyNSA0MSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNUMwIDIwLjkgOS40IDM2LjUgMTIuNSA0MUMxNS42IDM2LjUgMjUgMjAuOSAyNSAxMi41QzI1IDUuNiAxOS40IDAgMTIuNSAwWiIgZmlsbD0iIzI0ODlGRiIvPjxwYXRoIGQ9Ik0xMi41IDJDNi43IDIgMiA2LjcgMiAxMi41QzIgMTkuMyAxMC4yIDMzLjggMTIuNSAzOEMxNC44IDMzLjggMjMgMTkuMyAyMyAxMi41QzIzIDYuNyAxOC4zIDIgMTIuNSAyWiIgZmlsbD0iI2ZmZiIvPjwvc3ZnPg==');
}

/* 图层控制样式优化 */
:deep(.leaflet-control-layers) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

:deep(.leaflet-control-layers-toggle) {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSIjNjY2NjY2Ii8+Cjwvc3ZnPgo=');
  background-size: 20px 20px;
  background-repeat: no-repeat;
  background-position: center;
}

.drone-icon { font-size: 20px; line-height: 24px; }
</style>

