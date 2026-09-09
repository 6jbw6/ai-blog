<template>
  <header class="navbar-wrapper">
    <div class="navbar-container">
      <!-- 左侧区域：品牌 Logo + 主导航条目（对齐火山引擎左侧排列布局） -->
      <div class="nav-left-group">
        <router-link to="/" class="brand-logo">
          <span class="logo-icon-svg">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 21H8L12 13L16 21H22L12 2Z" fill="#18181b"/>
              <path d="M12 6.5L7.8 17H10.5L12 14L13.5 17H16.2L12 6.5Z" fill="#10b981"/>
            </svg>
          </span>
          <span class="logo-text">AI-Blog</span>
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link to="/categories" class="nav-item">分类与标签</router-link>
          <a class="nav-item" href="javascript:void(0)" @click="aiChatStore.openSearch()">RAG 知识库</a>
        </nav>
      </div>

      <!-- 右侧区域：火山引擎同款圆角胶囊搜索框 + 控制台直连 + 用户态 -->
      <div class="nav-right-group">
        <!-- 胶囊搜索框（严格参考火山引擎胶囊样式） -->
        <div class="volcano-search-capsule" @click="aiChatStore.openSearch()">
          <el-icon class="search-icon"><Search /></el-icon>
          <span class="search-placeholder">搜索博文与知识库切片...</span>
          <kbd class="kbd-badge">Ctrl K</kbd>
        </div>

        <!-- 快捷功能文本链接（对齐火山引擎“文档 / 控制台”风格） -->
        <div class="quick-links">
          <button class="nav-action-link btn-ai-link" @click="aiChatStore.openChat()">
            <span class="pulse-dot"></span>
            <span>AI 智能体</span>
          </button>

          <router-link to="/admin/dashboard" class="nav-action-link">
            控制台
          </router-link>
        </div>

        <!-- 用户认证与头像徽章（对齐火山引擎右侧圆形状态徽标） -->
        <div class="nav-user-area">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown trigger="click">
              <div class="user-avatar-pill">
                <el-avatar :size="28" :src="userStore.user?.avatar || '/user-avatar.svg'" />
                <span class="user-name">{{ userStore.user?.nickname }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="userStore.isAdmin" @click="$router.push('/admin/dashboard')">
                    <el-icon><DataAnalysis /></el-icon> 运营看板
                  </el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isAdmin" @click="$router.push('/admin/article/new')">
                    <el-icon><EditPen /></el-icon> 发布博文 (AI写作)
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="userStore.logout()">
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <router-link to="/login" class="btn-login-pill">
              登录 / 注册
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { Search, DataAnalysis, EditPen } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAiChatStore } from '@/stores/aiChat'

const userStore = useUserStore()
const aiChatStore = useAiChatStore()

// 快捷键 Ctrl+K 打开语义搜索
const handleKeyDown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    aiChatStore.openSearch()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.navbar-wrapper {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid #e4e4e7;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

.navbar-container {
  max-width: 1520px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 左侧 Logo + 菜单链接群组 */
.nav-left-group {
  display: flex;
  align-items: center;
  gap: 2.25rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.logo-icon-svg {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 800;
  color: #18181b;
  letter-spacing: -0.4px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.75rem;
}

.nav-item {
  color: #27272a;
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s ease;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #059669;
}

/* 右侧搜索 + 动作栏 */
.nav-right-group {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

/* 火山引擎胶囊搜索栏 */
.volcano-search-capsule {
  width: 250px;
  height: 34px;
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 9999px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.volcano-search-capsule:hover {
  border-color: #18181b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-icon {
  color: #71717a;
  font-size: 14px;
}

.search-placeholder {
  font-size: 0.82rem;
  color: #a1a1aa;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  user-select: none;
}

.kbd-badge {
  font-size: 0.68rem;
  background: #f4f4f5;
  border: 1px solid #e4e4e7;
  border-radius: 4px;
  padding: 1px 5px;
  color: #71717a;
  font-family: inherit;
}

/* 快捷链接 */
.quick-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-action-link {
  background: transparent;
  border: none;
  font-size: 0.88rem;
  font-weight: 500;
  color: #27272a;
  text-decoration: none;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 6px;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-action-link:hover {
  color: #059669;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 1.6s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* 用户状态区 */
.nav-user-area {
  display: flex;
  align-items: center;
}

.user-avatar-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 3px 10px 3px 4px;
  border-radius: 9999px;
  border: 1px solid #e4e4e7;
  background: #ffffff;
  transition: all 0.2s ease;
}

.user-avatar-pill:hover {
  border-color: #10b981;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #18181b;
}

.btn-login-pill {
  padding: 5px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #18181b;
  background: #f4f4f5;
  border: 1px solid #e4e4e7;
  border-radius: 9999px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-login-pill:hover {
  background: #18181b;
  color: #ffffff;
  border-color: #18181b;
}

@media (max-width: 900px) {
  .volcano-search-capsule {
    display: none;
  }

  .nav-left-group {
    gap: 1rem;
  }

  .nav-links {
    gap: 1rem;
  }
}
</style>
