<template>
  <div class="operator-dashboard">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never" class="welcome-card">
          <div class="welcome-content">
            <el-avatar :size="64" class="avatar" style="background: #e6a23c;">{{ username.charAt(0).toUpperCase() }}</el-avatar>
            <div class="text-info">
              <h2>你好，{{ username }}！欢迎回到仓储作业系统。</h2>
              <p>今日事今日毕，请严格遵守安全操作规范，认真核对好每一件流转商品。</p>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="quick-actions" style="margin-top: 20px;">
          <template #header><span class="card-title">快捷操作入口</span></template>
          <div class="action-wrapper">
            <div class="action-box in-box" @click="$router.push('/operator/inbound')">
              <el-icon class="action-icon"><Download /></el-icon>
              <span class="action-text">新建入库作业</span>
            </div>
            <div class="action-box out-box" @click="$router.push('/operator/outbound')">
              <el-icon class="action-icon"><Upload /></el-icon>
              <span class="action-text">新建出库作业</span>
            </div>
            <div class="action-box his-box" @click="$router.push('/operator/history')">
              <el-icon class="action-icon"><List /></el-icon>
              <span class="action-text">查询我的记录</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never" class="stat-card">
          <template #header><span class="card-title">我今日的作业战绩</span></template>
          <div class="stat-item">
            <div class="stat-label">今日完成入库 (单)</div>
            <div class="stat-value text-success">{{ todayInbound }}</div>
          </div>
          <el-divider border-style="dashed" />
          <div class="stat-item">
            <div class="stat-label">今日完成出库 (单)</div>
            <div class="stat-value text-danger">{{ todayOutbound }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Download, Upload, List } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const username = ref(localStorage.getItem('username') || '操作员')
const todayInbound = ref(0)
const todayOutbound = ref(0)

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 拉取今天的战绩
const fetchMyTodayStats = async () => {
  try {
    const res = await api.get('orders/')
    const allOrders = res.data

    // 获取当天的日期字符串进行对比
    const todayStr = new Date().toLocaleDateString()

    // 过滤条件：1. 必须是我操作的  2. 必须是今天发生的
    const myTodayOrders = allOrders.filter(order => {
      const orderDate = new Date(order.create_time).toLocaleDateString()
      // 这里同样把 operator_name 改为 operator_username
      return order.operator_username === username.value && orderDate === todayStr
    })

    todayInbound.value = myTodayOrders.filter(o => o.order_type === 'in').length
    todayOutbound.value = myTodayOrders.filter(o => o.order_type === 'out').length

  } catch (error) {
    ElMessage.error('获取今日统计数据失败')
  }
}

onMounted(() => {
  fetchMyTodayStats()
})
</script>

<style scoped>
.welcome-card { border-radius: 8px; background: linear-gradient(to right, #ffffff, #fdfbfb); border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.welcome-content { display: flex; align-items: center; gap: 20px; }
.text-info h2 { margin: 0 0 10px 0; font-size: 20px; color: #303133; }
.text-info p { margin: 0; color: #909399; font-size: 14px; }

.quick-actions { border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.card-title { font-weight: bold; font-size: 16px; color: #303133; }

.action-wrapper { display: flex; gap: 15px; }
.action-box {
  flex: 1; height: 120px; border-radius: 8px; display: flex; flex-direction: column;
  justify-content: center; align-items: center; cursor: pointer; transition: all 0.3s;
  color: #fff; gap: 10px;
}
.action-box:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }
.action-icon { font-size: 36px; }
.action-text { font-size: 15px; font-weight: 500; letter-spacing: 1px; }

/* 绚丽的渐变按钮色 */
.in-box { background: linear-gradient(135deg, #67c23a, #85ce61); }
.out-box { background: linear-gradient(135deg, #f56c6c, #f78989); }
.his-box { background: linear-gradient(135deg, #909399, #a6a9ad); }

.stat-card { border-radius: 8px; height: 100%; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.stat-item { padding: 15px 0; text-align: center; }
.stat-label { color: #606266; font-size: 15px; margin-bottom: 10px; }
.stat-value { font-size: 42px; font-weight: bold; }
.text-success { color: #67c23a; }
.text-danger { color: #f56c6c; }
</style>