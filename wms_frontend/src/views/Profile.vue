<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="never" class="box-card">
          <template #header>
            <div class="card-header"><span><el-icon><User /></el-icon> 个人基本信息</span></div>
          </template>
          <div class="avatar-wrapper">
            <el-avatar :size="80" style="background: #409eff; font-size: 30px;">
              {{ userForm.username ? userForm.username.charAt(0).toUpperCase() : 'U' }}
            </el-avatar>
          </div>
          <el-form :model="userForm" label-width="80px" style="margin-top: 30px;">
            <el-form-item label="登录账号">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>
            <el-form-item label="系统角色">
              <el-input v-model="userForm.role_name" disabled />
            </el-form-item>
            <el-form-item label="入职时间">
              <el-input v-model="userForm.date_joined" disabled />
            </el-form-item>
            <el-form-item label="真实姓名">
              <el-input v-model="userForm.real_name" placeholder="请输入您的真实姓名" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saveLoading">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="never" class="box-card">
          <template #header>
            <div class="card-header"><span><el-icon><Lock /></el-icon> 账号安全设置</span></div>
          </template>

          <el-alert title="定期修改密码有助于保护您的账号安全。修改密码后，系统将要求您重新登录。" type="warning" show-icon style="margin-bottom: 20px;" :closable="false" />

          <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px" style="max-width: 400px;">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="pwdForm.old_password" type="password" placeholder="请输入当前密码" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwdForm.new_password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input v-model="pwdForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="updatePassword" :loading="pwdLoading">确认修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/', timeout: 5000 })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- 个人信息逻辑 ---
const saveLoading = ref(false)
const userForm = ref({ username: '', role_name: '', real_name: '', date_joined: '' })

const fetchProfile = async () => {
  try {
    const res = await api.get('users/profile/')
    const data = res.data
    if (data.date_joined) {
      data.date_joined = new Date(data.date_joined).toLocaleDateString()
    }
    userForm.value = data
  } catch (error) {
    ElMessage.error('获取个人信息失败')
  }
}

const saveProfile = async () => {
  saveLoading.value = true
  try {
    const res = await api.put('users/profile/', { real_name: userForm.value.real_name })
    ElMessage.success(res.data.message)
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

// --- 修改密码逻辑 ---
const pwdFormRef = ref(null)
const pwdLoading = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const checkConfirm = (rule, value, callback) => {
  if (value === '') callback(new Error('请再次输入密码'))
  else if (value !== pwdForm.new_password) callback(new Error('两次输入的新密码不一致！'))
  else callback()
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }],
  confirm_password: [{ required: true, validator: checkConfirm, trigger: 'blur' }]
}

const updatePassword = async () => {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (valid) {
      ElMessageBox.confirm('修改密码后需要重新登录，是否继续？', '提示', { type: 'warning' }).then(async () => {
        pwdLoading.value = true
        try {
          const res = await api.post('users/update_password/', pwdForm)
          ElMessage.success(res.data.message)
          localStorage.clear()
          router.push('/login') // 注意：你的登录页如果是 '/' 或者 '/index'，请改成对应的路径
        } catch (error) {
          ElMessage.error(error.response?.data?.error || '修改失败！')
        } finally {
          pwdLoading.value = false
        }
      }).catch(() => {})
    }
  })
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container { height: 100%; padding: 10px; }
.box-card { min-height: 500px; border-radius: 8px; border: none; box-shadow: 0 2px 12px 0 rgba(0,0,0,.05); }
.card-header { font-weight: bold; color: #303133; display: flex; align-items: center; gap: 8px; }
.avatar-wrapper { display: flex; justify-content: center; margin-top: 20px; }
</style>