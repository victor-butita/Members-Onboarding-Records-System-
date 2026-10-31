<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { History, Search, RefreshCw, ShieldCheck } from 'lucide-vue-next'

const logs = ref([])
const searchQuery = ref('')
const selectedUnit = ref('ALL')
const selectedAction = ref('ALL')
const isLoading = ref(true)

const fetchAudit = async () => {
  isLoading.value = true
  try {
    let url = `/audit/?limit=200`
    if (selectedUnit.value !== 'ALL') url += `&unit=${selectedUnit.value}`
    if (selectedAction.value !== 'ALL') url += `&action=${selectedAction.value}`
    if (searchQuery.value) url += `&user_name=${encodeURIComponent(searchQuery.value)}`

    const res = await api.get(url)
    logs.value = res.data
  } catch (err) {
    console.error('Failed to load audit logs', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAudit()
})
</script>

<template>
  <div class="space-y-6">
    
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Independent Audit & Security Trail</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">System Audit & Change Trail</h1>
      </div>
      <button 
        @click="fetchAudit" 
        class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
      >
        <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
        <span>Refresh Trail</span>
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-3 text-xs">
      <div class="relative w-64">
        <input 
          type="text" 
          v-model="searchQuery"
          @input="fetchAudit"
          placeholder="Filter by officer name..." 
          class="w-full pl-9 pr-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>

      <select v-model="selectedUnit" @change="fetchAudit" class="px-3 py-2 border rounded-xl bg-slate-50 outline-none">
        <option value="ALL">All Units</option>
        <option value="CLERK_LP">Clerks (L&P)</option>
        <option value="MEDIA_RELATIONS">Media Relations</option>
        <option value="ICT">ICT</option>
        <option value="SECURITY">Security</option>
        <option value="HR_FINANCE">HR & Finance</option>
        <option value="PUBLIC">Member Portal (Public)</option>
      </select>

      <select v-model="selectedAction" @change="fetchAudit" class="px-3 py-2 border rounded-xl bg-slate-50 outline-none">
        <option value="ALL">All Actions</option>
        <option value="LOGIN">LOGIN</option>
        <option value="CHECKIN">CHECKIN</option>
        <option value="TICK">TICK (Clearance)</option>
        <option value="EDIT">EDIT</option>
        <option value="SUBMIT">SUBMIT (Portal)</option>
        <option value="UPLOAD">UPLOAD (Gazette)</option>
        <option value="USER_CHANGE">USER CHANGE</option>
      </select>
    </div>

    <!-- Audit Log Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-600 font-bold">
            <tr>
              <th class="py-3 px-4">Timestamp (UTC)</th>
              <th class="py-3 px-4">Officer / User</th>
              <th class="py-3 px-4">Unit</th>
              <th class="py-3 px-4">Action</th>
              <th class="py-3 px-4">Resource Target</th>
              <th class="py-3 px-4">Action Details</th>
              <th class="py-3 px-4">IP Address</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700 font-mono text-[11px]">
            <tr v-for="a in logs" :key="a.id" class="hover:bg-slate-50/80">
              <td class="py-2 px-4 text-slate-500 whitespace-nowrap">{{ new Date(a.timestamp).toLocaleString() }}</td>
              <td class="py-2 px-4 font-bold text-slate-900 font-sans whitespace-nowrap">{{ a.user_name }}</td>
              <td class="py-2 px-4 font-sans"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100">{{ a.unit }}</span></td>
              <td class="py-2 px-4 font-bold text-parliament-green">{{ a.action }}</td>
              <td class="py-2 px-4 text-slate-600">{{ a.resource_type }} #{{ a.resource_id || '—' }}</td>
              <td class="py-2 px-4 font-sans text-slate-800">{{ a.details }}</td>
              <td class="py-2 px-4 text-slate-400 whitespace-nowrap">{{ a.ip_address || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>
