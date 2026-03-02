<template>
  <div
    class="gallery-root"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
    @keydown="onKey"
    tabindex="0"
    ref="rootEl"
  >
    <!-- Empty state -->
    <div v-if="images.length === 0 && !loading" class="empty-state">
      <p>{{ hours === 0 ? '全部时间' : hours + ' 小时' }}内没有投稿</p>
    </div>

    <!-- Image -->
    <transition name="cross-fade" mode="out-in">
      <img
        v-if="current"
        :key="current.id"
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

    <!-- ── Hover overlay (controls only) ── -->
    <transition name="fade-ui">
      <div v-if="showUI && images.length > 0" class="ui-layer">

        <!-- Filter panel (top-right) -->
        <div class="filter-panel" @click.stop>
          <div class="flex flex-wrap gap-1 justify-end">
            <button
              v-for="p in presets" :key="p.hours"
              @click="setHours(p.hours)"
              class="filter-btn" :class="{ active: hours === p.hours && !customActive }"
            >{{ p.label }}</button>
          </div>
          <div class="flex items-center gap-1.5 mt-2 justify-end">
            <input
              v-model.number="customHoursInput"
              type="number" min="1"
              placeholder="自定义"
              class="custom-input"
              @keydown.enter="applyCustomHours"
            />
            <span class="text-xs text-gray-400">小时</span>
            <button class="filter-btn" :class="{ active: customActive }" @click="applyCustomHours">确定</button>
          </div>
          <div class="flex flex-col gap-1 mt-2">
            <label class="flex items-center gap-1.5 cursor-pointer select-none justify-end">
              <span class="text-xs text-gray-300">显示作者</span>
              <input type="checkbox" v-model="showAuthor" class="accent-indigo-400" />
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer select-none justify-end">
              <span class="text-xs text-gray-300">显示标题</span>
              <input type="checkbox" v-model="showTitle" class="accent-indigo-400" />
            </label>
          </div>
          <p class="text-xs text-gray-500 text-right mt-2">{{ idx + 1 }} / {{ images.length }}</p>
        </div>

        <!-- Prev arrow -->
        <button class="nav-btn nav-prev" @click.stop="prev" :disabled="idx === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="nav-icon">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <!-- Next arrow -->
        <button class="nav-btn nav-next" @click.stop="next" :disabled="idx === images.length - 1">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="nav-icon">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>

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
import api from '../api/index.js'

const presets = [
  { label: '24h',  hours: 24 },
  { label: '7天',  hours: 168 },
  { label: '30天', hours: 720 },
  { label: '90天', hours: 2160 },
  { label: '全部', hours: 0 },
]

const images           = ref([])
const idx              = ref(0)
const hours            = ref(168)
const customHoursInput = ref(null)
const customActive     = ref(false)
const showAuthor       = ref(true)
const showTitle        = ref(true)
const showUI           = ref(false)
const loading          = ref(false)
const rootEl           = ref(null)

let hideTimer = null

const current = computed(() => images.value[idx.value] || null)

async function load() {
  loading.value = true
  try {
    images.value = await api.get(`/images/gallery?hours=${hours.value}`)
    idx.value = 0
  } finally {
    loading.value = false
  }
}

function setHours(h) {
  hours.value = h
  customActive.value = false
  load()
}

function applyCustomHours() {
  const h = Number(customHoursInput.value)
  if (!h || h < 1) return
  hours.value = h
  customActive.value = !presets.some(p => p.hours === h)
  load()
}

function prev() { if (idx.value > 0) idx.value-- }
function next() { if (idx.value < images.value.length - 1) idx.value++ }

function onKey(e) {
  if (e.key === 'ArrowLeft')  prev()
  else if (e.key === 'ArrowRight') next()
}

function onMouseMove() {
  showUI.value = true
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => { showUI.value = false }, 3000)
}

function onMouseLeave() {
  clearTimeout(hideTimer)
  showUI.value = false
}

onMounted(() => { load(); rootEl.value?.focus() })
onBeforeUnmount(() => clearTimeout(hideTimer))
</script>

<style scoped>
.gallery-root {
  position: fixed;
  inset: 0;
  background: #000;
  outline: none;
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

/* Info badges: always above the image, not inside hover overlay */
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

/* Hover layer */
.ui-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 20;
}
.ui-layer > * { pointer-events: auto; }

/* Filter panel */
.filter-panel {
  position: absolute;
  top: clamp(10px, 1.2vh, 20px);
  right: clamp(12px, 1.2vw, 24px);
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: clamp(8px, 0.8vw, 14px);
  padding: clamp(10px, 1vh, 16px) clamp(12px, 1.1vw, 20px);
  min-width: clamp(180px, 16vw, 280px);
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

/* Nav arrows */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  width: clamp(44px, 3.8vw, 68px);
  height: clamp(44px, 3.8vw, 68px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}
.nav-btn:hover { background: rgba(79, 70, 229, 0.7); }
.nav-btn:disabled { opacity: 0.2; cursor: default; }
.nav-prev { left: clamp(12px, 1.8vw, 32px); }
.nav-next { right: clamp(12px, 1.8vw, 32px); }
.nav-icon {
  width: clamp(20px, 2vw, 34px);
  height: clamp(20px, 2vw, 34px);
}

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

.cross-fade-enter-active { transition: opacity 0.4s ease; }
.cross-fade-leave-active { transition: opacity 0.2s ease; }
.cross-fade-enter-from, .cross-fade-leave-to { opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-ui-enter-active, .fade-ui-leave-active { transition: opacity 0.2s ease; }
.fade-ui-enter-from, .fade-ui-leave-to { opacity: 0; }
</style>
