<template>
  <div class="system-settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <!-- 设置选项卡 -->
    <el-card>
      <el-tabs v-model="activeTab" tab-position="left">
        <!-- 基础设置 -->
        <el-tab-pane label="基础设置" name="basic">
          <div class="settings-content">
            <h3>基础设置</h3>
            <el-form :model="basicSettings" label-width="120px">
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
                <el-input v-model="basicSettings.systemVersion" disabled />
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
                  />
                  <el-icon v-else class="logo-uploader-icon">
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
                  <el-option label="中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>
              <el-form-item label="主题设置">
                <el-radio-group v-model="basicSettings.theme">
                  <el-radio label="light"> 浅色主题 </el-radio>
                  <el-radio label="dark"> 深色主题 </el-radio>
                  <el-radio label="auto"> 跟随系统 </el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBasicSettings">
                  保存设置
                </el-button>
                <el-button @click="resetBasicSettings"> 重置 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <div class="settings-content">
            <h3>安全设置</h3>
            <el-form :model="securitySettings" label-width="120px">
              <el-form-item label="密码策略">
                <el-checkbox-group v-model="securitySettings.passwordPolicy">
                  <el-checkbox label="minLength"> 最小长度8位 </el-checkbox>
                  <el-checkbox label="uppercase"> 包含大写字母 </el-checkbox>
                  <el-checkbox label="lowercase"> 包含小写字母 </el-checkbox>
                  <el-checkbox label="numbers"> 包含数字 </el-checkbox>
                  <el-checkbox label="specialChars"> 包含特殊字符 </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="密码过期">
                <el-input-number
                  v-model="securitySettings.passwordExpiry"
                  :min="0"
                  :max="365"
                  placeholder="天数"
                />
                <span style="margin-left: 10px">天后过期（0表示永不过期）</span>
              </el-form-item>
              <el-form-item label="登录失败锁定">
                <el-input-number
                  v-model="securitySettings.loginFailureLock"
                  :min="0"
                  :max="10"
                  placeholder="次数"
                />
                <span style="margin-left: 10px"
                  >次后锁定账户（0表示不锁定）</span
                >
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
              <el-form-item label="双因素认证">
                <el-switch
                  v-model="securitySettings.twoFactorAuth"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="IP白名单">
                <el-input
                  v-model="securitySettings.ipWhitelist"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入IP地址，每行一个"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSecuritySettings">
                  保存设置
                </el-button>
                <el-button @click="resetSecuritySettings"> 重置 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 邮件设置 -->
        <el-tab-pane label="邮件设置" name="email">
          <div class="settings-content">
            <h3>邮件设置</h3>
            <el-form :model="emailSettings" label-width="120px">
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
                  <el-option label="无" value="none" />
                  <el-option label="SSL" value="ssl" />
                  <el-option label="TLS" value="tls" />
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
                <el-button type="primary" @click="saveEmailSettings">
                  保存设置
                </el-button>
                <el-button @click="testEmailSettings"> 测试邮件 </el-button>
                <el-button @click="resetEmailSettings"> 重置 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 存储设置 -->
        <el-tab-pane label="存储设置" name="storage">
          <div class="settings-content">
            <h3>存储设置</h3>
            <el-form :model="storageSettings" label-width="120px">
              <el-form-item label="存储类型">
                <el-radio-group v-model="storageSettings.type">
                  <el-radio label="local"> 本地存储 </el-radio>
                  <el-radio label="oss"> 阿里云OSS </el-radio>
                  <el-radio label="s3"> AWS S3 </el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- 本地存储设置 -->
              <template v-if="storageSettings.type === 'local'">
                <el-form-item label="存储路径">
                  <el-input
                    v-model="storageSettings.localPath"
                    placeholder="请输入本地存储路径"
                  />
                </el-form-item>
                <el-form-item label="最大文件大小">
                  <el-input-number
                    v-model="storageSettings.maxFileSize"
                    :min="1"
                    :max="1024"
                  />
                  <span style="margin-left: 10px">MB</span>
                </el-form-item>
              </template>

              <!-- OSS设置 -->
              <template v-if="storageSettings.type === 'oss'">
                <el-form-item label="AccessKey ID">
                  <el-input
                    v-model="storageSettings.ossAccessKeyId"
                    placeholder="请输入AccessKey ID"
                  />
                </el-form-item>
                <el-form-item label="AccessKey Secret">
                  <el-input
                    v-model="storageSettings.ossAccessKeySecret"
                    type="password"
                    placeholder="请输入AccessKey Secret"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="Endpoint">
                  <el-input
                    v-model="storageSettings.ossEndpoint"
                    placeholder="请输入Endpoint"
                  />
                </el-form-item>
                <el-form-item label="Bucket">
                  <el-input
                    v-model="storageSettings.ossBucket"
                    placeholder="请输入Bucket名称"
                  />
                </el-form-item>
              </template>

              <!-- S3设置 -->
              <template v-if="storageSettings.type === 's3'">
                <el-form-item label="Access Key ID">
                  <el-input
                    v-model="storageSettings.s3AccessKeyId"
                    placeholder="请输入Access Key ID"
                  />
                </el-form-item>
                <el-form-item label="Secret Access Key">
                  <el-input
                    v-model="storageSettings.s3SecretAccessKey"
                    type="password"
                    placeholder="请输入Secret Access Key"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="Region">
                  <el-input
                    v-model="storageSettings.s3Region"
                    placeholder="请输入Region"
                  />
                </el-form-item>
                <el-form-item label="Bucket">
                  <el-input
                    v-model="storageSettings.s3Bucket"
                    placeholder="请输入Bucket名称"
                  />
                </el-form-item>
              </template>

              <el-form-item>
                <el-button type="primary" @click="saveStorageSettings">
                  保存设置
                </el-button>
                <el-button @click="testStorageSettings"> 测试连接 </el-button>
                <el-button @click="resetStorageSettings"> 重置 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 备份设置 -->
        <el-tab-pane label="备份设置" name="backup">
          <div class="settings-content">
            <h3>备份设置</h3>
            <el-form :model="backupSettings" label-width="120px">
              <el-form-item label="自动备份">
                <el-switch
                  v-model="backupSettings.autoBackup"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item v-if="backupSettings.autoBackup" label="备份频率">
                <el-select
                  v-model="backupSettings.frequency"
                  placeholder="请选择备份频率"
                >
                  <el-option label="每天" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
              <el-form-item v-if="backupSettings.autoBackup" label="备份时间">
                <el-time-picker
                  v-model="backupSettings.backupTime"
                  format="HH:mm"
                  placeholder="选择备份时间"
                />
              </el-form-item>
              <el-form-item label="保留天数">
                <el-input-number
                  v-model="backupSettings.retentionDays"
                  :min="1"
                  :max="365"
                />
                <span style="margin-left: 10px">天</span>
              </el-form-item>
              <el-form-item label="备份位置">
                <el-input
                  v-model="backupSettings.backupPath"
                  placeholder="请输入备份存储路径"
                />
              </el-form-item>
              <el-form-item label="备份内容">
                <el-checkbox-group v-model="backupSettings.backupContent">
                  <el-checkbox label="database"> 数据库 </el-checkbox>
                  <el-checkbox label="files"> 文件 </el-checkbox>
                  <el-checkbox label="config"> 配置文件 </el-checkbox>
                  <el-checkbox label="logs"> 日志文件 </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBackupSettings">
                  保存设置
                </el-button>
                <el-button @click="createBackup"> 立即备份 </el-button>
                <el-button @click="resetBackupSettings"> 重置 </el-button>
              </el-form-item>
            </el-form>

            <!-- 备份历史 -->
            <div class="backup-history">
              <h4>备份历史</h4>
              <el-table :data="backupHistory" stripe>
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column
                  prop="filename"
                  label="文件名"
                  min-width="150"
                />
                <el-table-column prop="size" label="文件大小" width="120" />
                <el-table-column prop="type" label="备份类型" width="120" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getBackupStatusTag(row.status)">
                      {{ getBackupStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="createdAt"
                  label="创建时间"
                  width="160"
                />
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      size="small"
                      :disabled="row.status !== 'completed'"
                      @click="downloadBackup(row)"
                    >
                      下载
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      @click="deleteBackup(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- 日志设置 -->
        <el-tab-pane label="日志设置" name="logs">
          <div class="settings-content">
            <h3>日志设置</h3>
            <el-form :model="logSettings" label-width="120px">
              <el-form-item label="日志级别">
                <el-select
                  v-model="logSettings.level"
                  placeholder="请选择日志级别"
                >
                  <el-option label="DEBUG" value="debug" />
                  <el-option label="INFO" value="info" />
                  <el-option label="WARNING" value="warning" />
                  <el-option label="ERROR" value="error" />
                  <el-option label="CRITICAL" value="critical" />
                </el-select>
              </el-form-item>
              <el-form-item label="日志格式">
                <el-select
                  v-model="logSettings.format"
                  placeholder="请选择日志格式"
                >
                  <el-option label="JSON" value="json" />
                  <el-option label="文本" value="text" />
                </el-select>
              </el-form-item>
              <el-form-item label="日志保留天数">
                <el-input-number
                  v-model="logSettings.retentionDays"
                  :min="1"
                  :max="365"
                />
                <span style="margin-left: 10px">天</span>
              </el-form-item>
              <el-form-item label="文件大小限制">
                <el-input-number
                  v-model="logSettings.maxFileSize"
                  :min="1"
                  :max="1024"
                />
                <span style="margin-left: 10px">MB</span>
              </el-form-item>
              <el-form-item label="日志轮转">
                <el-switch
                  v-model="logSettings.rotation"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="压缩日志">
                <el-switch
                  v-model="logSettings.compression"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveLogSettings">
                  保存设置
                </el-button>
                <el-button @click="viewLogs"> 查看日志 </el-button>
                <el-button @click="clearLogs"> 清理日志 </el-button>
                <el-button @click="resetLogSettings"> 重置 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <div class="settings-content">
            <h3>通知设置</h3>
            <el-form :model="notificationSettings" label-width="120px">
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
                  <el-checkbox label="task_start"> 任务开始 </el-checkbox>
                  <el-checkbox label="task_complete"> 任务完成 </el-checkbox>
                  <el-checkbox label="task_fail"> 任务失败 </el-checkbox>
                  <el-checkbox label="device_offline"> 设备离线 </el-checkbox>
                  <el-checkbox label="system_error"> 系统错误 </el-checkbox>
                  <el-checkbox label="security_alert"> 安全告警 </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings">
                  保存设置
                </el-button>
                <el-button @click="testNotification"> 测试通知 </el-button>
                <el-button @click="resetNotificationSettings"> 重置 </el-button>
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

// 响应式数据
const activeTab = ref("basic");
const uploadUrl = ref("/api/upload/logo");
const backupHistory = ref([]);

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
  passwordExpiry: 90,
  loginFailureLock: 5,
  sessionTimeout: 120,
  twoFactorAuth: false,
  ipWhitelist: "",
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

// 存储设置
const storageSettings = reactive({
  type: "local",
  localPath: "/data/uploads",
  maxFileSize: 100,
  ossAccessKeyId: "",
  ossAccessKeySecret: "",
  ossEndpoint: "",
  ossBucket: "",
  s3AccessKeyId: "",
  s3SecretAccessKey: "",
  s3Region: "",
  s3Bucket: "",
});

// 备份设置
const backupSettings = reactive({
  autoBackup: true,
  frequency: "daily",
  backupTime: "02:00",
  retentionDays: 30,
  backupPath: "/data/backups",
  backupContent: ["database", "files"],
});

// 日志设置
const logSettings = reactive({
  level: "info",
  format: "json",
  retentionDays: 30,
  maxFileSize: 100,
  rotation: true,
  compression: true,
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
const getBackupStatusTag = (status) => {
  const statusMap = {
    completed: "success",
    running: "warning",
    failed: "danger",
    pending: "info",
  };
  return statusMap[status] || "";
};

const getBackupStatusText = (status) => {
  const statusMap = {
    completed: "完成",
    running: "进行中",
    failed: "失败",
    pending: "等待中",
  };
  return statusMap[status] || status;
};

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
    passwordExpiry: 90,
    loginFailureLock: 5,
    sessionTimeout: 120,
    twoFactorAuth: false,
    ipWhitelist: "",
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

const saveStorageSettings = async () => {
  try {
    await systemApi.updateStorageSettings(storageSettings);
    ElMessage.success("存储设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const testStorageSettings = async () => {
  try {
    await systemApi.testStorageSettings(storageSettings);
    ElMessage.success("存储连接测试成功");
  } catch (error) {
    ElMessage.error("存储连接测试失败");
  }
};

const resetStorageSettings = () => {
  Object.assign(storageSettings, {
    type: "local",
    localPath: "/data/uploads",
    maxFileSize: 100,
    ossAccessKeyId: "",
    ossAccessKeySecret: "",
    ossEndpoint: "",
    ossBucket: "",
    s3AccessKeyId: "",
    s3SecretAccessKey: "",
    s3Region: "",
    s3Bucket: "",
  });
};

const saveBackupSettings = async () => {
  try {
    await systemApi.updateBackupSettings(backupSettings);
    ElMessage.success("备份设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const createBackup = async () => {
  try {
    await systemApi.createBackup();
    ElMessage.success("备份任务已创建");
    getBackupHistory();
  } catch (error) {
    ElMessage.error("创建备份失败");
  }
};

const resetBackupSettings = () => {
  Object.assign(backupSettings, {
    autoBackup: true,
    frequency: "daily",
    backupTime: "02:00",
    retentionDays: 30,
    backupPath: "/data/backups",
    backupContent: ["database", "files"],
  });
};

const getBackupHistory = async () => {
  try {
    const response = await systemApi.getBackupHistory();
    backupHistory.value = response.data;
  } catch (error) {
    console.error("获取备份历史失败:", error);
  }
};

const downloadBackup = async (backup) => {
  try {
    const response = await systemApi.downloadBackup(backup.id);
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = backup.filename;
    link.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error("下载失败");
  }
};

const deleteBackup = async (backup) => {
  try {
    await ElMessageBox.confirm("确定要删除这个备份吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await systemApi.deleteBackup(backup.id);
    ElMessage.success("删除成功");
    getBackupHistory();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

const saveLogSettings = async () => {
  try {
    await systemApi.updateLogSettings(logSettings);
    ElMessage.success("日志设置保存成功");
  } catch (error) {
    ElMessage.error("保存失败");
  }
};

const viewLogs = () => {
  ElMessage.info("日志查看功能开发中...");
};

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm("确定要清理历史日志吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await systemApi.clearLogs();
    ElMessage.success("日志清理成功");
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("清理失败");
    }
  }
};

const resetLogSettings = () => {
  Object.assign(logSettings, {
    level: "info",
    format: "json",
    retentionDays: 30,
    maxFileSize: 100,
    rotation: true,
    compression: true,
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

const loadSettings = async () => {
  try {
    const [basic, security, email, storage, backup, log, notification] =
      await Promise.all([
        systemApi.getBasicSettings(),
        systemApi.getSecuritySettings(),
        systemApi.getEmailSettings(),
        systemApi.getStorageSettings(),
        systemApi.getBackupSettings(),
        systemApi.getLogSettings(),
        systemApi.getNotificationSettings(),
      ]);

    Object.assign(basicSettings, basic.data);
    Object.assign(securitySettings, security.data);
    Object.assign(emailSettings, email.data);
    Object.assign(storageSettings, storage.data);
    Object.assign(backupSettings, backup.data);
    Object.assign(logSettings, log.data);
    Object.assign(notificationSettings, notification.data);
  } catch (error) {
    console.error("加载设置失败:", error);
  }
};

// 生命周期
onMounted(() => {
  loadSettings();
  getBackupHistory();
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

.backup-history {
  margin-top: 30px;
}

.backup-history h4 {
  margin-bottom: 15px;
  color: #303133;
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
