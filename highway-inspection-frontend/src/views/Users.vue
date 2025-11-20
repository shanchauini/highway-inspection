<template>
  <div class="user-management">
    <!-- 顶部统计 -->
    <div class="stats-cards">
      <el-card shadow="never" class="stat-card cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.total }}</div>
            <div class="cosmic-stat-label">用户总数</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><Avatar /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.byRole.operator }}</div>
            <div class="cosmic-stat-label">操作员</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card cosmic-card">
        <div class="stat-content">
          <el-icon class="stat-icon"><Lock /></el-icon>
          <div class="stat-info">
            <div class="cosmic-stat-value">{{ stats.byRole.admin }}</div>
            <div class="cosmic-stat-label">管理员</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主内容 -->
    <el-card class="main-card cosmic-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="cosmic-title-small">用户列表</span>
          <div class="tools">
            <button class="cosmic-button" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新建用户
            </button>
            <button class="cosmic-button" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </button>
          </div>
        </div>
      </template>

      <!-- 筛选 -->
      <div class="filter-section cosmic-form-section">
        <el-form :model="filterForm" inline>
          <el-form-item label="角色">
            <el-select v-model="filterForm.role" placeholder="全部角色" clearable @change="handleFilter">
              <el-option label="管理员" value="admin" />
              <el-option label="操作员" value="operator" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 用户表格 -->
      <el-table :data="usersStore.users" v-loading="usersStore.loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editUser(row)">编辑</el-button>
            <el-button size="small" type="info" @click="resetPassword(row)">重置密码</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDelete(row)"
              :disabled="isCurrentUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="usersStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="userForm.username" 
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>

        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item v-if="!editingUser" label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="userForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select 
            v-model="userForm.role" 
            placeholder="请选择角色" 
            style="width: 100%"
            :disabled="isCurrentUser(editingUser) && userForm.role === 'admin'"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
          </el-select>
          <div v-if="isCurrentUser(editingUser) && userForm.role === 'admin'" class="el-form-item-message">
            不能修改自己的管理员角色
          </div>
        </el-form-item>

        <el-form-item v-if="editingUser" label="新密码" prop="newPassword">
          <el-input 
            v-model="userForm.newPassword" 
            type="password" 
            placeholder="留空则不修改密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { 
  User, Avatar, Lock, Plus, Refresh
} from '@element-plus/icons-vue'
import { useUsersStore, type User as UserType } from '@/stores/users'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const usersStore = useUsersStore()
const userStore = useUserStore()

// 状态
const saving = ref(false)
const dialogVisible = ref(false)
const editingUser = ref<UserType | null>(null)
const userFormRef = ref<FormInstance>()

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选
const filterForm = ref({
  role: ''
})

// 用户表单
const userForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'operator' as 'admin' | 'operator',
  newPassword: ''
})

// 表单验证规则
const userRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 80, message: '用户名长度在 3 到 80 个字符', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (usersStore.isUsernameExists(value, editingUser.value?.id)) {
          callback(new Error('用户名已存在'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 128, message: '密码长度在 4 到 128 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== userForm.value.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
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
  ]
}

// 计算属性
const stats = computed(() => usersStore.getStatistics())

// 方法
const refreshData = async () => {
  await usersStore.fetchUsers(currentPage.value, pageSize.value, filterForm.value.role || undefined)
  ElMessage.success('数据已刷新')
}

const showCreateDialog = () => {
  editingUser.value = null
  resetForm()
  dialogVisible.value = true
}

const editUser = (user: UserType) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    password: '',
    confirmPassword: '',
    role: user.role,
    newPassword: ''
  }
  dialogVisible.value = true
}

const saveUser = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true

      try {
        if (editingUser.value) {
          // 更新用户
          const updates: { role?: 'admin' | 'operator'; password?: string } = {
            role: userForm.value.role
          }
          
          // 如果输入了新密码，则更新密码
          if (userForm.value.newPassword) {
            updates.password = userForm.value.newPassword
          }
          
          // 检查是否是当前用户试图修改自己的角色
          if (isCurrentUser(editingUser.value) && userForm.value.role !== 'admin') {
            ElMessage.error('不能将自己从管理员降级为操作员')
            return
          }
          
          await usersStore.updateUser(editingUser.value.id, updates)
          ElMessage.success('用户更新成功')
        } else {
          // 创建用户
          await usersStore.createUser(
            userForm.value.username,
            userForm.value.password,
            userForm.value.role
          )
          ElMessage.success('用户创建成功')
        }

        dialogVisible.value = false
        resetForm()
        await refreshData()
      } catch (error: any) {
        // 错误已在store中处理
        console.error('保存用户失败:', error)
      } finally {
        saving.value = false
      }
    }
  })
}

const resetForm = () => {
  userForm.value = {
    username: '',
    password: '',
    confirmPassword: '',
    role: 'operator',
    newPassword: ''
  }
  userFormRef.value?.resetFields()
}

const resetPassword = (user: UserType) => {
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.{4,128}/,
    inputErrorMessage: '密码长度在 4 到 128 个字符'
  }).then(async ({ value }) => {
    await usersStore.resetPassword(user.id, value)
    ElMessage.success('密码重置成功')
  }).catch(() => {
    ElMessage.info('已取消')
  })
}

const handleDelete = (user: UserType) => {
  ElMessageBox.confirm('确定要删除该用户吗？此操作不可恢复！', '确认删除', {
    type: 'error'
  }).then(async () => {
    await usersStore.deleteUser(user.id)
    ElMessage.success('用户已删除')
    await refreshData()
  }).catch(() => {})
}

const isCurrentUser = (user: UserType) => {
  return userStore.user && userStore.user.id === user.id.toString()
}

const handleFilter = () => {
  currentPage.value = 1
  refreshData()
}

const resetFilter = () => {
  filterForm.value = {
    role: ''
  }
  currentPage.value = 1
  refreshData()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  refreshData()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  refreshData()
}

const formatDateTime = (date?: string) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getRoleText = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    operator: '操作员'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, any> = {
    admin: 'danger',
    operator: 'primary'
  }
  return typeMap[role] || ''
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.user-management {
  padding: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tools {
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.pagination-section {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.el-form-item-message {
  color: #F56C6C;
  font-size: 12px;
  line-height: 1.5;
  padding-top: 4px;
  min-height: 18px;
}
</style>

