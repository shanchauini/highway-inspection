<template>
  <div class="dashboard">
    <!-- 顶部工具栏 -->
    <el-card class="toolbar-card cosmic-card" shadow="never">
      <div class="toolbar">
        <h3 class="cosmic-title">数据看板</h3>
        <div class="toolbar-right">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
            class="cosmic-date-picker"
          />
          <button class="cosmic-button" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <div class="stats-overview">
      <el-card shadow="never" class="overview-card cosmic-card">
        <div class="card-content">
          <el-icon class="card-icon"><TrendCharts /></el-icon>
          <div class="card-info">
            <div class="cosmic-stat-value">{{ flightStats.total }}</div>
            <div class="cosmic-stat-label">飞行任务总数</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="overview-card cosmic-card">
        <div class="card-content">
          <el-icon class="card-icon"><Clock /></el-icon>
          <div class="card-info">
            <div class="cosmic-stat-value">{{ flightStats.totalHours.toFixed(1) }}h</div>
            <div class="cosmic-stat-label">总飞行时长</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="overview-card cosmic-card">
        <div class="card-content">
          <el-icon class="card-icon"><Location /></el-icon>
          <div class="card-info">
            <div class="cosmic-stat-value">{{ flightStats.totalDistance.toFixed(0) }}km</div>
            <div class="cosmic-stat-label">总飞行里程</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="overview-card cosmic-card">
        <div class="card-content">
          <el-icon class="card-icon"><Warning /></el-icon>
          <div class="card-info">
            <div class="cosmic-stat-value">{{ inspectionStats.totalResults }}</div>
            <div class="cosmic-stat-label">巡检结果总数</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 飞行统计趋势 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">飞行任务趋势</span>
        </template>
        <v-chart class="chart" :option="flightTrendOption" autoresize />
      </el-card>

      <!-- 空域利用率 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">空域利用统计</span>
        </template>
        <v-chart class="chart" :option="airspaceUtilizationOption" autoresize />
      </el-card>

      <!-- 巡检结果类型分布 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">巡检结果类型分布</span>
        </template>
        <v-chart class="chart" :option="inspectionTypeDistributionOption" autoresize />
      </el-card>

      <!-- 巡检结果趋势 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">巡检结果趋势</span>
        </template>
        <v-chart class="chart" :option="inspectionTrendOption" autoresize />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, TrendCharts, Clock, Location, Warning } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart,
  LineChart,
  PieChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAirspaceStore } from '@/stores/airspace'
import { dashboardApi } from '@/api/modules'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
])

const airspaceStore = useAirspaceStore()

// 响应式数据
// 默认日期范围：从30天前到今日
const getDefaultDateRange = (): [string, string] => {
  const today = new Date()
  const thirtyDaysAgo = new Date(today)
  thirtyDaysAgo.setDate(today.getDate() - 29) // 30天前（包含今天，所以是29天前）
  return [
    thirtyDaysAgo.toISOString().split('T')[0],
    today.toISOString().split('T')[0]
  ]
}
const dateRange = ref<[string, string]>(getDefaultDateRange())

// 飞行统计数据（后端返回）
const flightStats = ref({
  total: 0,
  totalHours: 0,
  totalDistance: 0
})

// 巡检结果统计数据
const inspectionStats = ref({
  totalResults: 0,
  trafficCongestion: {
    total: 0,
    light: 0,
    medium: 0,
    heavy: 0
  },
  roadDamage: {
    total: 0,
    none: 0,
    light: 0,
    medium: 0,
    severe: 0
  },
  trend: [] as { date: string; count: number }[]
})

// 新增缺失的响应式变量
const flightTrend = ref({
  dates: [],
  counts: [],
  hours: []
})

const airspaceUsage = ref({
  available: 0,
  occupied: 0,
  unavailable: 0
})

// 飞行趋势图表配置
const flightTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['飞行任务数', '飞行时长(h)'],
    textStyle: {
      color: '#fff'
    }
  },
  xAxis: { 
    type: 'category', 
    data: flightTrend.value.dates,
    axisLine: {
      lineStyle: {
        color: '#fff'
      }
    },
    axisLabel: {
      color: '#fff'
    }
  },
  yAxis: [
    {
      type: 'value',
      name: '任务数',
      axisLine: {
        lineStyle: {
          color: '#fff'
        }
      },
      axisLabel: {
        color: '#fff'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      }
    },
    {
      type: 'value',
      name: '时长(h)',
      axisLine: {
        lineStyle: {
          color: '#fff'
        }
      },
      axisLabel: {
        color: '#fff'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      }
    }
  ],
  series: [
    {
      name: '飞行任务数',
      type: 'bar',
      data: flightTrend.value.counts,
      itemStyle: {
        color: '#409EFF'
      }
    },
    {
      name: '飞行时长(h)',
      type: 'line',
      yAxisIndex: 1,
      data: flightTrend.value.hours,
      itemStyle: {
        color: '#67C23A'
      }
    }
  ]
}))

// 空域利用率图表配置
const airspaceUtilizationOption = computed(() => {
  const airspaceStats = airspaceStore.getStatistics()
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#fff'
      }
    },
    series: [
      {
        name: '空域利用',
        type: 'pie',
        radius: '50%',
        data: [
          { value: airspaceStats.available, name: '可用', itemStyle: { color: '#67C23A' } },
          { value: airspaceStats.occupied, name: '占用中', itemStyle: { color: '#E6A23C' } },
          { value: airspaceStats.unavailable, name: '不可用', itemStyle: { color: '#909399' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// 巡检结果类型分布图表配置
const inspectionTypeDistributionOption = computed(() => {
  // 准备巡检结果类型分布数据
  const typeData = [
    { value: inspectionStats.value.trafficCongestion.light, name: '交通拥堵-轻度' },
    { value: inspectionStats.value.trafficCongestion.medium, name: '交通拥堵-中度' },
    { value: inspectionStats.value.trafficCongestion.heavy, name: '交通拥堵-重度' },
    { value: inspectionStats.value.roadDamage.none, name: '道路破损-无破损' },
    { value: inspectionStats.value.roadDamage.light, name: '道路破损-轻度' },
    { value: inspectionStats.value.roadDamage.medium, name: '道路破损-中度' },
    { value: inspectionStats.value.roadDamage.severe, name: '道路破损-严重' }
  ].filter(item => item.value > 0) // 只显示有数据的项

  return {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: 'top',
      textStyle: {
        color: '#fff'
      }
    },
    series: [
      {
        name: '巡检结果类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: typeData
      }
    ]
  }
})

// 巡检结果趋势图表配置
const inspectionTrendOption = computed(() => {
  // 使用巡检结果趋势数据
  const trendData = inspectionStats.value.trend
  
  return {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['巡检结果数量'],
      textStyle: {
        color: '#fff'
      }
    },
    xAxis: {
      type: 'category',
      data: trendData.map(t => t.date.slice(5)), // 只显示月日
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#fff'
        }
      },
      axisLabel: {
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#fff'
        }
      },
      axisLabel: {
        color: '#fff'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      }
    },
    series: [
      {
        name: '巡检结果数量',
        type: 'line',
        data: trendData.map(t => t.count),
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(244, 67, 54, 0.3)' },
              { offset: 1, color: 'rgba(244, 67, 54, 0.05)' }
            ]
          }
        },
        itemStyle: {
          color: '#409EFF'
        },
        smooth: true
      }
    ]
  }
})

// 生命周期
onMounted(async () => {
  try {
    await Promise.all([
      airspaceStore.fetchAirspaces(),
      fetchDashboardData()
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})

// 方法
// 获取看板数据
const loadDashboardData = async () => {
  try {
    const [start, end] = dateRange.value || []
    const params = start && end ? { start_date: start, end_date: end } : {}

    // 获取飞行统计数据
    const flightRes = await dashboardApi.getFlightStats(params)
    if (flightRes.code === 200 && flightRes.data) {
      flightStats.value = {
        total: flightRes.data.total_missions || 0,
        totalHours: flightRes.data.total_duration || 0,
        totalDistance: flightRes.data.total_distance || 0
      }
    }

    // 获取空域使用统计
    const airspaceRes = await dashboardApi.getAirspaceUsage(params)
    if (airspaceRes.code === 200 && airspaceRes.data) {
      // 处理空域使用统计
      const usageData = airspaceRes.data
      let totalUsage = 0
      usageData.forEach((item: any) => {
        totalUsage += item.usage_count || 0
      })
      
      airspaceUsage.value = {
        available: 100 - totalUsage, // 简化处理
        occupied: totalUsage,
        unavailable: 0
      }
    }

    // 获取巡检结果统计数据
    const inspectionTypeRes = await dashboardApi.getInspectionTypeDistribution(params)
    if (inspectionTypeRes.code === 200 && inspectionTypeRes.data) {
      // 更新巡检结果统计数据
      const typeData = inspectionTypeRes.data
      
      // 计算总数
      let totalResults = 0
      Object.values(typeData).forEach(count => {
        totalResults += count as number
      })
      
      inspectionStats.value.totalResults = totalResults
      
      // 分别统计交通拥堵和道路破损总数
      let trafficCongestionTotal = 0
      let roadDamageTotal = 0
      
      Object.keys(typeData).forEach(key => {
        if (key.includes('交通拥堵')) {
          trafficCongestionTotal += typeData[key]
        } else if (key.includes('道路破损')) {
          roadDamageTotal += typeData[key]
        }
      })
      
      inspectionStats.value.trafficCongestion.total = trafficCongestionTotal
      inspectionStats.value.roadDamage.total = roadDamageTotal
      
      // 更新拥堵程度统计
      inspectionStats.value.trafficCongestion.light = typeData['交通拥堵-轻度 (light)'] || 0
      inspectionStats.value.trafficCongestion.medium = typeData['交通拥堵-中度 (medium)'] || 0
      inspectionStats.value.trafficCongestion.heavy = typeData['交通拥堵-重度 (heavy)'] || 0
      
      // 更新破损程度统计
      inspectionStats.value.roadDamage.none = typeData['道路破损-无破损'] || 0
      inspectionStats.value.roadDamage.light = typeData['道路破损-轻度破损'] || 0
      inspectionStats.value.roadDamage.medium = typeData['道路破损-中度破损'] || 0
      inspectionStats.value.roadDamage.severe = typeData['道路破损-严重破损'] || 0
    }

    // 获取巡检结果趋势
    const inspectionTrendRes = await dashboardApi.getInspectionTrend({ ...params, days: 30 })
    if (inspectionTrendRes.code === 200 && inspectionTrendRes.data) {
      inspectionStats.value.trend = inspectionTrendRes.data
    }
    
    // 获取飞行任务趋势
    const flightTrendRes = await dashboardApi.getFlightTrend(params)
    if (flightTrendRes.code === 200 && flightTrendRes.data) {
      flightTrend.value = {
        dates: flightTrendRes.data.dates || [],
        counts: flightTrendRes.data.counts || [],
        hours: flightTrendRes.data.hours || []
      }
    }
  } catch (error) {
    console.error('获取看板数据失败:', error)
    ElMessage.error('获取看板数据失败')
  }
}

const fetchDashboardData = loadDashboardData

const handleDateChange = async () => {
  await loadDashboardData()
  ElMessage.info('数据已更新')
}

const refreshData = async () => {
  try {
    await loadDashboardData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100%;
  max-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  padding-bottom: 20px;
  box-sizing: border-box;
}

/* 宇宙主题滚动条样式 */
.dashboard::-webkit-scrollbar {
  width: 8px;
}

.dashboard::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin: 10px 0;
}

.dashboard::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(124, 77, 255, 0.5);
  transition: all 0.3s ease;
}

.dashboard::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #4fc3f7 0%, #7c4dff 100%);
  box-shadow: 0 0 15px rgba(124, 77, 255, 0.8);
}

/* Firefox 滚动条样式 */
.dashboard {
  scrollbar-width: thin;
  scrollbar-color: rgba(124, 77, 255, 0.6) rgba(255, 255, 255, 0.05);
}

.toolbar-card {
  flex-shrink: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar h3 {
  margin: 0;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

:deep(.cosmic-date-picker .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(124, 77, 255, 0.3) !important;
  border-radius: 8px !important;
}

:deep(.cosmic-date-picker .el-input__inner) {
  color: rgba(255, 255, 255, 0.9) !important;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.overview-card {
  cursor: pointer;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.card-icon {
  font-size: 48px;
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 8px rgba(124, 77, 255, 0.5));
}

.card-info {
  flex: 1;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  min-height: 400px;
}

.chart-card.large {
  grid-column: span 2;
}

:deep(.chart-card .el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 24px;
}

:deep(.chart-card .el-card__body) {
  padding: 24px;
  background: transparent;
}

.chart {
  height: 350px;
}

/* ECharts 图表深色主题适配 */
:deep(.chart) {
  filter: brightness(0.95);
}

@media (max-width: 1400px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.large {
    grid-column: span 1;
  }
}
</style>
