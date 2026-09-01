<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50">
    <div class="w-full max-w-md mx-4">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/50 p-8">
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Create account</h1>
          <p class="text-gray-500 mt-2 text-sm">Get started with order reconciliation</p>
        </div>

        <form @submit.prevent="register" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Username</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="Choose a username"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 transition-all outline-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="you@example.com"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 transition-all outline-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
            <input
              v-model="form.password"
              type="password"
              required
              minlength="8"
              placeholder="Minimum 8 characters"
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-400 transition-all outline-none"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-200"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Creating account...
            </span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600">
          {{ error }}
        </div>

        <p class="mt-6 text-center text-sm text-gray-500">
          Already have an account?
          <router-link to="/login" class="text-emerald-600 hover:text-emerald-700 font-medium transition-colors">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/api.js'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
      },
      loading: false,
      error: '',
    }
  },
  methods: {
    async register() {
      this.loading = true
      this.error = ''
      try {
        const res = await api.post('/auth/register/', this.form)
        localStorage.setItem('access_token', res.data.access)
        localStorage.setItem('refresh_token', res.data.refresh)
        this.$router.push('/')
      } catch (err) {
        this.error = err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Registration failed'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
