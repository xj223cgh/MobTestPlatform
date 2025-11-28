import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false })

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue'),
    meta: { title: '忘记密码', requiresAuth: false }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/auth/ResetPassword.vue'),
    meta: { title: '重置密码', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/layout/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
          path: 'home',
          name: 'Home',
          component: () => import('@/views/home/Home.vue'),
          meta: { title: '首页', icon: 'HomeFilled' }
        },
        {
          path: 'projects',
          name: 'Projects',
          component: () => import('@/views/project/ProjectManagement.vue'),
          meta: { title: '项目管理', icon: 'Briefcase' }
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: () => import('@/views/project/ProjectDetail.vue'),
          meta: { title: '项目详情', icon: 'Briefcase', hidden: true }
        },
        {
          path: 'iterations',
          name: 'Iterations',
          component: () => import('@/views/project/IterationManagement.vue'),
          meta: { title: '迭代管理', icon: 'SwitchButton' }
        },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/views/device/DeviceManagement.vue'),
        meta: { title: '设备管理', icon: 'Monitor' }
      },
      {
          path: 'test-cases',
          name: 'TestCases',
          component: () => import('@/views/testCase/TestCaseManagement.vue'),
          meta: { title: '用例管理', icon: 'Document' },
          children: [
            {
              path: 'case-reviews',
              name: 'CaseReviews',
              component: () => import('@/views/caseReview/CaseReviewManagement.vue'),
              meta: { title: '用例评审', icon: 'ChatRound' }
            }
          ]
        },
        {
          path: 'test-plans',
          name: 'TestPlans',
          component: () => import('@/views/testPlan/TestPlanManagement.vue'),
          meta: { title: '测试计划', icon: 'Tickets' }
        },
      {
          path: 'test-tasks',
          name: 'TestTasks',
          component: () => import('@/views/testTask/TestTaskManagement.vue'),
          meta: { title: '测试任务', icon: 'Menu' }
        },
        {
          path: 'bugs',
          name: 'Bugs',
          component: () => import('@/views/bug/BugManagement.vue'),
          meta: { title: '缺陷管理', icon: 'Warning' }
        },
      {
        path: 'report',
        name: 'ReportManagement',
        component: () => import('@/views/report/ReportManagement.vue'),
        meta: { title: '报告管理', icon: 'Document' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/UserManagement.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },

      {
        path: 'help',
        name: 'HelpCenter',
        component: () => import('@/views/help/HelpCenter.vue'),
        meta: { title: '帮助中心', icon: 'QuestionFilled' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/Profile.vue'),
        meta: { title: '个人中心', hidden: true }
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '访问被拒绝', requiresAuth: false }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  const isAuthenticated = userStore.isAuthenticated
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 移动端测试平台` : '移动端测试平台'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!isAuthenticated) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }
  } else {
    // 不需要认证的页面，如果已登录则跳转到首页
    if (isAuthenticated && to.path !== '/404' && to.path !== '/403') {
      next('/home')
      return
    }
  }
  
  next()
})

// 全局后置钩子
router.afterEach(() => {
  NProgress.done()
})

export default router