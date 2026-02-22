<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="panel-group">
      <el-col :span="6">
        <el-card shadow="hover" class="card-panel">
          <div class="card-panel-icon-wrapper icon-blue">
            <el-icon><Box /></el-icon>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">在库商品总数</div>
            <div class="card-panel-num">{{ stats.totalInventory }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="card-panel">
          <div class="card-panel-icon-wrapper icon-green">
            <el-icon><Money /></el-icon>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">库存预估总价值(元)</div>
            <div class="card-panel-num">{{ stats.totalValue.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="card-panel">
          <div class="card-panel-icon-wrapper icon-orange">
            <el-icon><Document /></el-icon>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">本月单据流转数</div>
            <div class="card-panel-num">{{ stats.monthlyOrders }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="card-panel">
          <div class="card-panel-icon-wrapper icon-red">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">触发库存预警数</div>
            <div class="card-panel-num">{{ stats.alertCount }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> 近7天出入库业务趋势</span>
            </div>
          </template>
          <div ref="lineChartRef" style="height: 350px; width: 100%;"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><PieChart /></el-icon> 各分类库存量占比</span>
            </div>
          </template>
          <div ref="pieChartRef" style="height: 350px; width: 100%;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Box, Money, Document, Warning, TrendCharts, PieChart } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// --- API 配置 ---
const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- 状态数据 ---
const stats = reactive({
  totalInventory: 0,
  totalValue: 0,
  monthlyOrders: 0,
  alertCount: 0
})

const lineChartRef = ref(null)
const pieChartRef = ref(null)

// --- 核心拉取与计算逻辑 ---
const fetchDashboardData = async () => {
  try {
    // 1. 并发拉取后端数据
    const [invRes, orderRes, prodRes] = await Promise.all([
      api.get('inventories/'),
      api.get('orders/'),
      api.get('products/')
    ])

    const inventories = invRes.data
    const orders = orderRes.data
    const products = prodRes.data

    // 2. 计算核心统计指标
    let totalInv = 0
    let totalVal = 0

    // 建立商品价格和分类字典，方便快速查找
    const productMap = {}
    products.forEach(p => { productMap[p.id] = p })

    // 计算库存总量和总价值
    inventories.forEach(inv => {
      totalInv += inv.quantity
      const prod = productMap[inv.product]
      if (prod) {
        totalVal += inv.quantity * parseFloat(prod.price)
      }
    })

    // 计算预警数 (库存低于下限)
    let alerts = 0
    products.forEach(p => {
      const pInv = inventories.filter(i => i.product === p.id).reduce((sum, i) => sum + i.quantity, 0)
      if (pInv < p.min_stock || pInv > p.max_stock) alerts++
    })

    stats.totalInventory = totalInv
    stats.totalValue = totalVal
    stats.monthlyOrders = orders.length // 简易处理：展示所有单据数作为本月数据
    stats.alertCount = alerts

    // 3. 渲染图表
    renderCharts(orders, inventories, productMap)

  } catch (error) {
    console.error('获取驾驶舱数据失败:', error)
  }
}

// --- 渲染图表 ---
const renderCharts = (orders, inventories, productMap) => {
  // 准备折线图数据 (提取近7天的日期)
  const days = []
  const inData = [0, 0, 0, 0, 0, 0, 0]
  const outData = [0, 0, 0, 0, 0, 0, 0]

  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }

  // 简易逻辑：将单据按天统计放入数组 (实际生产中这里由后端聚合返回)
  orders.forEach(order => {
    const d = new Date(order.create_time)
    const dateStr = `${d.getMonth() + 1}/${d.getDate()}`
    const index = days.indexOf(dateStr)
    if (index !== -1) {
      if (order.order_type === 'in') inData[index]++
      else outData[index]++
    }
  })

  // 准备饼图数据 (按分类汇总库存)
  const categoryCount = {}
  inventories.forEach(inv => {
    const prod = productMap[inv.product]
    if (prod && prod.category_name) {
      categoryCount[prod.category_name] = (categoryCount[prod.category_name] || 0) + inv.quantity
    }
  })
  const pieData = Object.keys(categoryCount).map(key => ({
    name: key,
    value: categoryCount[key]
  }))

  // 渲染 ECharts
  nextTick(() => {
    // 1. 折线图
    const lineChart = echarts.init(lineChartRef.value)
    lineChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['入库单数', '出库单数'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: days },
      yAxis: { type: 'value', minInterval: 1 },
      series: [
        { name: '入库单数', type: 'line', smooth: true, data: inData, itemStyle: { color: '#67c23a' }, areaStyle: { color: 'rgba(103,194,58,0.1)' } },
        { name: '出库单数', type: 'line', smooth: true, data: outData, itemStyle: { color: '#f56c6c' }, areaStyle: { color: 'rgba(245,108,108,0.1)' } }
      ]
    })

    // 2. 饼图
    const pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b} : {c} ({d}%)' },
      legend: { bottom: '0%', left: 'center' },
      series: [
        {
          name: '库存占比',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false, position: 'center' },
          emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
          labelLine: { show: false },
          data: pieData.length > 0 ? pieData : [{ name: '暂无数据', value: 0 }]
        }
      ]
    })

    // 监听窗口大小改变，自适应图表
    window.addEventListener('resize', () => {
      lineChart.resize()
      pieChart.resize()
    })
  })
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container { padding: 5px; }

/* 顶部卡片样式 */
.card-panel { height: 108px; cursor: pointer; border-radius: 8px; border: none; }
.card-panel:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important; transform: translateY(-2px); transition: all 0.3s; }
.card-panel :deep(.el-card__body) { padding: 20px; display: flex; align-items: center; justify-content: space-between; }

.card-panel-icon-wrapper {
  width: 60px; height: 60px; border-radius: 12px;
  display: flex; justify-content: center; align-items: center; font-size: 32px;
}
.icon-blue { color: #40c9c6; background: #e6f7f7; }
.icon-green { color: #36a3f7; background: #e1f0fe; }
.icon-orange { color: #f4516c; background: #fde8eb; }
.icon-red { color: #ffb980; background: #fff4ec; }

.card-panel-description { text-align: right; }
.card-panel-text { color: #8c8c8c; font-size: 14px; margin-bottom: 8px; font-weight: 500; }
.card-panel-num { color: #303133; font-size: 24px; font-weight: bold; }

/* 图表卡片样式 */
.chart-card { border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.card-header { display: flex; align-items: center; font-weight: bold; color: #303133; font-size: 16px; gap: 8px; }
</style>