<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo-box">
        <el-icon class="logo-icon"><Box /></el-icon>
        <span class="logo-text">WMS 管理端</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="custom-menu"
        background-color="#001529"
        text-color="#a6adb4"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/admin/monitor"><el-icon><Odometer /></el-icon><span>运维看板</span></el-menu-item>
        <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>账户管理</span></el-menu-item>
        <el-menu-item index="/admin/logs"><el-icon><Document /></el-icon><span>审计日志</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">系统管理员工作台</span>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" class="avatar">{{ username.charAt(0).toUpperCase() }}</el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Odometer, User, Document, Box, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
// 从 localStorage 获取用户名，如果没有则显示默认值
const username = ref(localStorage.getItem('username') || 'Admin')

// 处理下拉菜单点击事件
const handleCommand = (command) => {
  if (command === 'logout') {
    // 清除本地存储的凭证
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')
    ElMessage.success('已安全退出系统')
    // 返回登录页
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('个人设置功能正在开发中...')
  }
}
</script>

<style scoped>
/* =========== 核心布局框架 =========== */
.layout-container { height: 100vh; overflow: hidden; }

/* =========== 侧边栏样式 =========== */
.sidebar {
  background: #001529;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px 0 rgba(29,35,41,.05);
  z-index: 10;
}
.logo-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background: #002140;
  gap: 8px;
  letter-spacing: 1px;
}
.custom-menu { border-right: none; flex: 1; margin-top: 10px; }
/* 优化选中的菜单项样式，变成圆角浮动按钮风格 */
.custom-menu .el-menu-item { margin: 4px 8px; border-radius: 4px; height: 46px; line-height: 46px; }
.custom-menu .el-menu-item.is-active { background-color: #1890ff !important; }

/* =========== 顶部 Header 样式 =========== */
.header {
  height: 60px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  z-index: 9;
}
.page-title { font-size: 18px; font-weight: 600; color: #303133; }
.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 6px;
  transition: all 0.3s;
}
.user-dropdown:hover { background: #f5f7fa; }
.avatar { background: #1890ff; color: #fff; font-weight: bold; margin-right: 8px; }
.username { font-size: 14px; color: #606266; }

/* =========== 主内容区样式 =========== */
.main-content {
  background: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}
.content-wrapper {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  box-sizing: border-box;
  overflow-y: auto;
}

/* =========== 路由切换动画 =========== */
.fade-transform-leave-active, .fade-transform-enter-active { transition: all 0.3s; }
.fade-transform-enter-from { opacity: 0; transform: translateX(-20px); }
.fade-transform-leave-to { opacity: 0; transform: translateX(20px); }
</style>