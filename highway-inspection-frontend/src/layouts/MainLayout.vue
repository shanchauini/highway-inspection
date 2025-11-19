<template>
  <div class="main-layout">
    <!-- 宇宙背景 -->
    <div class="cosmic-background"></div>
    
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <h2 class="logo-title">公路巡检系统</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="rgba(48, 65, 86, 0.6)"
          text-color="rgba(191, 203, 217, 0.8)"
          active-text-color="#7c4dff"
        >
          <el-menu-item
            v-for="route in menuRoutes"
            :key="route.path"
            :index="route.path"
            class="cosmic-menu-item"
          >
            <el-icon><component :is="route.meta?.icon" /></el-icon>
            <span>{{ route.meta?.title }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header height="60px" class="header">
          <div class="header-left">
            <el-breadcrumb separator="/" class="cosmic-breadcrumb">
              <el-breadcrumb-item class="cosmic-breadcrumb-item">{{ $route.meta?.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" :src="userStore.user?.avatar">
                  {{ userStore.user?.name?.charAt(0) }}
                </el-avatar>
                <span class="username">{{ userStore.user?.name }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu class="cosmic-dropdown">
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 过滤菜单路由（根据用户角色）
const menuRoutes = computed(() => {
  return router.getRoutes()
    .filter(route => {
      // 排除登录、注册、根路径和个人资料（个人资料通过右上角菜单访问）
      return route.path !== '/' && 
             route.path !== '/login' && 
             route.path !== '/register' &&
             route.path !== '/profile'
    })
    .filter(route => {
      const roles = route.meta?.roles as string[]
      if (!roles) return true
      return roles.includes(userStore.user?.role || '')
    })
})

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.sidebar {
  background: rgba(48, 65, 86, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(43, 58, 75, 0.6);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  margin: 0;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #7c4dff 0%, #4fc3f7 50%, #7c4dff 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientFlow 3s ease infinite;
  text-shadow: 0 0 20px rgba(124, 77, 255, 0.8), 0 0 40px rgba(79, 195, 247, 0.6);
  filter: drop-shadow(0 0 10px rgba(124, 77, 255, 0.5));
}

@keyframes gradientFlow {
  0%, 100% { 
    background-position: 0% 50%;
    filter: drop-shadow(0 0 10px rgba(124, 77, 255, 0.5));
  }
  50% { 
    background-position: 100% 50%;
    filter: drop-shadow(0 0 20px rgba(79, 195, 247, 0.8));
  }
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 60px);
  background: transparent !important;
}

:deep(.cosmic-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.cosmic-menu-item:hover) {
  background: rgba(124, 77, 255, 0.2) !important;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(124, 77, 255, 0.3), rgba(79, 195, 247, 0.3)) !important;
  color: #fff !important;
  box-shadow: 0 0 15px rgba(124, 77, 255, 0.3);
}

.header {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.header-left {
  flex: 1;
}

:deep(.cosmic-breadcrumb) {
  color: #fff;
}

:deep(.cosmic-breadcrumb-item) {
  color: #fff !important;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.9);
}

.user-info:hover {
  background: rgba(124, 77, 255, 0.2);
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.main-content {
  background: transparent;
  padding: 20px;
  position: relative;
  z-index: 1;
  height: calc(100vh - 60px);
  overflow: hidden;
}

:deep(.cosmic-dropdown) {
  background: rgba(26, 31, 58, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

:deep(.cosmic-dropdown .el-dropdown-menu__item) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.cosmic-dropdown .el-dropdown-menu__item:hover) {
  background: rgba(124, 77, 255, 0.2) !important;
  color: #fff !important;
}
</style>
