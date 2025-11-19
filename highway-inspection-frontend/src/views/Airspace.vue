<template>
  <div class="airspace-management">
    <!-- 顶部工具栏 -->
    <el-card class="toolbar-card cosmic-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <h3 class="cosmic-title">空域管理</h3>
          <el-tag :type="statsTagType" class="cosmic-tag">
            总计: {{ stats.total }} | 
            可用: {{ stats.available }} | 
            占用: {{ stats.occupied }} | 
            不可用: {{ stats.unavailable }}
          </el-tag>
        </div>
        <div class="toolbar-right">
          <button 
            v-if="userStore.user?.role === 'admin'" 
            class="cosmic-button"
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            创建空域
          </button>
          <button class="cosmic-button" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </button>
        </div>
      </div>
    </el-card>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧地图 -->
      <el-card class="map-card cosmic-card" shadow="never">
        <template #header>
          <div class="map-header">
            <span class="cosmic-title-small">空域地图</span>
            <div class="map-controls">
          <el-radio-group v-model="mapFilter" size="small">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="suitable">适飞区</el-radio-button>
            <el-radio-button value="restricted">限制区</el-radio-button>
            <el-radio-button value="no_fly">禁飞区</el-radio-button>
          </el-radio-group>
            </div>
          </div>
        </template>
        <div id="airspace-map" class="airspace-map"></div>
        
        <!-- 图例 -->
        <div class="map-legend cosmic-legend">
          <div class="legend-item">
            <span class="legend-color" style="background: rgba(34, 139, 34, 0.3); border-color: #228b22;"></span>
            <span style="color: #000;">适飞区-可用</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: rgba(255, 165, 0, 0.3); border-color: #ffa500;"></span>
            <span style="color: #000;">适飞区-占用</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: rgba(255, 215, 0, 0.3); border-color: #ffd700;"></span>
            <span style="color: #000;">限制区</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: rgba(255, 0, 0, 0.3); border-color: #ff0000;"></span>
            <span style="color: #000;">禁飞区</span>
          </div>
        </div>
      </el-card>

      <!-- 右侧列表 -->
      <el-card class="list-card cosmic-card" shadow="never">
        <template #header>
          <span class="cosmic-title-small">空域列表</span>
        </template>
        
        <!-- 筛选 -->
        <div class="filter-section cosmic-form-section">
          <el-input 
            v-model="searchText" 
            placeholder="搜索空域名称或编号" 
            clearable
            style="width: 250px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-left: 12px;">
            <el-option label="可用" value="available" />
            <el-option label="占用" value="occupied" />
            <el-option label="不可用" value="unavailable" />
          </el-select>
        </div>

        <!-- 空域列表 -->
        <div class="airspace-list">
          <div 
            v-for="airspace in filteredAirspaces" 
            :key="airspace.id"
            class="airspace-item"
            :class="{ 'selected': selectedAirspace?.id === airspace.id }"
            @click="selectAirspace(airspace)"
          >
            <div class="airspace-item-header">
              <div class="airspace-name">
                <el-icon :style="{ color: getTypeColor(airspace.type) }">
                  <Location />
                </el-icon>
                <span class="name">{{ airspace.name }}</span>
                <el-tag :type="getStatusTagType(airspace.status)" size="small">
                  {{ getStatusText(airspace.status) }}
                </el-tag>
              </div>
              <el-tag size="small" :type="getTypeTagType(airspace.type)">
                {{ getTypeText(airspace.type) }}
              </el-tag>
            </div>
            <div class="airspace-item-content">
              <div class="info-row">
                <span class="label">编号:</span>
                <span class="value">{{ airspace.number }}</span>
              </div>
              <div class="info-row" v-if="airspace.remark">
                <span class="label">备注:</span>
                <span class="value">{{ airspace.remark }}</span>
              </div>
            </div>
            <div class="airspace-item-actions" v-if="userStore.user?.role === 'admin'">
              <el-button size="small" type="primary" @click.stop="editAirspace(airspace)">编辑</el-button>
              <el-button size="small" type="warning" @click.stop="changeStatus(airspace)">修改状态</el-button>
              <el-button size="small" type="danger" @click.stop="deleteAirspace(airspace)">删除</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑空域对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingAirspace ? '编辑空域' : '创建空域'"
      width="800px"
    >
      <el-form :model="airspaceForm" :rules="airspaceRules" ref="airspaceFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="空域名称" prop="name">
              <el-input v-model="airspaceForm.name" placeholder="请输入空域名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="空域编号" prop="number">
              <el-input v-model="airspaceForm.number" placeholder="请输入空域编号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="空域类型" prop="type">
              <el-select v-model="airspaceForm.type" placeholder="请选择空域类型">
                <el-option label="适飞区" value="suitable" />
                <el-option label="限制区" value="restricted" />
                <el-option label="禁飞区" value="no_fly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="空域状态" prop="status">
              <el-select v-model="airspaceForm.status" placeholder="请选择空域状态">
                <el-option label="可用" value="available" />
                <el-option label="不可用" value="unavailable" />
                <el-option label="占用" value="occupied" disabled>占用（由任务自动管理）</el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="airspaceForm.remark" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <el-form-item label="坐标点">
          <div class="coordinates-input">
            <div v-for="(coord, index) in airspaceForm.coordinates" :key="index" class="coord-row">
              <el-input-number 
                v-model="coord[0]" 
                :precision="6" 
                :step="0.001" 
                placeholder="纬度"
                style="width: 200px;"
              />
              <el-input-number 
                v-model="coord[1]" 
                :precision="6" 
                :step="0.001" 
                placeholder="经度"
                style="width: 200px; margin-left: 8px;"
              />
              <el-button 
                type="danger" 
                size="small" 
                @click="removeCoordinate(index)"
                style="margin-left: 8px;"
                v-if="airspaceForm.coordinates.length > 3"
              >
                删除
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addCoordinate" style="margin-top: 8px;">
              添加坐标点
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAirspace">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改状态对话框 -->
    <el-dialog v-model="statusDialogVisible" title="修改空域状态" width="500px">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusTagType(currentAirspace?.status || 'available')">
            {{ getStatusText(currentAirspace?.status || '') }}
          </el-tag>
        </el-form-item>
        <el-form-item label="新状态" prop="status">
          <el-select v-model="statusForm.status" placeholder="请选择新状态">
            <el-option label="可用" value="available" />
            <el-option label="不可用" value="unavailable" />
            <el-option 
              v-if="currentAirspace?.status === 'occupied'" 
              label="占用" 
              value="occupied" 
              disabled
            >
              占用（由任务自动管理，无法手动修改）
            </el-option>
          </el-select>
          <div v-if="currentAirspace?.status === 'occupied'" style="margin-top: 8px; color: #909399; font-size: 12px;">
            提示：占用状态由飞行任务自动管理，任务开始时自动设为占用，任务结束时自动释放。
          </div>
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input 
            v-model="statusForm.note" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入修改原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmStatusChange">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Location } from '@element-plus/icons-vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useUserStore } from '@/stores/user'
import { useAirspaceStore, type Airspace } from '@/stores/airspace'

const userStore = useUserStore()
const airspaceStore = useAirspaceStore()

let map: L.Map | null = null
const polygonLayers: Map<string, L.Polygon> = new Map()

// 响应式数据
const mapFilter = ref('all')
const searchText = ref('')
const statusFilter = ref('')
const selectedAirspace = ref<Airspace | null>(null)
const dialogVisible = ref(false)
const statusDialogVisible = ref(false)
const editingAirspace = ref<Airspace | null>(null)
const currentAirspace = ref<Airspace | null>(null)

// 表单数据
const airspaceForm = ref({
  name: '',
  number: '',
  type: 'suitable' as 'suitable' | 'restricted' | 'no_fly',
  remark: '',
  status: 'available' as 'available' | 'occupied' | 'unavailable',
  coordinates: [[39.9, 116.4], [39.92, 116.4], [39.92, 116.42], [39.9, 116.42]] as Array<[number, number]>
})

const statusForm = ref({
  status: 'available' as 'available' | 'occupied' | 'unavailable',
  note: ''
})

const airspaceRules = {
  name: [{ required: true, message: '请输入空域名称', trigger: 'blur' }],
  number: [{ required: true, message: '请输入空域编号', trigger: 'blur' }],
  type: [{ required: true, message: '请选择空域类型', trigger: 'change' }]
}

// 计算属性
const stats = computed(() => airspaceStore.getStatistics())
const statsTagType = computed(() => {
  if (stats.value.occupied > stats.value.available) return 'warning'
  return 'success'
})

const filteredAirspaces = computed(() => {
  let airspaces = airspaceStore.airspaces

  if (mapFilter.value !== 'all') {
    airspaces = airspaces.filter(a => a.type === mapFilter.value)
  }

  if (statusFilter.value) {
    airspaces = airspaces.filter(a => a.status === statusFilter.value)
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    airspaces = airspaces.filter(a => 
      a.name.toLowerCase().includes(search) || 
      a.number.toLowerCase().includes(search)
    )
  }

  return airspaces
})

// 生命周期
onMounted(async () => {
  await airspaceStore.fetchAirspaces()
  await nextTick()
  initMap()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})

// 监听过滤器变化，重新绘制地图
watch([mapFilter, () => airspaceStore.airspaces], () => {
  if (map) {
    updateMapPolygons()
  }
}, { deep: true })

// 地图初始化
const initMap = () => {
  // 延迟一下确保DOM完全渲染
  setTimeout(() => {
    try {
      const mapElement = document.getElementById('airspace-map')
      if (!mapElement) {
        console.error('地图容器未找到')
        return
      }
      
      map = L.map('airspace-map', {
        center: [39.9, 116.4],
        zoom: 11,
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

      updateMapPolygons()
    } catch (error) {
      console.error('地图初始化失败:', error)
    }
  }, 200)
}

// 更新地图多边形
const updateMapPolygons = () => {
  if (!map) return

  // 清除现有图层
  polygonLayers.forEach(layer => {
    map!.removeLayer(layer)
  })
  polygonLayers.clear()

  // 添加新图层
  const airspacesToShow = mapFilter.value === 'all' 
    ? airspaceStore.airspaces 
    : airspaceStore.airspaces.filter(a => a.type === mapFilter.value)

  airspacesToShow.forEach(airspace => {
    const { color, fillColor, fillOpacity } = getPolygonStyle(airspace)
    
    // 从GeoJSON格式提取坐标（注意：GeoJSON是[lng, lat]，Leaflet需要[lat, lng]）
    let coordinates: Array<[number, number]> = []
    if (airspace.area && airspace.area.coordinates && airspace.area.coordinates[0]) {
      coordinates = airspace.area.coordinates[0].map((coord: number[]) => [coord[1], coord[0]] as [number, number])
    }
    
    if (coordinates.length === 0) return
    
    const polygon = L.polygon(coordinates, {
      color,
      fillColor,
      fillOpacity,
      weight: 2
    }).addTo(map!)

    polygon.bindPopup(`
      <div style="padding: 8px;">
        <h4 style="margin: 0 0 8px 0;">${airspace.name}</h4>
        <p style="margin: 4px 0;"><strong>编号:</strong> ${airspace.number}</p>
        <p style="margin: 4px 0;"><strong>类型:</strong> ${getTypeText(airspace.type)}</p>
        <p style="margin: 4px 0;"><strong>状态:</strong> ${getStatusText(airspace.status)}</p>
        ${airspace.remark ? `<p style="margin: 4px 0;"><strong>备注:</strong> ${airspace.remark}</p>` : ''}
      </div>
    `)

    polygon.on('click', () => {
      selectedAirspace.value = airspace
    })

    polygonLayers.set(airspace.id.toString(), polygon)
  })
}

// 获取多边形样式
const getPolygonStyle = (airspace: Airspace) => {
  if (airspace.type === 'suitable') {
    if (airspace.status === 'available') {
      return { color: '#228b22', fillColor: '#90EE90', fillOpacity: 0.3 }
    } else if (airspace.status === 'occupied') {
      return { color: '#ffa500', fillColor: '#ffa500', fillOpacity: 0.3 }
    } else {
      return { color: '#999', fillColor: '#999', fillOpacity: 0.3 }
    }
  } else if (airspace.type === 'restricted') {
    return { color: '#ffd700', fillColor: '#ffd700', fillOpacity: 0.3 }
  } else {
    return { color: '#ff0000', fillColor: '#ff0000', fillOpacity: 0.3 }
  }
}

// 方法
const showCreateDialog = () => {
  editingAirspace.value = null
  resetAirspaceForm()
  dialogVisible.value = true
}

const editAirspace = (airspace: Airspace) => {
  editingAirspace.value = airspace
  // 从GeoJSON格式提取坐标（转换为[lat, lng]格式用于表单编辑）
  let coordinates: Array<[number, number]> = []
  if (airspace.area && airspace.area.coordinates && airspace.area.coordinates[0]) {
    coordinates = airspace.area.coordinates[0].map((coord: number[]) => [coord[1], coord[0]] as [number, number])
  }
  
  airspaceForm.value = {
    name: airspace.name,
    number: airspace.number,
    type: airspace.type,
    remark: airspace.remark || '',
    status: airspace.status,
    coordinates: coordinates.length > 0 ? coordinates : [[39.9, 116.4], [39.92, 116.4], [39.92, 116.42], [39.9, 116.42]]
  }
  dialogVisible.value = true
}

const resetAirspaceForm = () => {
  airspaceForm.value = {
    name: '',
    number: '',
    type: 'suitable',
    remark: '',
    status: 'available',
    coordinates: [[39.9, 116.4], [39.92, 116.4], [39.92, 116.42], [39.9, 116.42]]
  }
}

const addCoordinate = () => {
  airspaceForm.value.coordinates.push([39.9, 116.4])
}

const removeCoordinate = (index: number) => {
  airspaceForm.value.coordinates.splice(index, 1)
}

const saveAirspace = async () => {
  try {
    // 将坐标转换为GeoJSON格式（注意：表单中是[lat, lng]，GeoJSON需要[lng, lat]）
    const geoJsonCoordinates = airspaceForm.value.coordinates.map(coord => [coord[1], coord[0]])
    // 确保多边形闭合（第一个点和最后一个点相同）
    if (geoJsonCoordinates.length > 0) {
      const first = geoJsonCoordinates[0]
      const last = geoJsonCoordinates[geoJsonCoordinates.length - 1]
      if (first && last && first.length >= 2 && last.length >= 2 && 
          (first[0] !== last[0] || first[1] !== last[1])) {
        geoJsonCoordinates.push([first[0] as number, first[1] as number])
      }
    }
    
    const airspaceData = {
      name: airspaceForm.value.name,
      number: airspaceForm.value.number,
      type: airspaceForm.value.type,
      area: {
        type: 'Polygon' as const,
        coordinates: [geoJsonCoordinates]
      },
      remark: airspaceForm.value.remark || undefined,
      status: airspaceForm.value.status
    }

    if (editingAirspace.value) {
      await airspaceStore.updateAirspace(editingAirspace.value.id, airspaceData)
      ElMessage.success('空域已更新')
    } else {
      await airspaceStore.createAirspace(airspaceData)
      ElMessage.success('空域已创建')
    }

    dialogVisible.value = false
    await airspaceStore.fetchAirspaces(airspaceStore.currentPage, airspaceStore.pageSize)
    updateMapPolygons()
  } catch (error) {
    // 错误已在store中处理
    console.error('保存失败:', error)
  }
}

const changeStatus = (airspace: Airspace) => {
  // 如果当前状态是占用，不允许修改
  if (airspace.status === 'occupied') {
    ElMessage.warning('占用状态由飞行任务自动管理，无法手动修改。任务结束时将自动释放。')
    return
  }
  currentAirspace.value = airspace
  // 由于前面已经检查过不是 occupied，所以这里可以直接使用原状态
  statusForm.value = {
    status: airspace.status === 'available' ? 'available' : 'unavailable',
    note: ''
  }
  statusDialogVisible.value = true
}

const confirmStatusChange = async () => {
  try {
    if (!currentAirspace.value) return

    await airspaceStore.updateAirspace(currentAirspace.value.id, {
      status: statusForm.value.status
    })

    ElMessage.success('状态已更新')
    statusDialogVisible.value = false
    await airspaceStore.fetchAirspaces(airspaceStore.currentPage, airspaceStore.pageSize)
    updateMapPolygons()
  } catch (error) {
    // 错误已在store中处理
    console.error('更新失败:', error)
  }
}

const deleteAirspace = async (airspace: Airspace) => {
  try {
    await ElMessageBox.confirm(`确认删除空域 "${airspace.name}"？`, '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await airspaceStore.deleteAirspace(airspace.id)
    ElMessage.success('空域已删除')
    await airspaceStore.fetchAirspaces(airspaceStore.currentPage, airspaceStore.pageSize)
    updateMapPolygons()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在store中处理
      console.error('删除失败:', error)
    }
  }
}

const selectAirspace = (airspace: Airspace) => {
  selectedAirspace.value = airspace
  const polygon = polygonLayers.get(airspace.id.toString())
  if (polygon && map) {
    polygon.openPopup()
    map.fitBounds(polygon.getBounds())
  }
}

const refreshData = async () => {
  await airspaceStore.fetchAirspaces(airspaceStore.currentPage, airspaceStore.pageSize)
  updateMapPolygons()
  ElMessage.success('数据已刷新')
}

// 辅助方法
const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    suitable: '适飞区',
    restricted: '限制区',
    no_fly: '禁飞区'
  }
  return typeMap[type] || type
}

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    suitable: 'success',
    restricted: 'warning',
    no_fly: 'danger'
  }
  return typeMap[type] || ''
}

const getTypeColor = (type: string) => {
  const typeMap: Record<string, string> = {
    suitable: '#67C23A',
    restricted: '#E6A23C',
    no_fly: '#F56C6C'
  }
  return typeMap[type] || '#909399'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    available: '可用',
    occupied: '占用',
    unavailable: '不可用'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    available: 'success',
    occupied: 'warning',
    unavailable: 'info'
  }
  return statusMap[status] || ''
}
</script>

<style scoped>
.airspace-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar-card {
  flex-shrink: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left h3 {
  margin: 0;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
  height: calc(100vh - 280px);
}

.map-card {
  flex: 2;
  display: flex;
  flex-direction: column;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.airspace-map {
  flex: 1;
  min-height: 500px;
  height: 100%;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  position: relative;
}

/* 确保 Leaflet 地图容器样式正确 */
:deep(.airspace-map .leaflet-container) {
  height: 100% !important;
  width: 100% !important;
  z-index: 0;
}

.map-card {
  flex: 2;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

:deep(.map-card .el-card__body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 16px;
}

.map-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border: 2px solid;
  border-radius: 2px;
}

.list-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 400px;
  min-height: 0;
  overflow: hidden;
}

:deep(.list-card .el-card__body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.filter-section {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.airspace-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  min-height: 0;
  max-height: none;
}

/* 宇宙主题滚动条样式 */
.airspace-list::-webkit-scrollbar {
  width: 6px;
}

.airspace-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.airspace-list::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%);
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(124, 77, 255, 0.5);
}

.airspace-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #4fc3f7 0%, #7c4dff 100%);
  box-shadow: 0 0 12px rgba(124, 77, 255, 0.8);
}

.airspace-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(124, 77, 255, 0.6) rgba(255, 255, 255, 0.05);
}

.airspace-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.airspace-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.airspace-item.selected {
  border-color: #409EFF;
  background: #f0f9ff;
}

.airspace-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.airspace-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.airspace-name .name {
  font-weight: 600;
  font-size: 16px;
}

.airspace-item-content {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  margin-bottom: 6px;
  font-size: 14px;
}

.info-row .label {
  color: #909399;
  min-width: 70px;
}

.info-row .value {
  color: #606266;
  flex: 1;
}

.airspace-item-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.coordinates-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.coord-row {
  display: flex;
  align-items: center;
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>
