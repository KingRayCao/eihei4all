<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-3xl text-center space-y-10">

      <!-- Title -->
      <div class="space-y-3">
        <h1 class="text-5xl font-bold text-white tracking-tight">Eihei4All</h1>
        <p class="text-gray-400 text-lg">图片投稿 · 展示 · 轮播</p>
      </div>

      <!-- Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <router-link
          v-for="card in cards" :key="card.path"
          :to="card.path"
          class="group card p-6 flex flex-col items-center gap-4 hover:border-indigo-500/60 hover:bg-gray-800/60 transition-all duration-200 cursor-pointer"
        >
          <span class="text-4xl">{{ card.icon }}</span>
          <div class="text-center">
            <p class="font-semibold text-white text-lg group-hover:text-indigo-300 transition-colors">{{ card.title }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ card.desc }}</p>
          </div>
        </router-link>
      </div>

      <!-- Admin link -->
      <p v-if="auth.isAdmin" class="text-sm text-gray-600">
        <router-link to="/admin" class="hover:text-indigo-400 transition-colors">进入管理后台 →</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

const cards = [
  { path: '/upload', icon: '📤', title: '投稿',  desc: '登录后提交或管理你的图片' },
  { path: '/gallery', icon: '🖼️', title: '画廊', desc: '浏览所有P图，支持时间筛选' },
  { path: '/carousel', icon: '▶️', title: '轮播', desc: '全屏轮播，可直接接入OBS' },
]
</script>
