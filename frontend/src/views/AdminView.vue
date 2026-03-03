<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-4">
        <router-link to="/" class="text-gray-400 hover:text-white transition-colors text-sm">← 主页</router-link>
        <h1 class="text-white font-semibold">管理后台</h1>
      </div>
      <span class="text-sm text-gray-400">@{{ auth.user?.username }}</span>
    </header>

    <div class="flex-1 overflow-auto p-6 space-y-8">

      <!-- ── Pending users ── -->
      <section>
        <h2 class="text-base font-semibold mb-3 flex items-center gap-2">
          待审批用户
          <span v-if="pendingUsers.length" class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">{{ pendingUsers.length }}</span>
        </h2>
        <div v-if="pendingUsers.length === 0" class="text-sm text-gray-500 py-4">没有等待审批的用户</div>
        <div class="flex flex-wrap gap-3">
          <div v-for="u in pendingUsers" :key="u.id" class="card px-4 py-3 flex items-center gap-4">
            <div>
              <p class="font-medium">{{ u.username }}</p>
              <p class="text-xs text-gray-500">注册于 {{ fmtDate(u.created_at) }}</p>
            </div>
            <div class="flex gap-2">
              <button class="btn-primary text-xs py-1 px-3" @click="approveUser(u.id)">批准</button>
              <button class="btn-danger text-xs py-1 px-3" @click="confirmDeleteUser(u)">拒绝/删除</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── All users ── -->
      <section>
        <h2 class="text-base font-semibold mb-3">所有用户</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="text-left text-gray-400 border-b border-gray-800">
                <th class="py-2 pr-4 font-medium">ID</th>
                <th class="py-2 pr-4 font-medium">用户名</th>
                <th class="py-2 pr-4 font-medium">状态</th>
                <th class="py-2 pr-4 font-medium">权限</th>
                <th class="py-2 pr-4 font-medium">注册时间</th>
                <th class="py-2 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in approvedUsers" :key="u.id"
                class="border-b border-gray-800/50 hover:bg-white/[0.02]"
              >
                <td class="py-2 pr-4 text-gray-400">{{ u.id }}</td>
                <td class="py-2 pr-4 font-medium">
                  {{ u.username }}
                  <span v-if="u.id === auth.user?.id" class="text-xs text-gray-500 ml-1">(你)</span>
                </td>
                <td class="py-2 pr-4">
                  <span class="tag-done">已批准</span>
                </td>
                <td class="py-2 pr-4">
                  <span v-if="u.is_super_admin" class="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30">超管</span>
                  <span v-else-if="u.is_admin" class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">管理员</span>
                  <span v-else class="text-gray-500 text-xs">普通用户</span>
                </td>
                <td class="py-2 pr-4 text-gray-400 whitespace-nowrap">{{ fmtDate(u.created_at) }}</td>
                <td class="py-2">
                  <div class="flex gap-2 flex-wrap" v-if="!u.is_super_admin">
                    <button
                      v-if="auth.isSuperAdmin"
                      class="text-xs px-2 py-1 rounded border border-indigo-500/40 text-indigo-400 hover:bg-indigo-500/20 transition-colors"
                      @click="toggleAdmin(u)"
                    >{{ u.is_admin ? '撤销管理员' : '设为管理员' }}</button>
                    <button
                      class="text-xs px-2 py-1 rounded border border-gray-600 text-gray-400 hover:bg-white/10 transition-colors"
                      @click="openChangePwd(u)"
                    >改密码</button>
                    <button
                      v-if="u.id !== auth.user?.id"
                      class="text-xs px-2 py-1 rounded border border-red-700/40 text-red-400 hover:bg-red-500/20 transition-colors"
                      @click="confirmDeleteUser(u)"
                    >删除</button>
                  </div>
                </td>
              </tr>
              <tr v-if="approvedUsers.length === 0">
                <td colspan="6" class="py-6 text-center text-gray-500">暂无用户</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ── All images ── -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold">所有投稿记录</h2>
          <button class="btn-ghost text-sm py-1" @click="loadImages">刷新</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="text-left text-gray-400 border-b border-gray-800">
                <th class="py-2 pr-4 font-medium">ID</th>
                <th class="py-2 pr-4 font-medium">标题</th>
                <th class="py-2 pr-4 font-medium">提交者</th>
                <th class="py-2 pr-4 font-medium">P图</th>
                <th class="py-2 pr-4 font-medium">状态</th>
                <th class="py-2 pr-4 font-medium">提交时间</th>
                <th class="py-2 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="img in adminImages" :key="img.id"
                class="border-b border-gray-800/50 hover:bg-white/[0.02]"
              >
                <td class="py-2 pr-4 text-gray-400">{{ img.id }}</td>
                <td class="py-2 pr-4 max-w-[160px] truncate" :title="img.title">{{ img.title }}</td>
                <td class="py-2 pr-4 text-indigo-400">@{{ img.username }}</td>
                <td class="py-2 pr-4">
                  <a v-if="img.processed_path" :href="`/uploads/${img.processed_path}`" target="_blank">
                    <img :src="`/uploads/${img.processed_path}`" class="h-12 w-16 object-cover rounded hover:opacity-80" />
                  </a>
                  <span v-else class="text-gray-600">—</span>
                </td>
                <td class="py-2 pr-4">
                  <span :class="img.is_placeholder ? 'tag-placeholder' : 'tag-done'">
                    {{ img.is_placeholder ? '占坑中' : '已完成' }}
                  </span>
                </td>
                <td class="py-2 pr-4 text-gray-400 whitespace-nowrap">{{ fmtDate(img.created_at) }}</td>
                <td class="py-2">
                  <button class="btn-danger text-xs py-1 px-2" @click="confirmDeleteImage(img)">删除</button>
                </td>
              </tr>
              <tr v-if="adminImages.length === 0">
                <td colspan="7" class="py-6 text-center text-gray-500">暂无投稿</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>

  <!-- ── Change password modal ── -->
  <div v-if="pwdTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="card w-full max-w-sm p-6 space-y-4">
      <h3 class="font-semibold">修改密码 — {{ pwdTarget.username }}</h3>
      <input v-model="newPwd" class="input" type="password" placeholder="新密码（至少6位）" />
      <p v-if="pwdError" class="text-red-400 text-sm">{{ pwdError }}</p>
      <div class="flex gap-3">
        <button class="btn-ghost flex-1" @click="pwdTarget = null">取消</button>
        <button class="btn-primary flex-1" :disabled="pwdLoading" @click="doChangePwd">
          {{ pwdLoading ? '保存中…' : '保存' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Delete user confirm ── -->
  <div v-if="deleteUserTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="card w-full max-w-sm p-6 space-y-4 text-center">
      <p class="text-gray-200">确定要删除用户「<span class="font-semibold">{{ deleteUserTarget.username }}</span>」吗？</p>
      <p class="text-sm text-gray-500">该用户的所有投稿也会一并删除，此操作不可撤销。</p>
      <div class="flex gap-3">
        <button class="btn-ghost flex-1" @click="deleteUserTarget = null">取消</button>
        <button class="btn-danger flex-1" :disabled="deleteLoading" @click="doDeleteUser">
          {{ deleteLoading ? '删除中…' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Delete image confirm ── -->
  <div v-if="deleteImageTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="card w-full max-w-sm p-6 space-y-4 text-center">
      <p class="text-gray-200">确定要删除投稿「<span class="font-semibold">{{ deleteImageTarget.title }}</span>」吗？</p>
      <div class="flex gap-3">
        <button class="btn-ghost flex-1" @click="deleteImageTarget = null">取消</button>
        <button class="btn-danger flex-1" :disabled="deleteLoading" @click="doDeleteImage">
          {{ deleteLoading ? '删除中…' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'
import { hashPassword } from '../api/crypto.js'

const auth = useAuthStore()

// ── Data ──────────────────────────────────────────────────────────────────
const allUsers = ref([])
const adminImages = ref([])

const pendingUsers  = computed(() => allUsers.value.filter(u => !u.is_approved))
const approvedUsers = computed(() => allUsers.value.filter(u => u.is_approved))

async function loadUsers()  { try { allUsers.value   = await api.get('/admin/users')  } catch {} }
async function loadImages() { try { adminImages.value = await api.get('/admin/images') } catch {} }

// ── User actions ──────────────────────────────────────────────────────────
async function approveUser(id) {
  await api.put(`/admin/users/${id}/approve`)
  loadUsers()
}

async function toggleAdmin(u) {
  await api.put(`/admin/users/${u.id}/toggle-admin`)
  loadUsers()
}

// Change password
const pwdTarget = ref(null)
const newPwd    = ref('')
const pwdError  = ref('')
const pwdLoading = ref(false)

function openChangePwd(u) { pwdTarget.value = u; newPwd.value = ''; pwdError.value = '' }

async function doChangePwd() {
  pwdError.value = ''
  if (newPwd.value.length < 6) { pwdError.value = '密码至少6位'; return }
  pwdLoading.value = true
  try {
    await api.put(`/admin/users/${pwdTarget.value.id}/password`, { password: hashPassword(newPwd.value) })
    pwdTarget.value = null
  } catch (e) {
    pwdError.value = e.message
  } finally {
    pwdLoading.value = false
  }
}

// Delete user
const deleteUserTarget = ref(null)
const deleteLoading    = ref(false)

function confirmDeleteUser(u) { deleteUserTarget.value = u }

async function doDeleteUser() {
  deleteLoading.value = true
  try {
    await api.delete(`/admin/users/${deleteUserTarget.value.id}`)
    deleteUserTarget.value = null
    loadUsers()
    loadImages()
  } finally {
    deleteLoading.value = false
  }
}

// ── Image actions ─────────────────────────────────────────────────────────
const deleteImageTarget = ref(null)
function confirmDeleteImage(img) { deleteImageTarget.value = img }

async function doDeleteImage() {
  deleteLoading.value = true
  try {
    await api.delete(`/admin/images/${deleteImageTarget.value.id}`)
    deleteImageTarget.value = null
    loadImages()
  } finally {
    deleteLoading.value = false
  }
}

// ── Utils ─────────────────────────────────────────────────────────────────
function fmtDate(s) {
  if (!s) return '—'
  return new Date(s.replace(' ', 'T')).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => { loadUsers(); loadImages() })
</script>
