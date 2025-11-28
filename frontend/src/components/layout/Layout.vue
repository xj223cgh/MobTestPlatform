<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
            <h1 v-if="!isCollapsed" style="color: white; margin: 0; font-size: 18px;">MobTest</h1>
            <h1 v-else style="color: white; margin: 0; font-size: 14px;">MT</h1>
          </div>
      
      <el-menu
        :default-active="$route.path.replace('/', '')"
        :collapse="isCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item 
          v-for="menuRoute in menuRoutes" 
          :key="menuRoute.path" 
          :index="menuRoute.path.replace('/', '')"
        >
          <el-icon v-if="menuRoute.meta.icon">
            <component :is="menuRoute.meta.icon" />
          </el-icon>
          <template #title>{{ menuRoute.meta.title }}</template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="collapse-btn"
          >
            <el-icon><Expand v-if="isCollapsed" /><Fold v-else /></el-icon>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <!-- 动态生成面包屑 -->
            <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
            
            <!-- 生成中间层级面包屑 -->
            <template v-if="breadcrumbItems.length > 0">
              <el-breadcrumb-item
                v-for="item in breadcrumbItems"
                :key="item.path"
                :to="{ path: item.path }"
              >
                <div class="breadcrumb-item-with-close">
                  {{ item.title }}
                  <el-button
                    type="text"
                    size="small"
                    @click.stop="handleCloseBreadcrumb(item.path)"
                    class="breadcrumb-close-btn"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
              </el-breadcrumb-item>
            </template>
            
            <!-- 当前页面面包屑，带关闭按钮，仅当不是首页时显示 -->
            <el-breadcrumb-item v-if="currentRoute.meta.title && currentRoute.path !== '/home'">
              <div class="breadcrumb-item-with-close">
                {{ currentRoute.meta.title }}
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleCloseBreadcrumb()"
                  class="breadcrumb-close-btn"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 全屏按钮 -->
          <el-tooltip content="全屏" placement="bottom">
            <el-button type="text" @click="toggleFullscreen" class="header-btn">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>

          <!-- 用户信息 -->
          <el-dropdown @command="handleCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.avatar">
                {{ userStore.userName.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.userName }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import {
  Document,
  Setting,
  QuestionFilled,
  Expand,
  Fold,
  FullScreen,
  ArrowDown,
  User,
  SwitchButton,
  Odometer,
  Monitor,
  Menu,
  UserFilled,
  Warning,
  Tools,
  HomeFilled,
  Briefcase,
  ChatRound,
  Tickets,
  Close
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 当前路由
const currentRoute = computed(() => route)

// 菜单路由
  const menuRoutes = computed(() => {
    const routes = router.getRoutes() || []
    const layoutRoute = routes.find(route => route.name === 'Layout')
    
    if (!layoutRoute || !layoutRoute.children) {
      return []
    }
    
    // 直接返回Layout组件的children，保持路由配置中的顺序，排除hidden为true的路由
    return layoutRoute.children.filter(route => 
      route && 
      route.path && 
      route.meta?.title && 
      route.meta?.hidden !== true &&
      !['profile', '403', '404', 'login', 'register', 'forgot-password', 'reset-password'].includes(route.path)
    )
  })

// 生成面包屑层级
const breadcrumbItems = computed(() => {
  const items = []
  const path = currentRoute.value.path
  
  // 如果是项目详情页面，添加项目管理面包屑
  if (path.startsWith('/projects/') && path !== '/projects') {
    const projectRoute = menuRoutes.value.find(route => route.path === 'projects')
    if (projectRoute) {
      items.push({
        path: '/projects',
        title: projectRoute.meta.title
      })
    }
  }
  
  return items
})

// 切换侧边栏
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 关闭面包屑，返回指定页面或上一个页面
const handleCloseBreadcrumb = (path = '') => {
  if (path) {
    // 如果指定了路径，直接跳转到该路径
    router.push(path)
  } else if (currentRoute.value.path.startsWith('/projects/')) {
    // 如果当前是项目详情页面，返回项目列表页面
    router.push('/projects')
  } else {
    // 其他页面，返回首页
    router.push('/home')
  }
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // TODO: 跳转到设置页面
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        // 先开始登出流程，不等待API响应
        try {
          await userStore.logout()
        } catch (error) {
          // logout函数内部已经处理了错误，这里确保跳转
          console.log('登出处理完成，准备跳转')
        }
        
        // 无论API是否成功都跳转到登录页
        router.push('/login')
      }).catch(() => {
        // 用户取消登出，不做任何操作
      })
      break
  }
}
</script>

<style lang="scss" scoped>
.layout {
  display: flex;
  height: 100vh;
  background: $background-color;
}

.sidebar {
  width: $sidebar-width;
  background: #fff;
  border-right: 1px solid $border-light;
  transition: width 0.3s;
  overflow: hidden;
  
  &.collapsed {
    width: $sidebar-collapsed-width;
  }
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
    border-bottom: 1px solid $border-light;
    
    img {
      height: 32px;
      margin-right: 10px;
    }
    
    span {
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      white-space: nowrap;
    }
    
    .logo-mini {
      font-size: 16px;
      font-weight: 600;
      color: $primary-color;
    }
  }
  
  .sidebar-menu {
    border: none;
    
    .el-menu-item {
      height: 50px;
      line-height: 50px;
      
      &.is-active {
        background-color: #ecf5ff;
        border-right: 3px solid $primary-color;
        color: $primary-color;
      }
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: $header-height;
  background: #fff;
  border-bottom: 1px solid $border-light;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .collapse-btn {
      font-size: 18px;
      color: $text-regular;
      
      &:hover {
        color: $primary-color;
      }
    }
    
    .breadcrumb {
      display: flex;
      align-items: center;
      margin: 0;
      padding: 0;
    }
    
    .breadcrumb-item-with-close {
      display: flex;
      align-items: center;
      gap: 4px;
      height: 100%;
      align-items: center;
    }
    
    .breadcrumb-close-btn {
      padding: 0;
      margin: 0;
      font-size: 12px;
      color: $text-secondary;
      height: 20px;
      line-height: 20px;
      
      &:hover {
        color: $text-primary;
      }
    }
    
    .el-breadcrumb__item {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .header-btn {
      font-size: 18px;
      color: $text-regular;
      
      &:hover {
        color: $primary-color;
      }
    }
    
    .user-dropdown {
      cursor: pointer;
      
      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 10px;
        border-radius: $border-radius-base;
        transition: $transition;
        
        &:hover {
          background: $background-light;
        }
        
        .username {
          font-size: 14px;
          color: $text-regular;
        }
        
        .arrow {
          font-size: 12px;
          color: $text-secondary;
        }
      }
    }
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  background: $background-color;
}

// 响应式
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    height: 100vh;
    transform: translateX(-100%);
    
    &.collapsed {
      transform: translateX(0);
      width: $sidebar-collapsed-width;
    }
  }
  
  .main-container {
    margin-left: 0;
  }
}
</style>