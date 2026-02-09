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
        <!-- 报告设置 -->
        <el-tab-pane
          label="报告设置"
          name="report"
        >
          <div class="settings-content">
            <h3>报告设置</h3>
            <el-form
              :model="reportSettings"
              label-width="140px"
            >
              <el-form-item label="报告生成方式">
                <el-radio-group v-model="reportSettings.report_auto_generate">
                  <el-radio label="auto">
                    自动：任务状态变为「已完成」时自动生成报告并落库
                  </el-radio>
                  <el-radio label="manual">
                    手动：需在任务页对已完成任务点击「生成报告」按钮生成
                  </el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveReportSettings"
                >
                  保存设置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

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
              </el-form-item>
              <el-form-item label="时区设置">
                <el-select
                  v-model="basicSettings.timezone"
                  placeholder="请选择时区"
                >
                  <el-option
                    v-for="tz in timezones"
                    :key="tz.value"
                    :label="tz.label"
                    :value="tz.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="语言设置">
                <el-select
                  v-model="basicSettings.language"
                  placeholder="请选择语言"
                >
                  <el-option
                    label="中文"
                    value="zh-CN"
                  />
                  <el-option
                    label="English"
                    value="en-US"
                  />
                </el-select>
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
                  保存设置
                </el-button>
                <el-button @click="resetBasicSettings">
                  重置
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
              <el-form-item label="会话超时">
                <el-input-number
                  v-model="securitySettings.sessionTimeout"
                  :min="5"
                  :max="1440"
                  placeholder="分钟"
                />
                <span style="margin-left: 10px">分钟后自动登出</span>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveSecuritySettings"
                >
                  保存设置
                </el-button>
                <el-button @click="resetSecuritySettings">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 邮件设置 -->
        <el-tab-pane
          label="邮件设置"
          name="email"
        >
          <div class="settings-content">
            <h3>邮件设置</h3>
            <el-form
              :model="emailSettings"
              label-width="120px"
            >
              <el-form-item label="SMTP服务器">
                <el-input
                  v-model="emailSettings.smtpHost"
                  placeholder="请输入SMTP服务器地址"
                />
              </el-form-item>
              <el-form-item label="SMTP端口">
                <el-input-number
                  v-model="emailSettings.smtpPort"
                  :min="1"
                  :max="65535"
                />
              </el-form-item>
              <el-form-item label="加密方式">
                <el-select
                  v-model="emailSettings.encryption"
                  placeholder="请选择加密方式"
                >
                  <el-option
                    label="无"
                    value="none"
                  />
                  <el-option
                    label="SSL"
                    value="ssl"
                  />
                  <el-option
                    label="TLS"
                    value="tls"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="发件人邮箱">
                <el-input
                  v-model="emailSettings.fromEmail"
                  placeholder="请输入发件人邮箱"
                />
              </el-form-item>
              <el-form-item label="发件人名称">
                <el-input
                  v-model="emailSettings.fromName"
                  placeholder="请输入发件人名称"
                />
              </el-form-item>
              <el-form-item label="用户名">
                <el-input
                  v-model="emailSettings.username"
                  placeholder="请输入邮箱用户名"
                />
              </el-form-item>
              <el-form-item label="密码">
                <el-input
                  v-model="emailSettings.password"
                  type="password"
                  placeholder="请输入邮箱密码"
                  show-password
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveEmailSettings"
                >
                  保存设置
                </el-button>
                <el-button @click="testEmailSettings">
                  测试邮件
                </el-button>
                <el-button @click="resetEmailSettings">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane
          label="通知设置"
          name="notification"
        >
          <div class="settings-content">
            <h3>通知设置</h3>
            <el-form
              :model="notificationSettings"
              label-width="120px"
            >
              <el-form-item label="邮件通知">
                <el-switch
                  v-model="notificationSettings.email"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="短信通知">
                <el-switch
                  v-model="notificationSettings.sms"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="微信通知">
                <el-switch
                  v-model="notificationSettings.wechat"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="钉钉通知">
                <el-switch
                  v-model="notificationSettings.dingtalk"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="通知事件">
                <el-checkbox-group v-model="notificationSettings.events">
                  <el-checkbox label="task_start">
                    任务开始
                  </el-checkbox>
                  <el-checkbox label="task_complete">
                    任务完成
                  </el-checkbox>
                  <el-checkbox label="task_fail">
                    任务失败
                  </el-checkbox>
                  <el-checkbox label="device_offline">
                    设备离线
                  </el-checkbox>
                  <el-checkbox label="system_error">
                    系统错误
                  </el-checkbox>
                  <el-checkbox label="security_alert">
                    安全告警
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveNotificationSettings"
                >
                  保存设置
                </el-button>
                <el-button @click="testNotification">
                  测试通知
                </el-button>
                <el-button @click="resetNotificationSettings">
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
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { systemApi } from "@/api/system";
import { getUserSettings, updateUserSettings } from "@/api/settings";

// 响应式数据
const activeTab = ref("report");

// 报告设置（用户个人设置）
const reportSettings = reactive({
  report_auto_generate: "auto",
});
const uploadUrl = ref("/api/upload/logo");

// 基础设置
const basicSettings = reactive({
  systemName: "移动测试平台",
  systemDescription: "专业的移动应用自动化测试平台",
  systemVersion: "1.0.0",
  systemLogo: "",
  timezone: "Asia/Shanghai",
  language: "zh-CN",
  theme: "light",
});

// 安全设置
const securitySettings = reactive({
  passwordPolicy: ["minLength", "numbers"],
  loginFailureLock: 5,
  sessionTimeout: 120,
});

// 邮件设置
const emailSettings = reactive({
  smtpHost: "",
  smtpPort: 587,
  encryption: "tls",
  fromEmail: "",
  fromName: "",
  username: "",
  password: "",
});

// 通知设置
const notificationSettings = reactive({
  email: true,
  sms: false,
  wechat: false,
  dingtalk: false,
  events: ["task_complete", "task_fail", "system_error"],
});

// 时区选项
const timezones = [
  { label: "北京时间 (GMT+8)", value: "Asia/Shanghai" },
  { label: "东京时间 (GMT+9)", value: "Asia/Tokyo" },
  { label: "纽约时间 (GMT-5)", value: "America/New_York" },
  { label: "伦敦时间 (GMT+0)", value: "Europe/London" },
  { label: "巴黎时间 (GMT+1)", value: "Europe/Paris" },
];

// 方法
const saveBasicSettings = async () => {
  try {
    await systemApi.updateBasicSettings(basicSettings);
    ElMessage.success("基础设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    systemName: "移动测试平台",
    systemDescription: "专业的移动应用自动化测试平台",
    systemVersion: "1.0.0",
    systemLogo: "",
    timezone: "Asia/Shanghai",
    language: "zh-CN",
    theme: "light",
  });
};

const saveSecuritySettings = async () => {
  try {
    await systemApi.updateSecuritySettings(securitySettings);
    ElMessage.success("安全设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const resetSecuritySettings = () => {
  Object.assign(securitySettings, {
    passwordPolicy: ["minLength", "numbers"],
    loginFailureLock: 5,
    sessionTimeout: 120,
  });
};

const saveEmailSettings = async () => {
  try {
    await systemApi.updateEmailSettings(emailSettings);
    ElMessage.success("邮件设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const testEmailSettings = async () => {
  try {
    await systemApi.testEmailSettings();
    ElMessage.success("邮件测试成功");
  } catch (error) {
    ElMessage.error("邮件测试失败");
  }
};

const resetEmailSettings = () => {
  Object.assign(emailSettings, {
    smtpHost: "",
    smtpPort: 587,
    encryption: "tls",
    fromEmail: "",
    fromName: "",
    username: "",
    password: "",
  });
};

const saveNotificationSettings = async () => {
  try {
    await systemApi.updateNotificationSettings(notificationSettings);
    ElMessage.success("通知设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const testNotification = async () => {
  try {
    await systemApi.testNotification();
    ElMessage.success("通知测试成功");
  } catch (error) {
    ElMessage.error("通知测试失败");
  }
};

const resetNotificationSettings = () => {
  Object.assign(notificationSettings, {
    email: true,
    sms: false,
    wechat: false,
    dingtalk: false,
    events: ["task_complete", "task_fail", "system_error"],
  });
};

const handleLogoSuccess = (response) => {
  basicSettings.systemLogo = response.data.url;
  ElMessage.success("Logo上传成功");
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

const saveReportSettings = async () => {
  try {
    await updateUserSettings({
      report_auto_generate: reportSettings.report_auto_generate,
    });
    ElMessage.success("报告设置已保存");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const loadSettings = async () => {
  try {
    const userRes = await getUserSettings();
    if (userRes?.data && typeof userRes.data === "object") {
      if (userRes.data.report_auto_generate !== undefined) {
        reportSettings.report_auto_generate = userRes.data.report_auto_generate === "manual" ? "manual" : "auto";
      }
    }
  } catch (error) {
    console.error("加载用户设置失败:", error);
  }
  // 以下模块暂无后端接口，仅使用本地默认值，避免请求 404
  // 若后续接入 /api/system/settings/* 可再恢复请求
};

// 生命周期
onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.settings-content {
  padding: 20px;
}

.settings-content h3 {
  margin-bottom: 20px;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.logo-uploader .logo {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 6px;
  object-fit: cover;
}

.logo-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: 0.2s;
}

.logo-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.logo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
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
