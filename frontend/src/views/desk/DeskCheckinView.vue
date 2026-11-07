<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import {
  UserCheck, Search, CheckCircle2, AlertCircle, FileText, ExternalLink,
  ShieldCheck, RefreshCw, X, RotateCcw, Edit, Eye, Save, ArrowRight
} from 'lucide-vue-next'

const members = ref([])
const searchQuery = ref('')
const selectedStage = ref('ALL')
const isLoading = ref(true)

// Drawer / Modal states
const activeMember = ref(null)
const editingMember = ref(null)
const isSubmitting = ref(false)
const modalError = ref('')
const modalSuccess = ref('')
const editError = ref('')
const editSuccess = ref('')

// Verification form state (strictly Physical Docs + Biodata)
const verifyForm = ref({
  verified: true,
  biodata_confirmed: true,
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
  verifyForm.value.verified = m.original_docs_verified !== false
  verifyForm.value.biodata_confirmed = m.biodata_confirmed !== false
  verifyForm.value.notes = ''
  modalError.value = ''
  modalSuccess.value = ''
}

const openEditModal = (m) => {
  editingMember.value = {
    id: m.id,
    full_name: m.full_name,
    surname: m.surname,
    other_names: m.other_names,
    category: m.category,
    county: m.county,
    constituency: m.constituency,
    party: m.party,
    national_id: m.national_id || '',
    gender: m.gender || 'MALE',
    date_of_birth: m.date_of_birth || '',
    phone: m.phone || '',
    email: m.email || '',
    kra_pin: m.kra_pin || '',
    postal_address: m.postal_address || '',
    qualifications: m.qualifications || '',
    pa_name: m.pa_name || m.next_of_kin_name || '',
    pa_phone: m.pa_phone || m.next_of_kin_phone || '',
    pa_email: m.pa_email || m.next_of_kin_email || '',
    notes: m.notes || ''
  }
  editError.value = ''
  editSuccess.value = ''
}

const saveMemberEdits = async () => {
  if (!editingMember.value) return
  isSubmitting.value = true
  editError.value = ''
  editSuccess.value = ''

  try {
    const payload = {
      surname: editingMember.value.surname,
      other_names: editingMember.value.other_names,
      category: editingMember.value.category,
      county: editingMember.value.county,
      constituency: editingMember.value.constituency,
      party: editingMember.value.party,
      national_id: editingMember.value.national_id,
      gender: editingMember.value.gender,
      date_of_birth: editingMember.value.date_of_birth,
      phone: editingMember.value.phone,
      email: editingMember.value.email,
      kra_pin: editingMember.value.kra_pin,
      postal_address: editingMember.value.postal_address,
      qualifications: editingMember.value.qualifications,
      pa_name: editingMember.value.pa_name,
      pa_phone: editingMember.value.pa_phone,
      pa_email: editingMember.value.pa_email,
      next_of_kin_name: editingMember.value.pa_name,
      next_of_kin_relation: 'Personal Assistant',
      next_of_kin_phone: editingMember.value.pa_phone,
      next_of_kin_email: editingMember.value.pa_email,
      notes: editingMember.value.notes
    }

    await api.put(`/members/${editingMember.value.id}`, payload)
    editSuccess.value = 'Member particulars updated successfully.'
    setTimeout(() => {
      editingMember.value = null
      fetchDeskQueue()
    }, 900)
  } catch (err) {
    editError.value = err.response?.data?.detail || 'Failed to update member particulars.'
  } finally {
    isSubmitting.value = false
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
      notes: verifyForm.value.notes
    })
    modalSuccess.value = 'Physical documents and biodata confirmation successfully recorded.'
    setTimeout(() => {
      activeMember.value = null
      fetchDeskQueue()
    }, 900)
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
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Clerks (L&P) Physical Check-In & Document Verification</h1>
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
          class="w-full pl-9 pr-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green text-slate-900 font-medium"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>

      <div class="flex items-center space-x-2 w-full sm:w-auto">
        <span class="text-slate-500 font-semibold">Filter Stage:</span>
        <select v-model="selectedStage" @change="fetchDeskQueue" class="px-3 py-2 border rounded-xl outline-none bg-slate-50 text-slate-800 font-medium">
          <option value="ALL">All Stages</option>
          <option value="GAZETTED">Gazetted Only (Not Submitted)</option>
          <option value="SUBMITTED_ONLINE">Submitted Online</option>
          <option value="DESK_CHECKED_IN">Onboarded / Checked In</option>
          <option value="FULLY_CLEARED">Fully Cleared</option>
        </select>
      </div>
    </div>

    <!-- Members Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-700 font-bold uppercase tracking-wider text-[11px]">
            <tr>
              <th class="py-3.5 px-4">Member Name</th>
              <th class="py-3.5 px-4">Category</th>
              <th class="py-3.5 px-4">County / Seat</th>
              <th class="py-3.5 px-4">National ID</th>
              <th class="py-3.5 px-4">Current Stage</th>
              <th class="py-3.5 px-4">Physical Docs</th>
              <th class="py-3.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="m in members" :key="m.id" class="hover:bg-slate-50/80 transition-colors">
              <td class="py-3 px-4 font-bold text-slate-900">
                <div class="text-xs">Hon. {{ m.full_name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">{{ m.submission_reference || 'Not submitted online' }}</div>
              </td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-800">
                  {{ m.category.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <div class="font-medium text-slate-900">{{ m.county || '—' }}</div>
                <div class="text-[10px] text-slate-400">{{ m.constituency || 'Nominated' }}</div>
              </td>
              <td class="py-3 px-4 font-mono font-medium">{{ m.national_id || 'Pending' }}</td>
              <td class="py-3 px-4">
                <span 
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-bold"
                  :class="{
                    'bg-slate-100 text-slate-700': m.stage === 'GAZETTED',
                    'bg-amber-100 text-amber-800': m.stage === 'SUBMITTED_ONLINE',
                    'bg-blue-100 text-blue-800': m.stage === 'DESK_CHECKED_IN',
                    'bg-emerald-100 text-emerald-800': m.stage === 'FULLY_CLEARED'
                  }"
                >
                  {{ m.stage === 'DESK_CHECKED_IN' ? 'ONBOARDED' : m.stage.replace(/_/g, ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span v-if="m.original_docs_verified && m.biodata_confirmed" class="text-emerald-700 font-bold flex items-center space-x-1">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Verified</span>
                </span>
                <span v-else class="text-slate-400 font-medium">Pending</span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="openEditModal(m)"
                    class="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-bold text-[11px] shadow-sm flex items-center space-x-1"
                    title="View submitted details and correct any errors"
                  >
                    <Edit class="w-3.5 h-3.5 text-slate-600" />
                    <span>Edit</span>
                  </button>
                  <button 
                    @click="openVerifyModal(m)"
                    class="px-2.5 py-1.5 rounded-lg bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-[11px] shadow-sm flex items-center space-x-1"
                    title="Conduct physical documents inspection and biodata confirmation"
                  >
                    <CheckCircle2 class="w-3.5 h-3.5 text-white" />
                    <span>Verify</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL 1: VIEW & EDIT MEMBER SUBMITTED DETAILS -->
    <div v-if="editingMember" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full p-6 border border-slate-200 max-h-[92vh] overflow-y-auto">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <div class="text-[10px] font-bold text-parliament-gold uppercase">Registration Desk · Member Particulars</div>
            <h3 class="text-base font-extrabold text-slate-900">View / Update Particulars: Hon. {{ editingMember.full_name }}</h3>
          </div>
          <button @click="editingMember = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="editError" class="p-3 mb-4 rounded-xl bg-red-50 text-red-700 border border-red-200 text-xs">
          {{ editError }}
        </div>
        <div v-if="editSuccess" class="p-3 mb-4 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs">
          {{ editSuccess }}
        </div>

        <form @submit.prevent="saveMemberEdits" class="space-y-5 text-xs">
          
          <!-- Section 1: Names and Gazette Classification -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wide">1. Gazette Particulars</h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Surname *</label>
                <input type="text" v-model="editingMember.surname" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div class="sm:col-span-2">
                <label class="block font-semibold text-slate-700 mb-1">Other Names *</label>
                <input type="text" v-model="editingMember.other_names" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Category *</label>
                <select v-model="editingMember.category" class="w-full px-3 py-2 border rounded-xl outline-none bg-white font-medium">
                  <option value="MP">MP (Constituency)</option>
                  <option value="WOMAN_REP">Woman Representative</option>
                  <option value="NOMINATED">Nominated MP</option>
                </select>
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">County</label>
                <input type="text" v-model="editingMember.county" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Constituency / Seat</label>
                <input type="text" v-model="editingMember.constituency" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div class="sm:col-span-3">
                <label class="block font-semibold text-slate-700 mb-1">Political Party *</label>
                <input type="text" v-model="editingMember.party" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
            </div>
          </div>

          <!-- Section 2: Contact & Identification -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wide">2. Identification & Contact Details</h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">National ID / Passport *</label>
                <input type="text" v-model="editingMember.national_id" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-mono font-bold" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Date of Birth</label>
                <input type="date" v-model="editingMember.date_of_birth" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Gender</label>
                <select v-model="editingMember.gender" class="w-full px-3 py-2 border rounded-xl outline-none bg-white font-medium">
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                </select>
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Mobile Phone Number *</label>
                <input type="tel" v-model="editingMember.phone" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Email Address *</label>
                <input type="email" v-model="editingMember.email" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">KRA PIN Number *</label>
                <input type="text" v-model="editingMember.kra_pin" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green uppercase font-mono font-bold" />
              </div>
              <div class="sm:col-span-3">
                <label class="block font-semibold text-slate-700 mb-1">Postal Address</label>
                <input type="text" v-model="editingMember.postal_address" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div class="sm:col-span-3">
                <label class="block font-semibold text-slate-700 mb-1">Academic & Professional Qualifications</label>
                <textarea v-model="editingMember.qualifications" rows="2" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium"></textarea>
              </div>
            </div>
          </div>

          <!-- Section 3: Personal Assistant Liaison -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h4 class="font-bold text-slate-900 text-xs uppercase tracking-wide">3. Personal Assistant Information</h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">PA Full Name</label>
                <input type="text" v-model="editingMember.pa_name" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">PA Phone Number</label>
                <input type="tel" v-model="editingMember.pa_phone" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">PA Email Address</label>
                <input type="email" v-model="editingMember.pa_email" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
              </div>
            </div>
          </div>

          <!-- Section 4: Clerk Notes -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Clerk Desk Audit Notes</label>
            <textarea v-model="editingMember.notes" rows="2" placeholder="e.g. Corrected spelling of middle name from National ID card presentation" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium"></textarea>
          </div>

          <div class="flex items-center justify-end space-x-2 pt-4 border-t border-slate-100">
            <button 
              type="button" 
              @click="editingMember = null" 
              class="px-4 py-2 rounded-xl border border-slate-200 font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="isSubmitting"
              class="px-5 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold shadow-md flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Save class="w-4 h-4" />
              <span>{{ isSubmitting ? 'Saving Changes...' : 'Save Updates' }}</span>
            </button>
          </div>

        </form>
      </div>
    </div>

    <!-- MODAL 2: DOCUMENT VERIFICATION MODAL (Physical Docs + Biodata Confirmation) -->
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
                <span v-else class="text-slate-400 italic">No digital ID uploaded (verify physical original)</span>
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
                <span v-else class="text-slate-400 italic">No digital cert uploaded (verify physical original)</span>
              </div>
            </div>
          </div>

          <!-- Clerks Checklist (STRICTLY Physical Docs + Biodata Confirmation) -->
          <div class="space-y-3 pt-2">
            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors">
              <input type="checkbox" v-model="verifyForm.verified" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block text-sm">1. Physical Documents Verification</span>
                <span class="text-slate-500 text-[11px]">Original National Identity Card / Passport and official IEBC Certificate presented and physically verified against gazetted roll.</span>
              </div>
            </label>

            <label class="flex items-start space-x-2.5 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors">
              <input type="checkbox" v-model="verifyForm.biodata_confirmed" class="w-4 h-4 text-parliament-green rounded mt-0.5" />
              <div>
                <span class="font-bold text-slate-900 block text-sm">2. Bio Data Confirmation</span>
                <span class="text-slate-500 text-[11px]">Member confirmed date of birth, contact details, KRA PIN, postal address, and Personal Assistant particulars.</span>
              </div>
            </label>
          </div>

          <!-- Notes -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Clerk Notes / Remarks</label>
            <textarea v-model="verifyForm.notes" rows="2" placeholder="e.g. Originals verified in order, physical documents presented and verified." class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"></textarea>
          </div>

          <!-- Footer Actions -->
          <div class="flex items-center justify-between pt-4 border-t border-slate-100">
            <button 
              type="button" 
              @click="showReopenModal = true"
              class="px-3 py-1.5 rounded-lg border border-amber-300 bg-amber-50 text-amber-800 font-bold hover:bg-amber-100 flex items-center space-x-1"
            >
              <RotateCcw class="w-3.5 h-3.5" />
              <span>Reopen Online Form</span>
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
                class="px-5 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold shadow-md disabled:opacity-50 flex items-center space-x-1.5"
              >
                <CheckCircle2 class="w-4 h-4" />
                <span>{{ isSubmitting ? 'Saving...' : 'Confirm Verification & Onboard' }}</span>
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- REOPEN MODAL -->
    <div v-if="showReopenModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200">
        <h3 class="text-base font-bold text-slate-900 mb-2">Reopen Online Portal for Hon. {{ activeMember.full_name }}</h3>
        <p class="text-xs text-slate-600 mb-4">
          This will unlock the member's public form so they can update or upload revised documents online.
        </p>

        <div class="text-xs space-y-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Reason for Reopening *</label>
            <input type="text" v-model="reopenReason" required placeholder="e.g. Member requested to amend personal assistant email" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
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