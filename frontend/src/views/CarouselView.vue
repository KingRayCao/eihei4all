<template>
  <div
    class="carousel-root"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
    ref="rootEl"
  >
    <!-- Empty state -->
    <div v-if="images.length === 0 && !loading" class="empty-state">
      <p>{{ hours === 0 ? '全部时间' : hours + ' 小时' }}内没有投稿</p>
    </div>

    <!-- Image (key forces GIF restart on slide change) -->
    <transition name="cross-fade" mode="out-in">
      <img
        v-if="current"
        :key="current.id + '-' + tickKey"
        :src="`/uploads/${current.processed_path}`"
        class="main-img"
        draggable="false"
      />
    </transition>

    <!-- ── Info badges: always visible, independent of hover ── -->
    <div v-if="current" class="info-layer">
      <transition name="fade">
        <div v-if="showAuthor" class="info-badge author-badge">@{{ current.username }}</div>
      </transition>
      <transition name="fade">
        <div v-if="showTitle" class="info-badge title-badge">{{ current.title }}</div>
      </transition>
    </div>

    <!-- ── Hover overlay (controls) ── -->
    <transition name="fade-ui">
      <div v-if="showUI && images.length > 0" class="ui-layer">
        <div class="controls-panel" @click.stop>

          <!-- Time presets -->
          <div class="flex flex-wrap gap-1">
            <span class="text-xs text-gray-400 self-center mr-1">时间</span>
            <button
              v-for="p in presets" :key="p.hours"
              @click="setHours(p.hours)"
              class="filter-btn" :class="{ active: hours === p.hours && !customActive }"
            >{{ p.label }}</button>
          </div>

          <!-- Custom hours -->
          <div class="flex items-center gap-1.5 mt-2">
            <span class="text-xs text-gray-400 whitespace-nowrap">自定义</span>
            <input
              v-model.number="customHoursInput"
              type="number" min="1"
              placeholder="小时数"
              class="custom-input"
              @keydown.enter="applyCustomHours"
            />
            <span class="text-xs text-gray-400">小时</span>
            <button class="filter-btn" :class="{ active: customActive }" @click="applyCustomHours">确定</button>
          </div>

          <!-- Interval slider -->
          <div class="flex items-center gap-2 mt-3">
            <span class="text-xs text-gray-400 whitespace-nowrap">间隔</span>
            <input
              type="range" min="2" max="60" step="1"
              v-model.number="interval"
              @change="applySettings"
              class="flex-1 accent-indigo-500"
            />
            <span class="text-xs text-gray-300 w-10 text-right">{{ interval }}秒</span>
          </div>

          <!-- Author / Title toggles -->
          <div class="flex gap-4 mt-2">
            <label class="flex items-center gap-1.5 cursor-pointer select-none">
              <input type="checkbox" v-model="showAuthor" @change="applySettings" class="accent-indigo-400" />
              <span class="text-xs text-gray-300">显示作者</span>
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer select-none">
              <input type="checkbox" v-model="showTitle" @change="applySettings" class="accent-indigo-400" />
              <span class="text-xs text-gray-300">显示标题</span>
            </label>
          </div>

          <p class="text-xs text-gray-500 mt-2">{{ idx + 1 }} / {{ images.length }}</p>
        </div>
      </div>
    </transition>

    <!-- Loading -->
    <div v-if="loading" class="spinner-wrap">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/index.js'

const route  = useRoute()
const router = useRouter()

const presets = [
  { label: '24h',  hours: 24 },
  { label: '7天',  hours: 168 },
  { label: '30天', hours: 720 },
  { label: '90天', hours: 2160 },
  { label: '全部', hours: 0 },
]

// ── State initialised from URL params ─────────────────────────────────────
const hours            = ref(Number(route.query.hours    ?? 168))
const interval         = ref(Number(route.query.interval ?? 5))
const showAuthor       = ref(route.query.show_author !== 'false')
const showTitle        = ref(route.query.show_title  !== 'false')
const customHoursInput = ref(null)
const customActive     = ref(!presets.some(p => p.hours === hours.value))

const images  = ref([])
const idx     = ref(0)
const tickKey = ref(0)
const showUI  = ref(false)
const loading = ref(false)
const rootEl  = ref(null)

let timer     = null
let hideTimer = null

const current = computed(() => images.value[idx.value] || null)

// ── Data loading ──────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  clearInterval(timer)
  try {
    images.value = await api.get(`/images/gallery?hours=${hours.value}`)
    idx.value = 0
    tickKey.value++
  } finally {
    loading.value = false
    startTimer()
  }
}

function startTimer() {
  clearInterval(timer)
  if (images.value.length < 2) return
  timer = setInterval(() => {
    idx.value = (idx.value + 1) % images.value.length
    tickKey.value++
  }, interval.value * 1000)
}

// ── Settings ──────────────────────────────────────────────────────────────
function setHours(h) {
  hours.value = h
  customActive.value = false
  applySettings()
  load()
}

function applyCustomHours() {
  const h = Number(customHoursInput.value)
  if (!h || h < 1) return
  hours.value = h
  customActive.value = !presets.some(p => p.hours === h)
  applySettings()
  load()
}

function applySettings() {
  // Persist all settings into the URL so OBS can bookmark it
  router.replace({
    query: {
      hours:       hours.value,
      interval:    interval.value,
      show_author: showAuthor.value ? 'true' : 'false',
      show_title:  showTitle.value  ? 'true' : 'false',
    }
  })
  startTimer()
}

// ── Hover show/hide ───────────────────────────────────────────────────────
function onMouseMove() {
  showUI.value = true
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => { showUI.value = false }, 3000)
}

function onMouseLeave() {
  clearTimeout(hideTimer)
  showUI.value = false
}

// ── Lifecycle ─────────────────────────────────────────────────────────────
onMounted(() => load())
onBeforeUnmount(() => { clearInterval(timer); clearTimeout(hideTimer) })
</script>

<style scoped>
.carousel-root {
  position: fixed;
  inset: 0;
  background: #000;
  overflow: hidden;
  user-select: none;
}

.main-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* Info badges: always visible */
.info-layer {
  position: absolute;
  top: 0;
  left: 0;
  padding: clamp(10px, 1.2vh, 20px) clamp(12px, 1.2vw, 24px);
  display: flex;
  flex-direction: column;
  gap: clamp(4px, 0.5vh, 8px);
  pointer-events: none;
  z-index: 10;
}

.info-badge {
  display: inline-block;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: clamp(6px, 0.6vw, 10px);
  padding: clamp(5px, 0.5vh, 10px) clamp(10px, 0.9vw, 18px);
  font-size: clamp(14px, 1.15vw, 24px);
  line-height: 1.3;
  max-width: 45vw;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.author-badge { color: #a5b4fc; font-weight: 600; }
.title-badge  { color: #e5e7eb; }

/* Hover overlay */
.ui-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 20;
}
.ui-layer > * { pointer-events: auto; }

.controls-panel {
  position: absolute;
  top: clamp(10px, 1.2vh, 20px);
  right: clamp(12px, 1.2vw, 24px);
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: clamp(8px, 0.8vw, 14px);
  padding: clamp(12px, 1.1vh, 18px) clamp(14px, 1.2vw, 22px);
  min-width: clamp(220px, 18vw, 320px);
  color: #e5e7eb;
}

.filter-btn {
  font-size: clamp(11px, 0.9vw, 17px);
  padding: clamp(2px, 0.3vh, 5px) clamp(8px, 0.7vw, 14px);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.filter-btn:hover { color: #fff; background: rgba(255, 255, 255, 0.1); }
.filter-btn.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }

.custom-input {
  width: clamp(52px, 5vw, 80px);
  font-size: clamp(11px, 0.9vw, 17px);
  padding: clamp(2px, 0.3vh, 5px) clamp(6px, 0.5vw, 10px);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #e5e7eb;
  text-align: center;
  outline: none;
}
.custom-input:focus { border-color: #6366f1; }
.custom-input::-webkit-outer-spin-button,
.custom-input::-webkit-inner-spin-button { -webkit-appearance: none; }

.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: clamp(14px, 1.2vw, 22px);
}

.spinner-wrap {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.spinner {
  width: clamp(28px, 2.5vw, 48px);
  height: clamp(28px, 2.5vw, 48px);
  border: 2px solid #4f46e5;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.cross-fade-enter-active { transition: opacity 0.5s ease; }
.cross-fade-leave-active { transition: opacity 0.3s ease; }
.cross-fade-enter-from, .cross-fade-leave-to { opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-ui-enter-active, .fade-ui-leave-active { transition: opacity 0.2s ease; }
.fade-ui-enter-from, .fade-ui-leave-to { opacity: 0; }
</style>
