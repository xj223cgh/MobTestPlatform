<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="profile-avatar">
        <el-avatar
          :size="80"
          :src="userInfo.avatar"
          class="avatar-gradient"
        >
          {{ (userInfo.username || "?").charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="avatar-text">
          <h2>{{ userInfo.username || "未知人员" }}</h2>
          <p class="role-text">
            {{ getRoleText(userInfo.role) }}
          </p>
        </div>
      </div>
    </div>

    <div class="profile-content card">
      <el-tabs
        v-model="activeTab"
        class="profile-tabs"
      >
        <el-tab-pane
          label="个人信息"
          name="info"
        >
          <div class="info-section">
            <h3 class="section-title">
              基本信息
            </h3>
            <el-form
              ref="infoFormRef"
              :model="infoForm"
              :rules="infoRules"
              label-width="120px"
              class="info-form"
              size="large"
            >
              <el-row :gutter="20">
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item
                    label="用户名"
                    prop="username"
                  >
                    <el-input
                      v-model="infoForm.username"
                      disabled
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item
                    label="真实姓名"
                    prop="real_name"
                  >
                    <el-input
                      v-model="infoForm.real_name"
                      placeholder="请输入真实姓名"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item
                    label="性别"
                    prop="gender"
                  >
                    <el-radio-group v-model="infoForm.gender">
                      <el-radio value="male">
                        男
                      </el-radio>
                      <el-radio value="female">
                        女
                      </el-radio>
                      <el-radio value="other">
                        其他
                      </el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item
                    label="手机号"
                    prop="phone"
                  >
                    <el-input
                      v-model="infoForm.phone"
                      placeholder="请输入手机号"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row>
                <el-col :xs="24" :sm="24" :md="24">
                  <el-form-item
                    label="邮箱"
                    prop="email"
                  >
                    <div
                      v-if="boundEmailDisplay"
                      class="email-bound-row"
                    >
                      <span class="email-bound-text">{{ boundEmailDisplay }}</span>
                      <el-tag
                        size="small"
                        type="success"
                        effect="plain"
                        class="email-bound-tag"
                      >
                        已绑定
                      </el-tag>
                      <div class="email-bound-actions">
                        <el-button
                          type="primary"
                          plain
                          size="small"
                          @click="startChangeEmail"
                        >
                          更换邮箱
                        </el-button>
                        <el-button
                          type="danger"
                          plain
                          size="small"
                          @click="handleUnbindEmail"
                        >
                          解除绑定
                        </el-button>
                      </div>
                    </div>
                    <div
                      v-else
                      class="email-field-with-verify"
                    >
                      <QqEmailInput
                        v-model="infoForm.email"
                        placeholder="选填，QQ 号"
                        class="email-input"
                      />
                      <el-button
                        type="primary"
                        plain
                        size="default"
                        :loading="emailCodeSending"
                        @click="openEmailVerifyDialog"
                      >
                        验证邮箱
                      </el-button>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row>
                <el-col :xs="24" :sm="24" :md="24">
                  <el-form-item
                    label="部门"
                    prop="department"
                  >
                    <el-input
                      v-model="infoForm.department"
                      placeholder="请输入部门"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item label="角色">
                    <el-input
                      :value="getRoleText(userInfo.role)"
                      disabled
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="24" :md="12">
                  <el-form-item label="创建时间">
                    <el-input
                      :value="formatDate(userInfo.created_at)"
                      disabled
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item>
                <div class="form-actions">
                  <el-button
                    type="primary"
                    :loading="infoLoading"
                    size="large"
                    @click="updateInfo"
                  >
                    保存
                  </el-button>
                  <el-button
                    size="large"
                    @click="resetInfo"
                  >
                    重置
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="修改密码"
          name="password"
        >
          <div class="password-section">
            <h3 class="section-title">
              修改密码
            </h3>
            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="120px"
              class="password-form"
              size="large"
            >
              <el-row>
                <el-col :span="24">
                  <el-form-item
                    label="原密码"
                    prop="old_password"
                  >
                    <el-input
                      v-model="passwordForm.old_password"
                      type="password"
                      placeholder="请输入原密码"
                      show-password
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row>
                <el-col :span="24">
                  <el-form-item
                    label="新密码"
                    prop="new_password"
                  >
                    <el-input
                      v-model="passwordForm.new_password"
                      type="password"
                      placeholder="请输入新密码（至少6位）"
                      show-password
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row>
                <el-col :span="24">
                  <el-form-item
                    label="确认密码"
                    prop="confirm_password"
                  >
                    <el-input
                      v-model="passwordForm.confirm_password"
                      type="password"
                      placeholder="请再次输入新密码"
                      show-password
                      @keyup.enter="changePassword"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item>
                <div class="form-actions">
                  <el-button
                    type="primary"
                    :loading="passwordLoading"
                    size="large"
                    @click="changePassword"
                  >
                    修改密码
                  </el-button>
                  <el-button
                    size="large"
                    @click="resetPassword"
                  >
                    重置
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="emailVerifyDialogVisible"
      title="验证邮箱"
      width="400px"
      :close-on-click-modal="false"
      @close="closeEmailVerifyDialog"
    >
      <div class="email-verify-dialog">
        <p v-if="emailVerifyTarget" class="verify-tip">
          验证码已发送至 <strong>{{ emailVerifyTarget }}</strong>，请输入 6 位验证码完成验证。
        </p>
        <el-input
          v-model="emailVerifyCode"
          placeholder="请输入 6 位验证码"
          maxlength="6"
          clearable
          class="verify-code-input"
        />
      </div>
      <template #footer>
        <el-button @click="closeEmailVerifyDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="emailVerifyConfirming"
          @click="confirmEmailVerify"
        >
          确认绑定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="unbindDialogVisible"
      title="解除邮箱绑定"
      width="400px"
      :close-on-click-modal="false"
      @close="closeUnbindDialog"
    >
      <div class="unbind-verify-dialog">
        <p v-if="unbindEmailTarget" class="verify-tip">
          验证码已发送至 <strong>{{ unbindEmailTarget }}</strong>，请输入 6 位验证码完成解除。
        </p>
        <el-input
          v-model="unbindCode"
          placeholder="请输入 6 位验证码"
          maxlength="6"
          clearable
          class="verify-code-input"
        />
      </div>
      <template #footer>
        <el-button @click="closeUnbindDialog">取消</el-button>
        <el-button
          :loading="unbindResendLoading"
          @click="resendUnbindCode"
        >
          重新发送验证码
        </el-button>
        <el-button
          type="danger"
          :loading="unbindConfirming"
          @click="confirmUnbindEmail"
        >
          确认解除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { getUserInfo, changePassword as changePasswordApi, sendBindEmailCode, confirmEmailBinding, sendUnbindEmailCode, unbindEmail } from "@/api/auth";
import { updateUser } from "@/api/user";
import { isPermissionError } from "@/utils/request";
import QqEmailInput from "@/components/QqEmailInput.vue";

function getFullQqEmail(localPart) {
  const s = (localPart || "").trim();
  return s ? s + "@qq.com" : "";
}
function toEmailLocal(fullEmail) {
  if (!fullEmail || typeof fullEmail !== "string") return "";
  return fullEmail.trim().replace(/@qq\.com$/i, "");
}

const router = useRouter();

const userStore = useUserStore();

const activeTab = ref("info");
const userInfo = ref({});
const infoFormRef = ref();
const infoForm = reactive({
  username: "",
  real_name: "",
  gender: "other",
  phone: "",
  email: "",
  department: "",
});

const infoRules = {
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号格式",
      trigger: "blur",
    },
  ],
  email: [
    {
      validator: (_rule, value, callback) => {
        if (!value || !String(value).trim()) {
          callback();
          return;
        }
        const full = getFullQqEmail(value);
        if (!/^[1-9]\d{4,10}@qq\.com$/.test(full)) {
          callback(new Error("仅支持 QQ 邮箱，QQ 号为 5～11 位数字"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const passwordFormRef = ref();
const passwordForm = reactive({
  old_password: "",
  new_password: "",
  confirm_password: "",
});

const passwordRules = {
  old_password: [{ required: true, message: "请输入原密码", trigger: "blur" }],
  new_password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
  ],
  confirm_password: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const infoLoading = ref(false);
const passwordLoading = ref(false);

const getRoleText = (role) => {
  const roleMap = {
    super: "超级管理员",
    manager: "管理员",
    tester: "测试员",
    admin: "普通用户",
  };
  return roleMap[role] || role;
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN");
};

const loadUserInfo = async () => {
  try {
    const response = await getUserInfo();
    if (response.code === 200) {
      userInfo.value = response.data.user;

      infoForm.username = userInfo.value.username;
      infoForm.real_name = userInfo.value.real_name || "";
      infoForm.gender = userInfo.value.gender || "other";
      infoForm.phone = userInfo.value.phone || "";
      infoForm.email = toEmailLocal(userInfo.value.email);
      infoForm.department = userInfo.value.department || "";
      boundEmailDisplay.value = (userInfo.value.email || "").trim();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    console.error("获取用户信息失败:", error);
    ElMessage.error("获取用户信息失败");
  }
};

const updateInfo = async () => {
  if (!infoFormRef.value) return;

  try {
    await infoFormRef.value.validate();
    infoLoading.value = true;

    const response = await updateUser(userInfo.value.id, {
      real_name: infoForm.real_name,
      gender: infoForm.gender,
      phone: infoForm.phone,
      department: infoForm.department,
    });

    if (response.code === 200) {
      userStore.updateUserInfo({
        real_name: infoForm.real_name,
        gender: infoForm.gender,
        phone: infoForm.phone,
        department: infoForm.department,
      });

      ElMessage.success("个人信息更新成功");
      await loadUserInfo();
    } else {
      ElMessage.error(response.message || "更新失败");
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    console.error("更新个人信息失败:", error);
    ElMessage.error("更新失败，请稍后重试");
  } finally {
    infoLoading.value = false;
  }
};

const resetInfo = () => {
  infoForm.real_name = userInfo.value.real_name || "";
  infoForm.gender = userInfo.value.gender || "other";
  infoForm.phone = userInfo.value.phone || "";
  infoForm.email = toEmailLocal(userInfo.value.email);
  infoForm.department = userInfo.value.department || "";
  boundEmailDisplay.value = (userInfo.value.email || "").trim();
};

const startChangeEmail = () => {
  boundEmailDisplay.value = "";
  infoForm.email = "";
};

const unbindDialogVisible = ref(false);
const unbindEmailTarget = ref("");
const unbindCode = ref("");
const unbindConfirming = ref(false);
const unbindResendLoading = ref(false);

const handleUnbindEmail = () => {
  ElMessageBox.confirm(
    "解除绑定后，您将无法使用该邮箱验证码登录与找回密码，确定要解除吗？",
    "解除邮箱绑定",
    {
      confirmButtonText: "获取验证码",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(async () => {
      try {
        const res = await sendUnbindEmailCode();
        if (res.code === 200 || res.success) {
          unbindEmailTarget.value = boundEmailDisplay.value;
          unbindCode.value = "";
          unbindDialogVisible.value = true;
          ElMessage.success("验证码已发送到您的邮箱");
        }
      } catch (e) {
        if (!e._messageShown) ElMessage.error(e.response?.data?.message || "发送失败");
      }
    })
    .catch(() => {});
};

const closeUnbindDialog = () => {
  unbindDialogVisible.value = false;
  unbindEmailTarget.value = "";
  unbindCode.value = "";
};

const resendUnbindCode = async () => {
  unbindResendLoading.value = true;
  try {
    const res = await sendUnbindEmailCode();
    if (res.code === 200 || res.success) ElMessage.success("验证码已重新发送");
    else ElMessage.error(res.message || "发送失败");
  } catch (e) {
    if (!e._messageShown) ElMessage.error(e.response?.data?.message || "发送失败");
  } finally {
    unbindResendLoading.value = false;
  }
};

const confirmUnbindEmail = async () => {
  const code = (unbindCode.value || "").trim();
  if (!code || code.length !== 6) {
    ElMessage.warning("请输入 6 位验证码");
    return;
  }
  unbindConfirming.value = true;
  try {
    const res = await unbindEmail({ code });
    if (res.code === 200 || res.success) {
      ElMessage.success("已解除邮箱绑定");
      closeUnbindDialog();
      boundEmailDisplay.value = "";
      infoForm.email = "";
      await loadUserInfo();
    } else {
      ElMessage.error(res.message || "操作失败");
    }
  } catch (e) {
    if (!e._messageShown) ElMessage.error(e.response?.data?.message || "操作失败");
  } finally {
    unbindConfirming.value = false;
  }
};

const emailVerifyDialogVisible = ref(false);
const emailVerifyTarget = ref("");
const emailVerifyCode = ref("");
const emailCodeSending = ref(false);
const emailVerifyConfirming = ref(false);
/** 已绑定的邮箱（有值时显示「已绑定」+ 更换邮箱） */
const boundEmailDisplay = ref("");

const openEmailVerifyDialog = async () => {
  const fullEmail = getFullQqEmail(infoForm.email);
  if (!fullEmail || fullEmail === "@qq.com") {
    ElMessage.warning("请先输入 QQ 号");
    return;
  }
  if (!/^[1-9]\d{4,10}@qq\.com$/.test(fullEmail)) {
    ElMessage.warning("QQ 号需为 5～11 位数字");
    return;
  }
  emailCodeSending.value = true;
  try {
    const res = await sendBindEmailCode({ email: fullEmail });
    if (res.code === 200) {
      emailVerifyTarget.value = fullEmail;
      emailVerifyCode.value = "";
      emailVerifyDialogVisible.value = true;
      ElMessage.success("验证码已发送");
    }
  } catch (e) {
    if (!e._messageShown) ElMessage.error(e.response?.data?.message || "发送失败");
  } finally {
    emailCodeSending.value = false;
  }
};

const closeEmailVerifyDialog = () => {
  emailVerifyDialogVisible.value = false;
  emailVerifyTarget.value = "";
  emailVerifyCode.value = "";
};

const confirmEmailVerify = async () => {
  const code = (emailVerifyCode.value || "").trim();
  if (!code || code.length !== 6) {
    ElMessage.warning("请输入 6 位验证码");
    return;
  }
  const fullEmail = emailVerifyTarget.value;
  if (!fullEmail) return;
  emailVerifyConfirming.value = true;
  try {
    const res = await confirmEmailBinding({ email: fullEmail, code });
    if (res.code === 200 || res.success) {
      ElMessage.success("邮箱绑定成功");
      infoForm.email = toEmailLocal(fullEmail);
      boundEmailDisplay.value = fullEmail;
      closeEmailVerifyDialog();
      await loadUserInfo();
    }
  } catch (e) {
    if (!e._messageShown) ElMessage.error(e.response?.data?.message || "验证失败");
  } finally {
    emailVerifyConfirming.value = false;
  }
};

const changePassword = async () => {
  if (!passwordFormRef.value) return;

  try {
    await passwordFormRef.value.validate();
    passwordLoading.value = true;

    const response = await changePasswordApi({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    });

    if (response.code === 200) {
      resetPassword();

      try {
        await ElMessageBox.confirm(
          "密码修改成功，为了安全起见，请重新登录",
          "重新登录",
          {
            confirmButtonText: "去登录",
            cancelButtonText: "取消",
            type: "info",
            showCancelButton: false, // 强制用户重新登录
            closeOnClickModal: false,
            closeOnPressEscape: false,
          },
        );
      } catch {}

      await userStore.logout();
      router.replace("/login");
    } else {
      ElMessage.error(response.message || "密码修改失败");
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    if (error.name !== "MessageBoxCloseError") {
      console.error("修改密码失败:", error);
      ElMessage.error(
        error.response?.data?.message || "密码修改失败，请稍后重试",
      );
    }
  } finally {
    passwordLoading.value = false;
  }
};

const resetPassword = () => {
  passwordForm.old_password = "";
  passwordForm.new_password = "";
  passwordForm.confirm_password = "";
  passwordFormRef.value?.clearValidate();
};

onMounted(() => {
  loadUserInfo();
});
</script>

<style lang="scss" scoped>
.profile-container {
  box-sizing: border-box;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 32px 32px;
  background-color: var(--el-bg-color-page, #f5f7fa);
  min-height: calc(100vh - 64px); // 减去导航栏高度
  overflow-x: hidden;
}

.profile-header {
  width: 100%;
  min-width: 0;
  background: var(--el-bg-color, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  border-radius: 8px;
  padding: 28px 32px;
  margin-bottom: 20px;
  color: var(--el-text-color-primary, #303133);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .profile-avatar {
    display: flex;
    align-items: center;
    gap: 20px;

    .avatar-gradient {
      background: var(--el-fill-color-light, #f0f2f5);
      color: var(--el-text-color-regular, #606266);
      font-weight: 500;
    }

    .avatar-text {
      h2 {
        margin: 0 0 6px 0;
        font-size: 20px;
        font-weight: 600;
        color: var(--el-text-color-primary, #303133);
      }

      .role-text {
        margin: 0;
        color: var(--el-text-color-regular, #606266);
        font-size: 14px;
      }
    }
  }
}

.card {
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
  width: 100%;
  min-width: 0;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.profile-content {
  margin-bottom: 32px;
  width: 100%;
  min-width: 0;

  .profile-tabs {
    :deep(.el-tabs__header) {
      margin: 0;
      background: var(--el-bg-color, #fff);
      padding: 0 24px;
      border-bottom: 1px solid var(--el-border-color-lighter, #ebeef5);

      .el-tabs__nav-wrap {
        padding: 0;
      }

      .el-tabs__nav {
        height: 56px;
      }

      .el-tabs__item {
        height: 56px;
        line-height: 56px;
        font-size: 14px;
        color: var(--el-text-color-regular, #606266);
        padding: 0 16px;
        transition: all 0.3s ease;

        &.is-active {
          color: var(--el-color-primary, #1890ff);
          font-weight: 500;
        }
        &:hover {
          color: var(--el-color-primary, #1890ff);
        }
      }

      .el-tabs__active-bar {
        height: 2px;
        background: #1890ff;
      }
    }

    :deep(.el-tabs__content) {
      padding: 28px 32px 32px;
      background: var(--el-bg-color, #fff);
      min-height: 200px;
    }
  }
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary, #303133);
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.info-form,
.password-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-regular, #606266);
  }

  :deep(.el-input__wrapper) {
    border-radius: 6px;
    transition: all 0.3s ease;
  }

  :deep(.el-input__inner) {
    height: 40px;
    font-size: 14px;
    border-radius: 6px;
    transition: all 0.3s ease;
  }

  :deep(.el-radio__label) {
    font-size: 14px;
    color: #606266;
  }

  .form-actions {
    margin-top: 24px;
    display: flex;
    gap: 12px;
    justify-content: flex-start;
  }

  .el-button {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
  }

  .el-button--primary {
    background: #1890ff;
    border: 1px solid #1890ff;
    color: white;
  }

  .el-button--default {
    background: white;
    border: 1px solid #dcdfe6;
    color: #606266;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.profile-header,
.profile-content,
.info-section,
.password-section {
  animation: fadeIn 0.3s ease-out;
}

@media (max-width: 992px) {
  .profile-container {
    padding: 20px 24px 24px;
  }

  .profile-header {
    padding: 24px;
  }

  .profile-content .profile-tabs :deep(.el-tabs__content) {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .profile-container {
    padding: 16px 20px 24px;
    background-color: #f5f7fa;
    min-height: calc(100vh - 56px); // 调整为移动端导航栏高度
  }

  .profile-header {
    padding: 20px;

    .profile-avatar {
      flex-direction: column;
      text-align: center;
      gap: 16px;

      .avatar-text {
        h2 {
          font-size: 18px;
        }
      }
    }
  }

  .profile-content {
    .profile-tabs {
      :deep(.el-tabs__header) {
        padding: 0 16px;

        .el-tabs__nav {
          height: 48px;
        }

        .el-tabs__item {
          height: 48px;
          line-height: 48px;
          font-size: 13px;
          padding: 0 12px;
        }
      }

      :deep(.el-tabs__content) {
        padding: 16px;
      }
    }
  }

  .section-title {
    font-size: 15px;
    padding-bottom: 8px;
  }

  .info-form,
  .password-form {
    :deep(.el-form-item__label) {
      font-size: 13px;
    }

    :deep(.el-input__inner) {
      height: 38px;
      font-size: 13px;
    }

    .form-actions {
      flex-direction: column;
      gap: 10px;
    }

    .el-button {
      width: 100%;
      padding: 8px 16px;
    }
  }
}

@media (max-width: 480px) {
  .profile-container {
    padding: 12px 16px 20px;
  }

  .profile-header {
    padding: 20px 16px;
  }

  .profile-content {
    .profile-tabs {
      :deep(.el-tabs__header) {
        padding: 0 16px;
      }

      :deep(.el-tabs__content) {
        padding: 20px 16px;
      }
    }
  }

  .info-form,
  .password-form {
    :deep(.el-form) {
      label-width: 90px;
    }

    :deep(.el-form-item__label) {
      font-size: 12px;
    }
  }
}

.email-field-with-verify {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.email-field-with-verify .email-input {
  flex: 1;
  min-width: 0;
}

.email-verify-dialog .verify-tip,
.unbind-verify-dialog .verify-tip {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}
.email-verify-dialog .verify-code-input,
.unbind-verify-dialog .verify-code-input {
  width: 100%;
}

.email-bound-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.email-bound-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
}
.email-bound-tag {
  flex-shrink: 0;
}
.email-bound-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 4px;
}
/* 与用户管理页邮箱区域按钮样式一致，略缩小宽度 */
.email-bound-actions .el-button {
  margin: 0;
  width: auto;
  padding: 5px 10px;
  font-size: 12px;
}
</style>
