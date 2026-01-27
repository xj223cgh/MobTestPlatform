import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

import TestAIPage from "@/views/TestAIPage.vue";

// 配置NProgress
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
    name: "Register",
    component: () => import("@/views/auth/Register.vue"),
    meta: { title: "注册", requiresAuth: false },
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
        meta: { title: "项目管理", icon: "Briefcase" },
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
        meta: { title: "迭代管理", icon: "Calendar" },
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
        meta: { title: "需求管理", icon: "Document" },
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
        path: "users",
        name: "Users",
        component: () => import("@/views/user/UserManagement.vue"),
        meta: { title: "用户管理", icon: "User" },
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

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start();

  const userStore = useUserStore();

  // 设置页面标题
  document.title = to.meta.title
    ? `${to.meta.title} - 移动端测试平台`
    : "移动端测试平台";

  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    const isAuthenticated = userStore.isAuthenticated;

    if (isAuthenticated) {
      // 已登录，优化：只在页面刷新或从外部链接进入时检查后端认证状态
      // 避免每次路由跳转都发起网络请求
      if (from.path === "/" || from.path === "") {
        try {
          const isAuthValid = await userStore.checkAuth();
          if (!isAuthValid) {
            // 认证失效，跳转到登录页
            next("/login");
            return;
          }
        } catch (error) {
          // 检查失败，跳转到登录页
          next("/login");
          return;
        }
      }
    } else {
      // 未登录，跳转到登录页
      next("/login");
      return;
    }
  } else {
    // 不需要认证的页面，如果已登录则跳转到首页
    if (userStore.isAuthenticated && to.path !== "/404" && to.path !== "/403") {
      next("/home");
      return;
    }
  }

  next();
});

// 全局后置钩子
router.afterEach(() => {
  NProgress.done();
});

export default router;
