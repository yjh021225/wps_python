<template>
  <div class="users-container">
    <el-card shadow="never" class="box-card">
      <div class="header-wrapper">
        <h3 class="page-title">系统用户与账户管理</h3>
        <p class="page-desc">管理 WMS 系统内的所有登录账户，分配角色权限及控制账号状态。</p>
      </div>

      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增用户</el-button>
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名或真实姓名..."
          clearable
          style="width: 250px; margin-left: auto;"
          :prefix-icon="Search"
        />
      </div>

      <el-table :data="filteredData" v-loading="loading" border stripe style="width: 100%;">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column label="账户信息" min-width="180">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="32" :style="{ background: getAvatarColor(scope.row.role) }">
                {{ scope.row.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="info-text">
                <span class="username">{{ scope.row.username }}</span>
                <span class="realname">{{ scope.row.real_name || '未填写真实姓名' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role_name" label="系统角色" width="150" align="center">
          <template #default="scope">
            <el-tag :type="getRoleTagType(scope.row.role)" effect="dark">
              {{ scope.row.role_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="账户状态" width="120" align="center">
          <template #default="scope">
            <el-switch
              v-model="scope.row.is_active"
              @change="handleStatusChange(scope.row)"
              :disabled="scope.row.username === currentLoginUser"
            />
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="创建时间" width="180" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link :icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button
              size="small" type="danger" link :icon="Delete"
              @click="handleDelete(scope.row)"
              :disabled="scope.row.username === currentLoginUser"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      :title="dialogType === 'add' ? '新增系统账户' : '编辑系统账户'"
      v-model="dialogVisible"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="formData.username" placeholder="请输入唯一登录账号 (如: zhangsan)" :disabled="dialogType === 'edit'" />
        </el-form-item>

        <el-form-item label="登录密码" prop="password">
          <el-input v-model="formData.password" type="password" placeholder="为空则不修改密码" show-password />
          <div class="form-tip" v-if="dialogType === 'edit'">如不修改密码，请留空</div>
        </el-form-item>

        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="formData.real_name" placeholder="请输入员工真实姓名" />
        </el-form-item>

        <el-form-item label="分配角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择系统角色" class="w-100">
            <el-option label="系统管理员 (最高权限)" value="admin" />
            <el-option label="仓库管理员 (全局基础数据)" value="supervisor" />
            <el-option label="普通查询员 (出入库作业)" value="operator" />
          </el-select>
        </el-form-item>
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
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 当前登录用户（防止自己把自己删了或禁用了）
const currentLoginUser = localStorage.getItem('username')

const loading = ref(false)
const rawData = ref([])
const searchQuery = ref('')

// 弹窗表单控制
const dialogVisible = ref(false)
const dialogType = ref('add')
const submitLoading = ref(false)
const formRef = ref(null)

const defaultForm = { id: null, username: '', password: '', real_name: '', role: 'operator', is_active: true }
const formData = ref({ ...defaultForm })

// 密码如果是新增则必填，修改则非必填
const rules = computed(() => ({
  username: [{ required: true, message: '账号不能为空', trigger: 'blur' }],
  password: [{ required: dialogType.value === 'add', message: '新增账号时密码必填', trigger: 'blur' }],
  role: [{ required: true, message: '请分配角色', trigger: 'change' }]
}))

// --- 数据拉取 ---
const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('users/')
    rawData.value = res.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// --- 搜索过滤 ---
const filteredData = computed(() => {
  if (!searchQuery.value) return rawData.value
  const query = searchQuery.value.toLowerCase()
  return rawData.value.filter(item =>
    item.username.toLowerCase().includes(query) ||
    (item.real_name && item.real_name.toLowerCase().includes(query))
  )
})

// --- 样式辅助函数 ---
const getRoleTagType = (role) => {
  const map = { 'admin': 'danger', 'supervisor': 'success', 'operator': 'warning' }
  return map[role] || 'info'
}
const getAvatarColor = (role) => {
  const map = { 'admin': '#f56c6c', 'supervisor': '#67c23a', 'operator': '#e6a23c' }
  return map[role] || '#909399'
}
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', { hour12: false })
}

// --- 操作事件 ---
const handleAdd = () => {
  dialogType.value = 'add'
  formData.value = { ...defaultForm }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  formData.value = { ...row, password: '' } // 密码不回显
  dialogVisible.value = true
}

// 快捷更改状态（启用/停用）
const handleStatusChange = async (row) => {
  try {
    await api.put(`users/${row.id}/`, { ...row })
    ElMessage.success(`已${row.is_active ? '启用' : '停用'}账号: ${row.username}`)
  } catch (error) {
    row.is_active = !row.is_active // 失败则恢复开关状态
    ElMessage.error('状态更新失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除账户 "${row.username}" 吗？删除后该员工将无法登录。`, '高危操作警告', { type: 'warning' })
  .then(async () => {
    try {
      await api.delete(`users/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败，可能该账户已有绑定的业务单据')
    }
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (dialogType.value === 'add') {
          await api.post('users/', formData.value)
          ElMessage.success('账户创建成功')
        } else {
          await api.put(`users/${formData.value.id}/`, formData.value)
          ElMessage.success('账户信息更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error('保存失败，请检查账号是否已被注册！')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => fetchData())
</script>

<style scoped>
.users-container { height: 100%; }
.box-card { min-height: calc(100vh - 110px); border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.header-wrapper { margin-bottom: 25px; }
.page-title { margin: 0 0 8px 0; font-size: 18px; color: #303133; }
.page-desc { margin: 0; font-size: 13px; color: #909399; }
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }

.user-info { display: flex; align-items: center; gap: 12px; }
.info-text { display: flex; flex-direction: column; }
.username { font-weight: bold; color: #303133; font-size: 14px; }
.realname { color: #909399; font-size: 12px; }

.w-100 { width: 100%; }
.form-tip { font-size: 12px; color: #909399; margin-top: 4px; line-height: 1.2; }
</style>