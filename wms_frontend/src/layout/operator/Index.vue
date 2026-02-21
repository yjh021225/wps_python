<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">WMS | 操作员终端</div>
      <el-menu default-active="/dashboard" router class="el-menu-vertical" background-color="#001529" text-color="#a6adb4" active-text-color="#ffffff">
        <el-menu-item index="/dashboard"><el-icon><House /></el-icon><span>个人工作台</span></el-menu-item>
        <el-menu-item index="/operator/inbound"><el-icon><Download /></el-icon><span>入库作业</span></el-menu-item>
        <el-menu-item index="/operator/outbound"><el-icon><Upload /></el-icon><span>出库作业</span></el-menu-item>
        <el-menu-item index="/operator/history"><el-icon><List /></el-icon><span>个人记录查询</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">作业终端</div>
        <div class="header-right"><el-button type="danger" link>退出登录</el-button></div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* 同样复用核心样式 */
.layout-container { height: 100vh; }
.sidebar { background-color: #001529; box-shadow: 2px 0 6px rgba(0,21,41,.35); z-index: 10; }
.logo { height: 60px; line-height: 60px; text-align: center; color: #fff; font-size: 18px; font-weight: bold; background-color: #002140; }
.el-menu-vertical { border-right: none; }
.el-menu-item:hover { background-color: #1890ff !important; color: #fff !important; }
.el-menu-item.is-active { background-color: #1890ff !important; }
.header { background-color: #fff; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 4px rgba(0,21,41,.08); z-index: 9; }
.header-left { font-size: 16px; font-weight: 500; color: #333; }
.main-content { padding: 24px; }
</style>