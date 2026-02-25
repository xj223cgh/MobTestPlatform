<template>
  <div class="system-settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <!-- 设置选项卡 -->
    <el-card>
      <el-tabs
        v-model="activeTab"
        tab-position="left"
      >
        <!-- 基础设置 -->
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
                  <el-upload
                    class="logo-uploader"
                    :action="uploadUrl"
                    :show-file-list="false"
                    :on-success="handleLogoSuccess"
                    :before-upload="beforeLogoUpload"
                  >
                    <img
                      v-if="basicSettings.systemLogo"
                      :src="basicSettings.systemLogo"
                      class="logo"
                    >
                    <el-icon
                      v-else
                      class="logo-uploader-icon"
                    >
                      <Plus />
                    </el-icon>
                  </el-upload>
                  <el-button
                    type="default"
                    :disabled="!basicSettings.systemLogo"
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

        <!-- 功能设置 -->
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

        <!-- 安全设置 -->
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
import { ref, reactive, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { getUserSettings, updateUserSettings, getSystemSettings, updateSystemSettings } from "@/api/settings";
import { useSystemSettingsStore } from "@/stores/systemSettings";

const systemSettingsStore = useSystemSettingsStore();

// 响应式数据
const activeTab = ref("basic");

// 功能设置：报告生成方式（用户设置）+ 默认每页条数（系统设置）
const featureSettings = reactive({
  report_auto_generate: "auto",
  defaultPageSize: 10,
});
const uploadUrl = ref("/api/files/upload/logo");

// 基础设置
const basicSettings = reactive({
  systemName: "移动测试平台",
  systemDescription: "专业的移动应用自动化测试平台",
  systemVersion: "1.0.0",
  systemLogo: "",
  theme: "light",
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

const handleLogoSuccess = (response) => {
  const url = response?.data?.data?.url ?? response?.data?.url;
  if (url) {
    basicSettings.systemLogo = url;
    systemSettingsStore.systemLogo = url; // 立即应用为预览（侧边栏、标签页图标）
  }
  ElMessage.success("Logo 已选择，请点击「保存设置」生效");
};

const resetLogoToDefault = () => {
  if (!basicSettings.systemLogo) return;
  basicSettings.systemLogo = "";
  systemSettingsStore.systemLogo = ""; // 立即应用为预览
  ElMessage.success("已重置为默认图标，请点击「保存设置」生效");
};

const beforeLogoUpload = (file) => {
  const isJPG = file.type === "image/jpeg" || file.type === "image/png";
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isJPG) {
    ElMessage.error("Logo只能是 JPG/PNG 格式!");
    return false;
  }
  if (!isLt2M) {
    ElMessage.error("Logo大小不能超过 2MB!");
    return false;
  }
  return true;
};

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
      if (d.theme !== undefined) basicSettings.theme = d.theme;
      if (d.default_page_size !== undefined && d.default_page_size !== null && d.default_page_size !== "") {
        const v = Number(d.default_page_size);
        if (!Number.isNaN(v) && v >= 5 && v <= 100) featureSettings.defaultPageSize = v;
      }
      // 安全设置
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
        } catch (_) {}
      }
    }
  } catch (error) {
    console.error("加载系统设置失败:", error);
  }
};

// 生命周期
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
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: var(--el-text-color-primary, #303133);
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

.logo-uploader .logo {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 6px;
  object-fit: cover;
}

.logo-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color, #d9d9d9);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: 0.2s;
}

.logo-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary, #409eff);
}

.logo-uploader-icon {
  font-size: 28px;
  color: var(--el-text-color-placeholder, #8c939d);
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
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
