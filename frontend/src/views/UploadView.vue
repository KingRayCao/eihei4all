<template>
  <!-- ── Auth gate ── -->
  <div v-if="!auth.isAuthenticated" class="min-h-screen flex items-center justify-center p-4">
    <div class="card w-full max-w-sm p-8">
      <h1 class="text-2xl font-bold text-center mb-8 text-white">Eihei4All</h1>

      <!-- Login -->
      <form v-if="authMode === 'login'" @submit.prevent="doLogin" class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-200">登录</h2>
        <input v-model="form.username" class="input" placeholder="用户名" required />
        <input v-model="form.password" class="input" type="password" placeholder="密码" required />
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '登录中…' : '登录' }}
        </button>
        <p class="text-center text-sm text-gray-400">
          还没有账号？
          <button type="button" class="text-accent hover:underline" @click="switchMode('register')">注册</button>
        </p>
        <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
      </form>

      <!-- Register -->
      <form v-else-if="authMode === 'register'" @submit.prevent="doRegister" class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-200">注册</h2>
        <input v-model="form.username" class="input" placeholder="用户名（2-20个字符）" required />
        <input v-model="form.password" class="input" type="password" placeholder="密码（至少6位）" required />
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '提交中…' : '提交注册' }}
        </button>
        <p class="text-center text-sm text-gray-400">
          已有账号？
          <button type="button" class="text-accent hover:underline" @click="switchMode('login')">登录</button>
        </p>
        <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
      </form>

      <!-- Pending approval -->
      <div v-else class="text-center space-y-4">
        <div class="text-4xl">⏳</div>
        <p class="text-gray-300">注册成功！正在等待管理员审批，请稍后再来登录。</p>
        <button class="btn-ghost w-full" @click="switchMode('login')">返回登录</button>
      </div>
    </div>
  </div>

  <!-- ── Main app ── -->
  <div v-else class="min-h-screen flex flex-col">
    <!-- Top nav -->
    <header class="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between shrink-0">
      <nav class="flex gap-1">
        <button
          v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          class="px-4 py-1.5 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === tab.id
            ? 'bg-indigo-600 text-white'
            : 'text-gray-400 hover:text-white hover:bg-white/5'"
        >{{ tab.label }}</button>
      </nav>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-400">@{{ auth.user?.username }}</span>
        <router-link v-if="auth.isAdmin" to="/admin" class="btn-ghost text-sm py-1">管理后台</router-link>
        <button class="btn-ghost text-sm py-1" @click="auth.logout()">退出</button>
      </div>
    </header>

    <!-- ── Tab: 所有投稿 ── -->
    <div v-if="activeTab === 'all'" class="flex-1 overflow-auto p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">所有投稿记录</h2>
        <button class="btn-ghost text-sm py-1" @click="loadAll">刷新</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="text-left text-gray-400 border-b border-gray-800">
              <th class="py-2 pr-4 font-medium">ID</th>
              <th class="py-2 pr-4 font-medium">标题</th>
              <th class="py-2 pr-4 font-medium">提交者</th>
              <th class="py-2 pr-4 font-medium">出处/时间点</th>
              <th class="py-2 pr-4 font-medium">原图</th>
              <th class="py-2 pr-4 font-medium">P图</th>
              <th class="py-2 pr-4 font-medium">状态</th>
              <th class="py-2 pr-4 font-medium">提交时间</th>
              <th class="py-2 font-medium">更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="img in allImages" :key="img.id"
              class="border-b border-gray-800/50 hover:bg-white/[0.02] transition-colors"
            >
              <td class="py-2 pr-4 text-gray-400">{{ img.id }}</td>
              <td class="py-2 pr-4 max-w-[160px] truncate" :title="img.title">{{ img.title }}</td>
              <td class="py-2 pr-4 text-indigo-400">@{{ img.username }}</td>
              <td class="py-2 pr-4 text-gray-400 max-w-[120px] truncate" :title="img.source || ''">
                {{ img.source || '—' }}
              </td>
              <td class="py-2 pr-4">
                <a v-if="img.original_path" :href="`/uploads/${img.original_path}`" target="_blank">
                  <img :src="`/uploads/${img.original_path}`" class="h-12 w-16 object-cover rounded cursor-pointer hover:opacity-80" />
                </a>
                <span v-else class="text-gray-600">—</span>
              </td>
              <td class="py-2 pr-4">
                <a v-if="img.processed_path" :href="`/uploads/${img.processed_path}`" target="_blank">
                  <img :src="`/uploads/${img.processed_path}`" class="h-12 w-16 object-cover rounded cursor-pointer hover:opacity-80" />
                </a>
                <span v-else class="text-gray-600">—</span>
              </td>
              <td class="py-2 pr-4">
                <span :class="img.is_placeholder ? 'tag-placeholder' : 'tag-done'">
                  {{ img.is_placeholder ? '占坑中' : '已完成' }}
                </span>
              </td>
              <td class="py-2 pr-4 text-gray-400 whitespace-nowrap">{{ fmtDate(img.created_at) }}</td>
              <td class="py-2 text-gray-400 whitespace-nowrap">{{ fmtDate(img.updated_at) }}</td>
            </tr>
            <tr v-if="allImages.length === 0">
              <td colspan="9" class="py-8 text-center text-gray-500">暂无投稿记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Tab: 提交图片 ── -->
    <div v-if="activeTab === 'submit'" class="flex-1 overflow-auto p-6 flex justify-center">
      <div class="card w-full max-w-lg p-8 space-y-5">
        <h2 class="text-lg font-semibold">提交图片</h2>

        <div>
          <label class="block text-sm text-gray-400 mb-1">图片标题 <span class="text-red-400">*</span></label>
          <input v-model="submitForm.title" class="input" placeholder="给这张图起个标题" required />
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-1">出处与时间点 <span class="text-gray-600">（选填）</span></label>
          <input v-model="submitForm.source" class="input" placeholder="例：Mygo 第7集 20:56" />
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-1">原图 <span class="text-gray-600">（选填）</span></label>
          <input type="file" accept="image/*" @change="e => submitForm.original = e.target.files[0]"
            class="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-600/80 file:text-white hover:file:bg-indigo-500 cursor-pointer" />
          <img v-if="submitPreview.original" :src="submitPreview.original" class="mt-2 max-h-32 rounded" />
        </div>

        <label class="flex items-center gap-2 cursor-pointer select-none">
          <input type="checkbox" v-model="submitForm.is_placeholder"
            class="w-4 h-4 rounded accent-indigo-500" />
          <span class="text-sm text-gray-300">还没P完，先占个坑</span>
        </label>

        <div v-if="!submitForm.is_placeholder">
          <label class="block text-sm text-gray-400 mb-1">P图 <span class="text-red-400">*</span></label>
          <input type="file" accept="image/*" @change="e => submitForm.processed = e.target.files[0]"
            class="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-600/80 file:text-white hover:file:bg-indigo-500 cursor-pointer" />
          <img v-if="submitPreview.processed" :src="submitPreview.processed" class="mt-2 max-h-32 rounded" />
        </div>

        <p v-if="submitError" class="text-red-400 text-sm">{{ submitError }}</p>
        <p v-if="submitSuccess" class="text-emerald-400 text-sm">{{ submitSuccess }}</p>

        <button class="btn-primary w-full" :disabled="submitLoading" @click="doSubmit">
          {{ submitLoading ? '提交中…' : '提交' }}
        </button>
      </div>
    </div>

    <!-- ── Tab: 我的 ── -->
    <div v-if="activeTab === 'mine'" class="flex-1 overflow-auto p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">我的投稿</h2>
        <button class="btn-ghost text-sm py-1" @click="loadMine">刷新</button>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div v-for="img in myImages" :key="img.id" class="card p-4 space-y-3">
          <!-- Image preview -->
          <div class="flex gap-2">
            <a v-if="img.processed_path" :href="`/uploads/${img.processed_path}`" target="_blank" class="flex-1">
              <img :src="`/uploads/${img.processed_path}`" class="w-full h-28 object-cover rounded hover:opacity-80" />
            </a>
            <div v-else class="flex-1 h-28 bg-gray-800 rounded flex items-center justify-center">
              <span class="tag-placeholder">占坑中</span>
            </div>
          </div>
          <div>
            <p class="font-medium truncate" :title="img.title">{{ img.title }}</p>
            <p v-if="img.source" class="text-xs text-gray-500 truncate">{{ img.source }}</p>
            <p class="text-xs text-gray-600 mt-1">{{ fmtDate(img.created_at) }}</p>
          </div>
          <div class="flex gap-2">
            <button class="btn-ghost text-xs py-1 flex-1" @click="openEdit(img)">修改</button>
            <button class="btn-danger text-xs py-1 flex-1" @click="confirmDelete(img)">删除</button>
          </div>
        </div>
        <div v-if="myImages.length === 0" class="col-span-full py-12 text-center text-gray-500">
          还没有投稿记录
        </div>
      </div>
    </div>
  </div>

  <!-- ── Edit Modal ── -->
  <div v-if="editTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="card w-full max-w-lg p-8 space-y-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-semibold">修改投稿</h3>

      <div>
        <label class="block text-sm text-gray-400 mb-1">图片标题 <span class="text-red-400">*</span></label>
        <input v-model="editForm.title" class="input" />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">出处与时间点</label>
        <div class="flex gap-2">
          <input v-model="editForm.source" class="input flex-1" placeholder="留空则清除" />
        </div>
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">替换原图（留空则不修改）</label>
        <input type="file" accept="image/*" @change="e => editForm.original = e.target.files[0]"
          class="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-700 file:text-white hover:file:bg-gray-600 cursor-pointer" />
      </div>

      <label class="flex items-center gap-2 cursor-pointer select-none">
        <input type="checkbox" v-model="editForm.is_placeholder" class="w-4 h-4 rounded accent-indigo-500" />
        <span class="text-sm text-gray-300">还没P完，先占个坑</span>
      </label>

      <div>
        <label class="block text-sm text-gray-400 mb-1">
          {{ editTarget.is_placeholder ? '上传P图（将自动取消占坑）' : '替换P图（留空则不修改）' }}
        </label>
        <input type="file" accept="image/*" @change="e => editForm.processed = e.target.files[0]"
          class="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-700 file:text-white hover:file:bg-gray-600 cursor-pointer" />
      </div>

      <p v-if="editError" class="text-red-400 text-sm">{{ editError }}</p>

      <div class="flex gap-3 pt-2">
        <button class="btn-ghost flex-1" @click="editTarget = null">取消</button>
        <button class="btn-primary flex-1" :disabled="editLoading" @click="doEdit">
          {{ editLoading ? '保存中…' : '保存修改' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Delete confirm ── -->
  <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="card w-full max-w-sm p-6 space-y-4 text-center">
      <p class="text-gray-200">确定要删除「<span class="font-semibold">{{ deleteTarget.title }}</span>」吗？</p>
      <p class="text-sm text-gray-500">此操作不可撤销，图片文件将被永久删除。</p>
      <div class="flex gap-3">
        <button class="btn-ghost flex-1" @click="deleteTarget = null">取消</button>
        <button class="btn-danger flex-1" :disabled="deleteLoading" @click="doDelete">
          {{ deleteLoading ? '删除中…' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

const auth = useAuthStore()

// ── Auth ──────────────────────────────────────────────────────────────────
const authMode = ref('login') // 'login' | 'register' | 'pending'
const form = reactive({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

function switchMode(mode) {
  authMode.value = mode
  error.value = ''
  form.username = ''
  form.password = ''
}

async function doLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    loadAll()
    loadMine()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form.username, form.password)
    authMode.value = 'pending'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ── Tabs ──────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'all', label: '所有投稿' },
  { id: 'submit', label: '提交图片' },
  { id: 'mine', label: '我的' },
]
const activeTab = ref('all')

// ── All images ────────────────────────────────────────────────────────────
const allImages = ref([])
async function loadAll() {
  try { allImages.value = await api.get('/images/all') } catch {}
}

// ── Submit ────────────────────────────────────────────────────────────────
const submitForm = reactive({ title: '', source: '', is_placeholder: false, original: null, processed: null })
const submitError = ref('')
const submitSuccess = ref('')
const submitLoading = ref(false)
const submitPreview = reactive({ original: null, processed: null })

watch(() => submitForm.original, (f) => { submitPreview.original = f ? URL.createObjectURL(f) : null })
watch(() => submitForm.processed, (f) => { submitPreview.processed = f ? URL.createObjectURL(f) : null })

async function doSubmit() {
  submitError.value = ''
  submitSuccess.value = ''
  if (!submitForm.title.trim()) { submitError.value = '请填写标题'; return }
  if (!submitForm.is_placeholder && !submitForm.processed) { submitError.value = '请上传P图，或勾选占坑'; return }

  submitLoading.value = true
  try {
    const fd = new FormData()
    fd.append('title', submitForm.title.trim())
    if (submitForm.source) fd.append('source', submitForm.source)
    fd.append('is_placeholder', String(submitForm.is_placeholder))
    if (submitForm.original) fd.append('original', submitForm.original)
    if (submitForm.processed) fd.append('processed', submitForm.processed)

    await api.post('/images', fd)
    submitSuccess.value = '提交成功！'
    Object.assign(submitForm, { title: '', source: '', is_placeholder: false, original: null, processed: null })
    submitPreview.original = null
    submitPreview.processed = null
    loadAll()
    loadMine()
  } catch (e) {
    submitError.value = e.message
  } finally {
    submitLoading.value = false
  }
}

// ── My images ─────────────────────────────────────────────────────────────
const myImages = ref([])
async function loadMine() {
  try { myImages.value = await api.get('/images/mine') } catch {}
}

// ── Edit ──────────────────────────────────────────────────────────────────
const editTarget = ref(null)
const editForm = reactive({ title: '', source: '', is_placeholder: false, original: null, processed: null })
const editError = ref('')
const editLoading = ref(false)

function openEdit(img) {
  editTarget.value = img
  editForm.title = img.title
  editForm.source = img.source || ''
  editForm.is_placeholder = !!img.is_placeholder
  editForm.original = null
  editForm.processed = null
  editError.value = ''
}

async function doEdit() {
  editError.value = ''
  if (!editForm.title.trim()) { editError.value = '标题不能为空'; return }
  editLoading.value = true
  try {
    const fd = new FormData()
    fd.append('title', editForm.title.trim())
    fd.append('source', editForm.source || '')
    fd.append('clear_source', editForm.source ? 'false' : 'true')
    fd.append('is_placeholder', String(editForm.is_placeholder))
    if (editForm.original) fd.append('original', editForm.original)
    if (editForm.processed) fd.append('processed', editForm.processed)
    await api.put(`/images/${editTarget.value.id}`, fd)
    editTarget.value = null
    loadAll()
    loadMine()
  } catch (e) {
    editError.value = e.message
  } finally {
    editLoading.value = false
  }
}

// ── Delete ────────────────────────────────────────────────────────────────
const deleteTarget = ref(null)
const deleteLoading = ref(false)

function confirmDelete(img) { deleteTarget.value = img }
async function doDelete() {
  deleteLoading.value = true
  try {
    await api.delete(`/images/${deleteTarget.value.id}`)
    deleteTarget.value = null
    loadAll()
    loadMine()
  } catch {} finally {
    deleteLoading.value = false
  }
}

// ── Utils ─────────────────────────────────────────────────────────────────
function fmtDate(s) {
  if (!s) return '—'
  return new Date(s.replace(' ', 'T')).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  if (auth.isAuthenticated) {
    loadAll()
    loadMine()
  }
})
</script>
