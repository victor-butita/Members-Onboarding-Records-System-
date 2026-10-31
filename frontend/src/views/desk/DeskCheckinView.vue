<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import {
  UserCheck, Search, CheckCircle2, AlertCircle, FileText, ExternalLink,
  ShieldCheck, RefreshCw, X, RotateCcw, Edit
} from 'lucide-vue-next'

const members = ref([])
const searchQuery = ref('')
const selectedStage = ref('ALL')
const isLoading = ref(true)

// Drawer / Modal states
const activeMember = ref(null)
const isSubmitting = ref(false)
const modalError = ref('')
const modalSuccess = ref('')

// Verification form state
const verifyForm = ref({
  verified: true,
  biodata_confirmed: true,
  oath_recorded: true,
  assets_declaration_filed: true,
  notes: ''
})

// Reopen modal state
const showReopenModal = ref(false)
const reopenReason = ref('')

const fetchDeskQueue = async () => {
  isLoading.value = true
  try {
    let url = `/desk/queue?q=${encodeURIComponent(searchQuery.value)}`
    if (selectedStage.value !== 'ALL') {
      url += `&stage=${selectedStage.value}`
    }
    const res = await api.get(url)
    members.value = res.data
  } catch (err) {
    console.error('Failed to load desk queue', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDeskQueue()
})

const openVerifyModal = (m) => {
  activeMember.value = m
  verifyForm.value.verified = m.original_docs_verified || true
  verifyForm.value.biodata_confirmed = m.biodata_confirmed || true
  verifyForm.value.oath_recorded = m.oath_recorded || false
  verifyForm.value.assets_declaration_filed = m.assets_declaration_filed || false
  verifyForm.value.notes = ''
  modalError.value = ''
  modalSuccess.value = ''
}

const performCheckin = async (m) => {
  try {
    await api.post('/desk/checkin', { member_id: m.id })
    fetchDeskQueue()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to check in member.')
  }
}

const saveVerification = async () => {
  if (!activeMember.value) return
  isSubmitting.value = true
  modalError.value = ''
  modalSuccess.value = ''

  try {
    await api.post('/desk/verify-documents', {
      member_id: activeMember.value.id,
      verified: verifyForm.value.verified,
      biodata_confirmed: verifyForm.value.biodata_confirmed,
      oath_recorded: verifyForm.value.oath_recorded,
      assets_declaration_filed: verifyForm.value.assets_declaration_filed,
      notes: verifyForm.value.notes
    })
    modalSuccess.value = 'Original documents & statutory declarations recorded.'
    setTimeout(() => {
      activeMember.value = null
      fetchDeskQueue()
    }, 1000)
  } catch (err) {
    modalError.value = err.response?.data?.detail || 'Failed to save verification.'
  } finally {
    isSubmitting.value = false
  }
}

const triggerReopen = async () => {
  if (!activeMember.value || !reopenReason.value) return
  try {
    await api.post('/desk/reopen', {
      member_id: activeMember.value.id,
      reason: reopenReason.value
    })
    showReopenModal.value = false
    reopenReason.value = ''
    activeMember.value = null
    fetchDeskQueue()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to reopen form.')
  }
}
</script>

<template>
  <div class="space-y-6">
    
    <!-- Top Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Stage 3 · Registration Desk</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Clerks (L&P) Physical Check-In & Original Document Audit</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="fetchDeskQueue" 
          class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Filters & Search Bar -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
      <div class="relative w-full sm:w-80">
        <input 
          type="text" 
          v-model="searchQuery"
          @input="fetchDeskQueue"
          placeholder="Search by name, ID, or reference..." 
          class="w-full pl-9 pr-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>

      <div class="flex items-center space-x-2 w-full sm:w-auto">
        <span class="text-slate-500 font-semibold">Filter Stage:</span>
        <select v-model="selectedStage" @change="fetchDeskQueue" class="px-3 py-2 border rounded-xl outline-none bg-slate-50 text-slate-800 font-medium">
          <option value="ALL">All Stages</option>
          <option value="GAZETTED">Gazetted Only (Not Submitted)</option>
          <option value="SUBMITTED_ONLINE">Submitted Online</option>
          <option value="DESK_CHECKED_IN">Desk Checked In</option>
          <option value="FULLY_CLEARED">Fully Cleared</option>
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
              <th class="py-3 px-4">National ID</th>
              <th class="py-3 px-4">Stage</th>
              <th class="py-3 px-4">Original Docs</th>
              <th class="py-3 px-4">Oath / Assets</th>
              <th class="py-3 px-4 text-right">Desk Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="m in members" :key="m.id" class="hover:bg-slate-50/80 transition-colors">
              <td class="py-3 px-4 font-bold text-slate-900">
                <div>Hon. {{ m.full_name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">{{ m.submission_reference || 'Not submitted online' }}</div>
              </td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-800">
                  {{ m.category.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <div>{{ m.county || '—' }}</div>
                <div class="text-[10px] text-slate-400">{{ m.constituency || 'Nominated' }}</div>
              </td>
              <td class="py-3 px-4 font-mono">{{ m.national_id || 'Pending' }}</td>
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
                <span v-if="m.original_docs_verified" class="text-emerald-700 font-bold flex items-center space-x-1">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Verified</span>
                </span>
                <span v-else class="text-slate-400">Pending</span>
              </td>
              <td class="py-3 px-4">
                <span v-if="m.oath_recorded && m.assets_declaration_filed" class="text-emerald-700 font-bold flex items-center space-x-1">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Filed</span>
                </span>
                <span v-else class="text-slate-400">Pending</span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    v-if="m.stage === 'GAZETTED' || m.stage === 'SUBMITTED_ONLINE'"
                    @click="performCheckin(m)"
                    class="px-2.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] shadow-sm"
                  >
                    Check In
                  </button>
                  <button 
                    @click="openVerifyModal(m)"
                    class="px-2.5 py-1.5 rounded-lg bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-[11px] shadow-sm"
                  >
                    Verify & Oath
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Document Verification & Oath Modal -->
    <div v-if="activeMember" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 border border-slate-200 max-h-[90vh] overflow-y-auto">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <div class="text-[10px] font-bold text-parliament-gold uppercase">Physical Registration Station</div>
            <h3 class="text-base font-bold text-slate-900">Document Verification · Hon. {{ activeMember.full_name }}</h3>
          </div>
          <button @click="activeMember = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="modalError" class="p-3 mb-4 rounded-xl bg-red-50 text-red-700 border border-red-200 text-xs">
          {{ modalError }}
        </div>
        <div v-if="modalSuccess" class="p-3 mb-4 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs">
          {{ modalSuccess }}
        </div>

        <div class="space-y-4 text-xs">
          
          <!-- Document Comparison Area -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h4 class="font-bold text-slate-800">Scanned Documents on Record</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="p-3 rounded-lg bg-white border border-slate-200">
                <span class="text-slate-500 block mb-1">National ID Scan:</span>
                <a 
                  v-if="activeMember.id_document_path" 
                  :href="activeMember.id_document_path" 
                  target="_blank"
                  class="text-parliament-green font-bold flex items-center space-x-1 hover:underline"
                >
                  <FileText class="w-4 h-4" />
                  <span>View Scanned ID</span>
                  <ExternalLink class="w-3 h-3 ml-1" />
                </a>
                <span v-else class="text-slate-400 italic">No digital ID uploaded</span>
              </div>

              <div class="p-3 rounded-lg bg-white border border-slate-200">
                <span class="text-slate-500 block mb-1">IEBC Certificate:</span>
                <a 
                  v-if="activeMember.iebc_cert_path" 
                  :href="activeMember.iebc_cert_path" 
                  target="_blank"
                  class="text-parliament-green font-bold flex items-center space-x-1 hover:underline"
                >
                  <FileText class="w-4 h-4" />
                  <span>View IEBC Certificate</span>
                  <ExternalLink class="w-3 h-3 ml-1" />
                </a>
                <span v-else class="text-slate-400 italic">No digital IEBC cert uploaded</span>
              </div>
            </div>
          </div>

          <!-- Clerks Checklist -->
          <div class="space-y-3 pt-2">
            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
              <input type="checkbox" v-model="verifyForm.verified" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block">1. Original ID & IEBC Certificate Physically Inspected</span>
                <span class="text-slate-500 text-[11px]">Compared physical original documents against gazetted records and uploads.</span>
              </div>
            </label>

            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
              <input type="checkbox" v-model="verifyForm.biodata_confirmed" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block">2. Biodata & Personal Particulars Confirmed</span>
                <span class="text-slate-500 text-[11px]">Member confirmed date of birth, contact details, KRA PIN, and next of kin.</span>
              </div>
            </label>

            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
              <input type="checkbox" v-model="verifyForm.oath_recorded" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block">3. Parliamentary Oath & Code of Conduct Registered</span>
                <span class="text-slate-500 text-[11px]">Member signed the official induction code of conduct and oath documentation.</span>
              </div>
            </label>

            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
              <input type="checkbox" v-model="verifyForm.assets_declaration_filed" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block">4. Initial Declaration of Assets & Liabilities Filed</span>
                <span class="text-slate-500 text-[11px]">Sealed declaration envelope received in accordance with the Public Officer Ethics Act.</span>
              </div>
            </label>
          </div>

          <!-- Notes -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Clerk Notes / Remarks</label>
            <textarea v-model="verifyForm.notes" rows="2" placeholder="e.g. Originals verified in order, member requested oath in Kiswahili" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"></textarea>
          </div>

          <!-- Footer Actions -->
          <div class="flex items-center justify-between pt-4 border-t border-slate-100">
            <button 
              type="button" 
              @click="showReopenModal = true"
              class="px-3 py-1.5 rounded-lg border border-amber-300 bg-amber-50 text-amber-800 font-bold hover:bg-amber-100 flex items-center space-x-1"
            >
              <RotateCcw class="w-3.5 h-3.5" />
              <span>Reopen Online Form for Correction</span>
            </button>

            <div class="flex items-center space-x-2">
              <button 
                type="button" 
                @click="activeMember = null" 
                class="px-4 py-2 rounded-xl border border-slate-200 font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button 
                type="button" 
                @click="saveVerification"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold shadow-md disabled:opacity-50"
              >
                {{ isSubmitting ? 'Saving...' : 'Confirm & Tick Desk Verification' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Reopen Modal -->
    <div v-if="showReopenModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200">
        <h3 class="text-base font-bold text-slate-900 mb-2">Reopen Online Portal for Hon. {{ activeMember.full_name }}</h3>
        <p class="text-xs text-slate-600 mb-4">
          This will unlock the member's public form so they can update or upload revised documents online.
        </p>

        <div class="text-xs space-y-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Reason for Reopening *</label>
            <input type="text" v-model="reopenReason" required placeholder="e.g. Scanned ID was illegible / Correction of phone number" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
          </div>

          <div class="flex justify-end space-x-2 pt-2">
            <button @click="showReopenModal = false" class="px-3 py-1.5 border rounded-lg text-slate-600">Cancel</button>
            <button @click="triggerReopen" class="px-4 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg">Confirm Reopen</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
