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
            <div class="cosmic-stat-value">{{ alertStats.total }}</div>
            <div class="cosmic-stat-label">告警事件总数</div>
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

      <!-- 告警类型分布 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">告警类型分布</span>
        </template>
        <v-chart class="chart" :option="alertTypeOption" autoresize />
      </el-card>

      <!-- 告警趋势 -->
      <el-card shadow="never" class="chart-card cosmic-card">
        <template #header>
          <span class="cosmic-title-small">告警趋势</span>
        </template>
        <v-chart class="chart" :option="alertTrendOption" autoresize />
      </el-card>

      <!-- 巡检成果统计 -->
      <el-card shadow="never" class="chart-card large cosmic-card">
        <template #header>
          <span class="cosmic-title-small">公路巡检成果统计</span>
        </template>
        <v-chart class="chart" :option="inspectionResultsOption" autoresize />
      </el-card>

      <!-- 高频问题路段 -->
      <el-card shadow="never" class="chart-card large cosmic-card">
        <template #header>
          <span class="cosmic-title-small">高频问题路段 TOP10</span>
        </template>
        <v-chart class="chart" :option="problemSectionsOption" autoresize />
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
import { useAlertStore } from '@/stores/alert'
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

const alertStore = useAlertStore()
const airspaceStore = useAirspaceStore()

// 响应式数据
const dateRange = ref<[string, string]>([
  new Date(Date.now() - 30 * 24 * 3600000).toISOString().split('T')[0],
  new Date().toISOString().split('T')[0]
])

// 飞行统计数据（后端返回）
const flightStats = ref({
  total: 0,
  totalHours: 0,
  totalDistance: 0
})

// 告警统计数据
const alertStats = ref({
  total: 0,
  byType: {
    traffic_accident: 0,
    road_anomaly: 0,
    facility_abnormal: 0,
    intrusion: 0,
    collision: 0,
    weather: 0
  },
  trend: [] as { date: string; count: number }[]
})

// 计算属性
const alertStatsComputed = computed(() => {
  const stats = alertStore.getStatistics()
  // 根据日期范围过滤
  let filteredAlerts = alertStore.alerts
  if (dateRange.value) {
    const [start, end] = dateRange.value
    filteredAlerts = filteredAlerts.filter(a => {
      const date = a.created_at?.split('T')[0] || ''
      return date >= start && date <= end
    })
  }
  
  return {
    total: filteredAlerts.length,
    byType: {
      traffic_accident: filteredAlerts.filter(a => a.event_type === 'traffic_accident').length,
      road_anomaly: filteredAlerts.filter(a => a.event_type === 'road_anomaly').length,
      facility_abnormal: filteredAlerts.filter(a => a.event_type === 'facility_abnormal').length,
      intrusion: filteredAlerts.filter(a => a.event_type === 'intrusion').length,
      collision: filteredAlerts.filter(a => a.event_type === 'collision').length,
      weather: filteredAlerts.filter(a => a.event_type === 'weather').length
    },
    trend: []
  }
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

// 告警类型分布图表配置
const alertTypeOption = computed(() => {
  // 使用响应式数据而不是计算属性
  const stats = alertStats.value
  
  const alertTypeData = [
    { value: stats.byType.traffic_accident, name: '交通事故', itemStyle: { color: '#F56C6C' } },
    { value: stats.byType.road_anomaly, name: '路况异常', itemStyle: { color: '#E6A23C' } },
    { value: stats.byType.facility_abnormal, name: '设施异常', itemStyle: { color: '#409EFF' } },
    { value: stats.byType.intrusion, name: '空域侵入', itemStyle: { color: '#909399' } },
    { value: stats.byType.collision, name: '碰撞风险', itemStyle: { color: '#F56C6C' } },
    { value: stats.byType.weather, name: '气象预警', itemStyle: { color: '#67C23A' } }
  ]
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
      textStyle: {
        color: '#fff'
      }
    },
    series: [
      {
        name: '告警类型',
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
        data: alertTypeData
      }
    ]
  }
})

// 告警趋势图表配置
const alertTrendOption = computed(() => {
  // 使用响应式数据而不是计算属性
  const trendData = alertStats.value.trend
  
  return {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['告警数量'],
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
        name: '告警数量',
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
          color: '#F56C6C'
        },
        smooth: true
      }
    ]
  }
})

// 巡检成果统计图表配置
const inspectionResultsOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['发现数量', '已处理'],
    textStyle: {
      color: '#fff'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
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
  yAxis: {
    type: 'category',
    data: inspectionResults.value.categories,
    axisLine: {
      lineStyle: {
        color: '#fff'
      }
    },
    axisLabel: {
      color: '#fff'
    }
  },
  series: [
    {
      name: '发现数量',
      type: 'bar',
      data: inspectionResults.value.found,
      itemStyle: {
        color: '#409EFF'
      }
    },
    {
      name: '已处理',
      type: 'bar',
      data: inspectionResults.value.resolved,
      itemStyle: {
        color: '#67C23A'
      }
    }
  ]
}))

// 高频问题路段图表配置
const problemSectionsOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: '事件数量',
    nameTextStyle: {
      color: '#fff'
    },
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
  yAxis: { 
    type: 'category', 
    data: problemSections.value.sections,
    axisLine: {
      lineStyle: {
        color: '#fff'
      }
    },
    axisLabel: {
      color: '#fff'
    }
  },
  series: [
    {
      name: '事件数量',
      type: 'bar',
      data: problemSections.value.counts,
      itemStyle: {
        color: (params: any) => {
          const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A']
          return colors[Math.floor(params.dataIndex / 3)]
        }
      },
      label: {
        show: true,
        position: 'right'
      }
    }
  ]
}))

// 生命周期
onMounted(async () => {
  await loadDashboardData()
})

// 方法
// API 衍生数据
const flightTrend = ref<{ dates: string[]; counts: number[]; hours: number[] }>({ dates: [], counts: [], hours: [] })
const inspectionResults = ref<{ categories: string[]; found: number[]; resolved: number[] }>({ categories: [], found: [], resolved: [] })
const problemSections = ref<{ sections: string[]; counts: number[] }>({ sections: [], counts: [] })

const loadDashboardData = async () => {
  try {
    const params = (() => {
      if (!dateRange.value || dateRange.value.length !== 2) return {}
      const [start, end] = dateRange.value
      return { start_date: start, end_date: end }
    })()

    // 加载统计数据 - 使用dashboardApi
    const [statsRes, flightStatsRes, airspaceUsageRes, alertStatsRes, alertTrendRes] = await Promise.all([
      dashboardApi.getStats(params),
      dashboardApi.getFlightStats(params),
      dashboardApi.getAirspaceUsage(params),
      dashboardApi.getAlertStats(params),
      dashboardApi.getAlertTrend(params).catch(() => ({ code: 200, data: { dates: [], counts: [] } }))
    ])
    
    // 飞行统计卡片
    if (flightStatsRes.code === 200 && flightStatsRes.data) {
      flightStats.value = {
        total: flightStatsRes.data.total_missions || 0,
        totalHours: flightStatsRes.data.total_duration || 0,
        totalDistance: (flightStatsRes.data.total_missions || 0) * 5 // 假设每次任务平均5公里
      }
    }

    // 飞行趋势
    if (statsRes.code === 200 && statsRes.data) {
      // 从statsRes.data中获取飞行趋势数据
      const flightTrendData = statsRes.data.flight_trend || { dates: [], counts: [], hours: [] };
      flightTrend.value = {
        dates: flightTrendData.dates || [],
        counts: flightTrendData.counts || [],
        hours: flightTrendData.hours || []
      }
    } else {
      flightTrend.value = { dates: [], counts: [], hours: [] }
    }

    // 巡检成果
    if (statsRes.code === 200 && statsRes.data) {
      const inspectionData = statsRes.data.inspection_results || { categories: [], found: [], resolved: [] };
      inspectionResults.value = {
        categories: inspectionData.categories || [],
        found: inspectionData.found || [],
        resolved: inspectionData.resolved || []
      }
    } else {
      // 使用模拟数据
      inspectionResults.value = {
        categories: ['裂缝', '坑洼', '护栏损坏', '标志模糊', '路面磨损'],
        found: [28, 22, 15, 12, 23],
        resolved: [25, 18, 12, 8, 20]
      }
    }

    // 高频问题路段
    if (statsRes.code === 200 && statsRes.data) {
      const problemData = statsRes.data.problem_sections || { sections: [], counts: [] };
      problemSections.value = {
        sections: problemData.sections || [],
        counts: problemData.counts || []
      }
    } else {
      // 使用模拟数据
      problemSections.value = {
        sections: ['G15沈海高速K125', 'G2京沪高速K88', 'G3京台高速K205', 'G4京港澳高速K312', 'G5京昆高速K156', 'G6京藏高速K95', 'G7京新高速K234', 'G15沈海高速K89', 'G2京沪高速K145', 'G3京台高速K78'],
        counts: [24, 22, 20, 18, 16, 14, 12, 10, 8, 6]
      }
    }
    
    // 告警统计
    await Promise.all([
      airspaceStore.fetchAirspaces(),
      alertStore.fetchAlerts()
    ])

    if (alertStatsRes.code === 200 && alertStatsRes.data) {
      // 更新告警统计数据
      alertStats.value.total = alertStatsRes.data.total_alerts || 0;
      
      // 更新告警类型分布
      const typeStats = alertStatsRes.data.type_stats || {};
      alertStats.value.byType = {
        traffic_accident: typeStats.traffic_accident || 0,
        road_anomaly: typeStats.road_anomaly || 0,
        facility_abnormal: typeStats.facility_abnormal || 0,
        intrusion: typeStats.intrusion || 0,
        collision: typeStats.collision || 0,
        weather: typeStats.weather || 0
      };
    }

    // 告警趋势
    if (alertTrendRes.code === 200 && alertTrendRes.data) {
      const { dates, counts } = alertTrendRes.data
      // 更新告警趋势数据
      alertStats.value.trend = dates.map((d: string, i: number) => ({ date: d, count: counts[i] || 0 }))
    }
  } catch (error) {
    console.error('加载看板数据失败:', error)
    // 失败时不使用虚拟数据，保持为空，仍加载基础数据避免卡片完全空白
    await Promise.allSettled([airspaceStore.fetchAirspaces(), alertStore.fetchAlerts()])
  }
}

const handleDateChange = async () => {
  await loadDashboardData()
  ElMessage.info('数据已更新')
}

const refreshData = async () => {
  await loadDashboardData()
  ElMessage.success('数据已刷新')
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
