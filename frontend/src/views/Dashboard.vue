<template>
  <div class="min-h-screen bg-slate-50">
    <NavBar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Upload Section -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 mb-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-800">Data Ingestion</h2>
            <p class="text-sm text-gray-500">Upload your orders and payments CSV files</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-2">Orders CSV</label>
            <div class="relative border-2 border-dashed border-gray-200 rounded-xl p-6 hover:border-indigo-300 transition-colors">
              <input
                type="file"
                accept=".csv"
                @change="handleOrdersUpload"
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div class="text-center">
                <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-sm text-gray-500">Click to upload orders.csv</p>
              </div>
            </div>
            <p v-if="uploadStatus.orders" class="mt-2 text-sm text-emerald-600 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              {{ uploadStatus.orders }}
            </p>
          </div>

          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-2">Payments CSV</label>
            <div class="relative border-2 border-dashed border-gray-200 rounded-xl p-6 hover:border-indigo-300 transition-colors">
              <input
                type="file"
                accept=".csv"
                @change="handlePaymentsUpload"
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div class="text-center">
                <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-sm text-gray-500">Click to upload payments.csv</p>
              </div>
            </div>
            <p v-if="uploadStatus.payments" class="mt-2 text-sm text-emerald-600 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              {{ uploadStatus.payments }}
            </p>
          </div>
        </div>

        <div class="mt-6 flex items-center gap-4">
          <button
            @click="runReconcile"
            :disabled="reconciling"
            class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-6 py-2.5 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-100"
          >
            <svg v-if="reconciling" class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            {{ reconciling ? 'Running...' : 'Run Reconciliation' }}
          </button>
          <p v-if="reconcileStatus" class="text-sm text-gray-600">{{ reconcileStatus }}</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div v-if="summary" class="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <StatCard
          label="Total Orders"
          :value="summary.total_orders"
          icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          color="blue"
        />
        <StatCard
          label="Total Payments"
          :value="summary.total_payments"
          icon="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
          color="purple"
        />
        <StatCard
          label="Reconciled Value"
          :value="formatCurrency(summary.total_reconciled_value)"
          icon="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          color="emerald"
          isCurrency
        />
        <StatCard
          label="Disputed Value"
          :value="formatCurrency(summary.total_disputed_value)"
          icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          color="amber"
          isCurrency
        />
        <StatCard
          label="At Risk"
          :value="formatCurrency(summary.total_at_risk)"
          icon="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          color="rose"
          isCurrency
        />
      </div>

      <!-- Chart + Table -->
      <div v-if="summary" class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <!-- Discrepancy Chart -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-1">Discrepancy Breakdown</h3>
          <p class="text-sm text-gray-500 mb-6">Distribution by type</p>
          <div class="h-64 relative">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>

        <!-- Discrepancies Table -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 xl:col-span-2">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-800">Discrepancies</h3>
              <p class="text-sm text-gray-500 mt-1">Review and explain individual issues</p>
            </div>
            <div class="flex gap-3">
              <select
                v-model="filterType"
                @change="fetchDiscrepancies"
                class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
              >
                <option value="">All Types</option>
                <option v-for="(label, key) in typeOptions" :key="key" :value="key">{{ label }}</option>
              </select>
            </div>
          </div>

          <div class="mb-4">
            <div class="relative">
              <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                placeholder="Search order ID, reference, or description..."
                class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none transition-all"
              />
            </div>
          </div>

          <div v-if="loadingDiscrepancies" class="flex items-center justify-center py-12 text-gray-400">
            <svg class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            Loading discrepancies...
          </div>

          <div v-else-if="discrepancies.length === 0" class="text-center py-12 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            <p>No discrepancies found.</p>
          </div>

          <div v-else class="overflow-x-auto -mx-2">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100">
                  <th class="text-left py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">Type</th>
                  <th class="text-left py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">Order</th>
                  <th class="text-left py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">Payment</th>
                  <th class="text-right py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">At Risk</th>
                  <th class="text-left py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">Description</th>
                  <th class="text-left py-3 px-3 font-medium text-gray-500 text-xs uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="d in discrepancies" :key="d.id" class="hover:bg-slate-50/50 transition-colors">
                  <td class="py-3 px-3">
                    <span
                      class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
                      :class="typeBadgeClass(d.discrepancy_type)"
                    >
                      {{ d.discrepancy_type_display }}
                    </span>
                  </td>
                  <td class="py-3 px-3 font-mono text-xs text-gray-600">{{ d.order ? d.order.order_id : '-' }}</td>
                  <td class="py-3 px-3 font-mono text-xs text-gray-600">{{ d.payment ? d.payment.transaction_ref : '-' }}</td>
                  <td class="py-3 px-3 text-right font-medium text-gray-700">{{ formatCurrency(d.amount_at_risk) }}</td>
                  <td class="py-3 px-3">
                    <div class="relative group max-w-xs">
                      <p class="text-gray-600 truncate">{{ d.description }}</p>
                      <div class="absolute left-0 bottom-full mb-2 hidden group-hover:block z-50 w-80 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-xl">
                        {{ d.description }}
                        <div class="absolute left-4 top-full -mt-1 border-4 border-transparent border-t-gray-800"></div>
                      </div>
                    </div>
                  </td>
                  <td class="py-3 px-3">
                    <button
                      v-if="d.discrepancy_type !== 'fully_reconciled'"
                      @click="explainOne(d)"
                      :disabled="explainingId === d.id"
                      class="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-xs font-medium transition-colors"
                    >
                      <svg v-if="explainingId === d.id" class="animate-spin h-3 w-3" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
                      <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      {{ explainingId === d.id ? 'Thinking...' : 'Explain' }}
                    </button>
                    <span v-else class="text-gray-400 text-xs">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- LLM Explanation Panel -->
      <div v-if="explanation" class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="explanation = null">
        <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h4 class="font-semibold text-gray-800">AI Explanation</h4>
            </div>
            <button @click="explanation = null" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="p-6">
            <div class="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">{{ explanation }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/api.js'
import NavBar from '../components/NavBar.vue'
import StatCard from '../components/StatCard.vue'
import { Chart, PieController, ArcElement, Tooltip, Legend, Title } from 'chart.js'

Chart.register(PieController, ArcElement, Tooltip, Legend, Title)

export default {
  name: 'Dashboard',
  components: { NavBar, StatCard },
  data() {
    return {
      uploadStatus: { orders: '', payments: '' },
      reconciling: false,
      reconcileStatus: '',
      summary: null,
      discrepancies: [],
      loadingDiscrepancies: false,
      filterType: '',
      searchQuery: '',
      explanation: null,
      explainingId: null,
      typeOptions: {
        amount_mismatch: 'Amount Mismatch',
        currency_mismatch: 'Currency Mismatch',
        missing_payment: 'Missing Payment',
        orphan_payment: 'Orphan Payment',
        duplicate_payment: 'Duplicate Payment',
        status_mismatch: 'Status Mismatch',
        data_quality: 'Data Quality Issue',
      },
      chartInstance: null,
      searchTimeout: null,
    }
  },
  mounted() {
    this.fetchSummary()
    this.fetchDiscrepancies()
  },
  methods: {
    async handleOrdersUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      const form = new FormData()
      form.append('file', file)
      try {
        const res = await api.post('/upload/orders/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.uploadStatus.orders = res.data.detail
      } catch (err) {
        this.uploadStatus.orders = err.response?.data?.detail || 'Upload failed'
      }
    },
    async handlePaymentsUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      const form = new FormData()
      form.append('file', file)
      try {
        const res = await api.post('/upload/payments/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.uploadStatus.payments = res.data.detail
      } catch (err) {
        this.uploadStatus.payments = err.response?.data?.detail || 'Upload failed'
      }
    },
    async runReconcile() {
      this.reconciling = true
      this.reconcileStatus = ''
      try {
        const res = await api.post('/reconcile/')
        this.reconcileStatus = res.data.detail
        await this.fetchSummary()
        await this.fetchDiscrepancies()
      } catch (err) {
        this.reconcileStatus = err.response?.data?.detail || 'Reconciliation failed'
      } finally {
        this.reconciling = false
      }
    },
    async fetchSummary() {
      try {
        const res = await api.get('/dashboard/summary/')
        this.summary = res.data
        this.$nextTick(() => this.renderChart())
      } catch (err) {
        console.error(err)
      }
    },
    async fetchDiscrepancies() {
      this.loadingDiscrepancies = true
      try {
        const params = { page_size: 100 }
        if (this.filterType) params.type = this.filterType
        if (this.searchQuery) params.search = this.searchQuery
        const res = await api.get('/discrepancies/', { params })
        this.discrepancies = res.data.results || []
      } catch (err) {
        console.error(err)
      } finally {
        this.loadingDiscrepancies = false
      }
    },
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => this.fetchDiscrepancies(), 300)
    },
    renderChart() {
      if (!this.summary || !this.$refs.chartCanvas) return
      const labels = Object.keys(this.summary.discrepancy_breakdown)
      const data = Object.values(this.summary.discrepancy_breakdown)
      const colors = [
        '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#3B82F6', '#6B7280', '#14B8A6',
      ]
      if (this.chartInstance) {
        this.chartInstance.destroy()
      }
      this.chartInstance = new Chart(this.$refs.chartCanvas, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: colors.slice(0, labels.length),
            borderWidth: 0,
            hoverOffset: 4,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '65%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle',
                font: { size: 11 },
              },
            },
            tooltip: {
              backgroundColor: 'rgba(17, 24, 39, 0.9)',
              padding: 12,
              cornerRadius: 8,
              callbacks: {
                label: (context) => `${context.label}: ${context.raw}`,
              },
            },
          },
        },
      })
    },
    async explainOne(d) {
      this.explainingId = d.id
      this.explanation = null
      try {
        const res = await api.post('/explain/', { result_ids: [d.id] })
        this.explanation = res.data.explanation
      } catch (err) {
        this.explanation = err.response?.data?.detail || 'Explanation failed. Please try again.'
      } finally {
        this.explainingId = null
      }
    },
    typeBadgeClass(typeCode) {
      const map = {
        fully_reconciled: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
        amount_mismatch: 'bg-amber-50 text-amber-700 border border-amber-100',
        currency_mismatch: 'bg-purple-50 text-purple-700 border border-purple-100',
        missing_payment: 'bg-rose-50 text-rose-700 border border-rose-100',
        orphan_payment: 'bg-rose-50 text-rose-700 border border-rose-100',
        duplicate_payment: 'bg-pink-50 text-pink-700 border border-pink-100',
        status_mismatch: 'bg-blue-50 text-blue-700 border border-blue-100',
        data_quality: 'bg-gray-50 text-gray-700 border border-gray-100',
      }
      return map[typeCode] || 'bg-gray-50 text-gray-700 border border-gray-100'
    },
    formatCurrency(val) {
      const num = parseFloat(val)
      if (isNaN(num)) return '$0.00'
      return '$' + num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
  },
}
</script>
