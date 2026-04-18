<template>
  <div class="notification-center">
    <div class="page-header">
      <div class="header-content">
        <h1 class="header-title">消息中心</h1>
        <span class="header-description">查看和管理系统消息通知</span>
      </div>
    </div>

    <div class="search-section">
      <el-form :model="filters" inline>
        <el-form-item label="消息类型">
          <el-select v-model="filters.type" placeholder="全部类型" clearable class="filter-select filter-select--md">
            <el-option
              v-for="(label, key) in typeLabels"
              :key="key"
              :label="label"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_read" placeholder="全部状态" clearable class="filter-select filter-select--sm">
            <el-option label="未读" :value="false" />
            <el-option label="已读" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-select v-model="filters.time_range" placeholder="全部时间" clearable class="filter-select filter-select--md">
            <el-option label="24 小时内" value="1d" />
            <el-option label="7 天内" value="1w" />
            <el-option label="30 天内" value="1m" />
            <el-option label="90 天内" value="3m" />
            <el-option label="更早" value="older" />
          </el-select>
        </el-form-item>
        <el-form-item label="清理已读">
          <div class="clear-group">
            <el-select v-model="clearTimeRange" placeholder="选择范围" clearable class="filter-select filter-select--md">
              <el-option label="24小时内已读" value="1d" />
              <el-option label="7天内已读" value="1w" />
              <el-option label="30天内已读" value="1m" />
              <el-option label="90天内已读" value="3m" />
              <el-option label="更早已读" value="older" />
            </el-select>
            <el-button v-if="clearTimeRange" type="warning" @click="handleClearRead">清理</el-button>
          </div>
        </el-form-item>
        <div class="search-actions">
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="loadList(1)">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button :loading="readAllLoading" @click="handleReadAll">全部已读</el-button>
          </el-form-item>
          <el-form-item>
            <el-button :loading="unreadAllLoading" @click="handleUnreadAll">全部未读</el-button>
          </el-form-item>
        </div>
      </el-form>
    </div>

    <div class="table-section">
      <div class="table-scroll-viewport">
        <el-table
          v-loading="loading"
          :data="items"
          stripe
          border
          style="width: 100%"
          fit
          :row-class-name="({ row }) => getNotificationRoute(row) ? 'notification-row--navigable' : ''"
          @row-click="handleRowClick"
          row-key="id"
        >
          <el-table-column label="标题" min-width="180" align="center" show-overflow-tooltip>
            <template #default="{ row }">
              <span style="display: inline-flex; align-items: center; gap: 4px;">
                <el-icon v-if="row.is_pinned" style="font-size: 14px; color: var(--el-color-warning); flex-shrink: 0;"><Top /></el-icon>
                <span :style="getNotificationRoute(row) ? 'color: var(--el-color-primary);' : ''">{{ row.title }}</span>
                <el-tooltip v-if="getNotificationRoute(row)" content="点击跳转定位" placement="top" :show-after="400">
                  <el-icon style="font-size: 13px; color: var(--el-color-primary); flex-shrink: 0;"><Right /></el-icon>
                </el-tooltip>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="摘要/详情" min-width="260" align="center" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatNotificationDisplay(row) || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" min-width="90" align="center">
            <template #default="{ row }">
              {{ typeLabels[row.type] || row.type }}
            </template>
          </el-table-column>
          <el-table-column prop="is_read" label="状态" min-width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_read ? 'info' : 'warning'" size="small">
                {{ row.is_read ? '已读' : '未读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" min-width="120" align="center">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" align="center" fixed="right">
            <template #default="{ row }">
              <div class="operation-buttons" @click.stop>
                <el-tooltip :content="row.is_pinned ? '取消置顶' : '置顶'" placement="top">
                  <el-button link :type="row.is_pinned ? 'warning' : 'primary'" @click="handlePin(row)">
                    <el-icon :size="16"><Top v-if="!row.is_pinned" /><Bottom v-else /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip :content="row.is_read ? '标为未读' : '标为已读'" placement="top">
                  <el-button link type="primary" @click="handleToggleRead(row)">
                    <el-icon :size="16" v-if="row.is_read"><CircleClose /></el-icon>
                    <el-icon :size="16" v-else><CircleCheck /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="清除" placement="top">
                  <el-button link type="danger" @click="handleDeleteOne(row)">
                    <el-icon :size="16"><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="fixed-pagination">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getNotifications, markRead, markReadAll, markUnreadAll, clearRead, deleteNotification, pinNotification } from "@/api/notifications";
import { useNotificationStore } from "@/stores/notification";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import { getNotificationRoute, NOTIFICATION_TYPE_LABELS, formatNotificationDisplay } from "@/utils/notificationLink";
import { Delete, CircleCheck, CircleClose, Top, Bottom, Right, Search } from "@element-plus/icons-vue";

const router = useRouter();
const notificationStore = useNotificationStore();
const systemSettingsStore = useSystemSettingsStore();

const typeLabels = NOTIFICATION_TYPE_LABELS;
const loading = ref(false);
const readAllLoading = ref(false);
const unreadAllLoading = ref(false);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(systemSettingsStore.defaultPageSize || 10);
const clearTimeRange = ref("");

const filters = reactive({
  type: "",
  is_read: undefined,
  time_range: "",
});

async function loadList(p = page.value) {
  loading.value = true;
  try {
    const res = await getNotifications({
      page: p,
      size: pageSize.value,
      type: filters.type || undefined,
      is_read: filters.is_read,
      time_range: filters.time_range || undefined,
    });
    const data = res?.data || {};
    items.value = data.items || [];
    total.value = data.total || 0;
    page.value = data.page ?? p;
  } finally {
    loading.value = false;
  }
}

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return "刚刚";
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
  return d.toLocaleString("zh-CN");
}

async function handleRowClick(row) {
  const route = getNotificationRoute(row);
  if (row.id && !row.is_read) {
    try {
      await markRead(row.id);
      row.is_read = true;
      notificationStore.fetchUnreadCount();
    } catch (_) {}
  }
  if (route) {
    router.push(route);
  }
}

async function handleReadAll() {
  if (total.value === 0) {
    ElMessage.info("当前没有消息");
    return;
  }
  const hasUnread = items.value.some(item => !item.is_read);
  if (!hasUnread && filters.is_read === undefined) {
    ElMessage.info("所有消息已是已读状态");
    return;
  }
  readAllLoading.value = true;
  try {
    await markReadAll();
    ElMessage.success("已全部标记为已读");
    notificationStore.setUnreadCount(0);
    loadList(page.value);
  } catch (e) {
    ElMessage.error(e?.message || "操作失败");
  } finally {
    readAllLoading.value = false;
  }
}

async function handleUnreadAll() {
  if (total.value === 0) {
    ElMessage.info("当前没有消息");
    return;
  }
  const hasRead = items.value.some(item => item.is_read);
  if (!hasRead && filters.is_read === undefined) {
    ElMessage.info("所有消息已是未读状态");
    return;
  }
  unreadAllLoading.value = true;
  try {
    await markUnreadAll();
    ElMessage.success("已全部标记为未读");
    notificationStore.fetchUnreadCount();
    loadList(page.value);
  } catch (e) {
    ElMessage.error(e?.message || "操作失败");
  } finally {
    unreadAllLoading.value = false;
  }
}

async function handlePin(row) {
  try {
    const newPinned = !row.is_pinned;
    await pinNotification(row.id, { is_pinned: newPinned });
    row.is_pinned = newPinned;
    ElMessage.success(newPinned ? "已置顶" : "已取消置顶");
    loadList(page.value);
  } catch (e) {
    ElMessage.error(e?.message || "操作失败");
  }
}

async function handleToggleRead(row) {
  try {
    const newRead = !row.is_read;
    await markRead(row.id, { is_read: newRead });
    row.is_read = newRead;
    ElMessage.success(newRead ? "已标为已读" : "已标为未读");
    notificationStore.fetchUnreadCount();
  } catch (e) {
    ElMessage.error(e?.message || "操作失败");
  }
}

async function handleDeleteOne(row) {
  try {
    await deleteNotification(row.id);
    ElMessage.success("已清除");
    loadList(page.value);
    notificationStore.fetchUnreadCount();
  } catch (e) {
    ElMessage.error(e?.message || "清除失败");
  }
}

async function handleClearRead() {
  if (!clearTimeRange.value) return;
  try {
    const res = await clearRead(clearTimeRange.value);
    const cleared = res?.data?.cleared ?? 0;
    if (cleared === 0) {
      ElMessage.info("该时间范围内没有已读消息可清理");
    } else {
      ElMessage.success(`已清理 ${cleared} 条已读消息`);
    }
    clearTimeRange.value = "";
    loadList(1);
    notificationStore.fetchUnreadCount();
  } catch (e) {
    ElMessage.error(e?.message || "清理失败");
  }
}

function handleSizeChange(size) {
  pageSize.value = size;
  page.value = 1;
  loadList(1);
}

function handleCurrentChange(p) {
  page.value = p;
  loadList(p);
}

onMounted(() => {
  loadList(1);
  notificationStore.fetchUnreadCount();
});

watch([() => filters.type, () => filters.is_read, () => filters.time_range], () => {
  loadList(1);
});
</script>

<style lang="scss" scoped>
.notification-center {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.page-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: var(--el-bg-color, white);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);

  .header-content {
    display: flex;
    align-items: baseline;
    gap: 12px;
  }

  .header-title {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
    color: var(--el-text-color-primary, #303133);
  }

  .header-description {
    color: var(--el-text-color-regular, #606266);
    font-size: 14px;
  }
}

.search-section {
  flex-shrink: 0;
  background: var(--el-bg-color, white);
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);
}

.search-section :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  margin-bottom: 0;
}

.search-section :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
  flex: 0 0 auto;
  white-space: nowrap;
}

.search-section :deep(.el-form-item .el-select) {
  min-width: 0;
}

.clear-group {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.filter-select {
  max-width: 140px;
}
.filter-select--sm {
  width: 100px;
  max-width: 100px;
}
.filter-select--md {
  width: 130px;
  max-width: 130px;
}

.search-section .search-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0 10px;
  flex-shrink: 0;
}

.search-section .search-actions :deep(.el-form-item) {
  margin-bottom: 0;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color, white);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 70px;
  border: 1px solid var(--el-border-color-lighter, transparent);
}

.table-section .table-scroll-viewport {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

:deep(.notification-row--navigable) {
  cursor: pointer;
}
:deep(.notification-row--navigable:hover td) {
  background-color: var(--el-color-primary-light-9) !important;
}

.fixed-pagination {
  position: fixed;
  bottom: 0;
  right: 0;
  z-index: 100;
  background: var(--el-bg-color, white);
  padding: 15px 20px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px solid var(--el-border-color-light, #e4e7ed);
}

.fixed-pagination .pagination {
  margin: 0;
  text-align: center;
  border-top: none;
  width: 100%;
}

@media (max-width: 768px) {
  .fixed-pagination {
    left: 0;
    right: 0;
  }

  .table-section {
    margin-bottom: 70px;
  }
}

.operation-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  padding: 2px 0;
}

.operation-buttons :deep(.el-button) {
  flex: none;
  min-width: 0;
  padding: 2px 6px;
  margin: 0;
  font-size: 14px;
  white-space: nowrap;
}

.operation-buttons :deep(.el-button .el-icon) {
  font-size: 16px;
}
</style>
