<template>
  <div class="admin-dashboard-container">
    <div class="header-wrapper">
      <h3 class="page-title">系统运维监控看板</h3>
      <p class="page-desc">全站业务数据统计与全局流转趋势可视化监控。</p>
    </div>

    <div class="top-cards-wrapper">
      <el-card shadow="hover" class="data-card user-card">
        <div class="card-icon"><el-icon><User /></el-icon></div>
        <div class="card-info">
          <div class="card-title">用户总数</div>
          <div class="card-value">{{ stats.totalUsers }} <span class="unit">人</span></div>
        </div>
      </el-card>

      <el-card shadow="hover" class="data-card product-card">
        <div class="card-icon"><el-icon><Box /></el-icon></div>
        <div class="card-info">
          <div class="card-title">商品总数</div>
          <div class="card-value">{{ stats.totalProducts }} <span class="unit">种</span></div>
        </div>
      </el-card>

      <el-card shadow="hover" class="data-card inv-card">
        <div class="card-icon"><el-icon><TakeawayBox /></el-icon></div>
        <div class="card-info">
          <div class="card-title">当前库存总量</div>
          <div class="card-value">{{ stats.totalInventory }} <span class="unit">件</span></div>
        </div>
      </el-card>

      <el-card shadow="hover" class="data-card in-card">
        <div class="card-icon"><el-icon><Download /></el-icon></div>
        <div class="card-info">
          <div class="card-title">今日入库次数</div>
          <div class="card-value">{{ stats.todayInbound }} <span class="unit">次</span></div>
        </div>
      </el-card>

      <el-card shadow="hover" class="data-card out-card">
        <div class="card-icon"><el-icon><Upload /></el-icon></div>
        <div class="card-info">
          <div class="card-title">今日出库次数</div>
          <div class="card-value">{{ stats.todayOutbound }} <span class="unit">次</span></div>
        </div>
      </el-card>
    </div>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <div ref="inboundChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <div ref="outboundChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <div ref="trendChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { User, Box, TakeawayBox, Download, Upload } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 数据统计容器
const stats = reactive({
  totalUsers: 0,
  totalProducts: 0,
  totalInventory: 0,
  todayInbound: 0,
  todayOutbound: 0
})

// 图表 DOM 引用
const inboundChartRef = ref(null)
const outboundChartRef = ref(null)
const pieChartRef = ref(null)
const trendChartRef = ref(null)

// 拉取所有数据并计算
const fetchAndRenderData = async () => {
  try {
    // 1. 并发拉取四个维度的全量数据
    const [userRes, prodRes, invRes, orderRes] = await Promise.all([
      api.get('users/'),
      api.get('products/'),
      api.get('inventories/'),
      api.get('orders/')
    ])

    const users = userRes.data
    const products = prodRes.data
    const inventories = invRes.data
    const orders = orderRes.data

    // ================= 计算 1.1 数据统计 =================
    const todayStr = new Date().toLocaleDateString()

    stats.totalUsers = users.length
    stats.totalProducts = products.length
    stats.totalInventory = inventories.reduce((sum, item) => sum + item.quantity, 0)

    const todayOrders = orders.filter(o => new Date(o.create_time).toLocaleDateString() === todayStr)
    stats.todayInbound = todayOrders.filter(o => o.order_type === 'in').length
    stats.todayOutbound = todayOrders.filter(o => o.order_type === 'out').length

    // ================= 准备 1.2 图表数据 =================
    // 生成近7天的日期刻度
    const days = []
    const inCountData = [0, 0, 0, 0, 0, 0, 0]
    const outCountData = [0, 0, 0, 0, 0, 0, 0]

    for (let i = 6; i >= 0; i--) {
      const d = new Date()
      d.setDate(d.getDate() - i)
      days.push(`${d.getMonth() + 1}/${d.getDate()}`)
    }

    // 统计近7天每天的出入库次数
    orders.forEach(order => {
      const d = new Date(order.create_time)
      const dateStr = `${d.getMonth() + 1}/${d.getDate()}`
      const index = days.indexOf(dateStr)
      if (index !== -1) {
        if (order.order_type === 'in') inCountData[index]++
        else outCountData[index]++
      }
    })

    // 准备饼图数据 (分类库存占比)
    const categoryCount = {}
    // 为了拿分类名称，我们建个商品字典
    const productMap = {}
    products.forEach(p => productMap[p.id] = p)

    inventories.forEach(inv => {
      const prod = productMap[inv.product]
      if (prod && prod.category_name) {
        categoryCount[prod.category_name] = (categoryCount[prod.category_name] || 0) + inv.quantity
      }
    })
    const pieData = Object.keys(categoryCount).map(key => ({ name: key, value: categoryCount[key] }))

    // ================= 渲染 ECharts 图表 =================
    nextTick(() => {
      // 图1：入库趋势
      const inChart = echarts.init(inboundChartRef.value)
      inChart.setOption({
        title: { text: '近7天入库频次趋势', left: 'center', textStyle: { fontSize: 15 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: days, boundaryGap: false },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{ name: '入库次数', type: 'line', data: inCountData, smooth: true, itemStyle: { color: '#67c23a' }, areaStyle: { color: 'rgba(103,194,58,0.2)' } }]
      })

      // 图2：出库趋势
      const outChart = echarts.init(outboundChartRef.value)
      outChart.setOption({
        title: { text: '近7天出库频次趋势', left: 'center', textStyle: { fontSize: 15 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: days, boundaryGap: false },
        yAxis: { type: 'value', minInterval: 1 },
        series: [{ name: '出库次数', type: 'line', data: outCountData, smooth: true, itemStyle: { color: '#f56c6c' }, areaStyle: { color: 'rgba(245,108,108,0.2)' } }]
      })

      // 图3：库存占比饼图
      const pieChart = echarts.init(pieChartRef.value)
      pieChart.setOption({
        title: { text: '各商品分类库存占比', left: 'center', textStyle: { fontSize: 15 } },
        tooltip: { trigger: 'item', formatter: '{b} : {c}件 ({d}%)' },
        legend: { bottom: '0%', left: 'center' },
        series: [{ type: 'pie', radius: '55%', center: ['50%', '50%'], data: pieData.length ? pieData : [{name: '暂无', value: 0}], emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } } }]
      })

      // 图4：综合操作趋势 (柱状图对比)
      const trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        title: { text: '近7天总体操作频次对比', left: 'center', textStyle: { fontSize: 15 } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { bottom: '0%', data: ['入库操作', '出库操作'] },
        xAxis: { type: 'category', data: days },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
          { name: '入库操作', type: 'bar', data: inCountData, itemStyle: { color: '#67c23a' } },
          { name: '出库操作', type: 'bar', data: outCountData, itemStyle: { color: '#f56c6c' } }
        ]
      })

      // 窗口缩放自适应
      window.addEventListener('resize', () => {
        inChart.resize(); outChart.resize(); pieChart.resize(); trendChart.resize()
      })
    })

  } catch (error) {
    ElMessage.error('获取监控数据失败！')
  }
}

onMounted(() => {
  fetchAndRenderData()
})
</script>

<style scoped>
.admin-dashboard-container { padding: 5px; height: 100%; }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }

/* 顶部 5 个卡片的 Flex 布局 */
.top-cards-wrapper { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; }
.data-card { flex: 1; border-radius: 8px; border: none; }
.data-card :deep(.el-card__body) { padding: 20px; display: flex; align-items: center; gap: 15px; }

.card-icon { width: 50px; height: 50px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 26px; color: #fff; }
.user-card .card-icon { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }
.product-card .card-icon { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
.inv-card .card-icon { background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%); }
.in-card .card-icon { background: linear-gradient(135deg, #67c23a 0%, #a0c989 100%); }
.out-card .card-icon { background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%); }

.card-info { flex: 1; }
.card-title { font-size: 13px; color: #909399; margin-bottom: 5px; }
.card-value { font-size: 24px; font-weight: bold; color: #303133; line-height: 1; }
.unit { font-size: 12px; font-weight: normal; color: #909399; }

/* 图表区域 */
.chart-row { margin-bottom: 20px; }
.chart-card { border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.chart-box { height: 320px; width: 100%; padding-top: 10px; }
</style>