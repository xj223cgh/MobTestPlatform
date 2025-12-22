<template>
  <div class="profile-container">
    <div class="page-header">
      <h1 class="title">
        个人中心
      </h1>
    </div>

    <div class="profile-header">
      <div class="profile-avatar">
        <el-avatar
          :size="80"
          :src="userInfo.avatar"
          :class="avatar - gradient"
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
        <!-- 个人信息 -->
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
                <el-col :span="12">
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
                <el-col :span="12">
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
                <el-col :span="12">
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
                <el-col :span="12">
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
                <el-col :span="24">
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
                <el-col :span="12">
                  <el-form-item label="角色">
                    <el-input
                      :value="getRoleText(userInfo.role)"
                      disabled
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
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

        <!-- 修改密码 -->
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { getUserInfo, changePassword as changePasswordApi } from "@/api/auth";
import { updateUser } from "@/api/user";

const router = useRouter();

const userStore = useUserStore();

// 当前激活的标签页
const activeTab = ref("info");

// 用户信息
const userInfo = ref({});

// 个人信息表单
const infoFormRef = ref();
const infoForm = reactive({
  username: "",
  real_name: "",
  gender: "other",
  phone: "",
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
};

// 密码表单
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

// 加载状态
const infoLoading = ref(false);
const passwordLoading = ref(false);

// 获取角色文本
const getRoleText = (role) => {
  const roleMap = {
    super: "超级管理员",
    manager: "管理员",
    tester: "测试员",
    admin: "实习生",
  };
  return roleMap[role] || role;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN");
};

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const response = await getUserInfo();
    if (response.code === 200) {
      userInfo.value = response.data.user;

      // 填充表单
      infoForm.username = userInfo.value.username;
      infoForm.real_name = userInfo.value.real_name || "";
      infoForm.gender = userInfo.value.gender || "other";
      infoForm.phone = userInfo.value.phone || "";
      infoForm.department = userInfo.value.department || "";
    }
  } catch (error) {
    console.error("获取用户信息失败:", error);
    ElMessage.error("获取用户信息失败");
  }
};

// 更新个人信息
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
      // 更新store中的用户信息
      userStore.updateUserInfo({
        real_name: infoForm.real_name,
        gender: infoForm.gender,
        phone: infoForm.phone,
        department: infoForm.department,
      });

      ElMessage.success("个人信息更新成功");
      await loadUserInfo(); // 重新加载用户信息
    } else {
      ElMessage.error(response.message || "更新失败");
    }
  } catch (error) {
    console.error("更新个人信息失败:", error);
    ElMessage.error("更新失败，请稍后重试");
  } finally {
    infoLoading.value = false;
  }
};

// 重置个人信息表单
const resetInfo = () => {
  infoForm.real_name = userInfo.value.real_name || "";
  infoForm.gender = userInfo.value.gender || "other";
  infoForm.phone = userInfo.value.phone || "";
  infoForm.department = userInfo.value.department || "";
};

// 修改密码
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

      // 显示弹窗提示用户需要重新登录
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
      } catch (e) {
        // 即使弹窗被异常关闭，也强制执行登出和跳转
        console.log("弹窗被关闭，但仍需登出");
      }

      // 清除用户会话信息
      await userStore.logout();

      // 强制跳转到登录页面，使用 replace 模式避免用户可以返回到修改密码页面
      router.replace("/login");
    } else {
      ElMessage.error(response.message || "密码修改失败");
    }
  } catch (error) {
    // 如果用户点击了取消按钮，不做处理
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

// 重置密码表单
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
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #fafafa;
  min-height: calc(100vh - 64px); // 减去导航栏高度
}

.page-header {
  margin-bottom: 24px;

  .title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }
}

.profile-header {
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  color: #303133;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .profile-avatar {
    display: flex;
    align-items: center;
    gap: 20px;

    .avatar-gradient {
      background: #f0f2f5;
      color: #606266;
      font-weight: 500;
    }

    .avatar-text {
      h2 {
        margin: 0 0 6px 0;
        font-size: 20px;
        font-weight: 600;
      }

      .role-text {
        margin: 0;
        color: #606266;
        font-size: 14px;
      }
    }
  }
}

.card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.profile-content {
  margin-bottom: 30px;

  .profile-tabs {
    :deep(.el-tabs__header) {
      margin: 0;
      background: #fafafa;
      padding: 0 20px;
      border-bottom: 1px solid #ebeef5;

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
        color: #606266;
        padding: 0 16px;
        transition: all 0.3s ease;

        &.is-active {
          color: #1890ff;
          font-weight: 500;
        }
        &:hover {
          color: #1890ff;
        }
      }

      .el-tabs__active-bar {
        height: 2px;
        background: #1890ff;
      }
    }

    :deep(.el-tabs__content) {
      padding: 24px;
    }
  }
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.info-form,
.password-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    font-weight: 500;
    color: #606266;
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

// 添加简单过渡效果
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

// 响应式设计
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
    background-color: #fff;
    min-height: calc(100vh - 56px); // 调整为移动端导航栏高度
  }

  .page-header .title {
    font-size: 18px;
    text-align: center;
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
    padding: 12px;
  }

  .profile-header {
    padding: 16px;
  }

  .profile-content {
    .profile-tabs {
      :deep(.el-tabs__content) {
        padding: 12px;
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
</style>
