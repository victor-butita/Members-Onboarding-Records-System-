<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import {
  Settings, Mail, Send, CheckCircle2, AlertCircle, RefreshCw, Clock
} from 'lucide-vue-next'

const settingsMap = ref({})
const outbox = ref([])
const isPortalOpen = ref(true)
const closingDate = ref('2027-08-15 23:59:59')
const isSaving = ref(false)
const saveSuccess = ref('')

const fetchSettings = async () => {
  try {
    const sRes = await api.get('/settings/')
    settingsMap.value = sRes.data
    isPortalOpen.value = sRes.data.PORTAL_OPEN === 'true'
    closingDate.value = sRes.data.PORTAL_CLOSING_DATE || '2027-08-15 23:59:59'

    const oRes = await api.get('/settings/outbox')
    outbox.value = oRes.data
  } catch (err) {
    console.error('Failed to load settings', err)
  }
}

onMounted(() => {
  fetchSettings()
})

const savePortalSettings = async () => {
  isSaving.value = true
  saveSuccess.value = ''
  try {
    await api.post(`/settings/?key=PORTAL_OPEN&value=${isPortalOpen.value ? 'true' : 'false'}`)
    await api.post(`/settings/?key=PORTAL_CLOSING_DATE&value=${encodeURIComponent(closingDate.value)}`)
    saveSuccess.value = 'Portal control parameters updated.'
    setTimeout(() => { saveSuccess.value = '' }, 2000)
  } catch (err) {
    alert('Failed to update settings')
  } finally {
    isSaving.value = false
  }
}

const resendEmail = async (id) => {
  try {
    await api.post(`/settings/outbox/${id}/resend`)
    alert('Confirmation email resent.')
    fetchSettings()
  } catch (err) {
    alert('Failed to resend email.')
  }
}
</script>

<template>
  <div class="space-y-6">
    
    <div>
      <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">ICT Administration</div>
      <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">System Settings & Email Delivery Outbox</h1>
    </div>

    <!-- Portal Controls -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <h3 class="text-sm font-bold text-slate-900 pb-2 border-b">Member Portal Controls</h3>

      <div v-if="saveSuccess" class="p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs">
        {{ saveSuccess }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="p-4 rounded-xl border" :class="isPortalOpen ? 'bg-emerald-50/50 border-emerald-200' : 'bg-red-50/50 border-red-200'">
          <label class="flex items-center space-x-2.5 cursor-pointer">
            <input type="checkbox" v-model="isPortalOpen" class="w-4 h-4 text-parliament-green rounded" />
            <span class="font-bold text-slate-900 text-sm">Allow Public Online Submissions (Portal Open)</span>
          </label>
          <p class="text-slate-500 mt-1 pl-6">
            When disabled, members attempting to use the public link will see a notice that registration is closed.
          </p>
        </div>

        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <label class="block font-semibold text-slate-700 mb-1">Registration Closing Deadline</label>
          <input type="text" v-model="closingDate" class="w-full px-3 py-2 border rounded-xl outline-none font-mono" />
          <p class="text-[11px] text-slate-400 mt-1">Displayed on the public portal header.</p>
        </div>
      </div>

      <div class="flex justify-end pt-2">
        <button 
          @click="savePortalSettings"
          :disabled="isSaving"
          class="px-5 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white font-bold text-xs shadow-md"
        >
          {{ isSaving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>

    <!-- Email Outbox Queue -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="p-4 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 class="text-sm font-bold text-slate-900">Confirmation Email Outbox</h3>
          <p class="text-xs text-slate-500">All member confirmation receipts dispatched by the system (Outbox with resend guarantee).</p>
        </div>
        <button @click="fetchSettings" class="text-xs text-parliament-green font-bold hover:underline">Refresh</button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-600 font-bold">
            <tr>
              <th class="py-2.5 px-4">Recipient</th>
              <th class="py-2.5 px-4">Subject</th>
              <th class="py-2.5 px-4">Reference No</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4">Timestamp</th>
              <th class="py-2.5 px-4 text-right">Resend</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="e in outbox" :key="e.id" class="hover:bg-slate-50">
              <td class="py-2.5 px-4 font-bold text-slate-900">
                <div>{{ e.recipient_name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">{{ e.recipient_email }}</div>
              </td>
              <td class="py-2.5 px-4 truncate max-w-xs">{{ e.subject }}</td>
              <td class="py-2.5 px-4 font-mono font-bold text-parliament-green">{{ e.reference_no }}</td>
              <td class="py-2.5 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  {{ e.status }}
                </span>
              </td>
              <td class="py-2.5 px-4 font-mono text-slate-500">{{ new Date(e.created_at).toLocaleString() }}</td>
              <td class="py-2.5 px-4 text-right">
                <button 
                  @click="resendEmail(e.id)"
                  class="px-2.5 py-1 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 font-bold text-[11px] inline-flex items-center space-x-1"
                >
                  <Send class="w-3 h-3 text-slate-400" />
                  <span>Resend</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>
