<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  CheckSquare, Camera, Cpu, Shield, Briefcase, Search, CheckCircle2,
  AlertCircle, Upload, User, RefreshCw, X, CreditCard
} from 'lucide-vue-next'

const auth = useAuthStore()

// Active clearance tab
const activeTab = ref('MEDIA') // MEDIA, ICT, SECURITY, HR_FINANCE
const queue = ref([])
const searchQuery = ref('')
const isLoading = ref(true)

// Modals & Action forms
const selectedMember = ref(null)
const isSubmitting = ref(false)
const actionError = ref('')
const actionSuccess = ref('')

// Media Photo action form
const mediaForm = ref({
  approved: true,
  photo_source: 'UPLOAD',
  notes: '',
  replacementFile: null
})

// ICT Biometrics action form
const ictForm = ref({
  collected: true,
  notes: ''
})

// Security action form
const securityForm = ref({
  cleared: true,
  badge_number: '',
  notes: '',
  vettingFile: null
})

// HR & Finance action form
const hrFinForm = ref({
  hr_verified: true,
  finance_verified: true,
  bank_name: 'Kenya Commercial Bank (KCB)',
  bank_account: '',
  bank_branch: 'Parliament Road',
  nssf_number: '',
  sha_number: '',
  notes: ''
})

const fetchQueue = async () => {
  isLoading.value = true
  try {
    let unitParam = 'MEDIA_RELATIONS'
    if (activeTab.value === 'ICT') unitParam = 'ICT'
    else if (activeTab.value === 'SECURITY') unitParam = 'SECURITY'
    else if (activeTab.value === 'HR_FINANCE') unitParam = 'HR_FINANCE'

    const res = await api.get(`/clearance/queue/${unitParam}?status_filter=ALL`)
    queue.value = res.data
  } catch (err) {
    console.error('Failed to load unit queue', err)
  } finally {
    isLoading.value = false
  }
}

// Automatically set active tab based on logged-in user unit if specialized
onMounted(() => {
  if (auth.unit === 'MEDIA_RELATIONS') activeTab.value = 'MEDIA'
  else if (auth.unit === 'ICT') activeTab.value = 'ICT'
  else if (auth.unit === 'SECURITY') activeTab.value = 'SECURITY'
  else if (auth.unit === 'HR_FINANCE') activeTab.value = 'HR_FINANCE'
  
  fetchQueue()
})

const switchTab = (tab) => {
  activeTab.value = tab
  selectedMember.value = null
  fetchQueue()
}

const openActionModal = (m) => {
  selectedMember.value = m
  actionError.value = ''
  actionSuccess.value = ''

  if (activeTab.value === 'MEDIA') {
    mediaForm.value.approved = m.photo_approved || true
    mediaForm.value.photo_source = m.photo_source || 'UPLOAD'
    mediaForm.value.notes = ''
    mediaForm.value.replacementFile = null
  } else if (activeTab.value === 'ICT') {
    ictForm.value.collected = m.biometrics_collected || true
    ictForm.value.notes = ''
  } else if (activeTab.value === 'SECURITY') {
    securityForm.value.cleared = m.security_cleared || true
    securityForm.value.badge_number = m.badge_number || `NA-14P-${String(m.id).padStart(3, '0')}`
    securityForm.value.notes = ''
    securityForm.value.vettingFile = null
  } else if (activeTab.value === 'HR_FINANCE') {
    hrFinForm.value.hr_verified = m.hr_verified || true
    hrFinForm.value.finance_verified = m.finance_verified || true
    hrFinForm.value.bank_name = m.bank_name || 'Kenya Commercial Bank (KCB)'
    hrFinForm.value.bank_account = m.bank_account || ''
    hrFinForm.value.bank_branch = m.bank_branch || 'Parliament Road Branch'
    hrFinForm.value.nssf_number = m.nssf_number || ''
    hrFinForm.value.sha_number = m.sha_number || ''
    hrFinForm.value.notes = ''
  }
}

const submitMedia = async () => {
  isSubmitting.value = true
  actionError.value = ''
  actionSuccess.value = ''

  const fd = new FormData()
  fd.append('member_id', selectedMember.value.id)
  fd.append('approved', mediaForm.value.approved)
  fd.append('photo_source', mediaForm.value.photo_source)
  if (mediaForm.value.notes) fd.append('notes', mediaForm.value.notes)
  if (mediaForm.value.replacementFile) fd.append('replacement_photo', mediaForm.value.replacementFile)

  try {
    await api.post('/clearance/media/photo', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    actionSuccess.value = 'Media Relations photo status updated.'
    setTimeout(() => { selectedMember.value = null; fetchQueue(); }, 800)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Failed to update photo.'
  } finally {
    isSubmitting.value = false
  }
}

const submitIct = async () => {
  isSubmitting.value = true
  actionError.value = ''
  actionSuccess.value = ''

  try {
    await api.post('/clearance/ict/biometrics', {
      member_id: selectedMember.value.id,
      collected: ictForm.value.collected,
      notes: ictForm.value.notes
    })
    actionSuccess.value = 'Chamber attendance & voting biometrics recorded.'
    setTimeout(() => { selectedMember.value = null; fetchQueue(); }, 800)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Failed to record biometrics.'
  } finally {
    isSubmitting.value = false
  }
}

const submitSecurity = async () => {
  isSubmitting.value = true
  actionError.value = ''
  actionSuccess.value = ''

  const fd = new FormData()
  fd.append('member_id', selectedMember.value.id)
  fd.append('cleared', securityForm.value.cleared)
  fd.append('badge_number', securityForm.value.badge_number)
  if (securityForm.value.notes) fd.append('notes', securityForm.value.notes)
  if (securityForm.value.vettingFile) fd.append('vetting_form', securityForm.value.vettingFile)

  try {
    await api.post('/clearance/security/clearance', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    actionSuccess.value = 'Security clearance and badge issuance recorded.'
    setTimeout(() => { selectedMember.value = null; fetchQueue(); }, 800)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Failed to record security clearance.'
  } finally {
    isSubmitting.value = false
  }
}

const submitHrFinance = async () => {
  isSubmitting.value = true
  actionError.value = ''
  actionSuccess.value = ''

  try {
    await api.post('/clearance/hr-finance/clearance', {
      member_id: selectedMember.value.id,
      hr_verified: hrFinForm.value.hr_verified,
      finance_verified: hrFinForm.value.finance_verified,
      bank_name: hrFinForm.value.bank_name,
      bank_account: hrFinForm.value.bank_account,
      bank_branch: hrFinForm.value.bank_branch,
      nssf_number: hrFinForm.value.nssf_number,
      sha_number: hrFinForm.value.sha_number,
      notes: hrFinForm.value.notes
    })
    actionSuccess.value = 'HR & Finance clearance successfully saved.'
    setTimeout(() => { selectedMember.value = null; fetchQueue(); }, 800)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Failed to save HR/Finance clearance.'
  } finally {
    isSubmitting.value = false
  }
}

const filteredQueue = computed(() => {
  if (!searchQuery.value) return queue.value
  const q = searchQuery.value.toLowerCase()
  return queue.value.filter(m => 
    m.full_name?.toLowerCase().includes(q) ||
    m.national_id?.toLowerCase().includes(q) ||
    m.county?.toLowerCase().includes(q)
  )
})
</script>

<template>
  <div class="space-y-6">
    
    <!-- Top Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Stage 4 · Unit Clearance Stations</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Departmental Verification & Clearance Stations</h1>
      </div>
      <button 
        @click="fetchQueue" 
        class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
      >
        <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
        <span>Refresh Queue</span>
      </button>
    </div>

    <!-- Unit Tabs Navigation -->
    <div class="flex border-b border-slate-200 space-x-2 text-xs font-bold">
      <button 
        @click="switchTab('MEDIA')"
        class="py-3 px-4 border-b-2 flex items-center space-x-2 transition-all"
        :class="activeTab === 'MEDIA' ? 'border-parliament-green text-parliament-green bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
      >
        <Camera class="w-4 h-4" />
        <span>1. Media Relations (Photo)</span>
      </button>

      <button 
        @click="switchTab('ICT')"
        class="py-3 px-4 border-b-2 flex items-center space-x-2 transition-all"
        :class="activeTab === 'ICT' ? 'border-parliament-green text-parliament-green bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
      >
        <Cpu class="w-4 h-4" />
        <span>2. ICT (Biometrics)</span>
      </button>

      <button 
        @click="switchTab('SECURITY')"
        class="py-3 px-4 border-b-2 flex items-center space-x-2 transition-all"
        :class="activeTab === 'SECURITY' ? 'border-parliament-green text-parliament-green bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
      >
        <Shield class="w-4 h-4" />
        <span>3. Security (Badge & Vetting)</span>
      </button>

      <button 
        @click="switchTab('HR_FINANCE')"
        class="py-3 px-4 border-b-2 flex items-center space-x-2 transition-all"
        :class="activeTab === 'HR_FINANCE' ? 'border-parliament-green text-parliament-green bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
      >
        <Briefcase class="w-4 h-4" />
        <span>4. HR & Finance (Payroll/SHA)</span>
      </button>
    </div>

    <!-- Search filter -->
    <div class="bg-white p-3 rounded-2xl border border-slate-200 flex items-center space-x-3 text-xs">
      <div class="relative flex-1">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Filter queue by member name, ID number, or county..." 
          class="w-full pl-9 pr-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"
        />
        <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
      </div>
    </div>

    <!-- Active Unit Work Queue Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-600 font-bold">
            <tr>
              <th class="py-3 px-4">Member Name</th>
              <th class="py-3 px-4">Category</th>
              <th class="py-3 px-4">County / Seat</th>
              <th class="py-3 px-4">Desk Checked In</th>
              <th class="py-3 px-4">Current Unit Status</th>
              <th class="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="m in filteredQueue" :key="m.id" class="hover:bg-slate-50/80">
              <td class="py-3 px-4 font-bold text-slate-900">
                <div>Hon. {{ m.full_name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">ID: {{ m.national_id || 'Pending' }}</div>
              </td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100">
                  {{ m.category.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">{{ m.county || m.party }}</td>
              <td class="py-3 px-4">
                <span v-if="m.desk_checked_in_at" class="text-blue-700 font-bold flex items-center space-x-1">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Checked In</span>
                </span>
                <span v-else class="text-slate-400 italic">Not checked in</span>
              </td>
              <td class="py-3 px-4">
                <!-- Media status -->
                <template v-if="activeTab === 'MEDIA'">
                  <span v-if="m.photo_approved" class="text-emerald-700 font-bold flex items-center space-x-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>Photo Approved</span>
                  </span>
                  <span v-else class="text-amber-600 font-bold">Pending Review</span>
                </template>

                <!-- ICT status -->
                <template v-else-if="activeTab === 'ICT'">
                  <span v-if="m.biometrics_collected" class="text-emerald-700 font-bold flex items-center space-x-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>Biometrics Collected</span>
                  </span>
                  <span v-else class="text-amber-600 font-bold">Pending Chamber Enrollment</span>
                </template>

                <!-- Security status -->
                <template v-else-if="activeTab === 'SECURITY'">
                  <span v-if="m.security_cleared" class="text-emerald-700 font-bold flex items-center space-x-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>Badge #{{ m.badge_number || 'Issued' }}</span>
                  </span>
                  <span v-else class="text-amber-600 font-bold">Pending Vetting & Badge</span>
                </template>

                <!-- HR & Finance status -->
                <template v-else-if="activeTab === 'HR_FINANCE'">
                  <span v-if="m.hr_verified && m.finance_verified" class="text-emerald-700 font-bold flex items-center space-x-1">
                    <CheckCircle2 class="w-3.5 h-3.5" />
                    <span>HR & Finance Cleared</span>
                  </span>
                  <span v-else class="text-amber-600 font-bold">Payroll & Bank Pending</span>
                </template>
              </td>
              <td class="py-3 px-4 text-right">
                <button 
                  @click="openActionModal(m)"
                  class="px-3 py-1.5 rounded-lg bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-[11px] shadow-sm"
                >
                  Manage Clearance
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Action Drawer / Modal -->
    <div v-if="selectedMember" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <div class="text-[10px] font-bold text-parliament-gold uppercase">{{ activeTab }} Clearance Station</div>
            <h3 class="text-base font-bold text-slate-900">Hon. {{ selectedMember.full_name }}</h3>
          </div>
          <button @click="selectedMember = null" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="actionError" class="p-3 mb-4 rounded-xl bg-red-50 text-red-700 border border-red-200 text-xs">
          {{ actionError }}
        </div>
        <div v-if="actionSuccess" class="p-3 mb-4 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs">
          {{ actionSuccess }}
        </div>

        <!-- 1. MEDIA MODAL FORM -->
        <div v-if="activeTab === 'MEDIA'" class="space-y-4 text-xs">
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center space-x-4">
            <div class="w-20 h-24 bg-slate-200 rounded-lg overflow-hidden border flex items-center justify-center">
              <img v-if="selectedMember.passport_photo_path" :src="selectedMember.passport_photo_path" class="w-full h-full object-cover" />
              <User v-else class="w-8 h-8 text-slate-400" />
            </div>
            <div>
              <div class="font-bold text-slate-900 text-sm">Official Passport Photo</div>
              <div class="text-slate-500 mt-1">Source: {{ selectedMember.photo_source || 'Online Upload' }}</div>
              <div class="text-[11px] text-slate-600 mt-1">Verify adherence to parliamentary standards (suit, plain background).</div>
            </div>
          </div>

          <label class="flex items-center space-x-2 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
            <input type="checkbox" v-model="mediaForm.approved" class="w-4 h-4 text-parliament-green rounded" />
            <span class="font-bold text-slate-900">Approve this photograph for parliamentary records & gazette</span>
          </label>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">If unapproved, upload replacement photograph or camera capture:</label>
            <input type="file" @change="(e) => mediaForm.replacementFile = e.target.files[0]" accept="image/png,image/jpeg" class="w-full text-xs text-slate-600 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-slate-800 file:text-white" />
          </div>

          <div class="flex justify-end space-x-2 pt-3 border-t">
            <button @click="selectedMember = null" class="px-4 py-2 border rounded-xl font-semibold">Cancel</button>
            <button @click="submitMedia" :disabled="isSubmitting" class="px-5 py-2 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md">Save Photo Status</button>
          </div>
        </div>

        <!-- 2. ICT MODAL FORM -->
        <div v-else-if="activeTab === 'ICT'" class="space-y-4 text-xs">
          <div class="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900">
            <p class="font-bold text-sm">Chamber Attendance & Voting Biometrics</p>
            <p class="mt-1">Enroll fingerprint and biometric profile into the chamber electronic attendance and voting system.</p>
          </div>

          <label class="flex items-center space-x-2 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
            <input type="checkbox" v-model="ictForm.collected" class="w-4 h-4 text-parliament-green rounded" />
            <span class="font-bold text-slate-900">Confirm biometric capture complete & chamber card provisioned</span>
          </label>

          <div class="flex justify-end space-x-2 pt-3 border-t">
            <button @click="selectedMember = null" class="px-4 py-2 border rounded-xl font-semibold">Cancel</button>
            <button @click="submitIct" :disabled="isSubmitting" class="px-5 py-2 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md">Save Biometric Record</button>
          </div>
        </div>

        <!-- 3. SECURITY MODAL FORM -->
        <div v-else-if="activeTab === 'SECURITY'" class="space-y-4 text-xs">
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-800">
            <p class="font-bold text-sm">Security Screening & Parliament Badge</p>
            <p class="mt-1">Issue official parliamentary security identification badge and verify vetting form.</p>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Badge Number *</label>
            <input type="text" v-model="securityForm.badge_number" required placeholder="e.g. NA-14P-042" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-mono font-bold" />
          </div>

          <label class="flex items-center space-x-2 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
            <input type="checkbox" v-model="securityForm.cleared" class="w-4 h-4 text-parliament-green rounded" />
            <span class="font-bold text-slate-900">Member cleared by Parliamentary Security Directorate</span>
          </label>

          <div class="flex justify-end space-x-2 pt-3 border-t">
            <button @click="selectedMember = null" class="px-4 py-2 border rounded-xl font-semibold">Cancel</button>
            <button @click="submitSecurity" :disabled="isSubmitting" class="px-5 py-2 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md">Save Security Clearance</button>
          </div>
        </div>

        <!-- 4. HR & FINANCE MODAL FORM -->
        <div v-else-if="activeTab === 'HR_FINANCE'" class="space-y-3 text-xs">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Bank Name *</label>
              <input type="text" v-model="hrFinForm.bank_name" class="w-full px-3 py-1.5 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Bank Branch *</label>
              <input type="text" v-model="hrFinForm.bank_branch" class="w-full px-3 py-1.5 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Bank Account Number *</label>
              <input type="text" v-model="hrFinForm.bank_account" class="w-full px-3 py-1.5 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-mono" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">KRA PIN (Read-Only)</label>
              <input type="text" :value="selectedMember.kra_pin" disabled class="w-full px-3 py-1.5 border rounded-xl bg-slate-100 font-mono font-bold" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">NSSF Number</label>
              <input type="text" v-model="hrFinForm.nssf_number" placeholder="e.g. 12345678" class="w-full px-3 py-1.5 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">SHA / Social Health Number</label>
              <input type="text" v-model="hrFinForm.sha_number" placeholder="e.g. SHA-1234567" class="w-full px-3 py-1.5 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
            </div>
          </div>

          <div class="pt-2 space-y-2">
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="hrFinForm.hr_verified" class="w-4 h-4 text-parliament-green rounded" />
              <span class="font-bold text-slate-900">HR Records & Dependent Vetting Verified</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="hrFinForm.finance_verified" class="w-4 h-4 text-parliament-green rounded" />
              <span class="font-bold text-slate-900">Finance & Payroll Enrollment Approved</span>
            </label>
          </div>

          <div class="flex justify-end space-x-2 pt-3 border-t">
            <button @click="selectedMember = null" class="px-4 py-2 border rounded-xl font-semibold">Cancel</button>
            <button @click="submitHrFinance" :disabled="isSubmitting" class="px-5 py-2 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md">Save HR & Finance Clearance</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>
