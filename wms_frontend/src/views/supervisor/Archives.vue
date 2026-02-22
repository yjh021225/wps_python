<template>
  <div class="archives-container">
    <el-card shadow="never" class="box-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">

        <el-tab-pane label="供应商档案" name="supplier">
          <div class="toolbar">
            <el-button type="primary" :icon="Plus" @click="openDialog('supplier', 'add')">新增供应商</el-button>
            <el-input v-model="searchQuery.supplier" placeholder="搜索供应商名称..." clearable style="width: 250px; margin-left: auto;" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredSupplierData" v-loading="loading.supplier" border stripe>
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="name" label="供应商名称" min-width="180" />
            <el-table-column prop="contact_name" label="联系人" width="120" />
            <el-table-column prop="phone" label="联系电话" width="150" />
            <el-table-column prop="address" label="详细地址" min-width="250" show-overflow-tooltip />
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" link :icon="Edit" @click="openDialog('supplier', 'edit', scope.row)">编辑</el-button>
                <el-button size="small" type="danger" link :icon="Delete" @click="handleDelete('supplier', scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="仓库管理" name="warehouse">
          <div class="toolbar">
            <el-button type="success" :icon="Plus" @click="openDialog('warehouse', 'add')">新增仓库</el-button>
            <el-input v-model="searchQuery.warehouse" placeholder="搜索仓库名称..." clearable style="width: 250px; margin-left: auto;" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredWarehouseData" v-loading="loading.warehouse" border stripe>
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="name" label="仓库名称" min-width="200" />
            <el-table-column prop="location" label="仓库位置/地址" min-width="300" />
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" link :icon="Edit" @click="openDialog('warehouse', 'edit', scope.row)">编辑</el-button>
                <el-button size="small" type="danger" link :icon="Delete" @click="handleDelete('warehouse', scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="储位管理" name="location">
          <div class="toolbar">
            <el-button type="info" :icon="Plus" @click="openDialog('location', 'add')">新增储位</el-button>
            <el-input v-model="searchQuery.location" placeholder="搜索储位编码或仓库..." clearable style="width: 250px; margin-left: auto;" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredLocationData" v-loading="loading.location" border stripe>
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="warehouse_name" label="所属仓库" width="180">
              <template #default="scope">
                <el-tag effect="plain">{{ scope.row.warehouse_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="code" label="储位编码 (如 A-01)" min-width="150" />
            <el-table-column prop="description" label="储位描述" min-width="250" show-overflow-tooltip />
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" link :icon="Edit" @click="openDialog('location', 'edit', scope.row)">编辑</el-button>
                <el-button size="small" type="danger" link :icon="Delete" @click="handleDelete('location', scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="商品分类" name="category">
          <div class="toolbar">
            <el-button type="warning" :icon="Plus" @click="openDialog('category', 'add')">新增分类</el-button>
            <el-input v-model="searchQuery.category" placeholder="搜索分类名称..." clearable style="width: 250px; margin-left: auto;" :prefix-icon="Search" />
          </div>
          <el-table :data="filteredCategoryData" v-loading="loading.category" border stripe>
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="name" label="分类名称" min-width="180" />
            <el-table-column prop="description" label="分类描述" min-width="300" show-overflow-tooltip />
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" link :icon="Edit" @click="openDialog('category', 'edit', scope.row)">编辑</el-button>
                <el-button size="small" type="danger" link :icon="Delete" @click="handleDelete('category', scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="formData" label-width="100px">

        <template v-if="currentModule === 'supplier'">
          <el-form-item label="供应商名称" prop="name" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
            <el-input v-model="formData.name" placeholder="请输入名称" />
          </el-form-item>
          <el-form-item label="联系人"><el-input v-model="formData.contact_name" /></el-form-item>
          <el-form-item label="联系电话"><el-input v-model="formData.phone" /></el-form-item>
          <el-form-item label="详细地址"><el-input v-model="formData.address" type="textarea" /></el-form-item>
        </template>

        <template v-if="currentModule === 'warehouse'">
          <el-form-item label="仓库名称" prop="name" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
            <el-input v-model="formData.name" placeholder="请输入仓库名称" />
          </el-form-item>
          <el-form-item label="仓库位置"><el-input v-model="formData.location" type="textarea" placeholder="请输入具体位置" /></el-form-item>
        </template>

        <template v-if="currentModule === 'location'">
          <el-form-item label="所属仓库" prop="warehouse" :rules="[{ required: true, message: '请选择仓库', trigger: 'change' }]">
            <el-select v-model="formData.warehouse" placeholder="选择归属仓库" style="width: 100%;">
              <el-option v-for="w in rawData.warehouse" :key="w.id" :label="w.name" :value="w.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="储位编码" prop="code" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
            <el-input v-model="formData.code" placeholder="如：A区-01架" />
          </el-form-item>
          <el-form-item label="储位描述"><el-input v-model="formData.description" type="textarea" placeholder="如：常温液体存放区" /></el-form-item>
        </template>

        <template v-if="currentModule === 'category'">
          <el-form-item label="分类名称" prop="name" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
            <el-input v-model="formData.name" placeholder="请输入商品分类名称" />
          </el-form-item>
          <el-form-item label="分类描述"><el-input v-model="formData.description" type="textarea" placeholder="一句话描述该分类" /></el-form-item>
        </template>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

// --- API 配置 ---
const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- 模块映射配置 ---
const moduleConfig = {
  supplier: { endpoint: 'suppliers/', name: '供应商' },
  warehouse: { endpoint: 'warehouses/', name: '仓库' },
  location: { endpoint: 'locations/', name: '储位' }, // 新增的接口映射
  category: { endpoint: 'categories/', name: '分类' }
}

// --- 页面状态 ---
const activeTab = ref('supplier')
const currentModule = ref('supplier')

// 数据容器增加 location
const rawData = reactive({ supplier: [], warehouse: [], location: [], category: [] })
const loading = reactive({ supplier: false, warehouse: false, location: false, category: false })
const searchQuery = reactive({ supplier: '', warehouse: '', location: '', category: '' })

// --- 弹窗状态 ---
const dialogVisible = ref(false)
const dialogType = ref('add')
const submitLoading = ref(false)
const formRef = ref(null)
const formData = ref({})

const dialogTitle = computed(() => {
  const action = dialogType.value === 'add' ? '新增' : '编辑'
  const moduleName = moduleConfig[currentModule.value].name
  return `${action}${moduleName}`
})

// --- 搜索过滤逻辑 ---
const filteredSupplierData = computed(() => rawData.supplier.filter(i => i.name.toLowerCase().includes(searchQuery.supplier.toLowerCase())))
const filteredWarehouseData = computed(() => rawData.warehouse.filter(i => i.name.toLowerCase().includes(searchQuery.warehouse.toLowerCase())))
const filteredCategoryData = computed(() => rawData.category.filter(i => i.name.toLowerCase().includes(searchQuery.category.toLowerCase())))
const filteredLocationData = computed(() => {
  const q = searchQuery.location.toLowerCase()
  return rawData.location.filter(i => i.code.toLowerCase().includes(q) || (i.warehouse_name && i.warehouse_name.toLowerCase().includes(q)))
})

// --- 核心方法 ---

// 1. 获取数据
const fetchData = async (moduleKey) => {
  loading[moduleKey] = true
  try {
    const res = await api.get(moduleConfig[moduleKey].endpoint)
    rawData[moduleKey] = res.data
  } catch (error) {
    ElMessage.error(`获取${moduleConfig[moduleKey].name}数据失败`)
  } finally {
    loading[moduleKey] = false
  }
}

// 2. 切换 Tab 时加载对应数据
const handleTabClick = (tab) => {
  const moduleKey = tab.paneName
  if (rawData[moduleKey].length === 0) {
    fetchData(moduleKey)
  }
}

// 3. 打开弹窗 (合并新增与编辑)
const openDialog = async (moduleKey, type, row = null) => {
  currentModule.value = moduleKey
  dialogType.value = type

  // 智能体验：如果在建储位时，发现仓库列表是空的，自动去拉取一次仓库数据给下拉框用
  if (moduleKey === 'location' && rawData.warehouse.length === 0) {
    await fetchData('warehouse')
  }

  if (type === 'add') {
    formData.value = {}
  } else {
    // 回显数据。特别注意：如果是编辑储位，要把绑定的仓库ID抽出来塞给 formData.warehouse
    formData.value = { ...row }
  }
  dialogVisible.value = true
}

// 4. 删除逻辑
const handleDelete = (moduleKey, row) => {
  const moduleName = moduleConfig[moduleKey].name
  const displayName = row.name || row.code // 储位显示 code，其他显示 name
  ElMessageBox.confirm(`确定删除${moduleName} "${displayName}" 吗？`, '警告', { type: 'warning' })
  .then(async () => {
    try {
      await api.delete(`${moduleConfig[moduleKey].endpoint}${row.id}/`)
      ElMessage.success('删除成功')
      fetchData(moduleKey)
    } catch (error) {
      ElMessage.error('删除失败，可能该数据已被关联使用')
    }
  }).catch(() => {})
}

// 5. 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      const moduleKey = currentModule.value
      const endpoint = moduleConfig[moduleKey].endpoint
      try {
        if (dialogType.value === 'add') {
          await api.post(endpoint, formData.value)
          ElMessage.success('新增成功')
        } else {
          await api.put(`${endpoint}${formData.value.id}/`, formData.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData(moduleKey)
      } catch (error) {
        ElMessage.error('保存失败，请检查名称/编码是否重复')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 初始化默认加载第一个Tab的数据
onMounted(() => {
  fetchData('supplier')
})
</script>

<style scoped>
.archives-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.toolbar { display: flex; align-items: center; margin-bottom: 16px; margin-top: 8px; }
</style>