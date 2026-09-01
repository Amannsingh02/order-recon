<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />

    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- Upload Section -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold mb-4">Data Ingestion</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Orders CSV</label>
            <input
              type="file"
              accept=".csv"
              @change="handleOrdersUpload"
              class="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50"
            />
            <p v-if="uploadStatus.orders" class="mt-2 text-sm text-green-600">{{ uploadStatus.orders }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Payments CSV</label>
            <input
              type="file"
              accept=".csv"
              @change="handlePaymentsUpload"
              class="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50"
            />
            <p v-if="uploadStatus.payments" class="mt-2 text-sm text-green-600">{{ uploadStatus.payments }}</p>
          </div>
        </div>

        <div class="mt-6">
          <button
            @click="runReconcile"
            :disabled="reconciling"
            class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
          >
            {{ reconciling ? 'Running Reconciliation...' : 'Run Reconciliation' }}
          </button>
          <p v-if="reconcileStatus" class="mt-2 text-sm text-gray-600">{{ reconcileStatus }}</p>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="summary" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <StatCard label="Total Orders" :value="summary.total_orders" />
        <StatCard label="Total Payments" :value="summary.total_payments" />
        <StatCard label="Reconciled Value" :value="summary.total_reconciled_value" type="success" />
        <StatCard label="Disputed Value" :value="summary.total_disputed_value" type="warning" />
        <StatCard label="At Risk" :value="summary.total_at_risk" type="danger" />
      </div>

      <!-- Chart + Table -->
      <div v-if="summary" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Discrepancy Chart -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Discrepancy Breakdown</h3>
          <div class="h-64">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h3 class="text-lg font-semibold mb-4">Discrepancies</h3>

          <div class="flex flex-col sm:flex-row gap-4 mb-4">
            <select v-model="filterType" @change="fetchDiscrepancies" class="border border-gray-300 rounded px-3 py-2">
              <option value="">All Types</option>
              <option v-for="(label, key) in typeOptions" :key="key" :value="key">{{ label }}</option>
            </select>
            <input
              v-model="searchQuery"
              @input="fetchDiscrepancies"
              placeholder="Search order ID, reference, or description..."
              class="flex-1 border border-gray-300 rounded px-3 py-2"
            />
          </div>

          <div v-if="loadingDiscrepancies" class="text-center py-8 text-gray-500">Loading...</div>

          <div v-else-if="discrepancies.length === 0" class="text-center py-8 text-gray-500">No discrepancies found.</div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">Type</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">Order</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">Payment</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">At Risk</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">Description</th>
                  <th class="px-4 py-2 text-left font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="d in discrepancies" :key="d.id" class="hover:bg-gray-50">
                  <td class="px-4 py-2">
                    <span
                      class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                      :class="typeBadgeClass(d.discrepancy_type)"
                    >
                      {{ d.discrepancy_type_display }}
                    </span>
                  </td>
                  <td class="px-4 py-2">{{ d.order ? d.order.order_id : '-' }}</td>
                  <td class="px-4 py-2">{{ d.payment ? d.payment.transaction_ref : '-' }}</td>
                  <td class="px-4 py-2">${{ parseFloat(d.amount_at_risk).toFixed(2) }}</td>
                  <td class="px-4 py-2 max-w-xs truncate" :title="d.description">{{ d.description }}</td>
                  <td class="px-4 py-2">
                    <button
                      v-if="d.discrepancy_type !== 'fully_reconciled'"
                      @click="explainOne(d)"
                      :disabled="explainingId === d.id"
                      class="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
                    >
                      {{ explainingId === d.id ? 'Thinking...' : 'Explain' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- LLM Explanation Panel -->
          <div v-if="explanation" class="mt-6 bg-indigo-50 border border-indigo-200 rounded p-4">
            <div class="flex justify-between items-start">
              <h4 class="font-semibold text-indigo-900">AI Explanation</h4>
              <button @click="explanation = null" class="text-indigo-700 hover:text-indigo-900 text-sm">Close</button>
            </div>
            <p class="mt-2 text-sm text-indigo-800 whitespace-pre-wrap">{{ explanation }}</p>
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
        type: 'pie',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: colors.slice(0, labels.length),
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' },
          },
        },
      })
    },
    async explainOne(d) {
      this.explainingId = d.id
      this.explanation = null
      try {
        const res = await api.post('/explain/', { result_ids: [d.id] })
        const parsed = res.data.explanation
        // Try to extract a readable string from structured JSON response
        this.explanation = typeof parsed === 'string' ? parsed : JSON.stringify(parsed, null, 2)
      } catch (err) {
        this.explanation = err.response?.data?.detail || 'Explanation failed. Please try again.'
      } finally {
        this.explainingId = null
      }
    },
    typeBadgeClass(typeCode) {
      const map = {
        fully_reconciled: 'bg-green-100 text-green-800',
        amount_mismatch: 'bg-yellow-100 text-yellow-800',
        currency_mismatch: 'bg-purple-100 text-purple-800',
        missing_payment: 'bg-red-100 text-red-800',
        orphan_payment: 'bg-red-100 text-red-800',
        duplicate_payment: 'bg-pink-100 text-pink-800',
        status_mismatch: 'bg-blue-100 text-blue-800',
        data_quality: 'bg-gray-100 text-gray-800',
      }
      return map[typeCode] || 'bg-gray-100 text-gray-800'
    },
  },
}
</script>
