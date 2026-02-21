<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">WMS | 主管控制台</div>
      <el-menu default-active="/supervisor/dashboard" router class="el-menu-vertical" background-color="#001529" text-color="#a6adb4" active-text-color="#ffffff">
        <el-menu-item index="/supervisor/dashboard"><el-icon><DataLine /></el-icon><span>管理驾驶舱</span></el-menu-item>
        <el-menu-item index="/supervisor/archives"><el-icon><Files /></el-icon><span>仓库与供应商档案</span></el-menu-item>
        <el-menu-item index="/supervisor/product"><el-icon><Warning /></el-icon><span>商品与预警管理</span></el-menu-item>
        <el-menu-item index="/supervisor/global"><el-icon><Coordinate /></el-icon><span>全局库存监控</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">主管工作台</div>
        <div class="header-right"><el-button type="danger" link>退出登录</el-button></div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* 样式与 Admin 完全一致，直接复用以保持系统整体风格统一 */
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