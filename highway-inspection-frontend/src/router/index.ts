import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/',
    redirect: '/map',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '/map',
        name: 'Map',
        component: () => import('@/views/Map.vue'),
        meta: { title: '地图总览', icon: 'MapLocation' }
      },
      {
        path: '/video',
        name: 'Video',
        component: () => import('@/views/Video.vue'),
        meta: { title: '视频巡检', icon: 'VideoCamera' }
      },
      {
        path: '/flights',
        name: 'Flights',
        component: () => import('@/views/Flights.vue'),
        meta: { title: '飞行申请', icon: 'Document' }
      },
      {
        path: '/airspace',
        name: 'Airspace',
        component: () => import('@/views/Airspace.vue'),
        meta: { title: '空域管理', icon: 'Location' }
      },
      {
        path: '/inspection-results',
        name: 'InspectionResults',
        component: () => import('@/views/InspectionResults.vue'),
        meta: { title: '巡检结果', icon: 'Warning' }
      },
      {
        path: '/mission-history',
        name: 'MissionHistory',
        component: () => import('@/views/MissionHistory.vue'),
        meta: { title: '历史任务', icon: 'Finished' }
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据看板', icon: 'DataAnalysis' }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人资料', icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.path === '/login' || to.path === '/register') {
    next()
  } else if (!token) {
    next('/login')
  } else {
    next()
  }
})

export default router
