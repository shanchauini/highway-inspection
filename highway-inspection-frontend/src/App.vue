<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
onMounted(() => {
  userStore.initUser()
})
</script>

<template>
  <router-view />
  
</template>

<style scoped>
html, body, #app {
  height: 100%;
}
</style>
