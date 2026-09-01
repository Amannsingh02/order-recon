<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between mb-3">
      <div :class="`w-10 h-10 ${colorBg} rounded-xl flex items-center justify-center`">
        <svg class="w-5 h-5" :class="colorText" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon" />
        </svg>
      </div>
    </div>
    <p class="text-sm text-gray-500 font-medium mb-1">{{ label }}</p>
    <p class="text-2xl font-bold text-gray-800" :class="colorText">{{ value }}</p>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: String,
    value: [String, Number],
    icon: String,
    color: {
      type: String,
      default: 'gray',
    },
    isCurrency: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    colorBg() {
      const map = {
        blue: 'bg-blue-50',
        purple: 'bg-purple-50',
        emerald: 'bg-emerald-50',
        amber: 'bg-amber-50',
        rose: 'bg-rose-50',
        gray: 'bg-gray-50',
      }
      return map[this.color] || 'bg-gray-50'
    },
    colorText() {
      const map = {
        blue: 'text-blue-600',
        purple: 'text-purple-600',
        emerald: 'text-emerald-600',
        amber: 'text-amber-600',
        rose: 'text-rose-600',
        gray: 'text-gray-600',
      }
      return map[this.color] || 'text-gray-600'
    },
  },
}
</script>
