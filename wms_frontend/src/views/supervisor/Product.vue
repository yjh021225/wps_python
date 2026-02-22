<template>
  <div class="product-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">商品档案与预警设置</h3>
        <p class="page-desc">维护系统内所有流通商品的全局基础信息及库存上下限报警阈值</p>
      </div>

      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增商品</el-button>
        <el-input
          v-model="searchQuery"
          placeholder="搜索商品编码或名称..."
          clearable
          style="width: 300px; margin-left: auto;"
          :prefix-icon="Search"
        />
      </div>

      <el-table :data="filteredTableData" v-loading="loading" border stripe style="width: 100%;">
        <el-table-column prop="code" label="商品编码" width="120" fixed="left" />
        <el-table-column prop="name" label="商品名称" min-width="180" />
        <el-table-column prop="category_name" label="所属分类" width="120">
          <template #default="scope">
            <el-tag size="small" type="info" v-if="scope.row.category_name">{{ scope.row.category_name }}</el-tag>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="默认供应商" min-width="150" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="80" align="center" />
        <el-table-column prop="price" label="单价(元)" width="100" align="right" />

        <el-table-column label="库存预警区间" width="180" align="center">
          <template #default="scope">
            <span class="stock-alert">
              <span class="text-danger">{{ scope.row.min_stock }}</span>
              <span class="divider">~</span>
              <span class="text-success">{{ scope.row.max_stock }}</span>
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link :icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" link :icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      :title="dialogType === 'add' ? '新增商品档案' : '编辑商品档案'"
      v-model="dialogVisible"
      width="650px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="110px" class="custom-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品编码" prop="code">
              <el-input v-model="formData.code" placeholder="如: SKU-1001" :disabled="dialogType === 'edit'" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入商品名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属分类" prop="category">
              <el-select v-model="formData.category" placeholder="请选择商品分类" class="w-100">
                <el-option v-for="item in categoryOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认供应商" prop="supplier">
              <el-select v-model="formData.supplier" placeholder="请选择供应商" class="w-100">
                <el-option v-for="item in supplierOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计量单位" prop="unit">
              <el-input v-model="formData.unit" placeholder="如: 个、件、箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参考单价" prop="price">
              <el-input v-model="formData.price" type="number" placeholder="0.00">
                <template #append>元</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">库存预警规则</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预警下限" prop="min_stock">
              <el-input-number v-model="formData.min_stock" :min="0" class="w-100" />
              <div class="form-tip">低于此数值将触发缺货告警</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预警上限" prop="max_stock">
              <el-input-number v-model="formData.max_stock" :min="1" class="w-100" />
              <div class="form-tip">高于此数值将触发爆仓告警</div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">确定保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

// --- API 配置 ---
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  timeout: 5000
})
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- 状态数据 ---
const loading = ref(false)
const rawData = ref([])
const searchQuery = ref('')

// 下拉框选项数据
const categoryOptions = ref([])
const supplierOptions = ref([])

// --- 弹窗与表单状态 ---
const dialogVisible = ref(false)
const dialogType = ref('add')
const submitLoading = ref(false)
const formRef = ref(null)

const defaultForm = {
  id: null,
  code: '',
  name: '',
  category: null,
  supplier: null,
  unit: '个',
  price: '',
  min_stock: 10,
  max_stock: 1000
}
const formData = ref({ ...defaultForm })

// 表单验证规则
const rules = {
  code: [{ required: true, message: '商品编码不能为空', trigger: 'blur' }],
  name: [{ required: true, message: '商品名称不能为空', trigger: 'blur' }],
  category: [{ required: true, message: '请选择所属分类', trigger: 'change' }],
  min_stock: [{ required: true, message: '必填', trigger: 'blur' }],
  max_stock: [{ required: true, message: '必填', trigger: 'blur' }]
}

// --- 核心方法 ---

// 1. 获取商品列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('products/')
    rawData.value = res.data
  } catch (error) {
    ElMessage.error('获取商品数据失败')
  } finally {
    loading.value = false
  }
}

// 2. 获取下拉框依赖选项 (分类 & 供应商)
const fetchOptions = async () => {
  try {
    const [catRes, supRes] = await Promise.all([
      api.get('categories/'),
      api.get('suppliers/')
    ])
    categoryOptions.value = catRes.data
    supplierOptions.value = supRes.data
  } catch (error) {
    ElMessage.error('加载下拉选项失败')
  }
}

// 3. 搜索过滤
const filteredTableData = computed(() => {
  if (!searchQuery.value) return rawData.value
  const query = searchQuery.value.toLowerCase()
  return rawData.value.filter(item =>
    item.name.toLowerCase().includes(query) ||
    item.code.toLowerCase().includes(query)
  )
})

// 4. 打开新增弹窗
const handleAdd = () => {
  dialogType.value = 'add'
  formData.value = { ...defaultForm }
  dialogVisible.value = true
}

// 5. 打开编辑弹窗
const handleEdit = (row) => {
  dialogType.value = 'edit'
  formData.value = { ...row }
  dialogVisible.value = true
}

// 6. 删除商品
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除商品 "${row.name}" 吗？`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await api.delete(`products/${row.id}/`)
      ElMessage.success('删除成功！')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败，可能该商品已有库存或单据记录')
    }
  }).catch(() => {})
}

// 7. 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (formData.value.min_stock >= formData.value.max_stock) {
        ElMessage.warning('预警下限不能大于或等于预警上限！')
        return
      }

      submitLoading.value = true
      try {
        if (dialogType.value === 'add') {
          await api.post('products/', formData.value)
          ElMessage.success('新增商品成功！')
        } else {
          await api.put(`products/${formData.value.id}/`, formData.value)
          ElMessage.success('更新商品信息成功！')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error('保存失败，请检查商品编码是否重复！')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// --- 初始化 ---
onMounted(() => {
  fetchData()
  fetchOptions() // 加载下拉框数据
})
</script>

<style scoped>
.product-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }

.header-wrapper { margin-bottom: 20px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }

.toolbar { display: flex; align-items: center; margin-bottom: 20px; }
.w-100 { width: 100%; }

.text-gray { color: #909399; }
.text-danger { color: #f56c6c; font-weight: bold; }
.text-success { color: #67c23a; font-weight: bold; }
.divider { margin: 0 8px; color: #dcdfe6; }
.stock-alert { background: #f8f9fa; padding: 4px 12px; border-radius: 12px; font-size: 13px; }

.form-tip { font-size: 12px; color: #909399; margin-top: 4px; line-height: 1.2; }
.custom-form :deep(.el-form-item__label) { font-weight: 500; }
</style>