<template>
  <div class="notification-center">
    <div class="page-header">
      <h2>消息中心</h2>
    </div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="filters.type" placeholder="消息类型" clearable style="width: 140px">
          <el-option
            v-for="(label, key) in typeLabels"
            :key="key"
            :label="label"
            :value="key"
          />
        </el-select>
        <el-select v-model="filters.is_read" placeholder="已读状态" clearable style="width: 120px">
          <el-option label="未读" :value="false" />
          <el-option label="已读" :value="true" />
        </el-select>
        <el-select v-model="filters.time_range" placeholder="时间范围" clearable style="width: 140px">
          <el-option label="24 小时内" value="1d" />
          <el-option label="7 天内" value="1w" />
          <el-option label="30 天内" value="1m" />
          <el-option label="90 天内" value="3m" />
          <el-option label="更早" value="older" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadList(1)">查询</el-button>
        <el-button plain class="toolbar-batch-btn" @click="handleReadAll" :loading="readAllLoading">全部已读</el-button>
        <el-button plain class="toolbar-batch-btn" @click="handleUnreadAll" :loading="unreadAllLoading">全部未读</el-button>
        <el-select v-model="clearTimeRange" placeholder="清理已读" style="width: 120px" clearable>
          <el-option label="24小时内已读" value="1d" />
          <el-option label="7天内已读" value="1w" />
          <el-option label="30天内已读" value="1m" />
          <el-option label="90天内已读" value="3m" />
          <el-option label="更早已读" value="older" />
        </el-select>
        <el-button v-if="clearTimeRange" type="warning" @click="handleClearRead">清理</el-button>
      </div>
      <el-table
        v-loading="loading"
        :data="items"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="摘要/详情" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatNotificationDisplay(row) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            {{ typeLabels[row.type] || row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="is_read" label="状态" width="72">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'warning'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <span class="action-btns" @click.stop>
              <el-tooltip :content="row.is_pinned ? '取消置顶' : '置顶'" placement="top">
                <el-button link type="primary" size="small" @click="handlePin(row)">
                  <el-icon><Top /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip :content="row.is_read ? '标为未读' : '标为已读'" placement="top">
                <el-button link type="primary" size="small" @click="handleToggleRead(row)">
                  <el-icon v-if="row.is_read"><CircleClose /></el-icon>
                  <el-icon v-else><CircleCheck /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="清除" placement="top">
                <el-button link type="danger" size="small" @click="handleDeleteOne(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        class="pagination"
        @current-change="loadList"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getNotifications, markRead, markReadAll, markUnreadAll, clearRead, deleteNotification, pinNotification } from "@/api/notifications";
import { useNotificationStore } from "@/stores/notification";
import { getNotificationRoute, NOTIFICATION_TYPE_LABELS, formatNotificationDisplay } from "@/utils/notificationLink";
import { Delete, CircleCheck, CircleClose, Top } from "@element-plus/icons-vue";

const router = useRouter();
const notificationStore = useNotificationStore();

const typeLabels = NOTIFICATION_TYPE_LABELS;
const loading = ref(false);
const readAllLoading = ref(false);
const unreadAllLoading = ref(false);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
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

async function handleClearRead() {
  if (!clearTimeRange.value) return;
  try {
    const res = await clearRead(clearTimeRange.value);
    const cleared = res?.data?.cleared ?? 0;
    ElMessage.success(`已清理 ${cleared} 条已读消息`);
    clearTimeRange.value = "";
    loadList(1);
    notificationStore.fetchUnreadCount();
  } catch (e) {
    ElMessage.error(e?.message || "清理失败");
  }
}

onMounted(() => {
  loadList(1);
  notificationStore.fetchUnreadCount();
});

watch([() => filters.type, () => filters.is_read, () => filters.time_range], () => {
  loadList(1);
});
</script>

<style scoped>
.notification-center {
  padding: 16px;
}
.page-header {
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
}
.toolbar .toolbar-batch-btn {
  font-size: 14px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.el-table {
  cursor: pointer;
}
.action-btns {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.action-btns .el-button {
  padding: 4px;
}
</style>
