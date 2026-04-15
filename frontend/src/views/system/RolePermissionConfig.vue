<template>
  <div class="role-permission-config">
    <div class="page-header">
      <div class="header-content">
        <h1 class="header-title">权限配置</h1>
        <span class="header-description">选择角色并勾选功能埋点，保存后该角色用户将拥有所勾选的功能权限</span>
      </div>
      <div class="header-actions">
        <el-button
          v-if="isRoleEditable"
          type="primary"
          :loading="saving"
          @click="save"
        >
          保存配置
        </el-button>
      </div>
    </div>

    <div class="filter-section">
      <el-form inline class="filter-form">
        <el-form-item label="选择角色">
          <el-select
            v-model="currentRole"
            placeholder="请选择角色"
            style="width: 160px"
            @change="onRoleChange"
          >
            <el-option
              v-for="item in roleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 超级管理员或无可配置权限时，权限分组为全选且禁用 -->
    <div class="content-section">
      <div
        v-for="group in permissionGroups"
        :key="group.module"
        class="permission-group"
      >
        <div class="group-header">
          <span class="group-title">{{ group.moduleLabel }}</span>
          <div v-if="isRoleEditable" class="group-actions">
            <el-button
              link
              type="primary"
              size="small"
              @click="checkAllInGroup(group.module)"
            >
              全选
            </el-button>
            <el-button
              link
              type="info"
              size="small"
              @click="uncheckAllInGroup(group.module)"
            >
              清空
            </el-button>
          </div>
        </div>
        <div class="permission-list">
          <el-checkbox
            v-for="perm in group.permissions"
            :key="perm[0]"
            v-model="selectedMap[perm[0]]"
            :disabled="!isRoleEditable"
            class="perm-item"
          >
            {{ perm[1] }}（<code>{{ perm[0] }}</code>）
            <el-tag
              v-if="isEntryPermission(group, perm[0])"
              type="warning"
              size="small"
              class="entry-tag"
            >
              菜单入口
            </el-tag>
          </el-checkbox>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 角色权限配置页：按角色（超级管理员/管理员/测试人员）勾选功能权限，保存后即时生效
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getPermissionGroups, getRolePermissions, updateRolePermissions } from "@/api/role";
import { useUserStore } from "@/stores/user";

const roleOptions = [
  { value: "super", label: "超级管理员" },
  { value: "manager", label: "管理员" },
  { value: "tester", label: "测试人员" },
  { value: "admin", label: "普通用户" },
];

const ROLE_CONFIG_PERMISSION = {
  manager: "role.manager_config",
  tester: "role.tester_config",
  admin: "role.admin_config",
};

const userStore = useUserStore();
const currentRole = ref("manager");
const permissionGroups = ref([]);
const selectedMap = reactive({});
const saving = ref(false);

/** 当前用户是否拥有各角色的配置权限（仅展示用，不可编辑） */
const roleConfigEnabled = computed(() => ({
  manager: userStore.hasPermission(ROLE_CONFIG_PERMISSION.manager),
  tester: userStore.hasPermission(ROLE_CONFIG_PERMISSION.tester),
  admin: userStore.hasPermission(ROLE_CONFIG_PERMISSION.admin),
}));

/** 当前选中的角色是否可编辑：非超级管理员 且 拥有该角色对应的配置权限 */
const isRoleEditable = computed(() => {
  const role = currentRole.value;
  if (role === "super") return false;
  const perm = ROLE_CONFIG_PERMISSION[role];
  return perm ? userStore.hasPermission(perm) : false;
});

function isEntryPermission(group, code) {
  if (group.entryPermission === code) return true;
  const list = group.entryPermissions;
  return Array.isArray(list) && list.includes(code);
}

function setSelectedFromList(codes) {
  const set = new Set(codes || []);
  permissionGroups.value.forEach((g) => {
    g.permissions.forEach((p) => {
      selectedMap[p[0]] = set.has(p[0]);
    });
  });
}

function clearSelectedMap() {
  permissionGroups.value.forEach((g) => {
    g.permissions.forEach((p) => {
      selectedMap[p[0]] = false;
    });
  });
}

function setAllChecked() {
  permissionGroups.value.forEach((g) => {
    g.permissions.forEach((p) => {
      selectedMap[p[0]] = true;
    });
  });
}

function onRoleChange() {
  if (currentRole.value === "super") {
    setAllChecked();
    return;
  }
  loadRolePermissions();
}

function loadRolePermissions() {
  if (!currentRole.value || currentRole.value === "super") return;
  clearSelectedMap();
  getRolePermissions(currentRole.value)
    .then((res) => {
      if (res.code === 200 && res.data?.permissions) {
        setSelectedFromList(res.data.permissions);
      }
    })
    .catch((e) => {
      setSelectedFromList([]);
      const status = e.response?.status;
      if (status !== 401 && status !== 403) {
        ElMessage.error(e.response?.data?.message || "加载失败");
      }
    });
}

function loadGroups() {
  getPermissionGroups()
    .then((res) => {
      if (res.code === 200 && res.data?.groups) {
        permissionGroups.value = res.data.groups;
        clearSelectedMap();
        onRoleChange();
      }
    })
    .catch((e) => {
      const status = e.response?.status;
      if (status !== 401 && status !== 403) {
        ElMessage.error(e.response?.data?.message || "加载权限列表失败");
      }
    });
}

function checkAllInGroup(module) {
  const g = permissionGroups.value.find((x) => x.module === module);
  if (g) g.permissions.forEach((p) => (selectedMap[p[0]] = true));
}

function uncheckAllInGroup(module) {
  const g = permissionGroups.value.find((x) => x.module === module);
  if (g) g.permissions.forEach((p) => (selectedMap[p[0]] = false));
}

function save() {
  if (!isRoleEditable.value) return;
  const codes = Object.entries(selectedMap)
    .filter(([, v]) => v)
    .map(([k]) => k);
  saving.value = true;
  updateRolePermissions(currentRole.value, codes)
    .then(async (res) => {
      if (res.code === 200) {
        await userStore.fetchPermissions();
        ElMessage.success("配置保存成功，已刷新");
      } else {
        ElMessage.error(res.message || "保存失败");
      }
    })
    .catch((e) => {
      const status = e.response?.status;
      if (status !== 401 && status !== 403) {
        ElMessage.error(e.response?.data?.message || "保存失败");
      }
    })
    .finally(() => {
      saving.value = false;
    });
}

onMounted(() => {
  loadGroups();
});
</script>

<style lang="scss" scoped>
.role-permission-config {
  padding: 20px;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.page-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: var(--el-bg-color, #fff);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);

  .header-content {
    display: flex;
    align-items: baseline;
    gap: 12px;
    min-width: 0;
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

  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }
}

.filter-section {
  flex-shrink: 0;
  background: var(--el-bg-color, #fff);
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);
}

.filter-section :deep(.filter-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  margin-bottom: 0;
}

.filter-section :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.config-role-checkboxes {
  display: inline-flex;
  gap: 16px;
  align-items: center;
}

.content-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: var(--el-bg-color, #fff);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter, transparent);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.permission-group {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;

  &:last-child {
    margin-bottom: 0;
  }
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.group-title {
  font-weight: 600;
  font-size: 15px;
  color: var(--el-text-color-primary, #303133);
}

.group-actions {
  display: flex;
  gap: 8px;
}

.permission-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
}

.perm-item {
  min-width: 260px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.perm-item code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.entry-tag {
  margin-left: 4px;
}
</style>
