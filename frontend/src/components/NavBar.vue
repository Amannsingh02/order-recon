<template>
  <nav class="bg-white border-b border-slate-100 px-4 sm:px-6 lg:px-8 py-4">
    <div class="max-w-7xl mx-auto flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 3.666V14m-6 4h6m-6-10h6m-3 10.5v-6m-3 3h6m-9-3h6m-9 3h6"/>
          </svg>
        </div>
        <span class="text-lg font-bold text-gray-800">Order Recon</span>
      </div>

      <div v-if="user" class="flex items-center gap-4">
        <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg">
          <div class="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
            <span class="text-xs font-medium text-indigo-600">{{ user.username.charAt(0).toUpperCase() }}</span>
          </div>
          <span class="text-sm text-gray-600 font-medium hidden sm:block">{{ user.username }}</span>
        </div>
        <button
          @click="logout"
          class="text-sm text-gray-500 hover:text-rose-600 font-medium transition-colors flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          <span class="hidden sm:inline">Logout</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import api from '../utils/api.js'

export default {
  name: 'NavBar',
  data() {
    return {
      user: null,
    }
  },
  async created() {
    try {
      const res = await api.get('/auth/me/')
      this.user = res.data
    } catch {
      this.user = null
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.$router.push('/login')
    },
  },
}
</script>
