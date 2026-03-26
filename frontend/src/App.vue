<template>
  <div class="app-container">
    <!-- 头部导航 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon><Document-Copy /></el-icon>
          <span>VocabQuiz</span>
        </div>
        <div class="nav-steps" v-if="showSteps">
          <el-steps :active="currentStep" simple finish-status="success">
            <el-step title="上传图片" />
            <el-step title="确认词汇" />
            <el-step title="查看题目" />
          </el-steps>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 底部 -->
    <el-footer class="app-footer">
      <p>智能词汇出题系统 © 2024</p>
    </el-footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const showSteps = computed(() => route.path !== '/')

const currentStep = computed(() => {
  const pathMap = {
    '/': 0,
    '/vocab': 1,
    '/result': 2
  }
  return pathMap[route.path] || 0
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  cursor: pointer;
  transition: transform 0.3s;
}

.logo:hover {
  transform: scale(1.02);
}

.nav-steps {
  flex: 1;
  max-width: 500px;
  margin-left: 40px;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  text-align: center;
  padding: 20px;
}

.app-footer p {
  margin: 0;
  opacity: 0.8;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .nav-steps {
    display: none;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style>
