<template>
  <div
    class="layout"
    :class="{ 'sidebar-collapsed': isCollapsed }"
  >
    <aside
      class="sidebar"
      :class="{ collapsed: isCollapsed }"
    >
      <div class="logo">
        <h1
          v-if="!isCollapsed"
          class="sidebar-system-name"
          style="color: white; margin: 0; font-size: 18px"
        >
          {{ systemSettingsStore.systemName || 'MobTest' }}
        </h1>
        <h1
          v-else
          class="sidebar-system-name"
          style="color: white; margin: 0; font-size: 14px"
        >
          {{ systemSettingsStore.shortTitle || 'MT' }}
        </h1>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="isCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <template v-for="menuRoute in menuRoutes">
          <template v-if="menuRoute.children && menuRoute.children.length > 0">
            <template
              v-if="menuRoute.children.some((child) => !child.meta?.hidden)"
            >
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
                <template v-for="childRoute in menuRoute.children">
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

    <div class="main-container">
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
          <el-popover
            v-model:visible="notificationPopoverVisible"
            placement="bottom-end"
            :width="360"
            trigger="click"
            :show-arrow="false"
            popper-class="notification-popover"
            @show="onNotificationPopoverShow"
          >
            <template #reference>
              <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" :max="99" class="notification-badge">
                <el-tooltip content="消息" placement="bottom">
                  <el-button type="text" class="header-btn">
                    <el-icon><Bell /></el-icon>
                  </el-button>
                </el-tooltip>
              </el-badge>
            </template>
            <div class="notification-dropdown">
              <div class="notification-dropdown-header">消息</div>
              <div v-loading="notificationListLoading" class="notification-list">
                <template v-if="notificationList.length">
                  <div
                    v-for="(item, index) in notificationList"
                    :key="item.id"
                    class="notification-item"
                    :class="{
                      unread: !item.is_read,
                      'first-unpinned': isFirstUnpinned(index),
                    }"
                    @click="onNotificationItemClick(item)"
                  >
                    <el-tooltip
                      v-if="getNotificationFullContent(item)"
                      :content="getNotificationFullContent(item)"
                      placement="top"
                      :show-after="300"
                      popper-class="notification-full-content-tooltip"
                    >
                      <div class="notification-item-main">
                        <div class="notification-item-title">{{ item.title }}</div>
                        <div class="notification-item-summary">{{ formatNotificationSummary(item.summary) }}</div>
                      <div class="notification-item-meta">
                        <el-tag :type="item.is_read ? 'info' : 'warning'" size="small" class="notification-item-status">
                          {{ item.is_read ? '已读' : '未读' }}
                        </el-tag>
                        <span class="notification-item-time">{{ formatNotificationTime(item.created_at) }}</span>
                      </div>
                    </div>
                    </el-tooltip>
                    <div v-else class="notification-item-main">
                      <div class="notification-item-title">{{ item.title }}</div>
                      <div class="notification-item-summary">{{ formatNotificationSummary(item.summary) }}</div>
                      <div class="notification-item-meta">
                        <el-tag :type="item.is_read ? 'info' : 'warning'" size="small" class="notification-item-status">
                          {{ item.is_read ? '已读' : '未读' }}
                        </el-tag>
                        <span class="notification-item-time">{{ formatNotificationTime(item.created_at) }}</span>
                      </div>
                    </div>
                    <div class="notification-item-actions" @click.stop>
                      <el-tooltip :content="item.is_pinned ? '取消置顶' : '置顶'" placement="top">
                        <el-button link type="primary" size="small" class="notification-action-btn" @click="onDropdownPin(item)">
                          <el-icon><Top /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip :content="item.is_read ? '标为未读' : '标为已读'" placement="top">
                        <el-button link type="primary" size="small" class="notification-action-btn" @click="onDropdownToggleRead(item)">
                          <el-icon v-if="item.is_read"><CircleClose /></el-icon>
                          <el-icon v-else><CircleCheck /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip content="删除" placement="top">
                        <el-button link type="danger" size="small" class="notification-action-btn" @click="onDropdownDelete(item)">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </div>
                  </div>
                </template>
                <el-empty v-else description="暂无消息" :image-size="60" />
              </div>
              <div class="notification-dropdown-footer">
                <el-button type="primary" link size="small" :loading="readAllLoading" @click="markAllRead">
                  全部已读
                </el-button>
                <el-button type="primary" link size="small" :loading="unreadAllLoading" @click="markAllUnread">
                  全部未读
                </el-button>
              </div>
            </div>
          </el-popover>
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
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import { useSystemAppearance } from "@/composables/useSystemAppearance";
import { ElMessageBox } from "element-plus";
import {
  Expand,
  Fold,
  FullScreen,
  ArrowDown,
  User,
  SwitchButton,
  Setting,
  Bell,
  Top,
  CircleCheck,
  CircleClose,
  Delete,
} from "@element-plus/icons-vue";
import { useNotificationStore } from "@/stores/notification";
import { useNotificationSocket } from "@/composables/useNotificationSocket";
import { getNotifications, markRead, markReadAll, markUnreadAll, deleteNotification, pinNotification } from "@/api/notifications";
import { getNotificationRoute } from "@/utils/notificationLink";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const systemSettingsStore = useSystemSettingsStore();
const notificationStore = useNotificationStore();
const { connect: connectNotificationSocket, disconnect: disconnectNotificationSocket } = useNotificationSocket();

const notificationPopoverVisible = ref(false);
const notificationList = ref([]);
const notificationListLoading = ref(false);
const readAllLoading = ref(false);
const unreadAllLoading = ref(false);

function formatNotificationSummary(summary) {
  if (!summary || typeof summary !== "string") return "";
  return summary
    .replace(/结果：approved/g, "结果：已通过")
    .replace(/结果：rejected/g, "结果：已拒绝")
    .replace(/结果：pending/g, "结果：待审核");
}

/** 悬浮时显示的完整消息内容（标题 + 正文） */
function getNotificationFullContent(item) {
  if (!item) return "";
  const title = item.title ? String(item.title).trim() : "";
  const summary = item.summary != null ? formatNotificationSummary(String(item.summary)) : "";
  if (title && summary) return `${title}\n\n${summary}`;
  return title || summary || "";
}

function formatNotificationTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return "刚刚";
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
  return d.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

async function fetchNotificationList() {
  notificationListLoading.value = true;
  try {
    const res = await getNotifications({ page: 1, size: 15 });
    notificationList.value = res?.data?.items ?? [];
  } catch (_) {
    notificationList.value = [];
  } finally {
    notificationListLoading.value = false;
  }
}

function onNotificationPopoverShow() {
  fetchNotificationList();
}

/** 是否为“未置顶”区块的第一条（用于与置顶消息的视觉分界） */
function isFirstUnpinned(index) {
  const list = notificationList.value;
  if (!list.length || index >= list.length) return false;
  const item = list[index];
  if (item.is_pinned) return false;
  return index === 0 || list[index - 1].is_pinned;
}

async function onNotificationItemClick(item) {
  if (item.id && !item.is_read) {
    try {
      await markRead(item.id);
      item.is_read = true;
      notificationStore.fetchUnreadCount();
    } catch (_) {}
  }
  const routeOpt = getNotificationRoute(item);
  if (routeOpt) {
    try {
      await router.push(routeOpt);
    } catch (_) {}
  }
  notificationPopoverVisible.value = false;
}

async function markAllRead() {
  readAllLoading.value = true;
  try {
    await markReadAll();
    notificationStore.setUnreadCount(0);
    notificationList.value = notificationList.value.map((n) => ({ ...n, is_read: true }));
  } catch (_) {}
  finally {
    readAllLoading.value = false;
  }
}

async function markAllUnread() {
  unreadAllLoading.value = true;
  try {
    await markUnreadAll();
    notificationStore.fetchUnreadCount();
    await fetchNotificationList();
  } catch (_) {}
  finally {
    unreadAllLoading.value = false;
  }
}

async function onDropdownPin(item) {
  if (!item?.id) return;
  try {
    await pinNotification(item.id, { is_pinned: !item.is_pinned });
    await fetchNotificationList();
  } catch (_) {}
}

async function onDropdownToggleRead(item) {
  if (!item?.id) return;
  try {
    await markRead(item.id, { is_read: !item.is_read });
    item.is_read = !item.is_read;
    notificationStore.fetchUnreadCount();
  } catch (_) {}
}

async function onDropdownDelete(item) {
  if (!item?.id) return;
  try {
    await deleteNotification(item.id);
    notificationList.value = notificationList.value.filter((n) => n.id !== item.id);
    notificationStore.fetchUnreadCount();
  } catch (_) {}
}

// 应用基础设置：主题（深/浅/跟随系统）、语言（html lang）
useSystemAppearance(systemSettingsStore);

const isCollapsed = ref(false);

function setPageTitle() {
  const name = systemSettingsStore.systemName || "移动测试平台";
  const pageTitle = route.meta?.title;
  document.title = pageTitle ? `${name} - ${pageTitle}` : name;
}

function getDefaultFaviconHref() {
  const base = (import.meta.env.BASE_URL || "/").replace(/\/?$/, "/");
  return `${window.location.origin}${base}favicon.svg`;
}
function setFavicon() {
  const logo = systemSettingsStore.systemLogo;
  const hasLogo = logo && String(logo).trim() !== "";
  const href = hasLogo ? logo : getDefaultFaviconHref();
  let link = document.querySelector('link[rel="icon"]');
  if (!link) {
    link = document.createElement("link");
    link.rel = "icon";
    document.head.appendChild(link);
  }
  link.type = href.endsWith(".svg") ? "image/svg+xml" : "image/png";
  link.href = href;
}

onMounted(() => {
  systemSettingsStore.load();
  setPageTitle();
  setFavicon();
  if (userStore.isAuthenticated) {
    notificationStore.fetchUnreadCount();
    connectNotificationSocket();
  }
});
onUnmounted(() => {
  disconnectNotificationSocket();
});

watch(route, setPageTitle);
watch(() => systemSettingsStore.systemName, setPageTitle);
watch(() => systemSettingsStore.systemLogo, setFavicon);

const menuRoutes = computed(() => {
  const routes = router.getRoutes() || [];
  const layoutRoute = routes.find((route) => route.name === "Layout");

  if (!layoutRoute || !layoutRoute.children) {
    return [];
  }

  // 按权限过滤：若 meta.permissions 存在，则用户须拥有其中至少一个埋点才显示
  const hasPermission = userStore.hasPermission;
  return layoutRoute.children.filter(
    (r) =>
      r &&
      r.path &&
      r.meta?.title &&
      r.meta?.hidden !== true &&
      ![
        "profile",
        "403",
        "404",
        "login",
        "register",
        "forgot-password",
        "reset-password",
      ].includes(r.path) &&
      (!r.meta?.permissions?.length || r.meta.permissions.some((p) => hasPermission(p))),
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

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

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
        .catch(() => {});
      break;
  }
};
</script>

<style lang="scss" scoped>
.layout {
  display: flex;
  height: 100vh;
  background: var(--el-bg-color-page, $background-color);
}

.sidebar {
  width: $sidebar-width;
  background: var(--el-bg-color, #fff);
  border-right: 1px solid var(--el-border-color-light, $border-light);
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
    border-bottom: 1px solid var(--el-border-color-light, $border-light);
    gap: 10px;

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
        background-color: var(--el-color-primary-light-9, #ecf5ff);
        border-right: 3px solid var(--el-color-primary, $primary-color);
        color: var(--el-color-primary, $primary-color);
      }
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--el-bg-color-page, transparent);
}

.header {
  height: $header-height;
  background: var(--el-bg-color, #fff);
  border-bottom: 1px solid var(--el-border-color-light, $border-light);
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
      color: var(--el-text-color-regular, $text-regular);

      &:hover {
        color: var(--el-color-primary, $primary-color);
      }
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      margin: 0;
      padding: 0;
    }

    .el-breadcrumb__item {
      font-weight: normal !important;
    }

    .el-breadcrumb__separator {
      font-weight: normal;
    }

    .el-breadcrumb__item:not(:first-child) .el-breadcrumb__inner {
      color: var(--el-text-color-regular) !important;
    }

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

    .notification-badge {
      margin-right: 4px;
    }

    .header-btn {
      font-size: 18px;
      color: var(--el-text-color-regular, $text-regular);

      &:hover {
        color: var(--el-color-primary, $primary-color);
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
          background: var(--el-fill-color-light, $background-light);
        }

        .username {
          font-size: 14px;
          color: var(--el-text-color-regular, $text-regular);
        }

        .arrow {
          font-size: 12px;
          color: var(--el-text-color-secondary, $text-secondary);
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
  background: var(--el-bg-color-page, $background-color);

  &.content-no-outer-scroll {
    overflow: hidden;
  }
}

.content > * {
  flex: 1;
  min-height: 0;
}

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

<style lang="scss">
@use "@/styles/variables.scss" as *;

.layout {
  --layout-sidebar-width: #{$sidebar-width};
}

.layout.sidebar-collapsed {
  --layout-sidebar-width: #{$sidebar-collapsed-width};
}

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

/* popper 挂载在 body，需全局样式 */
.notification-popover {
  padding: 0 !important;
}
.notification-popover .notification-dropdown {
  max-height: 460px;
  display: flex;
  flex-direction: column;
}
.notification-popover .notification-dropdown-header {
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.notification-popover .notification-list {
  max-height: 360px;
  overflow-y: auto;
  min-height: 80px;
}
.notification-popover .notification-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--el-border-color-extra-light);
  cursor: pointer;
  transition: background 0.2s;
}
.notification-popover .notification-item.first-unpinned {
  border-top: 2px solid var(--el-border-color);
}
.notification-popover .notification-item:hover {
  background: var(--el-fill-color-light);
}
.notification-popover .notification-item.unread {
  background: var(--el-fill-color-extra-light);
}
.notification-popover .notification-item-main {
  flex: 1;
  min-width: 0;
}
.notification-popover .notification-item-title {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}
.notification-popover .notification-item-summary {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.notification-popover .notification-item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.notification-popover .notification-item-status {
  flex-shrink: 0;
}
.notification-popover .notification-item-time {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}
.notification-popover .notification-item-actions {
  display: flex;
  align-items: center;
  gap: 0;
  flex-shrink: 0;
}
.notification-popover .notification-action-btn {
  padding: 2px;
}
.notification-popover .notification-action-btn .el-icon {
  font-size: 14px;
}
.notification-popover .notification-dropdown-footer {
  padding: 8px 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

tr.notification-flash-row > td,
.el-table tr.notification-flash-row > td {
  background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  animation: notification-flash-bg 2.8s ease-in-out forwards !important;
}
.iteration-card.notification-flash-card {
  background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  animation: notification-flash-bg 2.8s ease-in-out forwards !important;
}
@keyframes notification-flash-bg {
  0% {
    background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  }
  12% {
    background-color: transparent !important;
  }
  22% {
    background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  }
  34% {
    background-color: transparent !important;
  }
  44% {
    background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  }
  60% {
    background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
  }
  100% {
    background-color: transparent !important;
  }
}

.layout .content .table-scroll-viewport {
  overflow: auto;
  max-height: calc(100vh - 320px);
  width: 100%;
}

.layout .content .table-scroll-viewport .el-table {
  min-width: max-content;
}

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
  min-width: 0 !important;
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

<style lang="scss">
.notification-full-content-tooltip.el-popper {
  max-width: 360px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}
</style>
