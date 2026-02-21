import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/Index.vue')
  },
  // ================= 1. 普通操作员路由组 =================
  {
    path: '/operator',
    name: 'OperatorLayout',
    component: () => import('../layout/operator/Index.vue'),
    redirect: '/operator/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../views/operator/Dashboard.vue') },
      { path: 'inbound', component: () => import('../views/operator/Inbound.vue') },
      { path: 'outbound', component: () => import('../views/operator/Outbound.vue') },
      { path: 'history', component: () => import('../views/operator/History.vue') }
    ]
  },
  // ================= 2. 仓库主管路由组 =================
  {
    path: '/supervisor',
    name: 'SupervisorLayout',
    component: () => import('../layout/supervisor/Index.vue'),
    redirect: '/supervisor/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../views/supervisor/Dashboard.vue') },
      { path: 'archives', component: () => import('../views/supervisor/Archives.vue') },
      { path: 'product', component: () => import('../views/supervisor/Product.vue') },
      { path: 'global', component: () => import('../views/supervisor/Global.vue') }
    ]
  },
  // ================= 3. 系统管理员路由组 =================
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('../layout/admin/Index.vue'),
    redirect: '/admin/monitor',
    children: [
      { path: 'monitor', component: () => import('../views/admin/Monitor.vue') },
      { path: 'users', component: () => import('../views/admin/Users.vue') },
      { path: 'logs', component: () => import('../views/admin/Logs.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router