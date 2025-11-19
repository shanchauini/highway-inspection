<template>
  <el-card class="page-card cosmic-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="cosmic-title-small">视频巡检</span>
        <div class="tools">
          <button class="cosmic-button" @click="importVideo">导入视频</button>
          <button class="cosmic-button" @click="startLiveStream">开始直播</button>
        </div>
      </div>
    </template>
    
    <el-row :gutter="20">
      <!-- 视频播放区域 -->
      <el-col :span="16">
        <el-card shadow="never" class="cosmic-card">
          <template #header>
            <span class="cosmic-title-small">视频播放</span>
          </template>
          <div class="video-container">
            <div v-if="!currentVideo" class="video-placeholder">
              <el-icon size="64"><VideoCamera /></el-icon>
              <p>请选择或导入视频文件</p>
            </div>
            <video 
              v-else
              ref="videoPlayer"
              controls
              class="video-player"
              :src="currentVideo"
            ></video>
          </div>
        </el-card>
      </el-col>
      
      <!-- 检测结果与事件列表 -->
      <el-col :span="8">
        <el-card shadow="never" class="cosmic-card">
          <template #header>
            <span class="cosmic-title-small">检测结果</span>
          </template>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="实时事件" name="events">
              <div class="events-list cosmic-scrollable">
                <el-empty description="暂无检测事件" />
              </div>
            </el-tab-pane>
            <el-tab-pane label="目标识别" name="targets">
              <div class="targets-list cosmic-scrollable">
                <el-empty description="暂无识别目标" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 文件上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="导入视频文件" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept="video/*"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将视频文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 MP4、AVI 等格式，文件大小不超过 500MB
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCamera, UploadFilled } from '@element-plus/icons-vue'
import { videoApi } from '@/api/modules'

const currentVideo = ref<string>('')
const activeTab = ref('events')
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const videoPlayer = ref<HTMLVideoElement>()

const importVideo = () => {
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const confirmUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择视频文件')
    return
  }
  
  uploading.value = true
  
  try {
    // 调用真实API上传视频
    const metadata = {
      taskId: 'task_' + Date.now(),
      collectionTime: new Date().toISOString(),
      collectionSection: 'G1京哈高速',
      droneNumber: 'UAV001'
    }
    
    const response = await videoApi.uploadVideo(selectedFile.value, metadata)
    
    // 创建本地预览URL
    const videoUrl = URL.createObjectURL(selectedFile.value)
    currentVideo.value = videoUrl
    
    ElMessage.success('视频导入成功')
    uploadDialogVisible.value = false
    
    // 自动开始分析
    if (response.videoId) {
      setTimeout(() => {
        startAnalysis(response.videoId)
      }, 1000)
    }
  } catch (error) {
    console.error('视频上传失败:', error)
    ElMessage.error('视频导入失败')
  } finally {
    uploading.value = false
  }
}

const startAnalysis = async (videoId: string) => {
  try {
    ElMessage.info('正在启动视频分析...')
    await videoApi.startAnalysis(videoId)
    ElMessage.success('视频分析已启动')
  } catch (error) {
    ElMessage.error('启动分析失败')
  }
}

const startLiveStream = async () => {
  try {
    ElMessage.info('正在连接无人机直播流...')
    
    // 获取直播流地址
    const response = await videoApi.getLiveStreamUrl('UAV001')
    
    if (response.streamUrl) {
      currentVideo.value = response.streamUrl
      ElMessage.success('直播流连接成功')
    } else {
      ElMessage.warning('暂无可用的直播流')
    }
  } catch (error) {
    ElMessage.error('连接直播流失败')
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

.events-list,
.targets-list {
  height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
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
</style>

