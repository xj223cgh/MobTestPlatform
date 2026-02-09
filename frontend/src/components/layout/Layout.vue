<template>
  <div
    class="layout"
    :class="{ 'sidebar-collapsed': isCollapsed }"
  >
    <!-- 侧边栏 -->
    <aside
      class="sidebar"
      :class="{ collapsed: isCollapsed }"
    >
      <div class="logo">
        <h1
          v-if="!isCollapsed"
          style="color: white; margin: 0; font-size: 18px"
        >
          MobTest
        </h1>
        <h1
          v-else
          style="color: white; margin: 0; font-size: 14px"
        >
          MT
        </h1>
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
          <!-- 检查是否有可见的子路由 -->
          <template v-if="menuRoute.children && menuRoute.children.length > 0">
            <!-- 过滤出可见的子路由 -->
            <template
              v-if="menuRoute.children.some((child) => !child.meta?.hidden)"
            >
              <!-- 有可见子路由，使用 el-sub-menu -->
              <el-sub-menu
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
                  <!-- 只渲染可见的子路由 -->
                  <template v-if="!childRoute.meta?.hidden">
                    <el-menu-item
                      v-if="
                        !childRoute.children || childRoute.children.length === 0
                      "
                      :key="`${childRoute.path}-item`"
                      :index="`/${menuRoute.path}/${childRoute.path}`"
                    >
                      <el-icon v-if="childRoute.meta.icon">
                        <component :is="childRoute.meta.icon" />
                      </el-icon>
                      <template #title>
                        {{ childRoute.meta.title }}
                      </template>
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
                      <el-menu-item
                        v-for="grandChildRoute in childRoute.children"
                        :key="grandChildRoute.path"
                        :index="`/${menuRoute.path}/${childRoute.path}/${grandChildRoute.path}`"
                      >
                        <el-icon v-if="grandChildRoute.meta.icon">
                          <component :is="grandChildRoute.meta.icon" />
                        </el-icon>
                        <template #title>
                          {{ grandChildRoute.meta.title }}
                        </template>
                      </el-menu-item>
                    </el-sub-menu>
                  </template>
                </template>
              </el-sub-menu>
            </template>
            <template v-else>
              <!-- 没有可见子路由，直接使用 el-menu-item -->
              <el-menu-item
                :key="`${menuRoute.path}-item`"
                :index="`/${menuRoute.path}`"
              >
                <el-icon v-if="menuRoute.meta.icon">
                  <component :is="menuRoute.meta.icon" />
                </el-icon>
                <template #title>
                  {{ menuRoute.meta.title }}
                </template>
              </el-menu-item>
            </template>
          </template>
          <!-- 没有子路由，直接使用 el-menu-item -->
          <el-menu-item
            v-else
            :key="`${menuRoute.path}-item`"
            :index="`/${menuRoute.path}`"
          >
            <el-icon v-if="menuRoute.meta.icon">
              <component :is="menuRoute.meta.icon" />
            </el-icon>
            <template #title>
              {{ menuRoute.meta.title }}
            </template>
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
            class="collapse-btn"
            @click="toggleSidebar"
          >
            <el-icon><Expand v-if="isCollapsed" /><Fold v-else /></el-icon>
          </el-button>

          <el-breadcrumb
            separator="/"
            class="breadcrumb"
          >
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbItems"
              :key="item.path"
            >
              <template v-if="index < breadcrumbItems.length - 1">
                <router-link :to="item.path">{{ item.title }}</router-link>
              </template>
              <span v-else>{{ item.title }}</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 全屏按钮 -->
          <el-tooltip
            content="全屏"
            placement="bottom"
          >
            <el-button
              type="text"
              class="header-btn"
              @click="toggleFullscreen"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>

          <!-- 用户信息 -->
          <el-dropdown
            class="user-dropdown"
            @command="handleCommand"
          >
            <div class="user-info">
              <el-avatar
                :size="32"
                :src="userStore.avatar"
              >
                {{ userStore.userName.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.userName }}</span>
              <el-icon class="arrow">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item
                  divided
                  command="logout"
                >
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容：测试任务页用 content-no-outer-scroll，仅表格内部滚动 -->
      <main
        class="content"
        :class="{ 'content-no-outer-scroll': ['TestTasks', 'ReportManagement', 'Users', 'Requirements', 'CaseReviews', 'Projects'].includes($route.name) }"
      >
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { ElMessageBox } from "element-plus";
import {
  Expand,
  Fold,
  FullScreen,
  ArrowDown,
  User,
  SwitchButton,
  Setting,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// 侧边栏折叠状态
const isCollapsed = ref(false);

// 菜单路由
const menuRoutes = computed(() => {
  const routes = router.getRoutes() || [];
  const layoutRoute = routes.find((route) => route.name === "Layout");

  if (!layoutRoute || !layoutRoute.children) {
    return [];
  }

  // 直接返回Layout组件的children，保持路由配置中的顺序，排除hidden为true的路由
  return layoutRoute.children.filter(
    (route) =>
      route &&
      route.path &&
      route.meta?.title &&
      route.meta?.hidden !== true &&
      ![
        "profile",
        "403",
        "404",
        "login",
        "register",
        "forgot-password",
        "reset-password",
      ].includes(route.path),
  );
});

// 根据当前路由生成层级面包屑：首页 + 父级（若有）+ 当前页
const breadcrumbItems = computed(() => {
  const path = route.path;
  const meta = route.meta || {};
  const title = meta.title;

  const items = [{ path: "/home", title: "首页" }];
  if (!title || path === "/home") return items;

  const allRoutes = router.getRoutes();
  const layoutRoute = allRoutes.find((r) => r.name === "Layout");
  const children = layoutRoute?.children || [];

  const layoutPrefix =
    !layoutRoute || layoutRoute.path === "/" ? "" : layoutRoute.path;

  // 详情页：路径含动态段（如 /projects/1、/test-tasks/2/execute）
  const segments = path.split("/").filter(Boolean);
  const isDetailRoute =
    segments.length >= 2 &&
    (path.includes("/execute") || /^[^/]+\/[^/]+/.test(path.replace(/^\//, "")));

  if (isDetailRoute) {
    const parentSegment = path.includes("/execute")
      ? segments[0]
      : segments[0];
    const parentPath = "/" + parentSegment;
    // 父级为列表页，path 不含动态参数（如 projects 而非 projects/:id）
    const parentRoute = children.find((r) => {
      if (r.path.includes(":")) return false;
      const full = (layoutPrefix + "/" + r.path).replace(/\/+/g, "/");
      return full === parentPath || "/" + r.path === parentPath;
    });
    if (parentRoute?.meta?.title) {
      const fullPath = (layoutPrefix + "/" + parentRoute.path).replace(
        /\/+/g,
        "/",
      );
      items.push({
        path: fullPath || "/",
        title: parentRoute.meta.title,
      });
    }
  }

  items.push({ path, title });
  return items;
});

// 切换侧边栏
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

// 处理下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case "profile":
      router.push("/profile");
      break;
    case "settings":
      router.push("/settings");
      break;
    case "logout":
      ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(async () => {
          // 先开始登出流程，不等待API响应
          try {
            await userStore.logout();
          } catch (error) {
            // logout函数内部已经处理了错误，这里确保跳转
            console.log("登出处理完成，准备跳转");
          }

          // 无论API是否成功都跳转到登录页
          router.push("/login");
        })
        .catch(() => {
          // 用户取消登出，不做任何操作
        });
      break;
  }
};
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
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: $background-color;

  /* 测试任务页：最外层不出现垂直滚动条，仅标签页内表格滚动 */
  &.content-no-outer-scroll {
    overflow: hidden;
  }
}

.content > * {
  flex: 1;
  min-height: 0;
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

<!-- 分页区域与左侧菜单无缝对齐，无间隔 -->
<style lang="scss">
@use "@/styles/variables.scss" as *;

.layout {
  --layout-sidebar-width: #{$sidebar-width};
}

.layout.sidebar-collapsed {
  --layout-sidebar-width: #{$sidebar-collapsed-width};
}

/* 所有功能页固定分页：左边紧贴侧边栏无间隔，左侧内边距与页面内容对齐 */
.layout .content .fixed-pagination,
.layout .content .pagination-container {
  left: var(--layout-sidebar-width) !important;
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .layout .content .fixed-pagination,
  .layout .content .pagination-container {
    left: 0 !important;
  }
}

/* 表格滚动视口：横向滚动条在视口底部，查看首行时也可直接左右滑动，无需滚到列表底部 */
.layout .content .table-scroll-viewport {
  overflow: auto;
  max-height: calc(100vh - 320px);
  width: 100%;
}

.layout .content .table-scroll-viewport .el-table {
  min-width: max-content;
}

/* 表格表头首行冻结：视口不滚动，仅表体区域滚动，表头自然固定 */
.layout .content .table-section .table-scroll-viewport {
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}

.layout .content .table-section .table-scroll-viewport .el-table {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 !important;
  min-height: 0 !important;
  min-width: 0 !important; /* 不撑出横向滚动条（测试任务/报告/用户/需求管理） */
}

.layout .content .table-section .table-scroll-viewport .el-table__header-wrapper {
  flex-shrink: 0 !important;
}

.layout .content .table-section .table-scroll-viewport .el-table__body-wrapper {
  flex: 1 !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
}
</style>
