<template>
  <div class="logs-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">系统安全审计日志</h3>
        <p class="page-desc">全量记录系统内所有人员的物资流转操作。审计日志具备最高安全级别，强制为只读权限，任何人都无法篡改或删除。</p>
      </div>

      <div class="toolbar">
        <el-select v-model="filterType" placeholder="所有动作类型" clearable style="width: 150px; margin-right: 15px;">
          <el-option label="入库操作" value="in" />
          <el-option label="出库操作" value="out" />
        </el-select>

        <el-input
          v-model="searchQuery"
          placeholder="搜索操作人账号 / 关联单据号..."
          clearable
          style="width: 300px;"
          :prefix-icon="Search"
        />
      </div>

      <el-table :data="filteredLogs" v-loading="loading" border stripe style="width: 100%;">
        <el-table-column type="index" label="溯源流水号" width="100" align="center" />

        <el-table-column label="操作人" width="150" align="center">
          <template #default="scope">
            <el-tag size="small" type="info" effect="plain" class="operator-tag">
              <el-icon><User /></el-icon> {{ scope.row.operator_username }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="动作类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.order_type === 'in' ? 'success' : 'danger'" effect="dark">
              {{ scope.row.order_type === 'in' ? '执行入库' : '执行出库' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="关联操作单据" width="220" />

        <el-table-column label="影响物资明细" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.items && scope.row.items.length > 0">
              共操作 {{ scope.row.items.length }} 种物资 (如: {{ scope.row.items[0].product_name }} 等)
            </span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>

        <el-table-column label="服务器记录时间" width="200" align="center">
          <template #default="scope">
            <div class="time-text">
              <el-icon><Clock /></el-icon> {{ formatDate(scope.row.create_time) }}
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, User, Clock } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const loading = ref(false)
const rawLogs = ref([])
const filterType = ref('')
const searchQuery = ref('')

// 获取所有日志 (借用单据表获取全量操作记录)
const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await api.get('orders/')
    rawLogs.value = res.data // 管理员视角，不需要过滤 operator_name，直接看全量
  } catch (error) {
    ElMessage.error('获取审计日志失败！')
  } finally {
    loading.value = false
  }
}

// 综合过滤
const filteredLogs = computed(() => {
  let data = rawLogs.value

  // 按动作类型过滤
  if (filterType.value) {
    data = data.filter(log => log.order_type === filterType.value)
  }

  // 按操作人或单据号搜索
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    data = data.filter(log =>
      log.operator_username.toLowerCase().includes(q) ||
      log.order_no.toLowerCase().includes(q)
    )
  }

  return data
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-container { height: 100%; padding: 5px; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #f56c6c; font-weight: 500; } /* 红色提示彰显安全性 */
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }

.operator-tag { display: flex; align-items: center; gap: 5px; justify-content: center; }
.time-text { display: flex; align-items: center; justify-content: center; gap: 6px; color: #606266; font-family: monospace; }
.text-gray { color: #909399; }
</style>