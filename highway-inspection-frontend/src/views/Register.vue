<template>
  <div class="register-page">
    <div class="cosmic-layer">
      <div class="nebula nebula-1"></div>
      <div class="nebula nebula-2"></div>
      <div class="floating-particles">
        <span
          v-for="(particle, index) in particles"
          :key="`particle-${index}`"
          class="particle"
          :style="particle"
        ></span>
      </div>
    </div>

    <div class="register-content">
      <div class="register-card cosmic-card glass-card">
        <div class="card-glow"></div>
        <header class="card-header">
          <h2 class="cosmic-title cosmic-title-large">创建账号</h2>
          <p class="card-subtitle"></p>
        </header>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          hide-required-asterisk
          class="cosmic-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入 3-80 位字符"
              class="cosmic-input"
              clearable
            >
              <template #prefix>
                <span class="input-prefix">@</span>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="至少 4 个字符，支持符号组合"
              class="cosmic-input"
            >
              <template #prefix>
                <span class="input-prefix">🔒</span>
              </template>
              <template #suffix>
                <el-icon class="password-toggle" @mousedown.prevent @click="showPassword = !showPassword">
                  <component :is="showPassword ? View : Hide" />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="再次输入以确认"
              class="cosmic-input"
            >
              <template #prefix>
                <span class="input-prefix">✨</span>
              </template>
              <template #suffix>
                <el-icon class="password-toggle" @mousedown.prevent @click="showConfirmPassword = !showConfirmPassword">
                  <component :is="showConfirmPassword ? View : Hide" />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-actions">
            <button
              type="button"
              class="cosmic-button full-width"
              :disabled="loading"
              @click="onSubmit"
            >
              {{ loading ? '注册中...' : '注册账号' }}
            </button>
            <div class="login-link">
              <span>已有账号？</span>
              <span class="login-anchor" @click="goToLogin">立即登录</span>
            </div>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/modules'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Hide, View } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const formRef = ref<FormInstance>()
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const createParticleStyle = () => {
  const size = Math.random() * 8 + 4
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    animationDuration: `${12 + Math.random() * 10}s`,
    animationDelay: `${Math.random() * 8}s`,
    opacity: (0.2 + Math.random() * 0.5).toFixed(2)
  }
}

const particles = ref(Array.from({ length: 20 }, () => createParticleStyle()))

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 80, message: '用户名长度在 3 到 80 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 128, message: '密码长度在 4 到 128 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const onSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        const response = await authApi.register(form.username, form.password, 'operator')

        if (response.code === 200) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } else {
          ElMessage.error(response.message || '注册失败')
        }
      } catch (error: any) {
        console.error('注册失败:', error)
        const errorMsg = error.response?.data?.message || error.message || '注册失败，请检查输入信息'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
@import '@/assets/styles/cosmic-theme.css';

.register-page {
  min-height: 100vh;
  position: relative;
  background: radial-gradient(circle at 20% 20%, rgba(79, 195, 247, 0.2), transparent 40%),
              radial-gradient(circle at 80% 0%, rgba(124, 77, 255, 0.25), transparent 45%),
              #050a1f;
  overflow: hidden;
  padding: 40px 0;
}

.cosmic-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.nebula {
  position: absolute;
  width: 60vw;
  height: 60vw;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.4;
  animation: nebulaFloat 18s ease-in-out infinite alternate;
}

.nebula-1 {
  top: -20%;
  left: -10%;
  background: radial-gradient(circle, rgba(79, 195, 247, 0.6), transparent 70%);
}

.nebula-2 {
  bottom: -30%;
  right: -10%;
  background: radial-gradient(circle, rgba(124, 77, 255, 0.6), transparent 65%);
  animation-delay: 6s;
}

@keyframes nebulaFloat {
  0% {
    transform: translate(0, 0) scale(1);
  }
  100% {
    transform: translate(30px, -30px) scale(1.1);
  }
}

.floating-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.floating-particles .particle {
  position: absolute;
  top: 100%;
  background: radial-gradient(circle, rgba(79, 195, 247, 0.9) 0%, transparent 70%);
  border-radius: 50%;
  box-shadow: 0 0 12px rgba(79, 195, 247, 0.6);
  animation: floatUp linear infinite;
}

@keyframes floatUp {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  100% {
    transform: translateY(-120vh) translateX(40px);
    opacity: 0.1;
  }
}

.register-content {
  position: relative;
  z-index: 1;
  max-width: 500px;
  margin: 0 auto;
  padding: 40px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-card {
  width: 100%;
  max-width: 500px;
  padding: 32px 32px 40px;
  position: relative;
  overflow: hidden;
}

.glass-card {
  background: rgba(12, 18, 46, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(25px);
}

.card-glow {
  position: absolute;
  inset: -2px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(79, 195, 247, 0.5), rgba(124, 77, 255, 0.5));
  filter: blur(50px);
  opacity: 0.3;
  z-index: -1;
}

.card-header {
  margin-bottom: 24px;
}

.card-subtitle {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.cosmic-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.cosmic-form :deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
}

.input-prefix {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.65);
}

.password-toggle {
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.password-toggle:hover {
  transform: scale(1.1);
}

.form-actions {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.full-width {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.cosmic-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.login-anchor {
  margin-left: 6px;
  color: #4fc3f7;
  cursor: pointer;
  background: linear-gradient(135deg, #4fc3f7, #7c4dff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 600;
}

.login-anchor:hover {
  text-shadow: 0 0 12px rgba(124, 77, 255, 0.7);
}

@media (max-width: 600px) {
  .register-page {
    padding: 20px 0;
  }

  .register-card {
    padding: 24px;
  }
}
</style>

