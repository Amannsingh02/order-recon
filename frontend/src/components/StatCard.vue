<template>
  <div class="bg-white rounded-lg shadow p-5">
    <p class="text-sm text-gray-500 uppercase tracking-wide">{{ label }}</p>
    <p class="text-2xl font-bold mt-1" :class="valueClass">{{ formattedValue }}</p>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: String,
    value: [String, Number],
    type: {
      type: String,
      default: 'neutral',
    },
  },
  computed: {
    formattedValue() {
      if (typeof this.value === 'number') {
        if (this.label.toLowerCase().includes('value') || this.label.toLowerCase().includes('risk')) {
          return '$' + this.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
        }
        return this.value.toLocaleString()
      }
      return this.value
    },
    valueClass() {
      if (this.type === 'success') return 'text-green-600'
      if (this.type === 'danger') return 'text-red-600'
      if (this.type === 'warning') return 'text-yellow-600'
      return 'text-gray-800'
    },
  },
}
</script>
