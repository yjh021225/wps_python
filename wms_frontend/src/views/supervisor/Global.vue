<template>
  <div class="global-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">全局库存监控</h3>
        <p class="page-desc">实时监控各个仓库、储位的商品库存余量，掌握全局物资分布状态</p>
      </div>

      <div class="toolbar">
        <el-button type="primary" :icon="Refresh" @click="fetchData">刷新数据</el-button>
        <el-input
          v-model="searchQuery"
          placeholder="搜索商品名称或编码..."
          clearable
          style="width: 300px; margin-left: auto;"
          :prefix-icon="Search"
        />
      </div>

      <el-table :data="filteredTableData" v-loading="loading" border stripe style="width: 100%;">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="product_code" label="商品编码" width="150" />
        <el-table-column prop="product_name" label="商品名称" min-width="200" />
        <el-table-column label="所在储位" min-width="200" align="center">
          <template #default="scope">
            <el-tag type="info" effect="plain" size="default">
              {{ scope.row.warehouse_name }} - {{ scope.row.location_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="当前库存量" width="150" align="center">
          <template #default="scope">
            <span
              class="stock-num"
              :class="{
                'text-danger': scope.row.quantity < scope.row.min_stock,
                'text-warning': scope.row.quantity > scope.row.max_stock,
                'text-success': scope.row.quantity >= scope.row.min_stock && scope.row.quantity <= scope.row.max_stock
              }"
            >
              {{ scope.row.quantity }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="健康状态" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.quantity < scope.row.min_stock" type="danger" effect="dark">缺货预警</el-tag>
            <el-tag v-else-if="scope.row.quantity > scope.row.max_stock" type="warning" effect="dark">爆仓预警</el-tag>
            <el-tag v-else type="success" effect="plain">库存健康</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后变动时间" min-width="180">
          <template #default="scope">
            <div class="time-text"><el-icon><Clock /></el-icon> {{ formatDate(scope.row.last_update) }}</div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search, Clock } from '@element-plus/icons-vue'
import axios from 'axios'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const loading = ref(false)
const rawData = ref([])
const searchQuery = ref('')

// 1. 获取库存数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('inventories/')
    rawData.value = res.data
  } catch (error) {
    ElMessage.error('获取库存数据失败！')
  } finally {
    loading.value = false
  }
}

// 2. 搜索过滤
const filteredTableData = computed(() => {
  if (!searchQuery.value) return rawData.value
  const query = searchQuery.value.toLowerCase()
  return rawData.value.filter(item =>
    item.product_name.toLowerCase().includes(query) ||
    item.product_code.toLowerCase().includes(query)
  )
})

// 3. 格式化时间显示
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.global-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }

.stock-num { font-size: 18px; font-weight: bold; }
.text-success { color: #67c23a; }
.text-danger { color: #f56c6c; }
.time-text { display: flex; align-items: center; gap: 6px; color: #606266; }
</style>