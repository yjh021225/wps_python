<template>
  <div class="login-wrapper">
    <el-card class="login-card" shadow="always">
      <div class="login-header">
        <h2 class="sys-name">WMS 仓储管理系统</h2>
        <p class="sys-desc">企业级智能仓储控制平台</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入账号 (测试填: admin / super / opt)"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码 (测试阶段随便填)"
            show-password
            clearable
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '身份验证中...' : '立即登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = reactive({
  username: [{ required: true, message: '账号不能为空', trigger: 'blur' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' }]
})

const handleLogin = () => {
  if (!loginFormRef.value) return

  loginFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true

      // 真实请求 Django 后端接口
      axios.post('http://127.0.0.1:8000/api/login/', {
        username: loginForm.username,
        password: loginForm.password
      })
      .then(res => {
        // 从后端响应中解构出数据
        const { access, role, username } = res.data

        // 将 Token 和 角色 存入浏览器的 localStorage
        localStorage.setItem('token', access)
        localStorage.setItem('role', role)
        localStorage.setItem('username', username)

        ElMessage.success(`登录成功，欢迎回来：${username}`)

        // 根据真实的 role 进行智能跳转
        if (role === 'admin') {
          router.push('/admin')
        } else if (role === 'supervisor') {
          router.push('/supervisor')
        } else {
          router.push('/operator')
        }
      })
      .catch(err => {
        console.error(err)
        ElMessage.error('账号或密码错误，请检查！')
      })
      .finally(() => {
        loading.value = false
      })
    } else {
      return false
    }
  })
}
</script>

<style scoped>
/* 充满屏幕的深色渐变背景，体现企业级科技感 */
.login-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #001529 0%, #003a70 100%);
}

/* 居中的白色登录卡片 */
.login-card {
  width: 420px;
  padding: 20px 20px 10px 20px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  border: none;
}

/* 标题样式 */
.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.sys-name {
  margin: 0;
  font-size: 26px;
  color: #303133;
  letter-spacing: 1px;
}

.sys-desc {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #909399;
  letter-spacing: 2px;
}

/* 按钮样式撑满 */
.login-btn {
  width: 100%;
  font-size: 16px;
  letter-spacing: 4px;
  margin-top: 10px;
  background-color: #1890ff;
  border-color: #1890ff;
}

.login-btn:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}
</style>