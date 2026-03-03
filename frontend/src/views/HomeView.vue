<template>
  <div class="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-3xl text-center space-y-10">

      <!-- Title -->
      <div class="space-y-3">
        <h1 class="text-5xl font-bold text-white tracking-tight">大家都是欸嘿酱！</h1>
        <p class="text-gray-400 text-lg">欸嘿酱图片投稿 · 展示 · 轮播</p>
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

      <!-- Usage Notice -->
      <div class="card p-6 text-left space-y-3">
        <h2 class="text-white font-semibold text-base">使用须知</h2>
        <ol class="text-sm text-gray-400 space-y-2 list-decimal list-inside leading-relaxed">
          <li>本网站提供投稿欸嘿酱、欸嘿酱图廊及欸嘿酱轮播功能。其中欸嘿酱轮播设置好后将网址复制到 OBS 浏览器源中可直接使用。</li>
          <li>只有投稿功能需要注册账号，其他功能均可直接使用。想要注册账号请提交注册申请并联系 QQ：<span class="text-indigo-400 font-medium">XXX</span> 或邮箱：<span class="text-indigo-400 font-medium">xxx@xxx.com</span>，并随附以前 P 过的欸嘿酱。</li>
          <li>请合理使用本网站。管理员有权采取包括删除 P 图、删除投稿者账号等行为。网站运营者不对用户上传的内容负责。</li>
        </ol>
      </div>

      <!-- Admin link -->
      <p v-if="auth.isAdmin" class="text-sm text-gray-600">
        <router-link to="/admin" class="hover:text-indigo-400 transition-colors">进入管理后台 →</router-link>
      </p>

      <!-- GitHub link -->
      <a
        href="https://github.com/KingRayCao/eihei4all"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-2 text-gray-600 hover:text-gray-300 transition-colors text-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
        </svg>
        KingRayCao/eihei4all
      </a>
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
