<template>
  <div class="auth-slide">
    <div class="slide-panel">
      <div class="slide-viewport">
        <div
          class="slide-track"
          :class="{ register: mode === 'register' }"
        >
          <!-- 登录：左侧图片，右侧表单 -->
          <div class="slide-page">
            <div class="side-image">
              <img
                :src="formImageUrl"
                alt=""
                class="side-image-img"
              />
              <div class="side-image-overlay" />
            </div>
            <div class="side-form form-login">
              <h2>登录</h2>
              <form
                class="form"
                @submit.prevent="handleLogin"
              >
                <div class="field">
                  <input
                    v-model="loginForm.username"
                    type="text"
                    placeholder="用户名"
                    @keyup.enter="handleLogin"
                  />
                </div>
                <div class="field">
                  <input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="密码"
                    @keyup.enter="handleLogin"
                  />
                </div>
                <div class="options">
                  <label class="checkbox">
                    <input
                      v-model="loginForm.remember"
                      type="checkbox"
                      @change="handleRememberChange"
                    />
                    <span>记住我</span>
                  </label>
                  <router-link
                    to="/forgot-password"
                    class="link"
                  >
                    忘记密码
                  </router-link>
                </div>
                <button
                  type="submit"
                  class="btn-primary"
                  :disabled="loginLoading"
                >
                  {{ loginLoading ? "登录中…" : "登录" }}
                </button>
                <p class="switch-tip">
                  还没有账号？<a
                    href="#"
                    @click.prevent="mode = 'register'"
                  >立即注册</a>
                </p>
              </form>
            </div>
          </div>

          <!-- 注册：左侧表单，右侧图片 -->
          <div class="slide-page">
            <div class="side-form form-register">
              <h2>注册</h2>
              <form
                class="form"
                @submit.prevent="handleRegister"
              >
                <div class="field">
                  <input
                    v-model="registerForm.username"
                    type="text"
                    placeholder="用户名"
                  />
                </div>
                <div class="field">
                  <input
                    v-model="registerForm.phone"
                    type="text"
                    placeholder="手机号"
                  />
                </div>
                <div class="field">
                  <input
                    v-model="registerForm.realName"
                    type="text"
                    placeholder="真实姓名"
                  />
                </div>
                <div class="field">
                  <input
                    v-model="registerForm.password"
                    type="password"
                    placeholder="密码"
                  />
                </div>
                <label class="checkbox full">
                  <input
                    v-model="registerForm.agreement"
                    type="checkbox"
                  />
                  <span>同意<el-link
                    type="primary"
                    class="policy-link"
                    @click.prevent="showAgreement"
                  >《用户协议》</el-link>和<el-link
                    type="primary"
                    class="policy-link"
                    @click.prevent="showPrivacy"
                  >《隐私政策》</el-link></span>
                </label>
                <button
                  type="submit"
                  class="btn-primary"
                  :disabled="registerLoading"
                >
                  {{ registerLoading ? "注册中…" : "注册" }}
                </button>
                <p class="switch-tip">
                  已有账号？<a
                    href="#"
                    @click.prevent="mode = 'login'"
                  >立即登录</a>
                </p>
              </form>
            </div>
            <div class="side-image">
              <img
                :src="formImageUrl"
                alt=""
                class="side-image-img"
              />
              <div class="side-image-overlay" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="auth-footer">
      <p>&copy; 2025 移动测试平台. All rights reserved.</p>
    </div>

    <!-- 用户协议弹窗 -->
    <el-dialog
      v-model="agreementDialogVisible"
      title="用户协议"
      width="560px"
      class="policy-dialog"
    >
      <div class="policy-content">
        <p><strong>【用户协议】</strong></p>
        <p>欢迎使用移动测试平台。使用本平台即表示您同意以下条款。</p>
        <p><strong>一、服务说明</strong></p>
        <p>本平台提供移动应用测试管理相关功能，包括但不限于项目管理、用例管理、任务执行与报告查看。</p>
        <p><strong>二、账号与安全</strong></p>
        <p>您应妥善保管账号与密码，对使用该账号进行的所有行为负责。发现盗用或异常请及时联系管理员。</p>
        <p><strong>三、使用规范</strong></p>
        <p>您应遵守法律法规及平台规则，不得利用本平台从事违法违规或侵害他人权益的行为。</p>
        <p><strong>四、协议变更</strong></p>
        <p>平台可能适时修订本协议，修订后继续使用即视为接受新协议。</p>
        <p class="policy-tip">以上为通用模板，正式使用前请由法务或合规部门审定并替换为正式文本。</p>
      </div>
    </el-dialog>

    <!-- 隐私政策弹窗 -->
    <el-dialog
      v-model="privacyDialogVisible"
      title="隐私政策"
      width="560px"
      class="policy-dialog"
    >
      <div class="policy-content">
        <p><strong>【隐私政策】</strong></p>
        <p>我们重视您的隐私。本政策说明我们如何收集、使用与保护您的信息。</p>
        <p><strong>一、信息收集</strong></p>
        <p>为提供服务，我们可能收集账号信息（如用户名、手机号、姓名）、使用行为与设备相关信息。</p>
        <p><strong>二、信息使用</strong></p>
        <p>所收集信息用于账号认证、功能提供、安全与合规、以及改进产品体验，不会用于与上述目的无关的营销。</p>
        <p><strong>三、信息保护</strong></p>
        <p>我们采取合理技术与管理措施保护您的信息，防止未经授权的访问、泄露或篡改。</p>
        <p><strong>四、政策更新</strong></p>
        <p>我们可能更新本政策，重大变更会通过平台或注册邮箱等方式通知。</p>
        <p class="policy-tip">以上为通用模板，正式使用前请由法务或合规部门审定并替换为正式文本。</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { register } from "@/api/auth";
import { ElMessage } from "element-plus";

const router = useRouter();
const userStore = useUserStore();

const mode = ref("login");
const formImageUrl =
  "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80";

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});
const loginLoading = ref(false);

const registerForm = reactive({
  username: "",
  phone: "",
  realName: "",
  password: "",
  agreement: false,
});
const registerLoading = ref(false);

const agreementDialogVisible = ref(false);
const privacyDialogVisible = ref(false);

function handleRememberChange() {
  if (!loginForm.remember) {
    userStore.clearRememberedCredentials();
  } else if (loginForm.username && loginForm.password) {
    userStore.updateRememberedCredentials(
      loginForm.username,
      loginForm.password,
      true,
    );
  }
}

onMounted(() => {
  const remembered = userStore.getRememberedCredentials();
  if (remembered) {
    loginForm.username = remembered.username;
    loginForm.password = remembered.password;
    loginForm.remember = remembered.remember;
  }
});

function validateLogin() {
  const u = loginForm.username?.trim();
  const p = loginForm.password;
  if (!u) {
    ElMessage.warning("请输入用户名");
    return false;
  }
  if (u.length < 3 || u.length > 20) {
    ElMessage.warning("用户名长度在 3 到 20 个字符");
    return false;
  }
  if (!p) {
    ElMessage.warning("请输入密码");
    return false;
  }
  if (p.length < 6) {
    ElMessage.warning("密码长度不能少于 6 个字符");
    return false;
  }
  return true;
}

async function handleLogin() {
  if (!validateLogin()) return;
  loginLoading.value = true;
  try {
    const success = await userStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
      remember: loginForm.remember,
    });
    if (success) router.push("/home");
  } catch (e) {
    console.error("登录失败:", e);
  } finally {
    loginLoading.value = false;
  }
}

function validateRegister() {
  const u = registerForm.username?.trim();
  const phone = registerForm.phone?.trim();
  const name = registerForm.realName?.trim();
  const p = registerForm.password;
  if (!u) {
    ElMessage.warning("请输入用户名");
    return false;
  }
  if (u.length < 3 || u.length > 20) {
    ElMessage.warning("用户名长度在 3 到 20 个字符");
    return false;
  }
  if (!/^[a-zA-Z0-9_]+$/.test(u)) {
    ElMessage.warning("用户名只能包含字母、数字和下划线");
    return false;
  }
  if (!phone) {
    ElMessage.warning("请输入手机号");
    return false;
  }
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    ElMessage.warning("请输入有效的手机号");
    return false;
  }
  if (!name) {
    ElMessage.warning("请输入真实姓名");
    return false;
  }
  if (name.length < 2 || name.length > 20) {
    ElMessage.warning("姓名长度在 2 到 20 个字符");
    return false;
  }
  if (!p) {
    ElMessage.warning("请输入密码");
    return false;
  }
  if (p.length < 6) {
    ElMessage.warning("密码长度不能少于 6 个字符");
    return false;
  }
  if (!registerForm.agreement) {
    ElMessage.warning("请阅读并同意用户协议和隐私政策");
    return false;
  }
  return true;
}

async function handleRegister() {
  if (!validateRegister()) return;
  registerLoading.value = true;
  try {
    const res = await register({
      username: registerForm.username.trim(),
      phone: registerForm.phone.trim(),
      real_name: registerForm.realName.trim(),
      password: registerForm.password,
    });
    if (res.code === 200) {
      ElMessage.success("注册成功，请登录");
      mode.value = "login";
    } else {
      ElMessage.error(res.message || "注册失败");
    }
  } catch (e) {
    console.error("注册失败:", e);
    // 有 response 时说明请求已到达服务器，错误提示由 request 拦截器统一展示，此处不再重复弹窗
    if (!e.response) {
      ElMessage.error(e.message || "注册失败，请稍后重试");
    }
  } finally {
    registerLoading.value = false;
  }
}

function showAgreement() {
  agreementDialogVisible.value = true;
}
function showPrivacy() {
  privacyDialogVisible.value = true;
}
</script>

<style lang="scss" scoped>
.auth-slide {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fa;
  position: relative;
}

.slide-panel {
  width: 100%;
  max-width: 780px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.slide-viewport {
  overflow: hidden;
}

.slide-track {
  display: flex;
  width: 200%;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  &.register {
    transform: translateX(-50%);
  }
}

.slide-page {
  width: 50%;
  flex-shrink: 0;
  display: flex;
  min-height: 360px;
}

.side-image {
  width: 50%;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  background: #e4e7ed;
}

.side-image-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.side-image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(245, 247, 250, 0.25) 0%, rgba(245, 247, 250, 0.4) 100%);
  pointer-events: none;
}

.side-form {
  width: 50%;
  flex-shrink: 0;
  padding: 28px 28px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  box-sizing: border-box;
}

.side-form.form-login {
  justify-content: center;
}
.side-form.form-login .form {
  flex: 0 0 auto;
}
.side-form.form-login .form .btn-primary {
  margin-top: 16px;
}

.side-form h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
  text-align: center;
}

.form {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;

  .field {
    margin-bottom: 14px;
    input {
      width: 100%;
      height: 38px;
      padding: 0 12px;
      border: 1px solid #dcdfe6;
      border-radius: 6px;
      background: #fff;
      color: #303133;
      font-size: 14px;
      box-sizing: border-box;
      transition: border-color 0.2s;
      &::placeholder {
        color: #c0c4cc;
      }
      &:focus {
        outline: none;
        border-color: #409eff;
      }
    }
  }

  .options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 9px;
    margin-bottom: 14px;
    font-size: 13px;
  }

  .options .link {
    font-size: 13px;
  }

  .checkbox {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #606266;
    cursor: pointer;
    font-size: 13px;
    line-height: 1.5;
    input {
      width: auto;
      flex-shrink: 0;
    }
    &.full {
      margin-bottom: 14px;
      font-size: 13px;
      line-height: 1.5;
      color: #909399;
    }
  }

  .policy-link {
    font-size: 13px;
    vertical-align: baseline;
  }

  .link {
    color: #409eff;
    text-decoration: none;
    &:hover {
      text-decoration: underline;
    }
  }

  .btn-primary {
    width: 100%;
    max-width: 200px;
    height: 44px;
    margin: 0 auto;
    margin-top: auto;
    padding: 0 24px;
    border: none;
    border-radius: 8px;
    background: #409eff;
    color: #fff;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, transform 0.02s;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
    &:hover:not(:disabled) {
      background: #66b1ff;
    }
    &:active:not(:disabled) {
      transform: scale(0.98);
    }
    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }

  .switch-tip {
    text-align: center;
    margin-top: 22px;
    font-size: 14px;
    color: #909399;
    a {
      color: #409eff;
      font-size: 14px;
      text-decoration: none;
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #909399;
  p {
    margin: 0;
  }
}

.policy-dialog {
  :deep(.el-dialog__header) {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }
  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }
}

.policy-dialog .policy-content {
  max-height: 60vh;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.75;
  color: #303133;
  p {
    margin: 0 0 12px 0;
    &:last-child {
      margin-bottom: 0;
    }
  }
  strong {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
  .policy-tip {
    margin-top: 20px;
    padding-top: 12px;
    border-top: 1px solid #ebeef5;
    font-size: 13px;
    color: #909399;
    line-height: 1.5;
  }
}

@media (max-width: 768px) {
  .slide-page {
    flex-direction: column;
    min-height: auto;
  }
  .side-image,
  .side-form {
    width: 100%;
  }
  .side-image {
    min-height: 140px;
  }
  .side-form {
    padding: 24px 20px;
  }
}
</style>
