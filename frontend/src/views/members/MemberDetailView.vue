<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import {
  Building2, User, CheckCircle2, Clock, FileText, ExternalLink,
  ShieldCheck, ArrowLeft, Printer, AlertCircle
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const memberId = route.params.id

const data = ref(null)
const isLoading = ref(true)

const fetchDossier = async () => {
  isLoading.value = true
  try {
    const res = await api.get(`/members/${memberId}`)
    data.value = res.data
  } catch (err) {
    console.error('Failed to load member dossier', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDossier()
})
</script>

<template>
  <div class="space-y-6">
    
    <!-- Top Bar -->
    <div class="flex items-center justify-between no-print">
      <button 
        @click="router.back()" 
        class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>Back to Register</span>
      </button>

      <button 
        @click="window.print()" 
        class="px-4 py-1.5 rounded-lg bg-slate-900 hover:bg-black text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm"
      >
        <Printer class="w-4 h-4 text-parliament-gold" />
        <span>Print Member Dossier</span>
      </button>
    </div>

    <!-- Main Dossier Card -->
    <div v-if="data" class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
      
      <!-- Member Header Banner -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div class="flex items-center space-x-4">
          <div class="w-20 h-24 bg-slate-100 rounded-xl overflow-hidden border border-slate-200 flex items-center justify-center flex-shrink-0">
            <img v-if="data.member.passport_photo_path" :src="data.member.passport_photo_path" class="w-full h-full object-cover" />
            <User v-else class="w-10 h-10 text-slate-400" />
          </div>
          <div>
            <div class="text-[10px] font-bold text-parliament-gold uppercase tracking-wider">Member of the 14th Parliament</div>
            <h1 class="text-xl font-extrabold text-slate-900">Hon. {{ data.member.full_name }}</h1>
            <div class="text-xs text-slate-500 mt-1 flex flex-wrap gap-x-3">
              <span><strong>Category:</strong> {{ data.member.category.replace('_', ' ') }}</span>
              <span v-if="data.member.constituency"><strong>Constituency:</strong> {{ data.member.constituency }}</span>
              <span v-if="data.member.county"><strong>County:</strong> {{ data.member.county }}</span>
              <span><strong>Party:</strong> {{ data.member.party }}</span>
            </div>
          </div>
        </div>

        <div class="flex flex-col items-end gap-1.5">
          <span 
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="{
              'bg-slate-100 text-slate-700': data.member.stage === 'GAZETTED',
              'bg-amber-100 text-amber-800': data.member.stage === 'SUBMITTED_ONLINE',
              'bg-blue-100 text-blue-800': data.member.stage === 'DESK_CHECKED_IN',
              'bg-emerald-100 text-emerald-800': data.member.stage === 'FULLY_CLEARED'
            }"
          >
            {{ data.member.stage.replace(/_/g, ' ') }}
          </span>
          <span class="text-xs font-mono font-bold text-slate-700">{{ data.member.submission_reference || 'Reference Pending' }}</span>
        </div>
      </div>

      <!-- Clearance Checklist Progress -->
      <div>
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Unit Clearance Checklist</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          
          <!-- 1. Clerks L&P -->
          <div class="p-3.5 rounded-xl border" :class="data.member.original_docs_verified ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>1. Original Documents (L&P)</span>
              <CheckCircle2 v-if="data.member.original_docs_verified" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.original_docs_verified ? `Verified by ${data.member.original_docs_verified_by}` : 'Pending Desk Inspection' }}
            </div>
          </div>

          <!-- 2. Media Relations -->
          <div class="p-3.5 rounded-xl border" :class="data.member.photo_approved ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>2. Media Relations (Photo)</span>
              <CheckCircle2 v-if="data.member.photo_approved" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.photo_approved ? `Approved by ${data.member.photo_approved_by}` : 'Pending Photo Review' }}
            </div>
          </div>

          <!-- 3. ICT -->
          <div class="p-3.5 rounded-xl border" :class="data.member.biometrics_collected ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>3. ICT (Chamber Biometrics)</span>
              <CheckCircle2 v-if="data.member.biometrics_collected" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.biometrics_collected ? `Captured by ${data.member.biometrics_collected_by}` : 'Pending Chamber Card' }}
            </div>
          </div>

          <!-- 4. Security -->
          <div class="p-3.5 rounded-xl border" :class="data.member.security_cleared ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>4. Parliamentary Security</span>
              <CheckCircle2 v-if="data.member.security_cleared" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.security_cleared ? `Badge #${data.member.badge_number} Issued` : 'Pending Security Clearance' }}
            </div>
          </div>

          <!-- 5. HR & Finance -->
          <div class="p-3.5 rounded-xl border" :class="data.member.hr_verified && data.member.finance_verified ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>5. HR & Finance Records</span>
              <CheckCircle2 v-if="data.member.hr_verified && data.member.finance_verified" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.finance_verified ? `${data.member.bank_name || 'Bank'} Enrolled` : 'Pending Bank & SHA Verification' }}
            </div>
          </div>

          <!-- 6. Oath & Assets -->
          <div class="p-3.5 rounded-xl border" :class="data.member.oath_recorded && data.member.assets_declaration_filed ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-200'">
            <div class="flex items-center justify-between font-bold">
              <span>6. Oath & Assets Declaration</span>
              <CheckCircle2 v-if="data.member.oath_recorded && data.member.assets_declaration_filed" class="w-4 h-4 text-emerald-600" />
              <Clock v-else class="w-4 h-4 text-slate-400" />
            </div>
            <div class="text-[11px] text-slate-500 mt-1">
              {{ data.member.oath_recorded ? 'Oath Signed & Assets Sealed' : 'Pending Formal Swearing-In' }}
            </div>
          </div>

        </div>
      </div>

      <!-- Personal Biodata Details Grid -->
      <div class="space-y-4">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider pb-1 border-b">Member Particulars & Biodata</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div><span class="text-slate-500 block">Date of Birth:</span> <strong class="text-slate-900">{{ data.member.date_of_birth || '—' }}</strong></div>
          <div><span class="text-slate-500 block">National ID / Passport:</span> <strong class="text-slate-900 font-mono">{{ data.member.national_id || '—' }}</strong></div>
          <div><span class="text-slate-500 block">KRA PIN Number:</span> <strong class="text-slate-900 font-mono">{{ data.member.kra_pin || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Official Mobile Phone:</span> <strong class="text-slate-900">{{ data.member.phone || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Official Email Address:</span> <strong class="text-slate-900">{{ data.member.email || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Postal Address:</span> <strong class="text-slate-900">{{ data.member.postal_address || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Next of Kin Name:</span> <strong class="text-slate-900">{{ data.member.next_of_kin_name || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Next of Kin Relationship:</span> <strong class="text-slate-900">{{ data.member.next_of_kin_relation || '—' }}</strong></div>
          <div><span class="text-slate-500 block">Next of Kin Contact:</span> <strong class="text-slate-900">{{ data.member.next_of_kin_phone || '—' }}</strong></div>
        </div>
      </div>

      <!-- Uploaded Documents -->
      <div class="space-y-3">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider pb-1 border-b">Document Scans & Attachments</h3>
        <div class="flex flex-wrap gap-3 text-xs">
          <a 
            v-if="data.member.id_document_path" 
            :href="data.member.id_document_path" 
            target="_blank" 
            class="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold flex items-center space-x-1.5"
          >
            <FileText class="w-4 h-4 text-parliament-green" />
            <span>National ID Scan</span>
            <ExternalLink class="w-3 h-3 text-slate-400" />
          </a>

          <a 
            v-if="data.member.iebc_cert_path" 
            :href="data.member.iebc_cert_path" 
            target="_blank" 
            class="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold flex items-center space-x-1.5"
          >
            <FileText class="w-4 h-4 text-parliament-green" />
            <span>IEBC Election Certificate</span>
            <ExternalLink class="w-3 h-3 text-slate-400" />
          </a>
        </div>
      </div>

      <!-- Chronological Audit Trail for this Member -->
      <div class="space-y-3 pt-2">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider pb-1 border-b">Member Audit & Activity History</h3>
        <div class="divide-y divide-slate-100 text-xs">
          <div v-for="log in data.logs" :key="log.id" class="py-2.5 flex items-center justify-between">
            <div>
              <span class="font-bold text-slate-900">{{ log.step }}</span>
              <span class="text-slate-500 text-[11px] block">{{ log.remarks }}</span>
            </div>
            <div class="text-right">
              <span class="text-slate-700 font-medium">{{ log.completed_by }} ({{ log.unit }})</span>
              <span class="text-slate-400 text-[10px] block font-mono">{{ new Date(log.timestamp).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>
