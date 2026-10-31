<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import {
  Users, Search, Filter, CheckCircle2, AlertCircle, ArrowRight,
  ExternalLink, Download, RefreshCw, X, ShieldAlert
} from 'lucide-vue-next'

const router = useRouter()
const members = ref([])
const isLoading = ref(true)

// Filters
const searchQuery = ref('')
const selectedCategory = ref('ALL')
const selectedStage = ref('ALL')
const selectedStatus = ref('ALL')

// Status change modal
const activeStatusMember = ref(null)
const newStatus = ref('PETITIONED')
const statusReason = ref('')
const isSubmittingStatus = ref(false)

const fetchMembers = async () => {
  isLoading.value = true
  try {
    let url = `/members/?q=${encodeURIComponent(searchQuery.value)}&limit=400`
    if (selectedCategory.value !== 'ALL') url += `&category=${selectedCategory.value}`
    if (selectedStage.value !== 'ALL') url += `&stage=${selectedStage.value}`
    if (selectedStatus.value !== 'ALL') url += `&status=${selectedStatus.value}`

    const res = await api.get(url)
    members.value = res.data
  } catch (err) {
    console.error('Failed to load members', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchMembers()
})

const exportCsv = () => {
  window.location.href = `/api/v1/reports/export/csv?category=${selectedCategory.value}`
}

const openStatusModal = (m) => {
  activeStatusMember.value = m
  newStatus.value = m.status === 'ACTIVE' ? 'PETITIONED' : 'ACTIVE'
  statusReason.value = ''
}

const submitStatusChange = async () => {
  if (!activeStatusMember.value || !statusReason.value) return
  isSubmittingStatus.value = true
  try {
    await api.post(`/members/${activeStatusMember.value.id}/status?status=${newStatus.value}&reason=${encodeURIComponent(statusReason.value)}`)
    activeStatusMember.value = null
    fetchMembers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to update status.')
  } finally {
    isSubmittingStatus.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Parliamentary Roll</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Register of Members (14th Parliament)</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="exportCsv"
          class="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-black text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm"
        >
          <Download class="w-4 h-4 text-parliament-gold" />
          <span>Export CSV</span>
        </button>
        <button 
          @click="fetchMembers" 
          class="px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
      <div class="relative w-full sm:w-72">
        <input 
          type="text" 
          v-model="searchQuery"
          @input="fetchMembers"
          placeholder="Search name, ID, county, party..." 
          class="w-full pl-9 pr-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Category Filter -->
        <select v-model="selectedCategory" @change="fetchMembers" class="px-3 py-2 border rounded-xl bg-slate-50 outline-none">
          <option value="ALL">All Categories</option>
          <option value="MP">Constituency MPs (290)</option>
          <option value="WOMAN_REP">County Woman Reps (47)</option>
          <option value="NOMINATED">Nominated Members (12)</option>
        </select>

        <!-- Stage Filter -->
        <select v-model="selectedStage" @change="fetchMembers" class="px-3 py-2 border rounded-xl bg-slate-50 outline-none">
          <option value="ALL">All Stages</option>
          <option value="GAZETTED">1. Gazetted</option>
          <option value="SUBMITTED_ONLINE">2. Submitted Online</option>
          <option value="DESK_CHECKED_IN">3. Desk Checked In</option>
          <option value="FULLY_CLEARED">4. Fully Cleared</option>
        </select>

        <!-- Status Filter -->
        <select v-model="selectedStatus" @change="fetchMembers" class="px-3 py-2 border rounded-xl bg-slate-50 outline-none">
          <option value="ALL">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="PETITIONED">Petitioned</option>
          <option value="NULLIFIED">Nullified / Vacant</option>
        </select>
      </div>
    </div>

    <!-- Members Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-600 font-bold">
            <tr>
              <th class="py-3 px-4">Member Name</th>
              <th class="py-3 px-4">Category</th>
              <th class="py-3 px-4">County / Constituency</th>
              <th class="py-3 px-4">Party</th>
              <th class="py-3 px-4">Stage</th>
              <th class="py-3 px-4">Legal Status</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="m in members" :key="m.id" class="hover:bg-slate-50/80">
              <td class="py-3 px-4 font-bold text-slate-900">
                <router-link :to="`/members/${m.id}`" class="hover:text-parliament-green flex items-center space-x-1.5">
                  <span>Hon. {{ m.full_name }}</span>
                </router-link>
                <div class="text-[10px] text-slate-400 font-mono">{{ m.submission_reference || 'Ref pending' }}</div>
              </td>
              <td class="py-3 px-4">
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="{
                    'bg-emerald-100 text-emerald-800': m.category === 'MP',
                    'bg-purple-100 text-purple-800': m.category === 'WOMAN_REP',
                    'bg-blue-100 text-blue-800': m.category === 'NOMINATED'
                  }"
                >
                  {{ m.category.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <div>{{ m.county || '—' }}</div>
                <div class="text-[10px] text-slate-400">{{ m.constituency || 'Nominated Seat' }}</div>
              </td>
              <td class="py-3 px-4 font-medium">{{ m.party }}</td>
              <td class="py-3 px-4">
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="{
                    'bg-slate-100 text-slate-700': m.stage === 'GAZETTED',
                    'bg-amber-100 text-amber-800': m.stage === 'SUBMITTED_ONLINE',
                    'bg-blue-100 text-blue-800': m.stage === 'DESK_CHECKED_IN',
                    'bg-emerald-100 text-emerald-800': m.stage === 'FULLY_CLEARED'
                  }"
                >
                  {{ m.stage.replace(/_/g, ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="{
                    'bg-emerald-50 text-emerald-800 border border-emerald-200': m.status === 'ACTIVE',
                    'bg-amber-50 text-amber-800 border border-amber-200': m.status === 'PETITIONED',
                    'bg-red-50 text-red-800 border border-red-200': m.status === 'NULLIFIED'
                  }"
                >
                  {{ m.status }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="openStatusModal(m)"
                    class="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700"
                    title="Update Court Petition or Nullification Status"
                  >
                    <ShieldAlert class="w-4 h-4" />
                  </button>
                  <router-link 
                    :to="`/members/${m.id}`" 
                    class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-[11px]"
                  >
                    Dossier 360°
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Status Change Modal (e.g. Election Petitions) -->
    <div v-if="activeStatusMember" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200 text-xs">
        <h3 class="text-sm font-bold text-slate-900 mb-1">Update Member Legal Status</h3>
        <p class="text-slate-500 mb-4">Hon. {{ activeStatusMember.full_name }} ({{ activeStatusMember.constituency || activeStatusMember.county }})</p>

        <div class="space-y-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">New Status</label>
            <select v-model="newStatus" class="w-full px-3 py-2 border rounded-xl outline-none">
              <option value="ACTIVE">ACTIVE</option>
              <option value="PETITIONED">PETITIONED (Election Petition Pending)</option>
              <option value="NULLIFIED">NULLIFIED (Seat Declared Vacant by Court)</option>
              <option value="WITHDRAWN">WITHDRAWN</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Legal Reason & Citation *</label>
            <textarea v-model="statusReason" required rows="2" placeholder="e.g. High Court Election Petition No. 12 of 2027 filed at Milimani Law Courts" class="w-full px-3 py-2 border rounded-xl outline-none"></textarea>
          </div>

          <div class="flex justify-end space-x-2 pt-2 border-t">
            <button @click="activeStatusMember = null" class="px-3 py-1.5 border rounded-lg">Cancel</button>
            <button @click="submitStatusChange" :disabled="isSubmittingStatus" class="px-4 py-1.5 bg-slate-900 text-white font-bold rounded-lg shadow-sm">Save Status</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
