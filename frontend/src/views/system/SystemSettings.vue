<template>
  <div class="system-settings">
    <div class="page-header">
      <h2>系统设置</h2>
      <el-button class="back-btn" @click="handleBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-card>
      <el-tabs
        v-model="activeTab"
        tab-position="left"
      >
        <el-tab-pane
          label="基础设置"
          name="basic"
        >
          <div class="settings-content">
            <h3>基础设置</h3>
            <el-form
              :model="basicSettings"
              label-width="120px"
            >
              <el-form-item label="系统名称">
                <el-input
                  v-model="basicSettings.systemName"
                  placeholder="请输入系统名称"
                />
              </el-form-item>
              <el-form-item label="系统描述">
                <el-input
                  v-model="basicSettings.systemDescription"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入系统描述"
                />
              </el-form-item>
              <el-form-item label="系统版本">
                <el-input
                  v-model="basicSettings.systemVersion"
                  disabled
                />
              </el-form-item>
              <el-form-item label="系统Logo">
                <div class="logo-upload-row">
                  <div
                    class="logo-preview-wrap"
                    @click="triggerLogoFileInput"
                  >
                    <img
                      :src="logoDisplayUrl"
                      class="logo-preview-img"
                      alt="Logo"
                    >
                    <div class="logo-preview-overlay">
                      <el-icon class="logo-preview-edit-icon">
                        <Edit />
                      </el-icon>
                    </div>
                  </div>
                  <input
                    ref="logoFileInputRef"
                    type="file"
                    accept="image/jpeg,image/png"
                    class="logo-file-input"
                    @change="onLogoFileChange"
                  >
                  <el-button
                    type="default"
                    :disabled="!basicSettings.systemLogo && !pendingLogoFile"
                    @click="resetLogoToDefault"
                  >
                    重置
                  </el-button>
                </div>
              </el-form-item>
              <el-form-item label="主题设置">
                <el-radio-group v-model="basicSettings.theme">
                  <el-radio label="light">
                    浅色主题
                  </el-radio>
                  <el-radio label="dark">
                    深色主题
                  </el-radio>
                  <el-radio label="auto">
                    跟随系统
                  </el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveBasicSettings"
                >
                  保存
                </el-button>
                <el-button @click="resetBasicSettings">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="功能设置"
          name="feature"
        >
          <div class="settings-content">
            <h3>功能设置</h3>
            <el-form
              :model="featureSettings"
              label-width="140px"
            >
              <el-form-item label="报告生成方式">
                <el-radio-group v-model="featureSettings.report_auto_generate">
                  <el-tooltip content="任务状态变为「已完成」时自动生成报告并落库" placement="top">
                    <el-radio label="auto">自动</el-radio>
                  </el-tooltip>
                  <el-tooltip content="需在任务页对已完成任务点击「生成报告」按钮生成" placement="top">
                    <el-radio label="manual">手动</el-radio>
                  </el-tooltip>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="默认每页条数">
                <el-select
                  v-model="featureSettings.defaultPageSize"
                  placeholder="请选择"
                  style="width: 120px"
                >
                  <el-option label="10 条/页" :value="10" />
                  <el-option label="20 条/页" :value="20" />
                  <el-option label="50 条/页" :value="50" />
                  <el-option label="100 条/页" :value="100" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveFeatureSettings"
                >
                  保存
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="消息通知"
          name="notification"
        >
          <div class="settings-content">
            <h3>消息通知</h3>
            <el-form
              :model="notificationSettings"
              label-width="140px"
            >
              <el-form-item label="新消息提示音">
                <el-switch v-model="notificationSettings.notification_sound" />
                <span style="margin-left: 10px">收到新消息时播放短提示音</span>
              </el-form-item>
              <el-form-item label="桌面通知">
                <el-switch v-model="notificationSettings.notification_desktop" />
                <span style="margin-left: 10px">使用浏览器桌面通知弹窗（需授权）</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings">
                  保存
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="安全设置"
          name="security"
        >
          <div class="settings-content">
            <h3>安全设置</h3>
            <el-form
              :model="securitySettings"
              label-width="120px"
            >
              <el-form-item label="密码策略">
                <el-checkbox-group v-model="securitySettings.passwordPolicy">
                  <el-checkbox label="minLength">
                    最小长度8位
                  </el-checkbox>
                  <el-checkbox label="uppercase">
                    包含大写字母
                  </el-checkbox>
                  <el-checkbox label="lowercase">
                    包含小写字母
                  </el-checkbox>
                  <el-checkbox label="numbers">
                    包含数字
                  </el-checkbox>
                  <el-checkbox label="specialChars">
                    包含特殊字符
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="登录失败锁定">
                <el-input-number
                  v-model="securitySettings.loginFailureLock"
                  :min="0"
                  :max="10"
                  placeholder="次数"
                />
                <span style="margin-left: 10px">次后锁定账户（0表示不锁定）</span>
              </el-form-item>
              <el-form-item label="会话超时时间">
                <el-input-number
                  v-model="securitySettings.sessionTimeout"
                  :min="30"
                  :max="10080"
                  placeholder="分钟"
                />
                <span style="margin-left: 10px">分钟后自动登出（默认 24 小时 = 1440 分钟，对新登录生效）</span>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveSecuritySettings"
                >
                  保存
                </el-button>
                <el-button @click="resetSecuritySettings">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Edit, ArrowLeft } from "@element-plus/icons-vue";
import { getUserSettings, updateUserSettings, getSystemSettings, updateSystemSettings, uploadLogo } from "@/api/settings";
import { isPermissionError } from "@/utils/request";
import { useSystemSettingsStore } from "@/stores/systemSettings";

const route = useRoute();
const router = useRouter();
const systemSettingsStore = useSystemSettingsStore();

// 响应式数据（支持 URL query.tab 定位到对应功能）
const activeTab = ref(
  ["feature", "security", "notification"].includes(route.query.tab) ? route.query.tab : "basic"
);

// 功能设置：报告生成方式（用户设置）+ 默认每页条数（系统设置）
const featureSettings = reactive({
  report_auto_generate: "auto",
  defaultPageSize: 10,
});
// 默认图标：与浏览器标签页一致（蓝色 M）
const defaultFaviconUrl = (import.meta.env.BASE_URL || "/").replace(/\/?$/, "/") + "favicon.svg";
const logoFileInputRef = ref(null);
const logoPreviewUrl = ref("");
const pendingLogoFile = ref(null);

// 显示用的 Logo：预览图 > 已保存的 Logo > 默认图标
const logoDisplayUrl = computed(
  () => logoPreviewUrl.value || basicSettings.systemLogo || defaultFaviconUrl
);

const basicSettings = reactive({
  systemName: "移动测试平台",
  systemDescription: "专业的移动应用自动化测试平台",
  systemVersion: "1.0.0",
  systemLogo: "",
  theme: "light",
});

// 消息通知（用户个人设置，默认提示音开、桌面通知关）
const notificationSettings = reactive({
  notification_sound: true,
  notification_desktop: false,
});

// 安全设置（会话超时默认 24 小时 = 1440 分钟）
const securitySettings = reactive({
  passwordPolicy: ["minLength", "numbers"],
  loginFailureLock: 5,
  sessionTimeout: 1440,
});

// 主题、Logo 修改后立即应用为预览效果，仅点击「保存设置」后持久化
watch(
  () => basicSettings.theme,
  (val) => {
    if (val != null) systemSettingsStore.theme = val;
  }
);

// 基础设置：与后端 /api/settings/system 的 key-value 映射
const BASIC_KEYS = {
  systemName: "system_name",
  systemDescription: "system_description",
  systemVersion: "system_version",
  systemLogo: "system_logo",
  theme: "theme",
};

const saveBasicSettings = async () => {
  try {
    let logoUrl = basicSettings.systemLogo;
    if (pendingLogoFile.value) {
      const res = await uploadLogo(pendingLogoFile.value);
      logoUrl = res?.data?.url ?? res?.data?.data?.url ?? "";
      if (logoPreviewUrl.value) URL.revokeObjectURL(logoPreviewUrl.value);
      logoPreviewUrl.value = "";
      pendingLogoFile.value = null;
      basicSettings.systemLogo = logoUrl;
    }
    const payload = {};
    for (const [frontKey, backKey] of Object.entries(BASIC_KEYS)) {
      if (basicSettings[frontKey] !== undefined && basicSettings[frontKey] !== null) {
        payload[backKey] = basicSettings[frontKey];
      }
    }
    await updateSystemSettings(payload);
    systemSettingsStore.setFromSettings(basicSettings);
    ElMessage.success("基础设置保存成功");
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(error?.response?.data?.message || "保存失败");
  }
};

const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    systemName: "移动测试平台",
    systemDescription: "专业的移动应用自动化测试平台",
    systemVersion: "1.0.0",
    systemLogo: "",
    theme: "light",
  });
};

// 安全设置与后端 key 映射
const SECURITY_KEYS = {
  sessionTimeout: "session_timeout_minutes",
  passwordPolicy: "password_policy",
  loginFailureLock: "login_failure_lock",
};

const saveNotificationSettings = async () => {
  try {
    await updateUserSettings({
      notification_sound: notificationSettings.notification_sound ? "true" : "false",
      notification_desktop: notificationSettings.notification_desktop ? "true" : "false",
    });
    ElMessage.success("消息通知设置已保存");
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(error?.response?.data?.message || "保存失败");
  }
};

const saveSecuritySettings = async () => {
  try {
    const payload = {
      [SECURITY_KEYS.sessionTimeout]: securitySettings.sessionTimeout,
      [SECURITY_KEYS.loginFailureLock]: securitySettings.loginFailureLock,
      [SECURITY_KEYS.passwordPolicy]:
        Array.isArray(securitySettings.passwordPolicy)
          ? JSON.stringify(securitySettings.passwordPolicy)
          : securitySettings.passwordPolicy,
    };
    await updateSystemSettings(payload);
    ElMessage.success("安全设置保存成功");
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(error?.response?.data?.message || "保存失败");
  }
};

const resetSecuritySettings = () => {
  Object.assign(securitySettings, {
    passwordPolicy: ["minLength", "numbers"],
    loginFailureLock: 5,
    sessionTimeout: 1440,
  });
};

const triggerLogoFileInput = () => {
  logoFileInputRef.value?.click();
};

const onLogoFileChange = (e) => {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;
  if (file.type !== "image/jpeg" && file.type !== "image/png") {
    ElMessage.error("Logo 仅支持 JPG/PNG 格式");
    return;
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error("Logo 大小不能超过 2MB");
    return;
  }
  if (logoPreviewUrl.value) URL.revokeObjectURL(logoPreviewUrl.value);
  logoPreviewUrl.value = URL.createObjectURL(file);
  pendingLogoFile.value = file;
  systemSettingsStore.systemLogo = logoPreviewUrl.value;
  ElMessage.success("已选择新 Logo，点击「保存」后生效");
};

const resetLogoToDefault = () => {
  if (!basicSettings.systemLogo && !pendingLogoFile.value) return;
  if (logoPreviewUrl.value) {
    URL.revokeObjectURL(logoPreviewUrl.value);
    logoPreviewUrl.value = "";
  }
  pendingLogoFile.value = null;
  basicSettings.systemLogo = "";
  systemSettingsStore.systemLogo = "";
  ElMessage.success("已重置为默认图标，点击「保存」后生效");
};

onBeforeUnmount(() => {
  if (logoPreviewUrl.value) URL.revokeObjectURL(logoPreviewUrl.value);
});

const saveFeatureSettings = async () => {
  try {
    await updateUserSettings({
      report_auto_generate: featureSettings.report_auto_generate,
    });
    await updateSystemSettings({
      default_page_size: featureSettings.defaultPageSize,
    });
    systemSettingsStore.setFromSettings({ defaultPageSize: featureSettings.defaultPageSize });
    ElMessage.success("功能设置已保存");
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(error?.response?.data?.message || "保存失败");
  }
};

const loadSettings = async () => {
  try {
    const userRes = await getUserSettings();
    if (userRes?.data && typeof userRes.data === "object") {
      if (userRes.data.report_auto_generate !== undefined) {
        featureSettings.report_auto_generate = userRes.data.report_auto_generate === "manual" ? "manual" : "auto";
      }
      if (userRes.data.notification_sound !== undefined) {
        notificationSettings.notification_sound = userRes.data.notification_sound !== "false";
      }
      if (userRes.data.notification_desktop !== undefined) {
        notificationSettings.notification_desktop = userRes.data.notification_desktop === "true";
      }
    }
  } catch (error) {
    console.error("加载用户设置失败:", error);
  }
  try {
    const sysRes = await getSystemSettings();
    if (sysRes?.data && typeof sysRes.data === "object") {
      const d = sysRes.data;
      if (d.system_name !== undefined) basicSettings.systemName = d.system_name;
      if (d.system_description !== undefined) basicSettings.systemDescription = d.system_description;
      if (d.system_version !== undefined) basicSettings.systemVersion = d.system_version;
      if (d.system_logo !== undefined) basicSettings.systemLogo = d.system_logo || "";
      logoPreviewUrl.value = "";
      pendingLogoFile.value = null;
      if (d.theme !== undefined) basicSettings.theme = d.theme;
      if (d.default_page_size !== undefined && d.default_page_size !== null && d.default_page_size !== "") {
        const v = Number(d.default_page_size);
        if (!Number.isNaN(v) && v >= 5 && v <= 100) featureSettings.defaultPageSize = v;
      }
      if (d.session_timeout_minutes !== undefined && d.session_timeout_minutes !== null && d.session_timeout_minutes !== "") {
        const v = Number(d.session_timeout_minutes);
        if (!Number.isNaN(v) && v >= 30 && v <= 10080) securitySettings.sessionTimeout = v;
      }
      if (d.login_failure_lock !== undefined && d.login_failure_lock !== null && d.login_failure_lock !== "") {
        const v = Number(d.login_failure_lock);
        if (!Number.isNaN(v) && v >= 0 && v <= 10) securitySettings.loginFailureLock = v;
      }
      if (d.password_policy !== undefined && d.password_policy) {
        try {
          const arr = typeof d.password_policy === "string" ? JSON.parse(d.password_policy) : d.password_policy;
          if (Array.isArray(arr)) securitySettings.passwordPolicy = arr;
          else securitySettings.passwordPolicy = [];
        } catch (e) {
          console.warn("密码策略格式无效，已使用默认策略", e);
          securitySettings.passwordPolicy = [];
        }
      }
      // 同步到全局 store，使侧边栏 Logo、标签页图标与当前系统设置一致
      systemSettingsStore.setFromSettings(basicSettings);
    }
  } catch (error) {
    console.error("加载系统设置失败:", error);
  }
};

// 返回（有历史则后退，否则回首页）
const handleBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/home");
  }
};

// URL query.tab 变化时同步当前选中的标签页
watch(
  () => route.query.tab,
  (tab) => {
    if (tab === "feature" || tab === "security") {
      activeTab.value = tab;
    }
  },
);

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.system-settings {
  padding: 20px;
  background-color: var(--el-bg-color-page);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: var(--el-text-color-primary, #303133);
}

.page-header .back-btn {
  flex-shrink: 0;
}

.settings-content {
  padding: 20px;
}

.settings-content h3 {
  margin-bottom: 20px;
  color: var(--el-text-color-primary, #303133);
  border-bottom: 2px solid var(--el-color-primary, #409eff);
  padding-bottom: 10px;
}

.logo-upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-preview-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--el-border-color, #dcdfe6);
  flex-shrink: 0;
  background: var(--el-fill-color-light, #f5f7fa);
}

.logo-preview-wrap:hover .logo-preview-overlay {
  opacity: 1;
}

.logo-preview-img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  object-position: center;
  border-radius: 8px;
}

.logo-preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.logo-preview-edit-icon {
  font-size: 28px;
  color: #fff;
}

.logo-file-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

@media (max-width: 768px) {
  .system-settings {
    padding: 10px;
  }

  .settings-content {
    padding: 10px;
  }
}
</style>
