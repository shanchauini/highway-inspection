<template>
  <div class="login-wrapper">
    <!-- 深空背景 -->
    <div class="cosmic-background">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
      <!-- 浮动粒子 -->
      <div class="particles">
        <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle()"></div>
      </div>
      <!-- 发光光晕 -->
      <div class="glow-orb glow-orb-1"></div>
      <div class="glow-orb glow-orb-2"></div>
      <div class="glow-orb glow-orb-3"></div>
    </div>

    <div class="login-container">
      <div class="system-title">公路巡检系统</div>
      <div class="login-layout">
        <div class="illustration-panel">
          <div class="illustration-image" :style="{ '--bg-image': `url(${highwayImageUrl})` }"></div>
          <div class="illustration-copy">
            <h2>智能巡检 · 实时报告</h2>
            <p>智能巡检场景下，结合道路与空域数据帮助管理员洞察实时状态。</p>
          </div>
        </div>

        <!-- 玻璃态登录卡片 -->
        <div class="login-card">
          <div class="card-glow"></div>
          <h2 class="title">
            <span class="title-text">登录</span>
            <span class="title-glow">登录</span>
          </h2>
          
          <el-form :model="form" :rules="rules" ref="formRef" class="cosmic-form">
            <el-form-item prop="username">
              <div class="input-wrapper">
                <div class="input-icon">👤</div>
                <el-input 
                  v-model="form.username" 
                  placeholder="用户名" 
                  class="cosmic-input"
                  clearable
                />
              </div>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="input-wrapper">
                <div class="input-icon">🔒</div>
                <el-input 
                  v-model="form.password" 
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="密码" 
                  class="cosmic-input"
                />
                <div class="password-toggle" @click="showPassword = !showPassword">
                  {{ showPassword ? '👁️' : '👁️‍🗨️' }}
                </div>
              </div>
            </el-form-item>
            
            <el-form-item prop="role">
              <div class="input-wrapper">
                <div class="input-icon">🎭</div>
                <el-select 
                  v-model="form.role" 
                  placeholder="选择角色"
                  class="cosmic-select"
                >
                  <el-option label="操作员" value="operator" />
                  <el-option label="管理员" value="admin" />
                </el-select>
              </div>
            </el-form-item>
            
            <el-form-item>
              <button 
                class="cosmic-button" 
                @click="onSubmit" 
                :disabled="loading"
              >
                <span class="button-text">{{ loading ? '登录中...' : '登录' }}</span>
                <span class="button-glow"></span>
              </button>
            </el-form-item>
            
            <el-form-item>
              <div class="register-link">
                <span class="register-text">还没有账号？</span>
                <span class="register-btn" @click="goToRegister">立即注册</span>
              </div>
            </el-form-item>
                                                                                            
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/modules'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref()
const showPassword = ref(false)
const isDevMode = import.meta.env.DEV // 开发环境标识

// 公路巡检图片路径
// 使用方法：
// 方法一（推荐）：将 highway-inspection.jpg 放入 public/ 目录，然后取消下面一行的注释
// const highwayImageUrl = ref<string>('/highway-inspection.jpg')
// 
// 方法二：使用 src/assets/images/ 目录，但需要先导入（图片存在后取消注释）
import highwayImageLocal from '@/assets/images/highway-inspection.png'
const highwayImageUrl = ref<string>(highwayImageLocal)
//
// 当前使用备用图片（在线图片，无需本地文件）
//const highwayImageUrl = ref<string>('https://images.unsplash.com/photo-1529429617124-aee711a70412?auto=format&fit=crop&w=1200&q=80')

const form = reactive({
  username: '',
  password: '',
  role: 'operator' as 'admin' | 'operator'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const getParticleStyle = () => {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const animationDelay = Math.random() * 20
  const animationDuration = Math.random() * 10 + 15
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`
  }
}

const onSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    // 开发模式：使用固定账号密码，无需后端
    const isDevAccount = (form.username === '名字1' || form.username === '1') && form.password === '1'
    
    if (isDevMode && isDevAccount) {
      // 模拟登录成功，延迟一下让loading效果更真实
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 根据选择的角色设置用户信息
      const devUser = {
        id: 'dev-1',
        username: '名字1',
        role: form.role,
        name: '名字1'
      }
      
      // 保存用户信息和模拟token
      userStore.login(
        devUser,
        'dev-token-' + Date.now()
      )
      
      ElMessage.success('开发模式登录成功')
      router.push('/map')
      return
    }
    
    // 正常模式：调用后端登录API
    const response: any = await authApi.login(form.username, form.password)
    
    // 检查响应格式
    if (response.code === 200 && response.data) {
      const { user, access_token } = response.data
      
      // 验证角色是否匹配
      if (user.role !== form.role) {
        ElMessage.error(`该账号不是${form.role === 'admin' ? '管理员' : '操作员'}，请选择正确的角色`)
        loading.value = false
        return
      }
      
      // 保存用户信息和token
      userStore.login(
        {
          id: user.id.toString(),
          username: user.username,
          role: user.role,
          name: user.username
        },
        access_token
      )
      
      ElMessage.success('登录成功')
      router.push('/map')
    } else {
      ElMessage.error(response.message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '登录失败，请检查用户名和密码'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1200px;
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.system-title {
  text-align: center;
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(120deg, #4fc3f7 0%, #7c4dff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(124, 77, 255, 0.5);
  letter-spacing: 4px;
}

.login-layout {
  display: flex;
  gap: 32px;
  align-items: stretch;
}

.illustration-panel {
  flex: 1;
  min-height: 520px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 45px rgba(5, 10, 32, 0.5);
}

.illustration-image {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(135deg, rgba(10, 14, 39, 0.85), rgba(5, 5, 15, 0.3)),
                    var(--bg-image, url('https://images.unsplash.com/photo-1529429617124-aee711a70412?auto=format&fit=crop&w=1200&q=80'));
  background-size: cover;
  background-position: center;
}

.illustration-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 20%, rgba(79, 195, 247, 0.4), transparent 55%);
  pointer-events: none;
}

.illustration-copy {
  position: absolute;
  bottom: 0;
  width: 100%;
  padding: 32px;
  background: linear-gradient(180deg, transparent, rgba(5, 11, 32, 0.85));
  color: rgba(255, 255, 255, 0.9);
}

.illustration-copy h2 {
  margin: 0 0 12px;
  font-size: 28px;
}

.illustration-copy p {
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.75);
}

/* 深空背景 */
.cosmic-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0f1419 50%, #1a1f3a 75%, #0a0e27 100%);
  background-size: 400% 400%;
  animation: cosmicGradient 20s ease infinite;
  z-index: 0;
}

@keyframes cosmicGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* 星星效果 */
.stars, .stars2, .stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image: radial-gradient(2px 2px at 20% 30%, #fff, transparent),
                    radial-gradient(2px 2px at 60% 70%, #fff, transparent),
                    radial-gradient(1px 1px at 50% 50%, #fff, transparent),
                    radial-gradient(1px 1px at 80% 10%, #fff, transparent),
                    radial-gradient(2px 2px at 90% 40%, #fff, transparent),
                    radial-gradient(1px 1px at 33% 60%, #fff, transparent),
                    radial-gradient(1px 1px at 55% 80%, #fff, transparent);
  background-repeat: repeat;
  background-size: 200px 200px;
  animation: sparkle 3s linear infinite;
  opacity: 0.8;
}

.stars2 {
  background-image: radial-gradient(1px 1px at 25% 25%, #4fc3f7, transparent),
                    radial-gradient(1px 1px at 75% 75%, #4fc3f7, transparent),
                    radial-gradient(1px 1px at 40% 60%, #4fc3f7, transparent);
  background-repeat: repeat;
  background-size: 300px 300px;
  animation: sparkle 5s linear infinite;
  opacity: 0.6;
}

.stars3 {
  background-image: radial-gradient(1px 1px at 15% 45%, #66bb6a, transparent),
                    radial-gradient(1px 1px at 85% 25%, #66bb6a, transparent);
  background-repeat: repeat;
  background-size: 400px 400px;
  animation: sparkle 7s linear infinite;
  opacity: 0.5;
}

@keyframes sparkle {
  from { transform: translateY(0); }
  to { transform: translateY(-200px); }
}

/* 浮动粒子 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: radial-gradient(circle, rgba(79, 195, 247, 0.8) 0%, transparent 70%);
  border-radius: 50%;
  bottom: -10px;
  animation: floatUp linear infinite;
  box-shadow: 0 0 10px rgba(79, 195, 247, 0.6);
}

@keyframes floatUp {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(50px);
    opacity: 0;
  }
}

/* 发光光晕 */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  animation: orbFloat 15s ease-in-out infinite;
}

.glow-orb-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #4fc3f7 0%, transparent 70%);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.glow-orb-2 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, #66bb6a 0%, transparent 70%);
  bottom: 15%;
  right: 15%;
  animation-delay: 5s;
}

.glow-orb-3 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #7c4dff 0%, transparent 70%);
  top: 50%;
  right: 10%;
  animation-delay: 10s;
}

@keyframes orbFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 玻璃态登录卡片 */
.login-card {
  position: relative;
  flex: 0 0 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  z-index: 1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(79, 195, 247, 0.2),
              inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, rgba(79, 195, 247, 0.3), rgba(102, 187, 106, 0.3));
  border-radius: 20px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
  filter: blur(10px);
}

.login-card:hover .card-glow {
  opacity: 1;
}

/* 标题 */
.title {
  text-align: center;
  margin: 0 0 40px;
  position: relative;
  height: 50px;
}

.title-text {
  position: relative;
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #4fc3f7 0%, #66bb6a 50%, #4fc3f7 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 3s ease infinite;
  z-index: 2;
  display: inline-block;
}

.title-glow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #4fc3f7 0%, #66bb6a 50%, #4fc3f7 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: blur(10px);
  opacity: 0.6;
  z-index: 1;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* 表单样式 */
.cosmic-form {
  margin-top: 20px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 15px;
  font-size: 18px;
  z-index: 2;
  filter: drop-shadow(0 0 3px rgba(79, 195, 247, 0.5));
}

/* 输入框样式 */
:deep(.cosmic-input .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(79, 195, 247, 0.3) !important;
  border-radius: 12px !important;
  padding-left: 45px !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.1) !important;
  transition: all 0.3s ease !important;
}

:deep(.cosmic-input .el-input__wrapper:hover) {
  border-color: rgba(79, 195, 247, 0.6) !important;
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.2) !important;
}

:deep(.cosmic-input .el-input__wrapper.is-focus) {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 25px rgba(79, 195, 247, 0.3) !important;
}

:deep(.cosmic-input .el-input__inner) {
  color: #fff !important;
  background: transparent !important;
}

:deep(.cosmic-input .el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4) !important;
}

/* 密码切换按钮 */
.password-toggle {
  position: absolute;
  right: 15px;
  cursor: pointer;
  font-size: 18px;
  z-index: 2;
  transition: transform 0.2s ease;
  filter: drop-shadow(0 0 3px rgba(79, 195, 247, 0.5));
}

.password-toggle:hover {
  transform: scale(1.2);
}

/* 选择框样式 */
:deep(.cosmic-select .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(79, 195, 247, 0.3) !important;
  border-radius: 12px !important;
  padding-left: 45px !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.1) !important;
  transition: all 0.3s ease !important;
}

:deep(.cosmic-select .el-select__wrapper:hover) {
  border-color: rgba(79, 195, 247, 0.6) !important;
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.2) !important;
}

:deep(.cosmic-select.is-focused .el-select__wrapper) {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 25px rgba(79, 195, 247, 0.3) !important;
}

:deep(.cosmic-select .el-select__selected-item) {
  color: #fff !important;
}

/* 登录按钮 */
.cosmic-button {
  position: relative;
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #4fc3f7 0%, #66bb6a 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4);
}

.cosmic-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 195, 247, 0.6);
  background: linear-gradient(135deg, #66bb6a 0%, #4fc3f7 100%);
}

.cosmic-button:active:not(:disabled) {
  transform: translateY(0);
}

.cosmic-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-text {
  position: relative;
  z-index: 2;
}

.button-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.cosmic-button:hover .button-glow {
  left: 100%;
}

/* 注册链接 */
.register-link {
  width: 100%;
  text-align: center;
  font-size: 14px;
  margin-top: 10px;
}

.register-text {
  margin-right: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.register-btn {
  color: #4fc3f7;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  background: linear-gradient(135deg, #4fc3f7 0%, #66bb6a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
}

.register-btn:hover {
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.8);
  transform: scale(1.05);
  display: inline-block;
}

/* 表单项样式 */
:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__error) {
  color: #ff6b6b;
  font-size: 12px;
  margin-top: 5px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .login-container {
    padding: 32px 16px 40px;
  }
}

@media (max-width: 960px) {
  .login-layout {
    flex-direction: column;
    align-items: center;
  }

  .illustration-panel {
    width: 100%;
    min-height: 360px;
  }

  .login-card {
    width: 100%;
    max-width: 520px;
    flex: none;
  }
}

@media (max-width: 768px) {
  .login-card {
    width: 90%;
    padding: 30px 20px;
  }
  
  .title-text,
  .title-glow {
    font-size: 28px;
  }

  .system-title {
    font-size: 32px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 25px 15px;
  }
  
  .title-text,
  .title-glow {
    font-size: 24px;
  }

  .system-title {
    font-size: 26px;
    letter-spacing: 2px;
  }
}
</style>

