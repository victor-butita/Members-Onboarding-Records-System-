<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import {
  FileSpreadsheet, Upload, CheckCircle2, AlertTriangle, FileText,
  Download, ArrowRight, RefreshCw, ShieldCheck
} from 'lucide-vue-next'

const selectedFile = ref(null)
const gazetteNoticeNo = ref('Vol. CXXIX - No. 170 (IEBC 2027)')
const previewData = ref(null)
const isPreviewing = ref(false)
const isCommitting = ref(false)
const error = ref('')
const commitSuccess = ref('')

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0] || null
  previewData.value = null
  commitSuccess.value = ''
  error.value = ''
}

const previewGazette = async () => {
  if (!selectedFile.value) return
  isPreviewing.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await api.post('/gazette/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    previewData.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to parse gazette file.'
  } finally {
    isPreviewing.value = false
  }
}

const commitGazette = async () => {
  if (!previewData.value || !gazetteNoticeNo.value) return
  isCommitting.value = true
  error.value = ''
  commitSuccess.value = ''

  try {
    const res = await api.post('/gazette/commit', {
      items: previewData.value.sample_records, // or all parsed records
      gazette_notice_no: gazetteNoticeNo.value,
      replace_existing_seats: true
    })
    commitSuccess.value = res.data.message
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to commit gazette records.'
  } finally {
    isCommitting.value = false
  }
}

const downloadTemplate = () => {
  window.location.href = '/api/v1/gazette/template'
}
</script>

<template>
  <div class="space-y-6">
    
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Stage 1 · Gazette Processing</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">IEBC Gazette Notice Ingestion & Validation</h1>
      </div>
      <button 
        @click="downloadTemplate" 
        class="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-black text-white text-xs font-bold flex items-center space-x-2 shadow-sm"
      >
        <Download class="w-4 h-4 text-parliament-gold" />
        <span>Download Excel Template</span>
      </button>
    </div>

    <!-- Upload Card -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <h3 class="text-sm font-bold text-slate-900">Upload Gazette Notice Document</h3>
      <p class="text-xs text-slate-600">
        Upload the official IEBC Gazette Notice in <strong>Excel (.xlsx)</strong>, <strong>CSV</strong>, or <strong>PDF</strong> format. The system automatically reads column headings (Surname, Other Names, Constituency, County, Party) and verifies counts against constitutional seats.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Gazette Notice Number / Title</label>
          <input 
            type="text" 
            v-model="gazetteNoticeNo"
            placeholder="e.g. Vol. CXXIX - No. 170" 
            class="w-full px-3 py-2 text-xs border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Notice File</label>
          <input 
            type="file" 
            @change="handleFileSelect"
            accept=".xlsx,.xls,.csv,.pdf"
            class="w-full text-xs text-slate-600 file:mr-2 file:py-2 file:px-3 file:rounded-xl file:border-0 file:bg-slate-800 file:text-white file:font-semibold hover:file:bg-slate-900 cursor-pointer"
          />
        </div>
      </div>

      <div class="pt-2 flex justify-end">
        <button 
          @click="previewGazette"
          :disabled="!selectedFile || isPreviewing"
          class="px-5 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-xs shadow-md transition-all flex items-center space-x-1.5 disabled:opacity-50"
        >
          <RefreshCw v-if="isPreviewing" class="w-3.5 h-3.5 animate-spin" />
          <span>{{ isPreviewing ? 'Analyzing Document...' : 'Parse & Validate Notice' }}</span>
        </button>
      </div>
    </div>

    <!-- Error / Success messages -->
    <div v-if="error" class="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center space-x-2">
      <AlertTriangle class="w-4 h-4 text-red-500 flex-shrink-0" />
      <span>{{ error }}</span>
    </div>
    <div v-if="commitSuccess" class="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2">
      <CheckCircle2 class="w-4 h-4 text-emerald-600 flex-shrink-0" />
      <span>{{ commitSuccess }}</span>
    </div>

    <!-- Preview & Count Validation Screen -->
    <div v-if="previewData" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
      
      <!-- Seat Target Verification Table -->
      <div>
        <h3 class="text-sm font-bold text-slate-900 pb-2 border-b border-slate-100 flex items-center justify-between">
          <span>Constitutional Seat Count Audit (290 / 47 / 12)</span>
          <span 
            class="text-xs px-2.5 py-0.5 rounded-full font-bold"
            :class="previewData.is_counts_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
          >
            {{ previewData.is_counts_valid ? '✓ Complete & Balanced' : '⚠️ Discrepancy Flagged' }}
          </span>
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4 text-xs">
          <div class="p-4 rounded-xl border" :class="previewData.count_mp === 290 ? 'bg-emerald-50/50 border-emerald-200' : 'bg-amber-50/50 border-amber-200'">
            <div class="text-slate-500 font-bold uppercase text-[10px]">Constituency MPs</div>
            <div class="text-2xl font-black text-slate-900 mt-1">{{ previewData.count_mp }} <span class="text-xs text-slate-400 font-normal">/ 290 Target</span></div>
            <div class="text-[11px] mt-1" :class="previewData.count_mp === 290 ? 'text-emerald-700 font-semibold' : 'text-amber-700 font-semibold'">
              {{ previewData.count_mp === 290 ? 'All 290 Constituencies Parsed' : `Difference: ${previewData.count_mp - 290}` }}
            </div>
          </div>

          <div class="p-4 rounded-xl border" :class="previewData.count_woman_rep === 47 ? 'bg-emerald-50/50 border-emerald-200' : 'bg-amber-50/50 border-amber-200'">
            <div class="text-slate-500 font-bold uppercase text-[10px]">County Woman Reps</div>
            <div class="text-2xl font-black text-slate-900 mt-1">{{ previewData.count_woman_rep }} <span class="text-xs text-slate-400 font-normal">/ 47 Target</span></div>
            <div class="text-[11px] mt-1" :class="previewData.count_woman_rep === 47 ? 'text-emerald-700 font-semibold' : 'text-amber-700 font-semibold'">
              {{ previewData.count_woman_rep === 47 ? 'All 47 Counties Accounted' : `Difference: ${previewData.count_woman_rep - 47}` }}
            </div>
          </div>

          <div class="p-4 rounded-xl border" :class="previewData.count_nominated === 12 ? 'bg-emerald-50/50 border-emerald-200' : 'bg-amber-50/50 border-amber-200'">
            <div class="text-slate-500 font-bold uppercase text-[10px]">Nominated Members</div>
            <div class="text-2xl font-black text-slate-900 mt-1">{{ previewData.count_nominated }} <span class="text-xs text-slate-400 font-normal">/ 12 Target</span></div>
            <div class="text-[11px] mt-1" :class="previewData.count_nominated === 12 ? 'text-emerald-700 font-semibold' : 'text-amber-700 font-semibold'">
              {{ previewData.count_nominated === 12 ? 'All 12 Party Slots Filled' : `Difference: ${previewData.count_nominated - 12}` }}
            </div>
          </div>
        </div>

        <div v-if="previewData.warnings?.length" class="mt-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
          <div class="font-bold">Notice Warnings:</div>
          <ul class="list-disc list-inside">
            <li v-for="(w, idx) in previewData.warnings" :key="idx">{{ w }}</li>
          </ul>
        </div>
      </div>

      <!-- Sample Extracted Records Grid -->
      <div>
        <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">Sample Parsed Members (Review Before Import)</h4>
        <div class="border border-slate-200 rounded-xl overflow-x-auto">
          <table class="w-full text-left text-xs divide-y divide-slate-100">
            <thead class="bg-slate-50 text-slate-600 font-bold">
              <tr>
                <th class="py-2.5 px-3">Surname</th>
                <th class="py-2.5 px-3">Other Names</th>
                <th class="py-2.5 px-3">Category</th>
                <th class="py-2.5 px-3">County</th>
                <th class="py-2.5 px-3">Constituency</th>
                <th class="py-2.5 px-3">Party</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-slate-700">
              <tr v-for="(rec, idx) in previewData.sample_records" :key="idx" class="hover:bg-slate-50">
                <td class="py-2 px-3 font-bold text-slate-900">{{ rec.surname }}</td>
                <td class="py-2 px-3">{{ rec.other_names }}</td>
                <td class="py-2 px-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100">{{ rec.category }}</span></td>
                <td class="py-2 px-3">{{ rec.county || '—' }}</td>
                <td class="py-2 px-3">{{ rec.constituency || '—' }}</td>
                <td class="py-2 px-3 font-medium">{{ rec.party }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Commit Action -->
      <div class="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="text-xs text-slate-500">
          Corrigenda Rule: Committing will automatically update existing seats or add new by-election winners.
        </div>
        <button 
          @click="commitGazette"
          :disabled="isCommitting"
          class="px-6 py-2.5 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-xs shadow-md transition-all flex items-center space-x-1.5 disabled:opacity-50"
        >
          <RefreshCw v-if="isCommitting" class="w-3.5 h-3.5 animate-spin" />
          <span>{{ isCommitting ? 'Importing Official Gazette...' : 'Commit to Official Member Register' }}</span>
        </button>
      </div>

    </div>

  </div>
</template>
