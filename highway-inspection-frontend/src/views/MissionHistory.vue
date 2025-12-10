<template>
  <div class="mission-history">
    <el-card shadow="never" class="cosmic-card">
      <template #header>
        <div class="header">
          <span class="cosmic-title-small">历史飞行任务</span>
          <div class="actions">
            <el-input v-model="keyword" placeholder="搜索操作员/申请ID" clearable style="width: 220px" />
            <button class="cosmic-button" @click="reload" :disabled="missionStore.loading">查询</button>
          </div>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table :data="filtered" v-loading="missionStore.loading" size="small" border stripe>
        <el-table-column label="任务ID" prop="id" width="90" align="center" />
        <el-table-column label="操作员" width="160">
          <template #default="{ row }">
            <el-tag type="info" v-if="row.operator?.username">{{ row.operator.username }}</el-tag>
            <span v-else>{{ row.operator_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="申请ID" prop="flight_application_id" width="120" align="center" />
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="结束时间" width="180">
          <template #default="{ row }">{{ formatTime(row.end_time) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="success" v-if="row.status === 'completed'">已完成</el-tag>
            <el-tag type="warning" v-else>执行中</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>

      <div class="pager">
        <el-pagination
          background
          :current-page="missionStore.currentPage"
          :page-size="missionStore.pageSize"
          :total="missionStore.total"
          layout="prev, pager, next, ->, total"
          @current-change="pageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="任务详情" width="900px">
      <div class="detail-wrap">
        <div class="detail-map" id="history-mission-map"></div>
        <div class="detail-info">
          <div class="info-row"><span class="label">任务ID：</span><span class="val">{{ current?.id }}</span></div>
          <div class="info-row"><span class="label">操作员：</span><span class="val">{{ current?.operator?.username || current?.operator_id }}</span></div>
          <div class="info-row"><span class="label">实际开始时间：</span><span class="val">{{ formatTime(current?.start_time) }}</span></div>
          <div class="info-row"><span class="label">实际结束时间：</span><span class="val">{{ formatTime(current?.end_time) }}</span></div>
          <el-divider />
          <div class="info-row"><span class="label">申请ID：</span><span class="val">{{ current?.flight_application_id }}</span></div>
          <div class="info-row"><span class="label">无人机型号：</span><span class="val">{{ current?.flight_application?.drone_model || '-' }}</span></div>
          <div class="info-row"><span class="label">任务目的：</span><span class="val">{{ current?.flight_application?.task_purpose || '-' }}</span></div>
          <div class="info-row"><span class="label">计划飞行时长：</span><span class="val">{{ current?.flight_application?.total_time ? current.flight_application.total_time + ' 分钟' : '-' }}</span></div>
          <div class="info-row"><span class="label">总飞行里程：</span><span class="val">{{ current?.route_distance ? current.route_distance.toFixed(2) + ' 公里' : '-' }}</span></div>
          <el-divider />
          <div class="info-row"><span class="label">视频数量：</span><span class="val">{{ videos.length }}</span></div>
          <div class="info-row"><span class="label">识别结果数量：</span><span class="val">{{ current?.analysis_results_count || 0 }}</span></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useMissionStore, type Mission } from '@/stores/mission'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'

dayjs.extend(utc)

const missionStore = useMissionStore()
const keyword = ref('')

const filtered = computed(() => {
  const list = missionStore.missions
  if (!keyword.value) return list
  const k = keyword.value.toLowerCase()
  return list.filter(m =>
    (m.operator?.username || String(m.operator_id)).toLowerCase().includes(k) ||
    String(m.flight_application_id).includes(k)
  )
})

async function reload(page?: number) {
  await missionStore.fetchMissions({ status: 'completed', page: page ?? missionStore.currentPage, page_size: missionStore.pageSize })
}

function pageChange(p: number) {
  reload(p)
}

const detailVisible = ref(false)
const current = ref<Mission | null>(null)
const videos = ref<any[]>([])
const alerts = ref<any[]>([])
let map: L.Map | null = null
let routeLayer: L.Polyline<any> | null = null

const formatTime = (t?: string | null) => {
  if (!t) return '-'
  // UTC时间转换为本地时间显示
  return dayjs.utc(t).local().format('YYYY/MM/DD HH:mm:ss')
}

const coordsFromRoute = (route: any): Array<[number, number]> => {
  if (!route) return []
  const raw = Array.isArray(route) ? route : (route.coordinates || [])
  return raw.map((c: number[]) => [c[1], c[0]] as [number, number]).filter((p: any) => Array.isArray(p) && p.length === 2)
}

const initMap = () => {
  map = L.map('history-mission-map', {
    center: [39.9, 116.4],
    zoom: 11,
    zoomControl: true
  })

 // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //maxZoom: 18,
    //attribution: '© OpenStreetMap contributors'
  //}).addTo(map!)

  // 使用高德地图（国内访问快速稳定）
   L.tileLayer('https://wprd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', {
        maxZoom: 18,
        attribution: '© 高德地图',
        subdomains: ['1', '2', '3', '4']
    }).addTo(map)
}

const renderCurrent = () => {
  if (!map || !current.value) return
  if (routeLayer) {
    map.removeLayer(routeLayer)
    routeLayer = null
  }
  const latlngs = coordsFromRoute(current.value.route)
  if (latlngs.length === 0) return
  routeLayer = L.polyline(latlngs, { color: '#67C23A', weight: 3 }).addTo(map!)
  map.fitBounds(routeLayer.getBounds(), { padding: [20, 20] })
}

async function openDetail(m: Mission) {
  current.value = m
  detailVisible.value = true
  videos.value = await missionStore.fetchMissionVideos(m.id).catch(() => [])
  alerts.value = await missionStore.fetchMissionAlerts(m.id).catch(() => [])
  await nextTick()
  if (!map) initMap()
  renderCurrent()
}

onMounted(async () => {
  await reload(1)
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.mission-history {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.actions {
  display: flex;
  gap: 8px;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}
.detail-wrap {
  display: flex;
  gap: 12px;
}
.detail-map {
  width: 520px;
  height: 420px;
  border-radius: 8px;
  overflow: hidden;
}
.detail-info {
  flex: 1;
}
.info-row {
  display: flex;
  margin: 6px 0;
}
.label {
  color: #909399;
  width: 90px;
}
.val {
  color: #606266;
  flex: 1;
}
</style>


