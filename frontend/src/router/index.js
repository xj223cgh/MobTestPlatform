import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

import TestAIPage from "@/views/TestAIPage.vue";

NProgress.configure({ showSpinner: false });

const routes = [
  {
    path: "/test-ai",
    name: "TestAI",
    component: TestAIPage,
    meta: { title: "AI API测试" },
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
    meta: { title: "登录", requiresAuth: false },
  },
  {
    path: "/register",
    redirect: "/login",
  },
  {
    path: "/forgot-password",
    name: "ForgotPassword",
    component: () => import("@/views/auth/ForgotPassword.vue"),
    meta: { title: "忘记密码", requiresAuth: false },
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: () => import("@/views/auth/ResetPassword.vue"),
    meta: { title: "重置密码", requiresAuth: false },
  },
  {
    path: "/mindmap-fullscreen",
    name: "MindmapFullscreen",
    component: () => import("@/views/testCase/MindmapFullscreen.vue"),
    meta: { title: "脑图全屏", requiresAuth: true, hidden: true },
  },
  {
    path: "/mindmap-editor",
    name: "MindmapEditor",
    component: () => import("@/views/testCase/MindmapEditor.vue"),
    meta: { title: "用例脑图编辑", requiresAuth: true, hidden: true },
  },
  {
    path: "/",
    name: "Layout",
    component: () => import("@/components/layout/Layout.vue"),
    meta: { requiresAuth: true },
    redirect: "/home",
    children: [
      {
        path: "home",
        name: "Home",
        component: () => import("@/views/home/Home.vue"),
        meta: { title: "首页", icon: "HomeFilled" },
      },
      {
        path: "projects",
        name: "Projects",
        component: () => import("@/views/project/ProjectManagement.vue"),
        meta: { title: "项目管理", icon: "Briefcase", permissions: ["project.list"] },
      },
      {
        path: "projects/:id",
        name: "ProjectDetail",
        component: () => import("@/views/project/ProjectDetail.vue"),
        meta: { title: "项目详情", icon: "Briefcase", hidden: true },
      },
      {
        path: "iterations",
        name: "Iterations",
        component: () => import("@/views/project/IterationManagement.vue"),
        meta: { title: "迭代管理", icon: "Calendar", permissions: ["iteration.list"] },
      },
      {
        path: "iterations/:id",
        name: "IterationDetail",
        component: () => import("@/views/project/IterationDetail.vue"),
        meta: { title: "迭代详情", icon: "Calendar", hidden: true },
      },
      {
        path: "requirements",
        name: "Requirements",
        component: () =>
          import("@/views/requirement/RequirementManagement.vue"),
        meta: { title: "需求管理", icon: "Document", permissions: ["requirement.list"] },
      },
      {
        path: "devices",
        name: "Devices",
        component: () => import("@/views/device/DeviceManagement.vue"),
        meta: { title: "设备管理", icon: "Monitor" },
      },
      {
        path: "devices/:id",
        name: "DeviceDetail",
        component: () => import("@/views/device/DeviceDetail.vue"),
        meta: { title: "设备详情", icon: "Monitor", hidden: true },
      },
      {
        path: "test-cases",
        name: "TestCases",
        component: () => import("@/views/testCase/TestCaseManagement.vue"),
        meta: { title: "用例管理", icon: "Document" },
      },
      {
        path: "case-reviews",
        name: "CaseReviews",
        component: () => import("@/views/caseReview/CaseReviewManagement.vue"),
        meta: { title: "用例评审", icon: "ChatRound" },
      },

      {
        path: "test-tasks",
        name: "TestTasks",
        component: () => import("@/views/testTask/TestTaskManagement.vue"),
        meta: { title: "测试任务", icon: "Menu" },
      },
      {
        path: "test-tasks/:id/execute",
        name: "TestCaseExecution",
        component: () => import("@/views/testTask/TestCaseExecution.vue"),
        meta: {
          title: "用例执行",
          icon: "Menu",
          hidden: true,
          requiresAuth: true,
        },
      },
      {
        path: "test-tasks/:id/device-execute",
        name: "DeviceScriptExecution",
        component: () => import("@/views/testTask/DeviceScriptExecution.vue"),
        meta: {
          title: "设备脚本执行",
          icon: "Menu",
          hidden: true,
          requiresAuth: true,
        },
      },
      {
        path: "report",
        name: "ReportManagement",
        component: () => import("@/views/report/ReportManagement.vue"),
        meta: { title: "报告管理", icon: "Odometer" },
      },
      {
        path: "report/:id",
        name: "ReportDetail",
        component: () => import("@/views/report/ReportDetail.vue"),
        meta: { title: "报告详情", icon: "Odometer", hidden: true },
      },
      {
        path: "report/record/:id",
        name: "ReportDetailByRecord",
        component: () => import("@/views/report/ReportDetail.vue"),
        meta: { title: "报告详情", icon: "Odometer", hidden: true },
      },
      {
        path: "users",
        name: "Users",
        component: () => import("@/views/user/UserManagement.vue"),
        meta: { title: "用户管理", icon: "User", permissions: ["user.list"] },
      },
      {
        path: "role-permissions",
        name: "RolePermissions",
        component: () => import("@/views/system/RolePermissionConfig.vue"),
        meta: { title: "权限配置", icon: "Key", permissions: ["role.permission_config"] },
      },
      {
        path: "help",
        name: "HelpCenter",
        component: () => import("@/views/help/HelpCenter.vue"),
        meta: { title: "帮助中心", icon: "QuestionFilled" },
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/views/profile/Profile.vue"),
        meta: { title: "个人中心", hidden: true },
      },
      {
        path: "settings",
        name: "Settings",
        component: () => import("@/views/system/SystemSettings.vue"),
        meta: { title: "系统设置", icon: "Setting", hidden: true },
      },
    ],
  },
  {
    path: "/403",
    name: "Forbidden",
    component: () => import("@/views/error/403.vue"),
    meta: { title: "访问被拒绝", requiresAuth: false },
  },
  {
    path: "/404",
    name: "NotFound",
    component: () => import("@/views/error/404.vue"),
    meta: { title: "页面不存在", requiresAuth: false },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/404",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  NProgress.start();

  const userStore = useUserStore();

  document.title = to.meta.title
    ? `${to.meta.title} - 移动端测试平台`
    : "移动端测试平台";

  if (to.meta.requiresAuth !== false) {
    const isAuthenticated = userStore.isAuthenticated;

    if (isAuthenticated) {
      // 已登录，优化：只在页面刷新或从外部链接进入时检查后端认证状态
      // 避免每次路由跳转都发起网络请求
      if (from.path === "/" || from.path === "") {
        try {
          const isAuthValid = await userStore.checkAuth();
          if (!isAuthValid) {
            next("/login");
            return;
          }
        } catch (error) {
          next("/login");
          return;
        }
      }
    } else {
      next("/login");
      return;
    }
  } else {
    // 已登录访问免认证页时跳转首页，排除 404/403
    if (
      userStore.isAuthenticated &&
      to.path !== "/404" &&
      to.path !== "/403"
    ) {
      next("/home");
      return;
    }
  }

  // 目标路由要求埋点权限时，校验用户是否具备任一权限
  if (userStore.isAuthenticated && to.meta?.permissions?.length) {
    const hasAny = to.meta.permissions.some((p) => userStore.hasPermission(p));
    if (!hasAny) {
      next("/403");
      return;
    }
  }

  next();
});

router.afterEach(() => {
  NProgress.done();
});

export default router;
