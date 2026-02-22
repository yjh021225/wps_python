<template>
  <div class="outbound-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">出库作业 (Outbound)</h3>
        <p class="page-desc">请根据出库需求，选择出库商品、源储位及发货数量。系统将自动校验库存是否充足。</p>
      </div>

      <div class="operation-panel">
        <el-form :inline="true" :model="currentItem" class="form-inline">
          <el-form-item label="出库商品" style="width: 250px;">
            <el-select v-model="currentItem.product_id" placeholder="请选择发货商品" filterable>
              <el-option v-for="p in products" :key="p.id" :label="`[${p.code}] ${p.name}`" :value="p.id" />
            </el-select>
          </el-form-item>

          <el-form-item label="源储位" style="width: 250px;">
            <el-select v-model="currentItem.storage_location_id" placeholder="从哪个储位发货" filterable>
              <el-option v-for="l in locations" :key="l.id" :label="`${l.warehouse_name} - ${l.code}`" :value="l.id" />
            </el-select>
          </el-form-item>

          <el-form-item label="扣减数量" style="width: 220px;">
            <el-input-number v-model="currentItem.quantity" :min="1" />
          </el-form-item>

          <el-form-item>
            <el-button type="danger" :icon="Plus" @click="addToList">加入清单</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider border-style="dashed" />

      <div class="list-panel">
        <div class="list-header">
          <h4>待出库明细清单 <el-tag size="small" type="info">{{ outboundList.length }} 项</el-tag></h4>
          <el-button type="danger" :icon="Check" :disabled="outboundList.length === 0" @click="submitOutbound" :loading="submitLoading">
            确认执行出库
          </el-button>
        </div>

        <el-table :data="outboundList" border stripe style="width: 100%; margin-top: 15px;">
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="product_name" label="商品信息" min-width="200" />
          <el-table-column prop="location_name" label="发货源储位" min-width="150" />
          <el-table-column prop="quantity" label="出库数量" width="120" align="center">
            <template #default="scope">
              <el-tag type="danger" effect="dark">- {{ scope.row.quantity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="info" link :icon="Delete" @click="removeFromList(scope.$index)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 20px;" v-if="outboundList.length > 0">
          <el-input v-model="remark" type="textarea" :rows="2" placeholder="可选: 填写发货备注信息（如: 发往华东大区一号店）" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Check } from '@element-plus/icons-vue'
import axios from 'axios'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const products = ref([])
const locations = ref([])
const currentItem = ref({ product_id: null, storage_location_id: null, quantity: 1 })
const outboundList = ref([])
const remark = ref('')
const submitLoading = ref(false)

const loadOptions = async () => {
  try {
    const [prodRes, locRes] = await Promise.all([api.get('products/'), api.get('locations/')])
    products.value = prodRes.data
    locations.value = locRes.data
  } catch (error) {
    ElMessage.error('加载基础数据失败')
  }
}

const addToList = () => {
  if (!currentItem.value.product_id || !currentItem.value.storage_location_id) {
    ElMessage.warning('请完整选择商品和源储位！')
    return
  }

  const product = products.value.find(p => p.id === currentItem.value.product_id)
  const location = locations.value.find(l => l.id === currentItem.value.storage_location_id)

  outboundList.value.push({
    product_id: product.id,
    product_name: `[${product.code}] ${product.name}`,
    storage_location_id: location.id,
    location_name: `${location.warehouse_name} - ${location.code}`,
    quantity: currentItem.value.quantity
  })

  currentItem.value.quantity = 1
  ElMessage.success('已加入发货清单')
}

const removeFromList = (index) => {
  outboundList.value.splice(index, 1)
}

const submitOutbound = () => {
  ElMessageBox.confirm('确认要将清单中的商品执行出库扣减吗？', '高危操作确认', { type: 'warning' })
  .then(async () => {
    submitLoading.value = true
    try {
      const res = await api.post('orders/execute_outbound/', {
        remark: remark.value,
        items: outboundList.value.map(item => ({
          product_id: item.product_id,
          storage_location_id: item.storage_location_id,
          quantity: item.quantity
        }))
      })

      ElMessage.success(`出库成功！发货单号：${res.data.order_no}`)
      outboundList.value = []
      remark.value = ''
      currentItem.value = { product_id: null, storage_location_id: null, quantity: 1 }
    } catch (error) {
      // 捕获后端的库存不足拦截信息并展示
      const errorMsg = error.response?.data?.error || '出库执行失败，请检查网络或后端日志！'
      ElMessage.error({ message: errorMsg, duration: 5000 })
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

onMounted(() => {
  loadOptions()
})
</script>

<style scoped>
.outbound-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }
.operation-panel { background: #fff5f5; padding: 20px 20px 0 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #fde2e2; }
.list-header { display: flex; justify-content: space-between; align-items: center; }
.list-header h4 { margin: 0; color: #303133; }
</style>