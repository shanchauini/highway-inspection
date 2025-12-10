<template>
  <el-card class="page-card cosmic-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="cosmic-title-small">智能巡检</span>
        <div class="tools">
          <el-select
            v-model="selectedMissionId"
            placeholder="选择所属任务"
            style="width: 200px; margin-right: 10px;"
            :loading="missionLoading"
            filterable
            clearable
          >
            <el-option
              v-for="mission in missionOptions"
              :key="mission.id"
              :label="mission.label"
              :value="mission.id"
            />
          </el-select>
          <el-select v-model="detectionType" placeholder="选择检测类型" style="width: 180px; margin-right: 10px;">
            <el-option label="交通拥堵检测" value="traffic_congestion" />
            <el-option label="地面破损检测" value="road_damage" />
          </el-select>
          <button class="cosmic-button" @click="importMedia">导入文件</button>
        </div>
      </div>
    </template>
    
    <el-row :gutter="20">
      <!-- 媒体播放区域 -->
      <el-col :span="16">
        <el-card shadow="never" class="cosmic-card">
          <template #header>
            <span class="cosmic-title-small">{{ mediaType === 'image' ? '图片预览' : '视频播放' }}</span>
          </template>
          <div class="video-container">
            <div v-if="!currentMedia" class="video-placeholder">
              <el-icon size="64"><VideoCamera /></el-icon>
              <p>请选择或导入图片/视频文件</p>
            </div>
            <img 
              v-else-if="mediaType === 'image'"
              :src="currentMedia"
              class="image-preview"
              alt="预览图片"
            />
            <video 
              v-else
              ref="videoPlayer"
              controls
              class="video-player"
              :src="currentMedia"
            ></video>
          </div>
        </el-card>
      </el-col>
      
      <!-- 检测结果区域 -->
      <el-col :span="8">
        <el-card shadow="never" class="cosmic-card detection-result-card">
          <template #header>
            <div class="card-header">
              <span class="cosmic-title-small">检测结果</span>
              <el-button 
                v-if="currentVideoId" 
                size="small" 
                type="primary" 
                :loading="loadingAnalysis"
                @click="loadAnalysisResults"
              >
                刷新结果
              </el-button>
            </div>
          </template>
          
          <!-- 交通拥堵检测结果 -->
          <div v-if="detectionType === 'traffic_congestion'" class="traffic-detection-result">
            <div v-if="loadingAnalysis" class="loading-container">
              <el-icon class="is-loading" :size="32"><Loading /></el-icon>
              <span>AI分析中...</span>
            </div>
            <div v-else-if="!currentVideoId" class="empty-container">
              <el-icon :size="48" color="rgba(255,255,255,0.3)"><VideoCamera /></el-icon>
              <p>请先导入图片进行检测</p>
            </div>
            <div v-else-if="analysisResults.length === 0" class="empty-container">
              <el-empty description="暂无检测结果，点击刷新重试" />
            </div>
            <div v-else class="traffic-result-display">
              <!-- 主要结果展示 -->
              <div 
                v-for="result in analysisResults" 
                :key="result.id" 
                class="traffic-result-card"
                :class="getTrafficLevelClass(result.target_type)"
              >
                <div class="traffic-level-indicator">
                  <div class="level-icon">
                    <el-icon :size="40">
                      <WarningFilled v-if="isHeavyTraffic(result.target_type)" />
                      <InfoFilled v-else-if="isMediumTraffic(result.target_type)" />
                      <SuccessFilled v-else />
                    </el-icon>
                  </div>
                  <div class="level-text">{{ getTrafficLevelText(result.target_type) }}</div>
                </div>
                
                <div class="traffic-details">
                  <div class="detail-row">
                    <span class="detail-label">拥堵等级</span>
                    <el-tag 
                      :type="getTrafficTagType(result.target_type)" 
                      size="large"
                      effect="dark"
                    >
                      {{ result.target_type }}
                    </el-tag>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">置信度</span>
                    <div class="confidence-bar">
                      <el-progress 
                        :percentage="Math.round((result.confidence || 0) * 100)" 
                        :color="getTrafficColor(result.target_type)"
                        :stroke-width="12"
                      />
                    </div>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">检测时间</span>
                    <span class="detail-value">{{ formatTime(result.occurred_time) }}</span>
                  </div>
                </div>
                
                <!-- 预警提示 -->
                <div 
                  v-if="isHeavyTraffic(result.target_type)" 
                  class="traffic-warning"
                >
                  <el-icon><WarningFilled /></el-icon>
                  <span>严重拥堵预警：建议立即采取交通疏导措施</span>
                </div>
                <div 
                  v-else-if="isMediumTraffic(result.target_type)" 
                  class="traffic-caution"
                >
                  <el-icon><InfoFilled /></el-icon>
                  <span>中度拥堵提示：请关注交通状况变化</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 地面破损检测结果 -->
          <div v-else-if="detectionType === 'road_damage'" class="road-damage-result">
            <div v-if="loadingAnalysis" class="loading-container">
              <el-icon class="is-loading" :size="32"><Loading /></el-icon>
              <span>AI分析中...</span>
            </div>
            <div v-else-if="!currentVideoId" class="empty-container">
              <el-icon :size="48" color="rgba(255,255,255,0.3)"><VideoCamera /></el-icon>
              <p>请先导入图片进行检测</p>
            </div>
            <div v-else-if="analysisResults.length === 0" class="empty-container">
              <el-empty description="暂无检测结果，点击刷新重试" />
            </div>
            <div v-else class="road-damage-display">
              <!-- 结果图片展示 -->
              <div v-if="roadDamageResultImage" class="result-image-container">
                <img 
                  :src="roadDamageResultImage" 
                  class="result-image"
                  alt="检测结果图片"
                  @click="showFullImage = true"
                />
                <div class="image-hint">点击查看大图</div>
              </div>
              
              <!-- 检测目标列表 -->
              <div class="damage-list">
                <div 
                  v-for="(result, index) in analysisResults" 
                  :key="result.id" 
                  class="damage-item"
                  :class="getDamageLevelClass(result.target_type)"
                >
                  <div class="damage-header">
                    <div class="damage-icon">
                      <el-icon :size="24">
                        <WarningFilled v-if="isSevereDamage(result.target_type)" />
                        <InfoFilled v-else-if="isModerateDamage(result.target_type)" />
                        <SuccessFilled v-else />
                      </el-icon>
                    </div>
                    <span class="damage-index">#{{ index + 1 }}</span>
                  </div>
                  
                  <div class="damage-details">
                    <div class="detail-row">
                      <span class="detail-label">破损程度</span>
                      <el-tag 
                        :type="getDamageTagType(result.target_type)" 
                        size="default"
                        effect="dark"
                      >
                        {{ result.target_type }}
                      </el-tag>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">置信度</span>
                      <div class="confidence-bar">
                        <el-progress 
                          :percentage="Math.round((result.confidence || 0) * 100)" 
                          :color="getDamageColor(result.target_type)"
                          :stroke-width="10"
                        />
                      </div>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">检测时间</span>
                      <span class="detail-value">{{ formatTime(result.occurred_time) }}</span>
                    </div>
                  </div>
                  
                  <!-- 预警提示 -->
                  <div v-if="isSevereDamage(result.target_type)" class="damage-warning">
                    <el-icon><WarningFilled /></el-icon>
                    <span>重度破损预警：建议立即安排维修</span>
                  </div>
                  <div v-else-if="isModerateDamage(result.target_type)" class="damage-caution">
                    <el-icon><InfoFilled /></el-icon>
                    <span>中度破损提示：请安排定期检修</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 其他检测类型 -->
          <div v-else class="other-detection-result">
            <div class="empty-container">
              <el-empty description="请选择检测类型" />
            </div>
          </div>
        </el-card>
        
        <!-- 结果图片大图弹窗（移到条件块外面） -->
        <el-dialog v-model="showFullImage" title="检测结果" width="80%">
          <img 
            v-if="roadDamageResultImage"
            :src="roadDamageResultImage" 
            style="width: 100%; height: auto;"
            alt="检测结果大图"
          />
        </el-dialog>
      </el-col>
    </el-row>
    
    <!-- 文件上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="导入文件" width="500px">
      <div style="margin-bottom: 15px;">
        <el-alert 
          :title="`当前检测类型: ${detectionTypeLabel}`" 
          type="info" 
          :closable="false"
        />
      </div>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :accept="acceptedFileTypes"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将图片或视频文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持图片格式：JPG、PNG、JPEG<br/>
            支持视频格式：MP4、AVI 等<br/>
            文件大小不超过 500MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :loading="uploading">
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCamera, UploadFilled, Loading, WarningFilled, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'
import { useVideoStore } from '@/stores/video'
import type { AnalysisResult } from '@/stores/ai'
import { useMissionStore } from '@/stores/mission'

const videoStore = useVideoStore()
const missionStore = useMissionStore()

const currentMedia = ref<string>('')
const currentVideoId = ref<number | null>(null)
const mediaType = ref<'video' | 'image'>('video')
const detectionType = ref<string>('traffic_congestion')
const selectedMissionId = ref<number | null>(null)
const missionLoading = ref(false)
// const activeTab = ref('events') // 暂时不用
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const videoPlayer = ref<HTMLVideoElement>()
const analysisResults = ref<AnalysisResult[]>([])
const loadingAnalysis = ref(false)
const showFullImage = ref(false)

// 获取地面破损检测结果图片URL
const roadDamageResultImage = computed(() => {
  const firstResult = analysisResults.value[0]
  if (firstResult && firstResult.result_image) {
    const imagePath = firstResult.result_image
    // 将本地路径转换为可访问的URL
    // 路径格式: uploads/detection_results/road_damage/xxx.jpg
    const relativePath = imagePath.replace(/\\/g, '/').split('uploads/')[1]
    if (relativePath) {
      return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'}/uploads/${relativePath}`
    }
  }
  return null
})

// 检测类型标签
const detectionTypeLabel = computed(() => {
  const typeMap: { [key: string]: string } = {
    'traffic_congestion': '交通拥堵检测',
    'road_damage': '地面破损检测'
  }
  return typeMap[detectionType.value] || '未知类型'
})

// 接受的文件类型
const acceptedFileTypes = computed(() => {
  return 'image/jpeg,image/jpg,image/png,video/mp4,video/avi,video/*'
})

// 只显示正在执行的任务
const missionOptions = computed(() => {
  return missionStore.activeMissions
    .filter(mission => mission.status === 'executing')
    .map(mission => ({
      id: mission.id,
      label: `任务 #${mission.id}${mission.route_distance ? ` | ${mission.route_distance.toFixed(1)}km` : ''}${mission.start_time ? ` | ${new Date(mission.start_time).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}` : ''}`
    }))
})

// ===== 交通拥堵检测辅助函数 =====

// 判断是否为重度拥堵
const isHeavyTraffic = (type: string) => {
  return type?.includes('heavy') || type?.includes('重度')
}

// 判断是否为中度拥堵
const isMediumTraffic = (type: string) => {
  return type?.includes('medium') || type?.includes('中度')
}

// 获取交通拥堵等级样式类
const getTrafficLevelClass = (type: string) => {
  if (isHeavyTraffic(type)) return 'level-heavy'
  if (isMediumTraffic(type)) return 'level-medium'
  return 'level-light'
}

// 获取交通拥堵等级文本
const getTrafficLevelText = (type: string) => {
  if (isHeavyTraffic(type)) return '严重拥堵'
  if (isMediumTraffic(type)) return '中度拥堵'
  return '轻微拥堵'
}

// 获取交通拥堵标签类型
const getTrafficTagType = (type: string): 'success' | 'warning' | 'danger' | 'info' => {
  if (isHeavyTraffic(type)) return 'danger'
  if (isMediumTraffic(type)) return 'warning'
  return 'success'
}

// 获取交通拥堵颜色
const getTrafficColor = (type: string) => {
  if (isHeavyTraffic(type)) return '#f56c6c'
  if (isMediumTraffic(type)) return '#e6a23c'
  return '#67c23a'
}

// ===== 地面破损检测辅助函数 =====

// 判断是否为重度破损
const isSevereDamage = (type: string) => {
  return type?.includes('重度')
}

// 判断是否为中度破损
const isModerateDamage = (type: string) => {
  return type?.includes('中度')
}

// 获取破损等级样式类
const getDamageLevelClass = (type: string) => {
  if (isSevereDamage(type)) return 'damage-severe'
  if (isModerateDamage(type)) return 'damage-moderate'
  return 'damage-light'
}

// 获取破损标签类型
const getDamageTagType = (type: string): 'success' | 'warning' | 'danger' | 'info' => {
  if (isSevereDamage(type)) return 'danger'
  if (isModerateDamage(type)) return 'warning'
  return 'success'
}

// 获取破损颜色
const getDamageColor = (type: string) => {
  if (isSevereDamage(type)) return '#f56c6c'
  if (isModerateDamage(type)) return '#e6a23c'
  return '#67c23a'
}

// 格式化时间
const formatTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 加载分析结果
const loadAnalysisResults = async () => {
  if (!currentVideoId.value) return
  
  loadingAnalysis.value = true
  try {
    const results = await videoStore.fetchAnalysisResults(currentVideoId.value)
    analysisResults.value = results || []
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  } finally {
    loadingAnalysis.value = false
  }
}

// 监听视频ID变化，自动加载分析结果
watch(currentVideoId, (newId) => {
  if (newId) {
    loadAnalysisResults()
  } else {
    analysisResults.value = []
  }
})

const importMedia = () => {
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  // 判断文件类型
  if (file.raw.type.startsWith('image/')) {
    mediaType.value = 'image'
  } else if (file.raw.type.startsWith('video/')) {
    mediaType.value = 'video'
  }
}

const confirmUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  if (!selectedMissionId.value) {
    ElMessage.warning('请选择所属任务')
    return
  }
  
  uploading.value = true
  
  try {
    // 创建FormData用于文件上传
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('mission_id', selectedMissionId.value.toString())
    formData.append('detection_type', detectionType.value)
    formData.append('collected_time', new Date().toISOString())
    formData.append('road_section', 'G1京哈高速')
    formData.append('file_format', selectedFile.value.name.split('.').pop() || 'mp4')
    formData.append('file_size', selectedFile.value.size.toString())
    formData.append('media_type', mediaType.value)
    
    // 调用上传API
    const response = await videoStore.uploadMediaFile(formData)
    
    if (response) {
      // 创建本地预览URL
      const mediaUrl = URL.createObjectURL(selectedFile.value)
      currentMedia.value = mediaUrl
      currentVideoId.value = response.id
      
      ElMessage.success(`${mediaType.value === 'image' ? '图片' : '视频'}导入成功`)
      uploadDialogVisible.value = false
      
      // 如果是图片，立即加载分析结果
      if (mediaType.value === 'image') {
        setTimeout(() => {
          loadAnalysisResults()
        }, 2000) // 给后端处理时间
      } else {
        // 视频需要手动触发分析
        ElMessage.info('视频已上传，请等待分析完成后刷新结果')
      }
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    ElMessage.error('文件导入失败')
  } finally {
    uploading.value = false
  }
}

onMounted(async () => {
  // 加载正在执行的任务列表
  missionLoading.value = true
  try {
    await missionStore.fetchActiveMissions()
    // 如果只有一个正在执行的任务，自动选中
    if (missionStore.activeMissions.length === 1 && missionStore.activeMissions[0]) {
      selectedMissionId.value = missionStore.activeMissions[0].id
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    missionLoading.value = false
  }
})
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

.video-container {
  width: 100%;
  height: 400px;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.events-list,
.targets-list {
  height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.6);
}

.loading-container {
  gap: 12px;
}

.results-container,
.targets-container {
  padding: 8px 0;
}

.result-item {
  padding: 12px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(124, 77, 255, 0.5);
  transform: translateX(4px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.result-content {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.confidence,
.bounding-box {
  margin-top: 4px;
}

.target-group {
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.target-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.target-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.target-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.target-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.target-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.target-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.target-confidence {
  font-size: 12px;
  color: rgba(124, 77, 255, 0.8);
  font-weight: 500;
}

/* 宇宙主题滚动条样式 */
.events-list::-webkit-scrollbar,
.targets-list::-webkit-scrollbar {
  width: 6px;
}

.events-list::-webkit-scrollbar-track,
.targets-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.events-list::-webkit-scrollbar-thumb,
.targets-list::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%);
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(124, 77, 255, 0.5);
}

.events-list::-webkit-scrollbar-thumb:hover,
.targets-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #4fc3f7 0%, #7c4dff 100%);
  box-shadow: 0 0 12px rgba(124, 77, 255, 0.8);
}

.events-list,
.targets-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(124, 77, 255, 0.6) rgba(255, 255, 255, 0.05);
}

/* 标签页未选中时字体为白色 */
:deep(.el-tabs__item) {
  color: #fff !important;
}

:deep(.el-tabs__item:hover) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-tabs__item.is-active) {
  color: #fff !important;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 100%);
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
}

/* ===== 交通拥堵检测结果样式 ===== */
.detection-result-card {
  min-height: 400px;
}

.traffic-detection-result,
.road-damage-result,
.other-detection-result {
  min-height: 350px;
}

.traffic-result-display {
  padding: 8px 0;
}

.traffic-result-card {
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.traffic-result-card.level-heavy {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.2) 0%, rgba(245, 108, 108, 0.05) 100%);
  border: 2px solid rgba(245, 108, 108, 0.5);
  box-shadow: 0 4px 20px rgba(245, 108, 108, 0.2);
}

.traffic-result-card.level-medium {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(230, 162, 60, 0.05) 100%);
  border: 2px solid rgba(230, 162, 60, 0.5);
  box-shadow: 0 4px 20px rgba(230, 162, 60, 0.2);
}

.traffic-result-card.level-light {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.05) 100%);
  border: 2px solid rgba(103, 194, 58, 0.5);
  box-shadow: 0 4px 20px rgba(103, 194, 58, 0.2);
}

.traffic-level-indicator {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.level-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.level-heavy .level-icon {
  color: #f56c6c;
}

.level-medium .level-icon {
  color: #e6a23c;
}

.level-light .level-icon {
  color: #67c23a;
}

.level-text {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.level-heavy .level-text {
  color: #f56c6c;
}

.level-medium .level-text {
  color: #e6a23c;
}

.level-light .level-text {
  color: #67c23a;
}

.traffic-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  min-width: 80px;
}

.detail-value {
  font-size: 14px;
  color: #fff;
}

.confidence-bar {
  flex: 1;
  margin-left: 16px;
}

.traffic-warning,
.traffic-caution {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
}

.traffic-warning {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
  animation: pulse-warning 2s infinite;
}

.traffic-caution {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.3);
}

@keyframes pulse-warning {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* ===== 地面破损检测结果样式 ===== */
.road-damage-display {
  padding: 8px 0;
}

.result-image-container {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.result-image {
  width: 100%;
  height: auto;
  max-height: 200px;
  object-fit: contain;
  background: #000;
  transition: transform 0.3s ease;
}

.result-image:hover {
  transform: scale(1.02);
}

.image-hint {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.damage-list {
  max-height: 300px;
  overflow-y: auto;
}

.damage-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.damage-item.damage-severe {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.2) 0%, rgba(245, 108, 108, 0.05) 100%);
  border: 1px solid rgba(245, 108, 108, 0.4);
}

.damage-item.damage-moderate {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(230, 162, 60, 0.05) 100%);
  border: 1px solid rgba(230, 162, 60, 0.4);
}

.damage-item.damage-light {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.05) 100%);
  border: 1px solid rgba(103, 194, 58, 0.4);
}

.damage-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.damage-icon {
  display: flex;
  align-items: center;
}

.damage-severe .damage-icon {
  color: #f56c6c;
}

.damage-moderate .damage-icon {
  color: #e6a23c;
}

.damage-light .damage-icon {
  color: #67c23a;
}

.damage-index {
  font-size: 14px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.8);
}

.damage-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.damage-warning,
.damage-caution {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
}

.damage-warning {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
  animation: pulse-warning 2s infinite;
}

.damage-caution {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.3);
}

/* 地面破损检测 - 开发中（保留备用） */
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.coming-soon h3 {
  margin: 16px 0 8px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
}

.coming-soon p {
  margin-bottom: 16px;
  font-size: 14px;
}

/* 空状态样式优化 */
.empty-container {
  min-height: 200px;
}

.empty-container p {
  margin-top: 12px;
  font-size: 14px;
}
</style>

