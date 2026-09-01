<template>
  <nav class="bg-gray-900 text-white px-6 py-4 flex justify-between items-center">
    <div class="text-xl font-bold">Order Recon</div>
    <div v-if="user" class="flex items-center gap-4">
      <span class="text-sm text-gray-300">{{ user.username }}</span>
      <button
        @click="logout"
        class="bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1.5 rounded"
      >
        Logout
      </button>
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
