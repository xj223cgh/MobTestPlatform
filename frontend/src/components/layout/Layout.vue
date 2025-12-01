<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
            <h1 v-if="!isCollapsed" style="color: white; margin: 0; font-size: 18px;">MobTest</h1>
            <h1 v-else style="color: white; margin: 0; font-size: 14px;">MT</h1>
          </div>
      
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <!-- 递归生成菜单，支持嵌套路由 -->
        <template v-for="menuRoute in menuRoutes">
          <!-- 如果有子路由，使用 el-sub-menu -->
          <el-sub-menu 
            v-if="menuRoute.children && menuRoute.children.length > 0" 
            :key="`${menuRoute.path}-submenu`"
            :index="`/${menuRoute.path}`"
          >
            <template #title>
              <el-icon v-if="menuRoute.meta.icon">
                <component :is="menuRoute.meta.icon" />
              </el-icon>
              {{ menuRoute.meta.title }}
            </template>
            <!-- 递归渲染子菜单 -->
            <template v-for="childRoute in menuRoute.children">
              <el-menu-item 
                v-if="!childRoute.children || childRoute.children.length === 0" 
                :key="`${childRoute.path}-item`"
                :index="`/${menuRoute.path}/${childRoute.path}`"
              >
                <el-icon v-if="childRoute.meta.icon">
                  <component :is="childRoute.meta.icon" />
                </el-icon>
                <template #title>{{ childRoute.meta.title }}</template>
              </el-menu-item>
              <!-- 支持多级嵌套 -->
              <el-sub-menu 
                v-else 
                :key="`${childRoute.path}-submenu`"
                :index="`/${menuRoute.path}/${childRoute.path}`"
              >
                <template #title>
                  <el-icon v-if="childRoute.meta.icon">
                    <component :is="childRoute.meta.icon" />
                  </el-icon>
                  {{ childRoute.meta.title }}
                </template>
                <!-- 递归渲染更深层级的子菜单 -->
                <el-menu-item v-for="grandChildRoute in childRoute.children" :key="grandChildRoute.path" :index="`/${menuRoute.path}/${childRoute.path}/${grandChildRoute.path}`">
                  <el-icon v-if="grandChildRoute.meta.icon">
                    <component :is="grandChildRoute.meta.icon" />
                  </el-icon>
                  <template #title>{{ grandChildRoute.meta.title }}</template>
                </el-menu-item>
              </el-sub-menu>
            </template>
          </el-sub-menu>
          <!-- 没有子路由，直接使用 el-menu-item -->
          <el-menu-item 
            v-else 
            :key="`${menuRoute.path}-item`"
            :index="`/${menuRoute.path}`"
          >
            <el-icon v-if="menuRoute.meta.icon">
              <component :is="menuRoute.meta.icon" />
            </el-icon>
            <template #title>{{ menuRoute.meta.title }}</template>
          </el-menu-item>
        </template>
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
            
            <!-- 生成所有面包屑 -->
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
import { ref, computed, watch } from 'vue'
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
  Close,
  Calendar
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 当前路由
const currentRoute = computed(() => route)

// 记录当前路由路径，用于检测浏览器返回
const previousRoutePath = ref(route.path)

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

// 面包屑历史记录 - 从sessionStorage恢复
const loadBreadcrumbHistory = () => {
  const savedHistory = sessionStorage.getItem('breadcrumbHistory')
  if (savedHistory) {
    try {
      return JSON.parse(savedHistory)
    } catch (e) {
      console.error('Failed to parse breadcrumb history from sessionStorage:', e)
      return []
    }
  }
  return []
}

const breadcrumbHistory = ref(loadBreadcrumbHistory())

// 保存面包屑历史到sessionStorage
const saveBreadcrumbHistory = () => {
  sessionStorage.setItem('breadcrumbHistory', JSON.stringify(breadcrumbHistory.value))
}

// 面包屑历史最大长度限制
const MAX_BREADCRUMB_HISTORY = 10

// 清理面包屑历史，移除最早的面包屑项
const cleanupBreadcrumbHistory = () => {
  if (breadcrumbHistory.value.length > MAX_BREADCRUMB_HISTORY) {
    breadcrumbHistory.value = breadcrumbHistory.value.slice(-MAX_BREADCRUMB_HISTORY)
  }
}

// 监听路由变化，更新面包屑历史
watch(
  () => route.path,
  (newPath) => {
    // 获取当前路由的标题
    const routeTitle = currentRoute.value.meta.title
    
    // 如果没有标题，不添加到面包屑
    if (!routeTitle) return
    
    // 如果是首页，清空面包屑历史
    if (newPath === '/home') {
      breadcrumbHistory.value = []
      saveBreadcrumbHistory()
      previousRoutePath.value = newPath
      return
    }
    
    // 检查是否已经存在相同路径的面包屑
    const existingPathIndex = breadcrumbHistory.value.findIndex(item => item.path === newPath)
    
    // 检查当前路由是否在面包屑历史中，用于处理浏览器返回
    const currentPathIndex = breadcrumbHistory.value.findIndex(item => item.path === previousRoutePath.value)
    
    if (existingPathIndex > -1) {
      // 如果新路径已经存在于面包屑历史中，且当前路径在新路径之后，说明是浏览器返回
      if (currentPathIndex > existingPathIndex) {
        // 删除当前路径及之后的面包屑
        breadcrumbHistory.value = breadcrumbHistory.value.slice(0, existingPathIndex + 1)
        saveBreadcrumbHistory()
      }
      // 更新之前的路由路径
      previousRoutePath.value = newPath
      return
    }
    
    // 检查是否已经存在相同标题的面包屑（用于动态路由，如项目详情）
    const existingTitleIndex = breadcrumbHistory.value.findIndex(item => item.title === routeTitle)
    
    if (existingTitleIndex > -1) {
      // 如果存在相同标题的面包屑，替换其路径为新路径
      breadcrumbHistory.value[existingTitleIndex] = {
        path: newPath,
        title: routeTitle
      }
    } else {
      // 添加到面包屑历史末尾
      breadcrumbHistory.value.push({
        path: newPath,
        title: routeTitle
      })
    }
    
    // 清理面包屑历史，保持最大长度
    cleanupBreadcrumbHistory()
    
    // 保存到localStorage
    saveBreadcrumbHistory()
    
    // 更新之前的路由路径
    previousRoutePath.value = newPath
  }
)

// 监听面包屑历史变化，保存到localStorage
watch(
  breadcrumbHistory,
  () => {
    saveBreadcrumbHistory()
  },
  { deep: true }
)

// 退出登录时清空面包屑历史（在userStore.logout时调用）
// 这里添加一个清理函数，方便在需要时调用
const clearBreadcrumbHistory = () => {
  breadcrumbHistory.value = []
  sessionStorage.removeItem('breadcrumbHistory')
}

// 暴露清理函数，方便其他组件调用
defineExpose({
  clearBreadcrumbHistory
})

// 生成面包屑层级
const breadcrumbItems = computed(() => {
  return breadcrumbHistory.value
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
  // 获取当前页面的路径
  const currentPath = route.path
  
  if (path) {
    // 如果指定了路径，检查是否是当前页面的面包屑
    const isCurrentPage = path === currentPath
    
    // 查找要删除的面包屑索引
    const index = breadcrumbHistory.value.findIndex(item => item.path === path)
    if (index > -1) {
      // 只删除指定的面包屑，不影响后续面包屑
      breadcrumbHistory.value.splice(index, 1)
      
      // 如果关闭的是当前页面的面包屑，跳转到未关闭的最新面包屑对应的页面
      if (isCurrentPage) {
        if (breadcrumbHistory.value.length > 0) {
          // 跳转到最后一个面包屑对应的页面
          const lastPath = breadcrumbHistory.value[breadcrumbHistory.value.length - 1].path
          router.push(lastPath)
        } else {
          // 如果没有面包屑了，跳转到首页
          router.push('/home')
        }
      }
      // 如果关闭的不是当前页面的面包屑，不跳转页面，保持当前页面不变
    }
  } else {
    // 关闭当前页面的面包屑（没有指定路径时）
    if (breadcrumbHistory.value.length > 0) {
      // 删除最后一个面包屑
      breadcrumbHistory.value.pop()
      // 跳转到前一个面包屑对应的页面
      if (breadcrumbHistory.value.length > 0) {
        const lastPath = breadcrumbHistory.value[breadcrumbHistory.value.length - 1].path
        router.push(lastPath)
      } else {
        // 如果没有面包屑了，跳转到首页
        router.push('/home')
      }
    }
  }
  // 保存面包屑历史到localStorage
  saveBreadcrumbHistory()
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
          
          /* 修复面包屑字体加粗问题，确保所有面包屑项字体粗细一致 */
          .el-breadcrumb__item {
            font-weight: normal !important;
          }
          
          /* 确保面包屑分隔符样式正常 */
          .el-breadcrumb__separator {
            font-weight: normal;
          }
          
          /* 修复面包屑颜色问题：除了首页，非当前页面的面包屑保持默认颜色 */
          .el-breadcrumb__item:not(:first-child) .el-breadcrumb__inner {
            color: var(--el-text-color-regular) !important;
          }
          
          /* 确保首页面包屑样式正常 */
          .el-breadcrumb__item:first-child .el-breadcrumb__inner {
            color: inherit;
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