<template>
  <div class="history-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">个人记录查询 (My History)</h3>
        <p class="page-desc">出于权限隔离要求，此处仅展示由您本人经手处理的出入库单据记录。</p>
      </div>

      <div class="toolbar">
        <el-radio-group v-model="typeFilter" @change="filterData">
          <el-radio-button label="all">全部单据</el-radio-button>
          <el-radio-button label="in">只看入库单</el-radio-button>
          <el-radio-button label="out">只看出库单</el-radio-button>
        </el-radio-group>
        <el-input
          v-model="searchQuery"
          placeholder="搜索单据编号..."
          clearable
          style="width: 250px; margin-left: auto;"
          :prefix-icon="Search"
        />
      </div>

      <el-table ref="historyTableRef" :data="filteredData" v-loading="loading" border stripe style="width: 100%;">

        <el-table-column type="expand" width="50">
          <template #default="props">
            <div class="expand-wrapper">
              <div class="expand-header">
                <el-icon><Tickets /></el-icon> 单据明细清单 (共 {{ props.row.items.length }} 种商品)
              </div>
              <el-table :data="props.row.items" border size="small" style="width: 800px; margin-top: 10px;">
                <el-table-column prop="product_name" label="商品名称" min-width="200" />
                <el-table-column prop="location_code" label="目标/源储位编码" width="150" align="center" />
                <el-table-column prop="quantity" label="操作数量" width="120" align="center">
                  <template #default="scope">
                    <span :class="props.row.order_type === 'in' ? 'text-success' : 'text-danger'" class="bold-num">
                      {{ props.row.order_type === 'in' ? '+' : '-' }}{{ scope.row.quantity }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="单据编号" width="180" />
        <el-table-column prop="order_type" label="单据类型" width="110" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.order_type === 'in' ? 'success' : 'danger'" effect="dark">
              {{ scope.row.order_type === 'in' ? '入库作业' : '出库作业' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="包含商品摘要" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.items && scope.row.items.length > 0">
              【{{ scope.row.items[0].product_name }}】 等 {{ scope.row.items.length }} 项物资
            </span>
            <span v-else class="text-gray">无明细</span>
          </template>
        </el-table-column>

        <el-table-column prop="create_time" label="操作时间" width="180" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注说明" min-width="150" show-overflow-tooltip />

        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="toggleExpand(scope.row)">
              查看明细 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Tickets, ArrowDown } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const username = ref(localStorage.getItem('username') || '操作员')
const loading = ref(false)
const rawData = ref([])
const typeFilter = ref('all')
const searchQuery = ref('')
const historyTableRef = ref(null) // 获取表格实例

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const fetchMyHistory = async () => {
  loading.value = true
  try {
    const res = await api.get('orders/')
    rawData.value = res.data.filter(order => order.operator_username === username.value)
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const filteredData = computed(() => {
  let data = rawData.value
  if (typeFilter.value !== 'all') {
    data = data.filter(item => item.order_type === typeFilter.value)
  }
  if (searchQuery.value) {
    data = data.filter(item => item.order_no.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  return data
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', { hour12: false })
}

// 点击按钮控制展开/折叠行
const toggleExpand = (row) => {
  if (historyTableRef.value) {
    historyTableRef.value.toggleRowExpansion(row)
  }
}

onMounted(() => {
  fetchMyHistory()
})
</script>

<style scoped>
.history-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }

/* 展开行内的样式 */
.expand-wrapper { padding: 15px 40px; background-color: #f4f6f8; border-radius: 4px; box-shadow: inset 0 0 8px rgba(0,0,0,0.02); }
.expand-header { font-weight: bold; color: #409eff; display: flex; align-items: center; gap: 6px; }

.text-gray { color: #909399; }
.bold-num { font-weight: bold; font-size: 15px; }
.text-success { color: #67c23a; }
.text-danger { color: #f56c6c; }
</style>