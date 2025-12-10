<template>
  <el-card class="page-card cosmic-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="cosmic-title-small">飞行申请管理</span>
        <div class="tools">
          <button class="cosmic-button" @click="showCreateDialog" v-if="userStore.user?.role === 'operator'">
            <el-icon><Plus /></el-icon>
            新建申请
          </button>
          <button class="cosmic-button" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </button>
        </div>
      </div>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-section cosmic-form-section">
      <el-form :model="filterForm" inline>
        <el-form-item label="申请状态" class="white-label">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已过期" value="expired" />
            <el-option label="已终止" value="terminated" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请人" class="white-label">
          <el-input v-model="filterForm.applicantName" placeholder="请输入申请人姓名" clearable />
        </el-form-item>
        <el-form-item>
          <button class="cosmic-button" @click="handleFilter">筛选</button>
          <button class="cosmic-button" @click="resetFilter" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);">重置</button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 申请列表 -->
    <div class="table-wrapper">
      <el-table :data="filteredApplications" v-loading="loading" stripe>
      <el-table-column prop="id" label="申请ID" width="120" />
      <el-table-column label="申请人" width="100">
        <template #default="{ row }">
          {{ row.applicant?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="drone_model" label="无人机型号" width="120" />
      <el-table-column prop="task_purpose" label="任务目的" min-width="150" show-overflow-tooltip />
      <el-table-column label="申请空域" width="100">
        <template #default="{ row }">
          {{ row.airspace?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="total_time" label="计划时长(分钟)" width="120" />
      <el-table-column prop="planned_start_time" label="开始时间" width="150">
        <template #default="{ row }">
          {{ formatDateTime(row.planned_start_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="420" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewApplication(row)">查看</el-button>
          <el-button 
            v-if="userStore.user?.role === 'operator' && row.status === 'draft'" 
            size="small" 
            type="primary" 
            @click="editApplication(row)"
          >
            编辑
          </el-button>
          <el-button 
            v-if="userStore.user?.role === 'operator' && row.status === 'draft'"
            size="small"
            type="danger"
            plain
            @click="deleteDraft(row)"
          >
            删除
          </el-button>
          <el-button 
            v-if="userStore.user?.role === 'admin' && row.status === 'pending'" 
            size="small" 
            type="success" 
            @click="approveApplication(row)"
          >
            审批
          </el-button>
          <el-button
            v-if="userStore.user?.role === 'operator' && row.status === 'pending'"
            size="small"
            type="warning"
            plain
            @click="withdrawApplication(row)"
          >
            撤回
          </el-button>
          <el-button 
            v-if="userStore.user?.role === 'operator' && row.status === 'approved'" 
            size="small" 
            type="warning" 
            @click="requestLaunch(row)"
          >
            放飞申请
          </el-button>
          <el-button
            v-if="userStore.user?.role === 'admin' && row.status === 'approved'"
            size="small"
            type="danger"
            plain
            @click="terminateApplication(row)"
          >
            终止计划
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalApplications"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑申请对话框 -->
    <el-dialog 
      v-model="createDialogVisible" 
      :title="editingApplication ? '编辑申请' : '新建申请'" 
      width="800px"
    >
      <el-form :model="applicationForm" :rules="applicationRules" ref="applicationFormRef" label-width="120px">
        <el-form-item label="无人机型号" prop="drone_model">
          <el-input v-model="applicationForm.drone_model" placeholder="请输入无人机型号" />
        </el-form-item>
        
        <el-form-item label="任务目的" prop="task_purpose">
          <el-input v-model="applicationForm.task_purpose" type="textarea" :rows="3" placeholder="请详细描述任务目的" />
        </el-form-item>

        <el-form-item label="申请空域" prop="planned_airspace_id">
          <el-select v-model="applicationForm.planned_airspace_id" placeholder="请选择空域">
            <el-option 
              v-for="airspace in availableAirspaces" 
              :key="airspace.id" 
              :label="`${airspace.name} (${airspace.number}) ${airspace.status === 'occupied' ? '(占用中)' : ''}`" 
              :value="airspace.id"
            />
          </el-select>
          <div class="form-tip">提示：占用中的空域也可以申请，系统会自动检查时间是否冲突</div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="planned_start_time">
              <el-date-picker 
                v-model="applicationForm.planned_start_time" 
                type="datetime" 
                placeholder="选择开始时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="planned_end_time">
              <el-date-picker 
                v-model="applicationForm.planned_end_time" 
                type="datetime" 
                placeholder="选择结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="计划时长(分钟)" prop="total_time">
          <el-input-number v-model="applicationForm.total_time" :min="1" :max="480" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAsDraft">
          {{ editingApplication ? '保存修改' : '保存草稿' }}
        </el-button>
        <el-button
          v-if="editingApplication"
          type="danger"
          plain
          @click="handleDeleteFromDialog"
        >
          删除草稿
        </el-button>
        <el-button type="success" @click="submitApplication">提交申请</el-button>
      </template>
    </el-dialog>

    <!-- 申请详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="申请详情" width="800px">
      <el-descriptions :column="2" border v-if="currentApplication">
        <el-descriptions-item label="申请ID">{{ currentApplication.id }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentApplication.applicant?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="无人机型号">{{ currentApplication.drone_model }}</el-descriptions-item>
        <el-descriptions-item label="申请空域">{{ currentApplication.airspace?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="任务目的" :span="2">
          {{ currentApplication.task_purpose }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ formatDateTime(currentApplication.planned_start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ formatDateTime(currentApplication.planned_end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="计划时长">{{ currentApplication.total_time }}分钟</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentApplication.status)">
            {{ getStatusText(currentApplication.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentApplication.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(currentApplication.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="驳回理由" v-if="currentApplication.rejection_reason" :span="2">
          {{ currentApplication.rejection_reason }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog v-model="approveDialogVisible" title="审批申请" width="600px">
      <div class="approval-content">
        <h4>申请信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="申请人">{{ currentApplication?.applicant?.username || '-' }}</el-descriptions-item>
          <el-descriptions-item label="无人机">{{ currentApplication?.drone_model }}</el-descriptions-item>
          <el-descriptions-item label="任务目的">{{ currentApplication?.task_purpose }}</el-descriptions-item>
          <el-descriptions-item label="申请空域">{{ currentApplication?.airspace?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="计划时长">{{ currentApplication?.total_time }}分钟</el-descriptions-item>
          <el-descriptions-item label="飞行时间">{{ formatDateTime(currentApplication?.planned_start_time || '') }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px;">审批决定</h4>
        <el-form :model="approvalForm" ref="approvalFormRef" label-width="100px">
          <el-form-item label="审批结果" prop="decision">
            <el-radio-group v-model="approvalForm.decision">
              <el-radio :value="'approved'">批准</el-radio>
              <el-radio :value="'rejected'">驳回</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="审批意见" prop="reason">
            <el-input 
              v-model="approvalForm.reason" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入审批意见"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmApproval">确认审批</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useFlightStore, type FlightApplication } from '@/stores/flight'
import { useAirspaceStore } from '@/stores/airspace'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'

dayjs.extend(utc)

const userStore = useUserStore()
const flightStore = useFlightStore()
const airspaceStore = useAirspaceStore()

// 响应式数据
const loading = ref(false)
const createDialogVisible = ref(false)
const approveDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const editingApplication = ref<FlightApplication | null>(null)
const currentApplication = ref<FlightApplication | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const applicationFormRef = ref<any>(null)

// 筛选表单
const filterForm = ref({
  status: '',
  applicantName: ''
})

// 申请表单
const applicationForm = ref({
  drone_model: '',
  task_purpose: '',
  planned_airspace_id: '',
  planned_start_time: '',
  planned_end_time: '',
  total_time: 60,
  route: {
    type: 'LineString',
    coordinates: []
  } as any,
  is_long_term: false // 默认短期申请，不在表单中显示
})

// 审批表单
const approvalForm = ref({
  decision: 'approved' as 'approved' | 'rejected',
  reason: ''
})

// 飞行时长验证函数
const validateFlightDuration = (rule: any, value: number, callback: any) => {
  if (!value) {
    return callback(new Error('请输入飞行时长'))
  }
  
  if (value < 1) {
    return callback(new Error('飞行时长至少为1分钟'))
  }
  
  const startTime = applicationForm.value.planned_start_time
  const endTime = applicationForm.value.planned_end_time
  
  if (startTime && endTime) {
    const timeWindowMinutes = dayjs(endTime).diff(dayjs(startTime), 'minute')
    
    if (timeWindowMinutes <= 0) {
      return callback(new Error('结束时间必须晚于开始时间'))
    }
    
    if (value > timeWindowMinutes) {
      return callback(new Error(`飞行时长不能超过时间窗口（${timeWindowMinutes}分钟）`))
    }
  }
  
  callback()
}

// 表单验证规则
const applicationRules = {
  drone_model: [{ required: true, message: '请输入无人机型号', trigger: 'blur' }],
  task_purpose: [{ required: true, message: '请输入任务目的', trigger: 'blur' }],
  planned_airspace_id: [{ required: true, message: '请选择申请空域', trigger: 'change' }],
  planned_start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  planned_end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  total_time: [
    { required: true, message: '请输入计划时长', trigger: 'blur' },
    { validator: validateFlightDuration, trigger: 'blur' }
  ]
}

// 监听时间变化，触发时长验证
watch([
  () => applicationForm.value.planned_start_time,
  () => applicationForm.value.planned_end_time
], () => {
  // 如果已经填写了时长，重新验证
  if (applicationForm.value.total_time && applicationFormRef.value) {
    applicationFormRef.value.validateField('total_time')
  }
})

// 计算属性 - 从airspace store获取适飞区空域（包括占用中的空域）
const availableAirspaces = computed(() => airspaceStore.airspaces.filter(a => a.type === 'suitable'))

const filteredApplications = computed(() => {
  let apps = flightStore.applications
  
  // 应用筛选条件
  if (filterForm.value.status) {
    apps = apps.filter(app => app.status === filterForm.value.status)
  }
  if (filterForm.value.applicantName) {
    apps = apps.filter(app => {
      const applicantName = app.applicant?.username || ''
      return applicantName.toLowerCase().includes(filterForm.value.applicantName.toLowerCase())
    })
  }
  
  return apps
})

const totalApplications = computed(() => flightStore.total)

const getAirspaceCenter = (coords?: any): [number, number] | null => {
  if (!Array.isArray(coords)) return null
  const points = (coords as any[]).filter((p): p is [number, number] => Array.isArray(p) && p.length >= 2)
  if (points.length === 0) return null
  const sum = points.reduce(
    (acc, p) => {
      return [acc[0] + p[0], acc[1] + p[1]] as [number, number]
    },
    [0, 0] as [number, number]
  )
  return [sum[0] / points.length, sum[1] / points.length]
}

// 生成随机航线坐标
const generateRandomRoute = (airspaceCoords: any, numPoints: number = 8): any => {
  if (!Array.isArray(airspaceCoords) || airspaceCoords.length === 0) {
    return { type: 'LineString', coordinates: [[116.4, 39.9], [116.41, 39.91]] }
  }

  // 获取空域边界
  const coords = airspaceCoords[0] as [number, number][]
  if (coords.length < 3) {
    return { type: 'LineString', coordinates: [[116.4, 39.9], [116.41, 39.91]] }
  }

  // 计算边界框
  let minLng = coords[0][0], maxLng = coords[0][0]
  let minLat = coords[0][1], maxLat = coords[0][1]
  
  coords.forEach(point => {
    minLng = Math.min(minLng, point[0])
    maxLng = Math.max(maxLng, point[0])
    minLat = Math.min(minLat, point[1])
    maxLat = Math.max(maxLat, point[1])
  })

  // 生成随机航线点
  const routeCoords: [number, number][] = []
  
  // 起点
  const startLng = minLng + (maxLng - minLng) * 0.3
  const startLat = minLat + (maxLat - minLat) * 0.3
  routeCoords.push([startLng, startLat])
  
  // 中间点
  for (let i = 1; i < numPoints - 1; i++) {
    const ratio = i / (numPoints - 1)
    // 添加一些随机偏移
    const offset = (Math.random() - 0.5) * 0.01
    const lng = minLng + (maxLng - minLng) * ratio + offset
    const lat = minLat + (maxLat - minLat) * (0.3 + 0.4 * Math.sin(ratio * Math.PI)) + offset
    routeCoords.push([lng, lat])
  }
  
  // 终点
  const endLng = minLng + (maxLng - minLng) * 0.7
  const endLat = minLat + (maxLat - minLat) * 0.7
  routeCoords.push([endLng, endLat])
  
  return {
    type: 'LineString',
    coordinates: routeCoords
  }
}

// 生命周期
onMounted(async () => {
  await airspaceStore.fetchAirspaces()
  await flightStore.fetchFlights(currentPage.value, pageSize.value)
})

// 方法
const showCreateDialog = () => {
  editingApplication.value = null
  resetApplicationForm()
  createDialogVisible.value = true
}

const editApplication = (app: FlightApplication) => {
  editingApplication.value = app
  applicationForm.value = {
    drone_model: app.drone_model,
    task_purpose: app.task_purpose,
    planned_airspace_id: String(app.planned_airspace_id),
    planned_start_time: app.planned_start_time ? dayjs.utc(app.planned_start_time).local().format('YYYY-MM-DDTHH:mm:ss') : '',
    planned_end_time: app.planned_end_time ? dayjs.utc(app.planned_end_time).local().format('YYYY-MM-DDTHH:mm:ss') : '',
    total_time: app.total_time,
    route: app.route || { type: 'LineString', coordinates: [] },
    is_long_term: app.is_long_term || false // 保留字段但不显示
  }
  createDialogVisible.value = true
}

const resetApplicationForm = () => {
  applicationForm.value = {
    drone_model: '',
    task_purpose: '',
    planned_airspace_id: '',
    planned_start_time: '',
    planned_end_time: '',
    total_time: 60,
    route: { type: 'LineString', coordinates: [] },
    is_long_term: false // 默认短期申请
  }
}

const saveAsDraft = async () => {
  if (!applicationFormRef.value) return
  
  await applicationFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        // 验证必填字段
        if (!applicationForm.value.planned_start_time || !applicationForm.value.planned_end_time) {
          ElMessage.warning('请选择开始时间和结束时间')
          return
        }
        
        // 生成随机航线
        const selectedAirspaceId = Number(applicationForm.value.planned_airspace_id)
        const airspace = airspaceStore.airspaces.find(a => a.id === selectedAirspaceId)
        let route = applicationForm.value.route
        
        // 总是生成新的随机航线，而不是使用已有的
        if (airspace?.area?.coordinates) {
          route = generateRandomRoute(airspace.area.coordinates)
        } else {
          // 如果没有空域数据，使用默认航线
          route = { type: 'LineString', coordinates: [[116.4, 39.9], [116.41, 39.91], [116.42, 39.92]] }
        }
        
        const appData: any = {
          drone_model: applicationForm.value.drone_model,
          task_purpose: applicationForm.value.task_purpose,
          planned_airspace_id: Number(applicationForm.value.planned_airspace_id),
          planned_start_time: dayjs(applicationForm.value.planned_start_time).utc().format(),
          planned_end_time: dayjs(applicationForm.value.planned_end_time).utc().format(),
          total_time: applicationForm.value.total_time, // 直接使用表单填写的时长
          route: route,
          is_long_term: false // 默认短期申请
        }

        if (editingApplication.value) {
          await flightStore.updateFlight(editingApplication.value.id, appData)
          ElMessage.success('草稿已更新')
        } else {
          await flightStore.createFlight(appData)
          ElMessage.success('草稿已保存')
        }
        
        createDialogVisible.value = false
        await flightStore.fetchFlights(currentPage.value, pageSize.value)
      } catch (error) {
        // 错误已在store中处理
        console.error('保存失败:', error)
      }
    }
  })
}

const submitApplication = async () => {
  if (!applicationFormRef.value) return
  
  await applicationFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        // 验证必填字段
        if (!applicationForm.value.planned_start_time || !applicationForm.value.planned_end_time) {
          ElMessage.warning('请选择开始时间和结束时间')
          return
        }
        
        // 生成随机航线
        const selectedAirspaceId = Number(applicationForm.value.planned_airspace_id)
        const airspace = airspaceStore.airspaces.find(a => a.id === selectedAirspaceId)
        let route = applicationForm.value.route
        
        // 总是生成新的随机航线，而不是使用已有的
        if (airspace?.area?.coordinates) {
          route = generateRandomRoute(airspace.area.coordinates)
        } else {
          // 如果没有空域数据，使用默认航线
          route = { type: 'LineString', coordinates: [[116.4, 39.9], [116.41, 39.91], [116.42, 39.92]] }
        }
        
        const appData: any = {
          drone_model: applicationForm.value.drone_model,
          task_purpose: applicationForm.value.task_purpose,
          planned_airspace_id: Number(applicationForm.value.planned_airspace_id),
          planned_start_time: dayjs(applicationForm.value.planned_start_time as string).utc().format(),
          planned_end_time: dayjs(applicationForm.value.planned_end_time as string).utc().format(),
          total_time: applicationForm.value.total_time, // 直接使用表单填写的时长
          route: route,
          is_long_term: false // 默认短期申请
        }

        if (editingApplication.value) {
          // 如果是编辑状态，先更新再提交
          await flightStore.updateFlight(editingApplication.value.id, appData)
          await flightStore.submitFlight(editingApplication.value.id)
          ElMessage.success('申请已提交')
        } else {
          // 如果是新建，直接创建并提交（不保存草稿）
          const newApp = await flightStore.createFlight(appData)
          if (newApp) {
            await flightStore.submitFlight(newApp.id)
            ElMessage.success('申请已提交')
          }
        }
        
        createDialogVisible.value = false
        await flightStore.fetchFlights(currentPage.value, pageSize.value)
      } catch (error) {
        // 错误已在store中处理
        console.error('提交失败:', error)
      }
    }
  })
}

const approveApplication = (app: FlightApplication) => {
  currentApplication.value = app
  approvalForm.value = {
    decision: 'approved',
    reason: ''
  }
  approveDialogVisible.value = true
}

const confirmApproval = async () => {
  try {
    if (!currentApplication.value) return
    
    if (approvalForm.value.decision === 'approved') {
      await flightStore.approveFlight(currentApplication.value.id)
      ElMessage.success('申请已批准')
    } else {
      await flightStore.rejectFlight(currentApplication.value.id, approvalForm.value.reason)
      ElMessage.success('申请已驳回')
    }
    
    approveDialogVisible.value = false
    await flightStore.fetchFlights(currentPage.value, pageSize.value)
  } catch (error) {
    // 错误已在store中处理
    console.error('审批失败:', error)
  }
}

const requestLaunch = async (app: FlightApplication) => {
  try {
    // 检查时间是否在申请范围内（所有时间转换为本地时间比较）
    const now = dayjs()
    const startTime = dayjs.utc(app.planned_start_time).local()
    const endTime = dayjs.utc(app.planned_end_time).local()
    
    if (now.isBefore(startTime)) {
      ElMessage.warning(`放飞时间未到，申请的开始时间为：${formatDateTime(app.planned_start_time)}`)
      return
    }
    
    if (now.isAfter(endTime)) {
      ElMessage.warning(`放飞时间已过，申请的结束时间为：${formatDateTime(app.planned_end_time)}`)
      return
    }
    
    // 验证预计结束时间
    const estimatedFinishTime = now.add(app.total_time, 'minute')
    
    if (estimatedFinishTime.isAfter(endTime)) {
      const timeShortage = estimatedFinishTime.diff(endTime, 'minute')
      ElMessage.error({
        message: `预计结束时间（${estimatedFinishTime.format('HH:mm:ss')}）超出计划结束时间（${endTime.format('HH:mm:ss')}）约${timeShortage}分钟，无法完成飞行任务，不得放飞！`,
        duration: 5000,
        showClose: true
      })
      return
    }
    
    await ElMessageBox.confirm(
      `确认申请放飞？\n申请时间：${formatDateTime(app.planned_start_time)} 至 ${formatDateTime(app.planned_end_time)}\n当前时间：${formatDateTime(now.format())}\n预计结束：${estimatedFinishTime.format('YYYY-MM-DD HH:mm:ss')}`,
      '确认放飞',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await flightStore.launchFlight(app.id)
    ElMessage.success('放飞成功，任务已创建')
    await flightStore.fetchFlights(currentPage.value, pageSize.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在store中处理
      console.error('放飞失败:', error)
    }
  }
}

// 后端暂不支持删除飞行申请

const viewApplication = async (app: FlightApplication) => {
  try {
    // 获取完整的申请详情
    const response = await flightStore.getFlightById(app.id)
    if (response) {
      currentApplication.value = response
      detailDialogVisible.value = true
    } else {
      // 如果获取失败，使用当前数据
      currentApplication.value = app
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取申请详情失败:', error)
    // 即使失败也显示基本信息
    currentApplication.value = app
    detailDialogVisible.value = true
  }
}

const refreshData = async () => {
  await flightStore.fetchFlights(currentPage.value, pageSize.value)
  ElMessage.success('数据已刷新')
}

const handleFilter = () => {
  currentPage.value = 1
}

const resetFilter = () => {
  filterForm.value = {
    status: '',
    applicantName: ''
  }
  currentPage.value = 1
}

const handleSizeChange = async (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  await flightStore.fetchFlights(currentPage.value, pageSize.value)
}

const handleCurrentChange = async (page: number) => {
  currentPage.value = page
  await flightStore.fetchFlights(currentPage.value, pageSize.value)
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return dayjs.utc(dateTime).local().format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    expired: 'info',
    terminated: 'danger'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    expired: '已过期',
    terminated: '已终止'
  }
  return statusMap[status] || status
}

const deleteDraft = async (app: FlightApplication) => {
  try {
    await ElMessageBox.confirm(
      `确定删除飞行申请草稿「${app.task_purpose || app.drone_model}」吗？`,
      '删除草稿',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await flightStore.deleteFlight(app.id)
    if (editingApplication.value?.id === app.id) {
      createDialogVisible.value = false
      editingApplication.value = null
    }
    await flightStore.fetchFlights(currentPage.value, pageSize.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除草稿失败:', error)
    }
  }
}

const handleDeleteFromDialog = async () => {
  if (editingApplication.value) {
    await deleteDraft(editingApplication.value)
  }
}

const withdrawApplication = async (app: FlightApplication) => {
  try {
    await ElMessageBox.confirm(
      `确认撤回申请「${app.task_purpose || app.drone_model}」吗？撤回后可继续编辑并重新提交。`,
      '撤回申请',
      {
        confirmButtonText: '撤回',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await flightStore.withdrawFlight(app.id)
    await flightStore.fetchFlights(currentPage.value, pageSize.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('撤回申请失败:', error)
    }
  }
}

const terminateApplication = async (app: FlightApplication) => {
  try {
    await ElMessageBox.confirm(
      `确认终止申请「${app.task_purpose || app.drone_model}」吗？终止后将释放该空域使用计划。`,
      '终止计划',
      {
        confirmButtonText: '终止',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await flightStore.terminateFlight(app.id)
    await flightStore.fetchFlights(currentPage.value, pageSize.value)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('终止申请失败:', error)
    }
  }
}
</script>

<style scoped>
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
}

:deep(.white-label .el-form-item__label) {
  color: #fff !important;
}

:deep(.el-pagination) {
  color: #fff !important;
}

:deep(.el-pagination .el-pagination__total) {
  color: #fff !important;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  color: #fff !important;
}

:deep(.el-pagination .el-pager li) {
  color: #fff !important;
}

:deep(.el-pagination .el-pagination__sizes .el-select .el-input__inner) {
  color: #fff !important;
}

:deep(.el-pagination .el-pagination__jump) {
  color: #fff !important;
}

:deep(.el-pagination .el-pagination__jump .el-input__inner) {
  color: #fff !important;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.approval-content h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}
</style>
