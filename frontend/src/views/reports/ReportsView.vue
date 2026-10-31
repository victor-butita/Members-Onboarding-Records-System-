<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import {
  FileText, Printer, Download, Filter, RefreshCw, Building2,
  CheckCircle2, Clock, Users, ShieldCheck, AlertCircle
} from 'lucide-vue-next'

const selectedReport = ref('executive_summary')
const selectedCategory = ref('ALL')
const reportData = ref(null)
const isLoading = ref(true)

const reportList = [
  { id: 'executive_summary', title: '1. Executive Summary Report' },
  { id: 'register_of_members', title: '2. Register of Members by Category' },
  { id: 'online_submissions', title: '3. Online Submissions Audit' },
  { id: 'physical_onboarding', title: '4. Physical Onboarding & Desk Verification' },
  { id: 'outstanding_clearance', title: '5. Outstanding Clearance by Unit' },
  { id: 'document_status', title: '6. Document Verification Status' },
  { id: 'audit_log', title: '7. Comprehensive System Audit Log' }
]

const fetchReport = async () => {
  isLoading.value = true
  try {
    let url = `/reports/${selectedReport.value}?category=${selectedCategory.value}`
    const res = await api.get(url)
    reportData.value = res.data
  } catch (err) {
    console.error('Failed to load report', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchReport()
})

const selectReport = (id) => {
  selectedReport.value = id
  fetchReport()
}

const printReport = () => {
  window.print()
}

const exportCsv = () => {
  window.location.href = `/api/v1/reports/export/csv?category=${selectedCategory.value}`
}
</script>

<template>
  <div class="space-y-6">
    
    <!-- Header (No Print) -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 no-print">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Office of the Clerk · Statutory Reporting</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Statutory Reports & Oversight Audits</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="exportCsv" 
          class="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-black text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm"
        >
          <Download class="w-4 h-4 text-parliament-gold" />
          <span>Export Master CSV</span>
        </button>
        <button 
          @click="printReport" 
          class="px-4 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm"
        >
          <Printer class="w-4 h-4 text-parliament-gold" />
          <span>Print Official Report</span>
        </button>
      </div>
    </div>

    <!-- Tabbed Report Selector (No Print) -->
    <div class="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap gap-2 text-xs font-bold no-print">
      <button 
        v-for="rep in reportList" 
        :key="rep.id"
        @click="selectReport(rep.id)"
        class="px-3.5 py-2 rounded-xl transition-all"
        :class="selectedReport === rep.id ? 'bg-parliament-green text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
      >
        {{ rep.title }}
      </button>
    </div>

    <!-- Official Printable Paper Format -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-10 space-y-6">
      
      <!-- Republic of Kenya Letterhead -->
      <div class="text-center pb-6 border-b-2 border-slate-900">
        <div class="w-12 h-12 rounded-full bg-slate-900 text-parliament-gold flex items-center justify-center mx-auto mb-2 font-bold">
          <Building2 class="w-6 h-6" />
        </div>
        <div class="text-xs font-extrabold uppercase tracking-widest text-slate-900">Republic of Kenya</div>
        <h2 class="text-lg font-black uppercase text-slate-900">The National Assembly</h2>
        <div class="text-xs font-bold text-slate-600">Fourteenth Parliament · Members' Onboarding & Records System (MORS)</div>
        <h3 class="text-base font-extrabold text-parliament-green uppercase tracking-wide mt-3">
          {{ reportData?.title || 'Statutory Report' }}
        </h3>
        <p class="text-[10px] text-slate-400 font-mono mt-0.5">
          Generated on: {{ new Date().toLocaleString() }} · Certified by Office of the Clerk
        </p>
      </div>

      <!-- 1. EXECUTIVE SUMMARY REPORT VIEW -->
      <div v-if="selectedReport === 'executive_summary' && reportData" class="space-y-6 text-xs">
        <div>
          <h4 class="font-bold text-slate-900 text-sm uppercase pb-1 border-b">1. Overall Onboarding Progression Funnel</h4>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
            <div class="p-3 rounded-xl bg-slate-50 border">
              <span class="text-slate-500 block">Total Gazetted:</span>
              <span class="text-xl font-black text-slate-900">{{ reportData.total_members }}</span>
            </div>
            <div class="p-3 rounded-xl bg-amber-50 border border-amber-200">
              <span class="text-amber-700 block">Online Submissions:</span>
              <span class="text-xl font-black text-amber-900">{{ reportData.stages.SUBMITTED_ONLINE }}</span>
            </div>
            <div class="p-3 rounded-xl bg-blue-50 border border-blue-200">
              <span class="text-blue-700 block">Desk Check-Ins:</span>
              <span class="text-xl font-black text-blue-900">{{ reportData.stages.DESK_CHECKED_IN }}</span>
            </div>
            <div class="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
              <span class="text-emerald-700 block">Fully Cleared:</span>
              <span class="text-xl font-black text-emerald-900">{{ reportData.stages.FULLY_CLEARED }}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="font-bold text-slate-900 text-sm uppercase pb-1 border-b">2. Clearance Steps Completed by Unit</h4>
          <div class="divide-y divide-slate-100 border rounded-xl mt-3">
            <div class="p-3 flex justify-between"><span>Clerks (L&P) Original Document Verification</span><strong>{{ reportData.unit_progress.clerks_verified }} / {{ reportData.total_members }}</strong></div>
            <div class="p-3 flex justify-between"><span>Media Relations Official Passport Photo Approved</span><strong>{{ reportData.unit_progress.media_approved }} / {{ reportData.total_members }}</strong></div>
            <div class="p-3 flex justify-between"><span>ICT Chamber Attendance & Voting Biometrics</span><strong>{{ reportData.unit_progress.ict_biometrics }} / {{ reportData.total_members }}</strong></div>
            <div class="p-3 flex justify-between"><span>Security Clearance & Parliamentary Badge Issued</span><strong>{{ reportData.unit_progress.security_cleared }} / {{ reportData.total_members }}</strong></div>
            <div class="p-3 flex justify-between"><span>HR Information & Records Verified</span><strong>{{ reportData.unit_progress.hr_verified }} / {{ reportData.total_members }}</strong></div>
            <div class="p-3 flex justify-between"><span>Finance, Payroll & SHA/SHIF Accounts Verified</span><strong>{{ reportData.unit_progress.finance_verified }} / {{ reportData.total_members }}</strong></div>
          </div>
        </div>
      </div>

      <!-- 2. REGISTER OF MEMBERS REPORT -->
      <div v-else-if="selectedReport === 'register_of_members' && reportData" class="space-y-4 text-xs">
        <div class="flex justify-between items-center text-slate-500">
          <span>Official Roll: {{ reportData.total }} Members Gazetted</span>
        </div>
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">#</th>
              <th class="py-2 px-3">Full Member Name</th>
              <th class="py-2 px-3">Category</th>
              <th class="py-2 px-3">County / Seat</th>
              <th class="py-2 px-3">Party</th>
              <th class="py-2 px-3">Current Stage</th>
              <th class="py-2 px-3">Ref No</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 font-mono text-slate-400">{{ idx + 1 }}</td>
              <td class="py-1.5 px-3 font-bold text-slate-900">Hon. {{ r.full_name }}</td>
              <td class="py-1.5 px-3">{{ r.category.replace('_', ' ') }}</td>
              <td class="py-1.5 px-3">{{ r.county }} / {{ r.constituency }}</td>
              <td class="py-1.5 px-3">{{ r.party }}</td>
              <td class="py-1.5 px-3 font-semibold">{{ r.stage.replace(/_/g, ' ') }}</td>
              <td class="py-1.5 px-3 font-mono text-slate-500">{{ r.submission_reference }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 3. ONLINE SUBMISSIONS REPORT -->
      <div v-else-if="selectedReport === 'online_submissions' && reportData" class="space-y-4 text-xs">
        <div class="text-slate-500">Total Pre-Registered Online: {{ reportData.total }} Members</div>
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">Member Name</th>
              <th class="py-2 px-3">National ID</th>
              <th class="py-2 px-3">Reference No</th>
              <th class="py-2 px-3">Submission Timestamp</th>
              <th class="py-2 px-3">ID Upload</th>
              <th class="py-2 px-3">IEBC Cert</th>
              <th class="py-2 px-3">Photo</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 font-bold text-slate-900">Hon. {{ r.full_name }}</td>
              <td class="py-1.5 px-3 font-mono">{{ r.national_id }}</td>
              <td class="py-1.5 px-3 font-mono font-bold text-parliament-green">{{ r.submission_reference }}</td>
              <td class="py-1.5 px-3 font-mono">{{ r.submitted_at }}</td>
              <td class="py-1.5 px-3">{{ r.has_id_upload ? '✓ Attached' : '—' }}</td>
              <td class="py-1.5 px-3">{{ r.has_iebc_cert ? '✓ Attached' : '—' }}</td>
              <td class="py-1.5 px-3">{{ r.has_photo ? '✓ Attached' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 4. PHYSICAL ONBOARDING REPORT -->
      <div v-else-if="selectedReport === 'physical_onboarding' && reportData" class="space-y-4 text-xs">
        <div class="text-slate-500">Checked In at Desk: {{ reportData.total }} Members</div>
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">Member Name</th>
              <th class="py-2 px-3">Checked In Timestamp</th>
              <th class="py-2 px-3">Verifying Officer (Clerk)</th>
              <th class="py-2 px-3">Original Docs Verified</th>
              <th class="py-2 px-3">Oath Recorded</th>
              <th class="py-2 px-3">Assets Filed</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 font-bold text-slate-900">Hon. {{ r.full_name }}</td>
              <td class="py-1.5 px-3 font-mono">{{ r.checked_in_at }}</td>
              <td class="py-1.5 px-3">{{ r.checked_in_by }}</td>
              <td class="py-1.5 px-3">{{ r.original_docs_verified ? '✓ Verified' : 'Pending' }}</td>
              <td class="py-1.5 px-3">{{ r.oath_recorded ? '✓ Administered' : 'Pending' }}</td>
              <td class="py-1.5 px-3">{{ r.assets_declaration_filed ? '✓ Received' : 'Pending' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 5. OUTSTANDING CLEARANCE BY UNIT REPORT -->
      <div v-else-if="selectedReport === 'outstanding_clearance' && reportData" class="space-y-4 text-xs">
        <div class="text-slate-500">Members with Pending Clearance Steps: {{ reportData.total }}</div>
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">Member Name</th>
              <th class="py-2 px-3">Category</th>
              <th class="py-2 px-3">County</th>
              <th class="py-2 px-3">Outstanding Clearance Units</th>
              <th class="py-2 px-3">Stage</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 font-bold text-slate-900">Hon. {{ r.full_name }}</td>
              <td class="py-1.5 px-3">{{ r.category.replace('_', ' ') }}</td>
              <td class="py-1.5 px-3">{{ r.county }}</td>
              <td class="py-1.5 px-3">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 mr-1.5" v-for="u in r.pending_units" :key="u">
                  {{ u }}
                </span>
              </td>
              <td class="py-1.5 px-3 font-semibold">{{ r.stage.replace(/_/g, ' ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 6. DOCUMENT VERIFICATION STATUS REPORT -->
      <div v-else-if="selectedReport === 'document_status' && reportData" class="space-y-4 text-xs">
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">Member Name</th>
              <th class="py-2 px-3">National ID</th>
              <th class="py-2 px-3">ID Uploaded</th>
              <th class="py-2 px-3">IEBC Cert Uploaded</th>
              <th class="py-2 px-3">Passport Photo Uploaded</th>
              <th class="py-2 px-3">Originals Inspected</th>
              <th class="py-2 px-3">Photo Approved</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 font-bold text-slate-900">Hon. {{ r.full_name }}</td>
              <td class="py-1.5 px-3 font-mono">{{ r.national_id }}</td>
              <td class="py-1.5 px-3">{{ r.id_uploaded ? '✓' : '—' }}</td>
              <td class="py-1.5 px-3">{{ r.iebc_uploaded ? '✓' : '—' }}</td>
              <td class="py-1.5 px-3">{{ r.photo_uploaded ? '✓' : '—' }}</td>
              <td class="py-1.5 px-3 font-bold" :class="r.originals_verified ? 'text-emerald-700' : 'text-slate-400'">{{ r.originals_verified ? 'VERIFIED' : 'PENDING' }}</td>
              <td class="py-1.5 px-3 font-bold" :class="r.photo_approved ? 'text-emerald-700' : 'text-slate-400'">{{ r.photo_approved ? 'APPROVED' : 'PENDING' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 7. COMPLETE AUDIT LOG REPORT -->
      <div v-else-if="selectedReport === 'audit_log' && reportData" class="space-y-4 text-xs">
        <div class="text-slate-500">Immutable Trail: Showing Latest {{ reportData.total }} Events</div>
        <table class="w-full text-left divide-y divide-slate-200 border">
          <thead class="bg-slate-50 font-bold text-slate-700">
            <tr>
              <th class="py-2 px-3">Timestamp</th>
              <th class="py-2 px-3">Officer Name</th>
              <th class="py-2 px-3">Unit</th>
              <th class="py-2 px-3">Action</th>
              <th class="py-2 px-3">Details</th>
              <th class="py-2 px-3">IP Address</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
            <tr v-for="(r, idx) in reportData.records" :key="idx">
              <td class="py-1.5 px-3 text-slate-500">{{ r.timestamp }}</td>
              <td class="py-1.5 px-3 font-bold text-slate-900 font-sans">{{ r.user_name }}</td>
              <td class="py-1.5 px-3 font-sans">{{ r.unit }}</td>
              <td class="py-1.5 px-3 font-bold text-parliament-green">{{ r.action }}</td>
              <td class="py-1.5 px-3 font-sans">{{ r.details }}</td>
              <td class="py-1.5 px-3 text-slate-400">{{ r.ip_address || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Official Signoff Footer (Prints on bottom) -->
      <div class="pt-8 border-t-2 border-slate-900 flex justify-between text-xs mt-8">
        <div>
          <div class="font-bold text-slate-900">PREPARED BY:</div>
          <div class="mt-4 text-slate-600">_________________________________</div>
          <div class="font-semibold text-slate-800 mt-1">Allan Kimani</div>
          <div class="text-slate-500 text-[10px]">Administrative Officer III, Onboarding Secretariat</div>
        </div>

        <div class="text-right">
          <div class="font-bold text-slate-900">CERTIFIED & APPROVED BY:</div>
          <div class="mt-4 text-slate-600">_________________________________</div>
          <div class="font-semibold text-slate-800 mt-1">The Clerk of the National Assembly</div>
          <div class="text-slate-500 text-[10px]">Republic of Kenya</div>
        </div>
      </div>

    </div>

  </div>
</template>
