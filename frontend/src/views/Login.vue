<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
    <div class="w-full max-w-md mx-4">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/50 p-8">
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 3.666V14m-6 4h6m-6-10h6m-3 10.5v-6m-3 3h6m-9-3h6m-3 3h6m-9 3h6"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Welcome back</h1>
          <p class="text-gray-500 mt-2 text-sm">Sign in to your reconciliation dashboard</p>
        </div>

        <form @submit.prevent="login" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Username</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="Enter your username"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition-all outline-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="Enter your password"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition-all outline-none"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-200"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Signing in...
            </span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600">
          {{ error }}
        </div>

        <p class="mt-6 text-center text-sm text-gray-500">
          Don't have an account?
          <router-link to="/register" class="text-indigo-600 hover:text-indigo-700 font-medium transition-colors">Create one</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/api.js'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
      loading: false,
      error: '',
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = ''
      try {
        const res = await api.post('/auth/login/', this.form)
        localStorage.setItem('access_token', res.data.access)
        localStorage.setItem('refresh_token', res.data.refresh)
        this.$router.push('/')
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
