<template>
  <div class="alert-center">
    <!-- 顶部统计卡片 -->
    <div class="stats-cards">
      <el-card shadow="never" class="stat-card critical cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><WarningFilled /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.byLevel.critical }}</div>
            <div class="cosmic-stat-label">严重告警</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card high cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><Warning /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.byLevel.high }}</div>
            <div class="cosmic-stat-label">高级告警</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card medium cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><InfoFilled /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.byLevel.medium }}</div>
            <div class="cosmic-stat-label">中级告警</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card total cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><DocumentCopy /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.total }}</div>
            <div class="cosmic-stat-label">总计</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主内容 -->
    <el-card class="main-card cosmic-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="cosmic-title-small">告警列表</span>
          <div class="tools">
            <button class="cosmic-button" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :model="filterForm" inline>
          <el-form-item label="告警类型">
            <el-select v-model="filterForm.type" placeholder="全部类型" clearable>
              <el-option label="交通事故" value="traffic_accident" />
              <el-option label="路况异常" value="road_anomaly" />
              <el-option label="设施异常" value="facility_abnormal" />
              <el-option label="空域侵入" value="intrusion" />
              <el-option label="碰撞风险" value="collision" />
              <el-option label="状态异常" value="status_abnormal" />
              <el-option label="气象预警" value="weather" />
            </el-select>
          </el-form-item>
          <el-form-item label="告警等级">
            <el-select v-model="filterForm.level" placeholder="全部等级" clearable>
              <el-option label="严重" value="critical" />
              <el-option label="高级" value="high" />
              <el-option label="中级" value="medium" />
              <el-option label="低级" value="low" />
            </el-select>
          </el-form-item>
          <el-form-item label="处理状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
              <el-option label="新发现" value="new" />
              <el-option label="已确认" value="confirmed" />
              <el-option label="处理中" value="processing" />
              <el-option label="已关闭" value="closed" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">筛选</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 告警表格 -->
      <div class="table-wrapper">
        <el-table :data="filteredAlerts" v-loading="alertStore.loading" stripe @row-click="viewAlertDetail">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <div class="expand-row" v-if="row.title">
                <span class="expand-label">告警标题:</span>
                <span>{{ row.title }}</span>
              </div>
              <div class="expand-row" v-if="row.road_section">
                <span class="expand-label">路段:</span>
                <span>{{ row.road_section }}</span>
              </div>
              <div class="expand-row" v-if="row.mission_id">
                <span class="expand-label">关联任务ID:</span>
                <span>{{ row.mission_id }}</span>
              </div>
              <div class="expand-row" v-if="row.video_id">
                <span class="expand-label">关联视频ID:</span>
                <span>{{ row.video_id }}</span>
              </div>
              <div class="expand-row">
                <span class="expand-label">发生时间:</span>
                <span>{{ formatDateTime(row.occurred_time || row.created_at) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="告警ID" width="120" />
        <el-table-column prop="title" label="告警标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="event_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.event_type)">{{ getTypeText(row.event_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.severity)">{{ getLevelText(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="occurred_time" label="发生时间" width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.occurred_time || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'new'" 
              size="small" 
              type="primary" 
              @click.stop="confirmAlert(row)"
            >
              确认
            </el-button>
            <el-button 
              v-if="row.status === 'confirmed' || row.status === 'new'" 
              size="small" 
              type="success" 
              @click.stop="processAlert(row)"
            >
              处理
            </el-button>
            <el-button 
              v-if="row.status === 'processing'" 
              size="small" 
              type="success" 
              @click.stop="closeAlert(row)"
            >
              关闭
            </el-button>
            <el-button 
              v-if="row.video_id" 
              size="small" 
              type="info" 
              @click.stop="playVideo(row)"
            >
              查看视频
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-section" v-if="totalAlerts > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalAlerts"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 空状态提示 -->
      <el-empty v-if="!alertStore.loading && filteredAlerts.length === 0" description="暂无告警数据" />
    </el-card>


  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Warning, InfoFilled, DocumentCopy, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAlertStore, type Alert } from '@/stores/alert'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()
const alertStore = useAlertStore()

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const dateRange = ref<[string, string] | null>(null)
const currentAlert = ref<Alert | null>(null)

// 筛选表单
const filterForm = ref({
  type: '',
  level: '',
  status: ''
})

// 计算属性
const stats = computed(() => {
  const statistics = alertStore.getStatistics()
  // 将severity映射到level显示
  return {
    total: statistics.total,
    byLevel: {
      critical: statistics.bySeverity.high, // 高级告警显示为严重
      high: statistics.bySeverity.high,
      medium: statistics.bySeverity.medium,
      low: statistics.bySeverity.low
    },
    byStatus: statistics.byStatus,
    bySeverity: statistics.bySeverity
  }
})

const filteredAlerts = computed(() => {
  let alerts = alertStore.alerts

  if (filterForm.value.type) {
    alerts = alerts.filter(a => a.event_type === filterForm.value.type)
  }
  if (filterForm.value.level) {
    alerts = alerts.filter(a => a.severity === filterForm.value.level)
  }
  if (filterForm.value.status) {
    alerts = alerts.filter(a => a.status === filterForm.value.status)
  }
  if (dateRange.value) {
    const [start, end] = dateRange.value
    alerts = alerts.filter(a => {
      const date = a.created_at?.split('T')[0] || ''
      return date >= start && date <= end
    })
  }

  return alerts
})

const totalAlerts = computed(() => alertStore.total)

// 生命周期
onMounted(async () => {
  try {
    await alertStore.fetchAlerts(currentPage.value, pageSize.value)
  } catch (error) {
    console.error('加载告警数据失败:', error)
    // 即使失败也显示空列表，而不是空白页面
  }
})

// 方法
const refreshData = async () => {
  try {
    await alertStore.fetchAlerts(currentPage.value, pageSize.value)
    // 只在成功且有数据时显示成功消息（避免无后端时显示成功但实际失败）
    if (alertStore.alerts.length > 0) {
      ElMessage.success('数据已刷新')
    } else if (!import.meta.env.DEV) {
      // 生产环境即使没有数据也显示成功
      ElMessage.success('数据已刷新')
    }
  } catch (error: any) {
    console.error('刷新告警数据失败:', error)
    // 错误处理已经在 store 中完成，这里不需要重复处理
  }
}

const handleFilter = () => {
  currentPage.value = 1
}

const resetFilter = () => {
  filterForm.value = {
    type: '',
    level: '',
    status: ''
  }
  dateRange.value = null
  currentPage.value = 1
}

const viewAlertDetail = (row: Alert) => {
  // 可以打开详情对话框
  console.log('查看告警详情:', row)
}

const confirmAlert = async (alert: Alert) => {
  try {
    await ElMessageBox.confirm('确认此告警？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await alertStore.updateAlert(alert.id, { status: 'confirmed' })
    ElMessage.success('告警已确认')
    await alertStore.fetchAlerts(currentPage.value, pageSize.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('确认失败:', error)
    }
  }
}

const processAlert = async (alert: Alert) => {
  try {
    await ElMessageBox.confirm('确认开始处理此告警？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await alertStore.updateAlert(alert.id, { status: 'processing' })
    ElMessage.success('告警已开始处理')
    await alertStore.fetchAlerts(currentPage.value, pageSize.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('处理失败:', error)
    }
  }
}

const closeAlert = async (alert: Alert) => {
  try {
    await ElMessageBox.confirm('确认关闭此告警？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await alertStore.updateAlert(alert.id, { status: 'closed' })
    ElMessage.success('告警已关闭')
    await alertStore.fetchAlerts(currentPage.value, pageSize.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('关闭失败:', error)
    }
  }
}

// 后端暂不支持删除告警

const playVideo = (alert: Alert) => {
  // 跳转到视频页面并播放
  if (alert.video_id) {
    router.push({
      path: '/video',
      query: { videoId: alert.video_id, alertId: alert.id }
    })
  } else {
    ElMessage.warning('该告警没有关联视频')
  }
}

// 辅助方法
const formatDateTime = (dateTime?: string) => {
  if (!dateTime) return ''
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm')
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    collision: '碰撞风险',
    intrusion: '空域侵入',
    status_abnormal: '状态异常',
    weather: '气象预警',
    road_anomaly: '路况异常',
    traffic_accident: '交通事故',
    facility_abnormal: '设施异常'
  }
  return typeMap[type] || type
}

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    traffic_accident: 'danger',
    collision: 'danger',
    road_anomaly: 'warning',
    intrusion: 'warning',
    facility_abnormal: 'info',
    status_abnormal: 'info',
    weather: ''
  }
  return typeMap[type] || ''
}

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    critical: '严重',
    high: '高级',
    medium: '中级',
    low: '低级'
  }
  return levelMap[level] || level
}

const getLevelTagType = (level: string) => {
  const levelMap: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: ''
  }
  return levelMap[level] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    new: '新发现',
    confirmed: '已确认',
    processing: '处理中',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    new: 'danger',
    confirmed: 'warning',
    processing: 'info',
    closed: 'success'
  }
  return statusMap[status] || ''
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67C23A'
  if (confidence >= 70) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped>
.alert-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.critical {
  border-left: 4px solid #F56C6C;
}

.stat-card.high {
  border-left: 4px solid #E6A23C;
}

.stat-card.medium {
  border-left: 4px solid #409EFF;
}

.stat-card.total {
  border-left: 4px solid #67C23A;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 48px;
}

.stat-card.critical .stat-icon {
  color: #F56C6C;
}

.stat-card.high .stat-icon {
  color: #E6A23C;
}

.stat-card.medium .stat-icon {
  color: #409EFF;
}

.stat-card.total .stat-icon {
  color: #67C23A;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.main-card {
  flex: 1;
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

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.expand-content {
  padding: 16px;
  background: #f5f7fa;
}

.expand-row {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.expand-label {
  font-weight: 600;
  min-width: 100px;
  color: #606266;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
