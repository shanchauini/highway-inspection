<template>
  <div class="profile-page">
    <el-card shadow="never" class="cosmic-card">
      <template #header>
        <div class="card-header">
          <span class="cosmic-title-small">个人资料</span>
        </div>
      </template>

      <el-form :model="profileForm" :rules="rules" ref="formRef" label-width="120px" style="max-width: 600px" class="cosmic-form-section">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-tag :type="profileForm.role === 'admin' ? 'danger' : 'primary'">
            {{ profileForm.role === 'admin' ? '管理员' : '操作员' }}
          </el-tag>
        </el-form-item>

        <el-form-item label="创建时间">
          <span>{{ formatDateTime(profileForm.created_at) }}</span>
        </el-form-item>

        <el-form-item label="更新时间">
          <span>{{ formatDateTime(profileForm.updated_at) }}</span>
        </el-form-item>

        <el-divider class="cosmic-divider" />

        <h3 class="cosmic-title-small">修改密码</h3>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input 
            v-model="profileForm.newPassword" 
            type="password" 
            placeholder="请输入新密码（留空则不修改）"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="profileForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <button class="cosmic-button" @click="updatePassword" :disabled="saving">修改密码</button>
          <button class="cosmic-button" @click="resetForm" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);">重置</button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api/modules'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const saving = ref(false)

const profileForm = reactive({
  id: 0,
  username: '',
  role: 'operator' as 'admin' | 'operator',
  created_at: '',
  updated_at: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (profileForm.newPassword && value !== profileForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  newPassword: [
    { 
      validator: (rule, value, callback) => {
        if (value && (value.length < 4 || value.length > 128)) {
          callback(new Error('密码长度在 4 到 128 个字符'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  if (!userStore.user) {
    ElMessage.error('用户信息不存在')
    return
  }

  try {
    // 使用当前登录用户的ID获取完整用户信息
    // 后端API要求：普通用户只能查看自己，管理员可以查看所有用户
    const userId = parseInt(userStore.user.id)
    if (isNaN(userId)) {
      ElMessage.error('用户ID格式错误')
      return
    }

    const response = await userApi.getUserById(userId) as any
    
    if (response.code === 200 && response.data) {
      const user = response.data
      profileForm.id = user.id
      profileForm.username = user.username
      profileForm.role = user.role
      profileForm.created_at = user.created_at
      profileForm.updated_at = user.updated_at
    } else {
      ElMessage.error(response.message || '获取用户信息失败')
    }
  } catch (error: any) {
    console.error('获取用户信息失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '获取用户信息失败'
    
    // 如果是403权限错误，说明后端权限检查有问题，但前端应该能访问自己的信息
    if (error.response?.status === 403) {
      ElMessage.error('无权限查看用户信息，请检查登录状态')
    } else {
      ElMessage.error(errorMsg)
    }
    
    // 如果API失败，使用store中的基本信息
    if (userStore.user) {
      const userId = parseInt(userStore.user.id)
      if (!isNaN(userId)) {
        profileForm.id = userId
        profileForm.username = userStore.user.username
        profileForm.role = userStore.user.role as 'admin' | 'operator'
      }
    }
  }
}

// 修改密码
const updatePassword = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (!profileForm.newPassword) {
        ElMessage.warning('请输入新密码')
        return
      }

      if (profileForm.newPassword.length < 4 || profileForm.newPassword.length > 128) {
        ElMessage.warning('密码长度在 4 到 128 个字符')
        return
      }

      if (profileForm.newPassword !== profileForm.confirmPassword) {
        ElMessage.warning('两次输入密码不一致')
        return
      }

      if (!profileForm.id || profileForm.id === 0) {
        ElMessage.error('用户ID无效，请刷新页面重试')
        await fetchUserInfo()
        return
      }

      saving.value = true
      try {
        const response = await userApi.updateUser(profileForm.id, {
          password: profileForm.newPassword
        }) as any

        if (response.code === 200) {
          ElMessage.success('密码修改成功')
          resetForm()
        } else {
          ElMessage.error(response.message || '密码修改失败')
        }
      } catch (error: any) {
        console.error('修改密码失败:', error)
        const errorMsg = error.response?.data?.message || error.message || '修改密码失败'
        ElMessage.error(errorMsg)
      } finally {
        saving.value = false
      }
    }
  })
}

const resetForm = () => {
  profileForm.newPassword = ''
  profileForm.confirmPassword = ''
  formRef.value?.resetFields()
}

const formatDateTime = (date?: string) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.profile-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 20px 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>

