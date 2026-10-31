<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import {
  Building2, Search, User, ShieldCheck, CheckCircle2, AlertCircle,
  Upload, FileText, Printer, ArrowRight, ArrowLeft, RefreshCw, Phone, Mail
} from 'lucide-vue-next'

const currentStep = ref(1) // 1: Search, 2: Biodata, 3: Uploads, 4: Confirmation
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const selectedMember = ref(null)

const portalStatus = ref({
  is_open: true,
  closing_date: '',
  parliament_term: '14th Parliament of Kenya',
  help_desk_email: 'mors.support@parliament.go.ke',
  help_desk_phone: '+254 (0)20 284 8000'
})

// Form Data
const formData = ref({
  gender: 'MALE',
  date_of_birth: '',
  national_id: '',
  phone: '',
  email: '',
  kra_pin: '',
  postal_address: '',
  qualifications: '',
  next_of_kin_name: '',
  next_of_kin_relation: '',
  next_of_kin_phone: '',
  next_of_kin_email: '',
  spam_honeypot: '' // Spam prevention
})

// Files
const idDocFile = ref(null)
const iebcCertFile = ref(null)
const photoFile = ref(null)
const photoPreviewUrl = ref(null)

const submissionResult = ref(null)
const errorMessage = ref('')
const isSubmitting = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/portal/status')
    portalStatus.value = res.data
  } catch (err) {
    console.error('Failed to load portal status', err)
  }
})

const searchGazette = async () => {
  if (!searchQuery.value || searchQuery.value.trim().length < 2) {
    searchResults.value = []
    return
  }
  isSearching.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/portal/search?q=${encodeURIComponent(searchQuery.value.trim())}`)
    searchResults.value = res.data
  } catch (err) {
    errorMessage.value = 'Failed to search gazette records.'
  } finally {
    isSearching.value = false
  }
}

const selectMember = async (item) => {
  if (item.is_submission_locked && !item.reopened_for_correction) {
    errorMessage.value = `This record is already submitted under reference ${item.submission_reference || 'MORS'}. Please contact the Registration Desk if you need to make changes.`
    return
  }
  try {
    const res = await api.get(`/portal/member/${item.id}`)
    selectedMember.value = res.data
    // Pre-populate if available
    formData.value.gender = res.data.gender || 'MALE'
    formData.value.date_of_birth = res.data.date_of_birth || ''
    formData.value.national_id = res.data.national_id || ''
    formData.value.phone = res.data.phone || ''
    formData.value.email = res.data.email || ''
    formData.value.kra_pin = res.data.kra_pin || ''
    formData.value.postal_address = res.data.postal_address || ''
    formData.value.qualifications = res.data.qualifications || ''
    formData.value.next_of_kin_name = res.data.next_of_kin_name || ''
    formData.value.next_of_kin_relation = res.data.next_of_kin_relation || ''
    formData.value.next_of_kin_phone = res.data.next_of_kin_phone || ''
    formData.value.next_of_kin_email = res.data.next_of_kin_email || ''

    currentStep.value = 2
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    errorMessage.value = 'Could not load member details.'
  }
}

const handlePhotoChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    photoFile.value = file
    photoPreviewUrl.value = URL.createObjectURL(file)
  }
}

const handleIdDocChange = (e) => {
  idDocFile.value = e.target.files[0] || null
}

const handleIebcCertChange = (e) => {
  iebcCertFile.value = e.target.files[0] || null
}

const submitOnboarding = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  const data = new FormData()
  data.append('member_id', selectedMember.value.id)
  data.append('gender', formData.value.gender)
  data.append('date_of_birth', formData.value.date_of_birth)
  data.append('national_id', formData.value.national_id)
  data.append('phone', formData.value.phone)
  data.append('email', formData.value.email)
  data.append('kra_pin', formData.value.kra_pin)
  data.append('postal_address', formData.value.postal_address)
  if (formData.value.qualifications) data.append('qualifications', formData.value.qualifications)
  data.append('next_of_kin_name', formData.value.next_of_kin_name)
  data.append('next_of_kin_relation', formData.value.next_of_kin_relation)
  data.append('next_of_kin_phone', formData.value.next_of_kin_phone)
  if (formData.value.next_of_kin_email) data.append('next_of_kin_email', formData.value.next_of_kin_email)
  if (formData.value.spam_honeypot) data.append('spam_honeypot', formData.value.spam_honeypot)

  if (idDocFile.value) data.append('id_document', idDocFile.value)
  if (iebcCertFile.value) data.append('iebc_cert', iebcCertFile.value)
  if (photoFile.value) data.append('passport_photo', photoFile.value)

  try {
    const res = await api.post('/portal/submit', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    submissionResult.value = res.data
    currentStep.value = 4
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Submission failed. Please verify your entries.'
  } finally {
    isSubmitting.value = false
  }
}

const printReferenceSlip = () => {
  window.print()
}

const restartForm = () => {
  currentStep.value = 1
  selectedMember.value = null
  searchQuery.value = ''
  searchResults.value = []
  submissionResult.value = null
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans">
    
    <!-- Top Bar with Official Emblem -->
    <header class="bg-parliament-green text-white border-b-4 border-parliament-gold shadow-md no-print">
      <div class="max-w-5xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center space-x-3 text-center sm:text-left">
          <div class="w-12 h-12 rounded-full bg-white/10 border-2 border-parliament-gold flex items-center justify-center p-2 shadow-inner">
            <Building2 class="w-7 h-7 text-parliament-gold" />
          </div>
          <div>
            <div class="text-[11px] font-extrabold text-parliament-gold tracking-widest uppercase">Republic of Kenya</div>
            <h1 class="text-base font-extrabold leading-tight">The National Assembly</h1>
            <p class="text-xs text-emerald-100">Members' Onboarding & Records System (MORS)</p>
          </div>
        </div>

        <div class="flex items-center space-x-3 text-xs">
          <div class="px-3 py-1 rounded-full bg-emerald-900/60 border border-emerald-700/50 text-emerald-100 flex items-center space-x-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>14th Parliament Portal</span>
          </div>
          <router-link to="/login" class="text-xs text-parliament-gold hover:underline font-semibold">
            Staff Sign In &rarr;
          </router-link>
        </div>
      </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 lg:p-8">
      
      <!-- Stepper Header (Only when active) -->
      <div v-if="currentStep < 4" class="mb-8 no-print">
        <div class="flex items-center justify-between relative max-w-xl mx-auto">
          <!-- Step 1 -->
          <div class="flex flex-col items-center relative z-10">
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all"
              :class="currentStep >= 1 ? 'bg-parliament-green text-white ring-4 ring-emerald-100' : 'bg-slate-200 text-slate-500'"
            >1</div>
            <span class="text-[11px] font-bold mt-1 text-slate-700">Find Name</span>
          </div>
          <div class="flex-1 h-0.5 bg-slate-200 -mt-4 mx-2" :class="{'bg-parliament-green': currentStep >= 2}"></div>
          
          <!-- Step 2 -->
          <div class="flex flex-col items-center relative z-10">
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all"
              :class="currentStep >= 2 ? 'bg-parliament-green text-white ring-4 ring-emerald-100' : 'bg-slate-200 text-slate-500'"
            >2</div>
            <span class="text-[11px] font-bold mt-1 text-slate-700">Biodata</span>
          </div>
          <div class="flex-1 h-0.5 bg-slate-200 -mt-4 mx-2" :class="{'bg-parliament-green': currentStep >= 3}"></div>

          <!-- Step 3 -->
          <div class="flex flex-col items-center relative z-10">
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all"
              :class="currentStep >= 3 ? 'bg-parliament-green text-white ring-4 ring-emerald-100' : 'bg-slate-200 text-slate-500'"
            >3</div>
            <span class="text-[11px] font-bold mt-1 text-slate-700">Documents</span>
          </div>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="errorMessage" class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start space-x-2 no-print">
        <AlertCircle class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>

      <!-- STEP 1: Search Gazette Name -->
      <div v-if="currentStep === 1" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
        <div class="text-center max-w-lg mx-auto mb-6">
          <h2 class="text-xl font-extrabold text-slate-900">Member Pre-Registration</h2>
          <p class="text-xs text-slate-600 mt-1">
            Please enter your name exactly as published in the official IEBC Gazette Notice for the 14th Parliament.
          </p>
        </div>

        <div class="max-w-lg mx-auto">
          <div class="relative flex items-center">
            <input 
              type="text" 
              v-model="searchQuery"
              @input="searchGazette"
              placeholder="Search by surname or full name (e.g. Kariuki, Otieno, Wanjiku)..."
              class="w-full pl-10 pr-4 py-3 text-sm border-2 border-slate-200 rounded-xl focus:border-parliament-green focus:ring-2 focus:ring-emerald-100 outline-none text-slate-900"
            />
            <Search class="w-5 h-5 text-slate-400 absolute left-3" />
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''; searchResults = []"
              class="text-xs text-slate-400 hover:text-slate-600 absolute right-3 font-semibold"
            >Clear</button>
          </div>

          <!-- Live Results list -->
          <div v-if="searchResults.length > 0" class="mt-4 border border-slate-200 rounded-xl divide-y divide-slate-100 overflow-hidden shadow-sm">
            <div 
              v-for="item in searchResults" 
              :key="item.id"
              @click="selectMember(item)"
              class="p-4 hover:bg-emerald-50/60 cursor-pointer transition-colors flex items-center justify-between"
            >
              <div>
                <div class="font-bold text-sm text-slate-900 flex items-center space-x-2">
                  <span>Hon. {{ item.full_name }}</span>
                  <span 
                    class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-emerald-100 text-emerald-800': item.category === 'MP',
                      'bg-purple-100 text-purple-800': item.category === 'WOMAN_REP',
                      'bg-blue-100 text-blue-800': item.category === 'NOMINATED'
                    }"
                  >
                    {{ item.category.replace('_', ' ') }}
                  </span>
                </div>
                <div class="text-xs text-slate-500 mt-1 flex flex-wrap gap-x-3">
                  <span v-if="item.constituency"><strong>Constituency:</strong> {{ item.constituency }}</span>
                  <span v-if="item.county"><strong>County:</strong> {{ item.county }}</span>
                  <span><strong>Party:</strong> {{ item.party }}</span>
                </div>
              </div>
              <ArrowRight class="w-4 h-4 text-parliament-green flex-shrink-0 ml-2" />
            </div>
          </div>

          <div v-else-if="searchQuery && !isSearching && searchResults.length === 0" class="mt-4 p-4 rounded-xl bg-slate-50 border text-center text-xs text-slate-500">
            No matching gazetted member found. Please verify spelling against the gazette notice or contact the Clerk's Office.
          </div>
        </div>

        <!-- Safeguard Note -->
        <div class="mt-8 pt-6 border-t border-slate-100 flex items-start space-x-3 text-xs text-slate-500">
          <ShieldCheck class="w-5 h-5 text-parliament-gold flex-shrink-0 mt-0.5" />
          <p>
            <strong>Official Safeguard:</strong> Only persons gazetted by the Independent Electoral and Boundaries Commission (IEBC) can be onboarded into MORS. Physical documents will be cross-verified at the registration desk.
          </p>
        </div>
      </div>

      <!-- STEP 2: Biodata Form -->
      <div v-if="currentStep === 2" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
        
        <!-- Prefilled Gazette Banner (Read Only) -->
        <div class="mb-6 p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
          <div class="text-[11px] font-bold text-emerald-800 uppercase tracking-wider mb-2 flex items-center space-x-1">
            <CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" />
            <span>Official IEBC Gazette Details (Locked & Verified)</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
            <div>
              <span class="text-slate-500 block">Full Gazette Name:</span>
              <span class="font-bold text-slate-900 text-sm">Hon. {{ selectedMember.full_name }}</span>
            </div>
            <div>
              <span class="text-slate-500 block">Category:</span>
              <span class="font-bold text-slate-900">{{ selectedMember.category.replace('_', ' ') }}</span>
            </div>
            <div>
              <span class="text-slate-500 block">Political Party:</span>
              <span class="font-bold text-slate-900">{{ selectedMember.party }}</span>
            </div>
            <div v-if="selectedMember.county">
              <span class="text-slate-500 block">County:</span>
              <span class="font-bold text-slate-900">{{ selectedMember.county }}</span>
            </div>
            <div v-if="selectedMember.constituency">
              <span class="text-slate-500 block">Constituency:</span>
              <span class="font-bold text-slate-900">{{ selectedMember.constituency }}</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="currentStep = 3" class="space-y-6 text-xs">
          <!-- Honeypot anti-spam field -->
          <input type="text" v-model="formData.spam_honeypot" class="hidden" tabindex="-1" autocomplete="off" />

          <div>
            <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-100 mb-4">1. Personal Biodata</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Gender *</label>
                <select v-model="formData.gender" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green">
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Date of Birth *</label>
                <input type="date" v-model="formData.date_of_birth" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">National ID / Valid Passport Number *</label>
                <input type="text" v-model="formData.national_id" required placeholder="e.g. 12345678" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">KRA PIN Number *</label>
                <input type="text" v-model="formData.kra_pin" required placeholder="e.g. A012345678K" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green uppercase" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Mobile Phone Number *</label>
                <input type="tel" v-model="formData.phone" required placeholder="e.g. +254 712 345 678" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Official Email Address *</label>
                <input type="email" v-model="formData.email" required placeholder="e.g. member@example.com" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div class="sm:col-span-2">
                <label class="block font-semibold text-slate-700 mb-1">Postal Address *</label>
                <input type="text" v-model="formData.postal_address" required placeholder="e.g. P.O. Box 41842-00100, Nairobi" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div class="sm:col-span-2">
                <label class="block font-semibold text-slate-700 mb-1">Highest Academic & Professional Qualifications</label>
                <textarea v-model="formData.qualifications" rows="2" placeholder="e.g. Master of Laws (LLM), Bachelor of Arts, CPA(K)" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"></textarea>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-100 mb-4">2. Next of Kin Information</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Full Name of Next of Kin *</label>
                <input type="text" v-model="formData.next_of_kin_name" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Relationship *</label>
                <input type="text" v-model="formData.next_of_kin_relation" required placeholder="e.g. Spouse, Son, Sister" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Next of Kin Phone Number *</label>
                <input type="tel" v-model="formData.next_of_kin_phone" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>

              <div>
                <label class="block font-semibold text-slate-700 mb-1">Next of Kin Email Address</label>
                <input type="email" v-model="formData.next_of_kin_email" class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green" />
              </div>
            </div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-100">
            <button 
              type="button" 
              @click="currentStep = 1" 
              class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-bold hover:bg-slate-50 flex items-center space-x-1.5"
            >
              <ArrowLeft class="w-4 h-4" />
              <span>Back</span>
            </button>
            <button 
              type="submit" 
              class="px-6 py-2.5 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold shadow-md flex items-center space-x-1.5"
            >
              <span>Next: Document Scans</span>
              <ArrowRight class="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>

      <!-- STEP 3: Document Uploads -->
      <div v-if="currentStep === 3" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
        <div class="mb-6">
          <h2 class="text-lg font-extrabold text-slate-900">Upload Required Documents</h2>
          <p class="text-xs text-slate-600 mt-0.5">
            Allowed file formats: PDF, JPG, PNG (Max. 5 MB per file). Original documents must be presented physically at the Registration Desk.
          </p>
        </div>

        <div class="space-y-6 text-xs">
          <!-- 1. Passport Photo -->
          <div class="p-4 rounded-xl border-2 border-dashed border-slate-200 hover:border-parliament-green transition-colors">
            <div class="flex flex-col sm:flex-row items-center gap-4">
              <div class="w-24 h-28 bg-slate-100 rounded-lg border flex items-center justify-center overflow-hidden flex-shrink-0">
                <img v-if="photoPreviewUrl" :src="photoPreviewUrl" class="w-full h-full object-cover" />
                <User v-else class="w-10 h-10 text-slate-400" />
              </div>
              <div class="flex-1 text-center sm:text-left">
                <label class="block font-bold text-slate-900 mb-1 text-sm">1. Official Passport Photograph *</label>
                <p class="text-slate-500 mb-2">Clear colour photograph with a plain white or off-white background.</p>
                <input type="file" @change="handlePhotoChange" accept="image/png,image/jpeg" class="text-xs text-slate-600 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-parliament-green file:text-white file:font-semibold hover:file:bg-parliament-green-dark cursor-pointer" />
              </div>
            </div>
          </div>

          <!-- 2. National ID Scan -->
          <div class="p-4 rounded-xl border border-slate-200">
            <label class="block font-bold text-slate-900 mb-1 text-sm">2. Scanned National ID or Valid Passport (Front & Back) *</label>
            <p class="text-slate-500 mb-2">PDF, JPG, or PNG up to 5 MB.</p>
            <input type="file" @change="handleIdDocChange" accept=".pdf,image/png,image/jpeg" class="text-xs text-slate-600 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-slate-800 file:text-white file:font-semibold hover:file:bg-slate-900 cursor-pointer" />
          </div>

          <!-- 3. IEBC Certificate Scan -->
          <div class="p-4 rounded-xl border border-slate-200">
            <label class="block font-bold text-slate-900 mb-1 text-sm">3. Scanned IEBC Certificate of Election / Nomination *</label>
            <p class="text-slate-500 mb-2">The official Form 23 / Nomination Certificate issued by IEBC.</p>
            <input type="file" @change="handleIebcCertChange" accept=".pdf,image/png,image/jpeg" class="text-xs text-slate-600 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-slate-800 file:text-white file:font-semibold hover:file:bg-slate-900 cursor-pointer" />
          </div>

          <!-- Summary Confirmation -->
          <div class="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900">
            <p class="font-bold">Declaration and Physical Verification Requirement:</p>
            <p class="mt-1">
              I hereby declare that the information and scanned documents submitted herein are genuine and true. I understand that physical check-in and original document inspection are mandatory before being cleared for the swearing-in ceremony.
            </p>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-100">
            <button 
              type="button" 
              @click="currentStep = 2" 
              class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-bold hover:bg-slate-50 flex items-center space-x-1.5"
            >
              <ArrowLeft class="w-4 h-4" />
              <span>Back</span>
            </button>
            <button 
              type="button"
              @click="submitOnboarding"
              :disabled="isSubmitting"
              class="px-8 py-2.5 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-extrabold shadow-lg transition-all flex items-center space-x-2 disabled:opacity-50"
            >
              <RefreshCw v-if="isSubmitting" class="w-4 h-4 animate-spin" />
              <span>{{ isSubmitting ? 'Submitting Details...' : 'Complete & Submit Registration' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- STEP 4: Confirmation Slip & Reference Card -->
      <div v-if="currentStep === 4 && submissionResult" class="bg-white rounded-2xl shadow-lg border-2 border-parliament-gold p-6 sm:p-10">
        
        <div class="text-center pb-6 border-b border-slate-200">
          <div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-3">
            <CheckCircle2 class="w-10 h-10" />
          </div>
          <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-widest">Republic of Kenya · The National Assembly</div>
          <h2 class="text-2xl font-black text-slate-900 mt-1">Onboarding Pre-Registration Complete</h2>
          <p class="text-xs text-slate-600 mt-1">A confirmation notice has been dispatched to your email address.</p>
        </div>

        <!-- Official Reference Box -->
        <div class="my-6 p-6 rounded-2xl bg-slate-900 text-white text-center shadow-inner">
          <div class="text-xs uppercase text-parliament-gold font-bold tracking-wider">Your Official MORS Reference Number</div>
          <div class="text-3xl font-black tracking-widest text-white mt-1">{{ submissionResult.reference_number }}</div>
          <div class="text-xs text-slate-400 mt-1">Please quote this reference number upon arrival at Parliament Buildings.</div>
        </div>

        <!-- Details Summary -->
        <div class="space-y-4 text-xs">
          <h3 class="font-bold text-sm text-slate-900 pb-1 border-b border-slate-100">Member Onboarding Summary</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 p-4 rounded-xl">
            <div><span class="text-slate-500">Member Name:</span> <strong class="text-slate-900 block">{{ submissionResult.member_name }}</strong></div>
            <div><span class="text-slate-500">Category:</span> <strong class="text-slate-900 block">{{ submissionResult.category.replace('_', ' ') }}</strong></div>
            <div><span class="text-slate-500">National ID:</span> <strong class="text-slate-900 block">{{ formData.national_id }}</strong></div>
            <div><span class="text-slate-500">Official Mobile:</span> <strong class="text-slate-900 block">{{ formData.phone }}</strong></div>
            <div><span class="text-slate-500">Submission Timestamp:</span> <strong class="text-slate-900 block">{{ new Date().toLocaleString() }}</strong></div>
            <div><span class="text-slate-500">Next Step:</span> <strong class="text-parliament-green block">Report to Clerks (L&P) Registration Desk</strong></div>
          </div>

          <!-- Instructions on Arrival -->
          <div class="p-4 rounded-xl border border-slate-200 space-y-2">
            <h4 class="font-bold text-slate-900">Next Steps at Parliament Buildings:</h4>
            <ul class="list-disc list-inside space-y-1 text-slate-600">
              <li>Carry your <strong>ORIGINAL National Identity Card</strong> or valid Passport.</li>
              <li>Carry your <strong>ORIGINAL IEBC Certificate of Election/Nomination</strong>.</li>
              <li>Report to the <strong>Registration Desk (Clerks L&P)</strong> for physical document verification.</li>
              <li>Proceed through <strong>Media Relations</strong> (Photo approval), <strong>ICT</strong> (Chamber biometrics), <strong>Security</strong> (Badge), and <strong>HR & Finance</strong>.</li>
            </ul>
          </div>

          <!-- Secretariat Contact for Corrections -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div>
              <div class="font-bold text-slate-800">Need to make a correction?</div>
              <div class="text-slate-500">Contact the Registration Secretariat before check-in:</div>
            </div>
            <div class="text-right text-slate-700">
              <div class="flex items-center space-x-1.5"><Mail class="w-3.5 h-3.5 text-parliament-green" /> <span>{{ portalStatus.help_desk_email }}</span></div>
              <div class="flex items-center space-x-1.5 mt-0.5"><Phone class="w-3.5 h-3.5 text-parliament-green" /> <span>{{ portalStatus.help_desk_phone }}</span></div>
            </div>
          </div>
        </div>

        <div class="mt-8 flex flex-col sm:flex-row justify-center gap-3 no-print">
          <button 
            @click="printReferenceSlip"
            class="px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-black text-white font-bold flex items-center justify-center space-x-2 shadow-md"
          >
            <Printer class="w-4 h-4 text-parliament-gold" />
            <span>Print Confirmation Slip</span>
          </button>
          <button 
            @click="restartForm"
            class="px-6 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-bold hover:bg-slate-50"
          >
            Onboard Another Member
          </button>
        </div>

      </div>

    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-500 no-print">
      <div class="max-w-4xl mx-auto px-4">
        <p class="font-bold text-slate-700">Office of the Clerk · The National Assembly of Kenya</p>
        <p class="mt-1">Members' Onboarding & Records System (MORS) · 14th Parliament Induction 2027</p>
      </div>
    </footer>

  </div>
</template>
