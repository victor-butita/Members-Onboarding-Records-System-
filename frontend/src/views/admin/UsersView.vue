<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  UserCog, UserPlus, KeyRound, CheckCircle2, AlertCircle, RefreshCw, X, Shield
} from 'lucide-vue-next'

const auth = useAuthStore()
const users = ref([])
const isLoading = ref(true)

// Add user modal
const showAddModal = ref(false)
const newUser = ref({
  username: '',
  email: '',
  full_name: '',
  password: 'Password123!',
  unit: auth.unit === 'SYSTEM_ADMIN' ? 'ICT' : auth.unit,
  role: 'STAFF'
})
const addError = ref('')
const addSuccess = ref('')
const isSubmitting = ref(false)

// Reset password modal
const activeResetUser = ref(null)
const tempPassword = ref('Password123!')
const resetSuccess = ref('')

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/users/')
    users.value = res.data
  } catch (err) {
    console.error('Failed to load users', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})

const handleCreateUser = async () => {
  addError.value = ''
  addSuccess.value = ''
  isSubmitting.value = true
  try {
    await api.post('/users/', newUser.value)
    addSuccess.value = 'Staff account provisioned. Temporary password set.'
    setTimeout(() => {
      showAddModal.value = false
      fetchUsers()
    }, 1000)
  } catch (err) {
    addError.value = err.response?.data?.detail || 'Failed to create user.'
  } finally {
    isSubmitting.value = false
  }
}

const handleResetPassword = async () => {
  if (!activeResetUser.value) return
  try {
    await api.post(`/users/${activeResetUser.value.id}/reset-password?temp_password=${encodeURIComponent(tempPassword.value)}`)
    resetSuccess.value = `Password reset for ${activeResetUser.value.username}.`
    setTimeout(() => {
      activeResetUser.value = null
      resetSuccess.value = ''
    }, 1200)
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to reset password.')
  }
}
</script>

<template>
  <div class="space-y-6">
    
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">User Administration & Hierarchy</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Staff Accounts & Unit Delegations</h1>
      </div>
      <button 
        @click="showAddModal = true; addError = ''; addSuccess = ''"
        class="px-4 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white text-xs font-bold flex items-center space-x-1.5 shadow-md"
      >
        <UserPlus class="w-4 h-4" />
        <span>Add Staff Account</span>
      </button>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-600 font-bold">
            <tr>
              <th class="py-3 px-4">Full Name</th>
              <th class="py-3 px-4">Username</th>
              <th class="py-3 px-4">Email</th>
              <th class="py-3 px-4">Department / Unit</th>
              <th class="py-3 px-4">Role</th>
              <th class="py-3 px-4">Active</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50/80">
              <td class="py-3 px-4 font-bold text-slate-900">{{ u.full_name }}</td>
              <td class="py-3 px-4 font-mono">{{ u.username }}</td>
              <td class="py-3 px-4 text-slate-500">{{ u.email }}</td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100">
                  {{ u.unit.replace('_', ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="u.role === 'SUPER_USER' ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700'"
                >
                  {{ u.role }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span v-if="u.is_active" class="text-emerald-700 font-bold">Active</span>
                <span v-else class="text-red-600 font-bold">Disabled</span>
              </td>
              <td class="py-3 px-4 text-right">
                <button 
                  @click="activeResetUser = u"
                  class="px-2.5 py-1 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold text-[11px] flex items-center space-x-1 ml-auto"
                >
                  <KeyRound class="w-3.5 h-3.5 text-slate-400" />
                  <span>Reset Pwd</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200 text-xs">
        <div class="flex items-center justify-between pb-3 border-b mb-4">
          <h3 class="text-sm font-bold text-slate-900">Provision Staff Account</h3>
          <button @click="showAddModal = false"><X class="w-5 h-5 text-slate-400" /></button>
        </div>

        <div v-if="addError" class="p-3 mb-3 rounded-lg bg-red-50 text-red-700">{{ addError }}</div>
        <div v-if="addSuccess" class="p-3 mb-3 rounded-lg bg-emerald-50 text-emerald-800">{{ addSuccess }}</div>

        <form @submit.prevent="handleCreateUser" class="space-y-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Full Name *</label>
            <input type="text" v-model="newUser.full_name" required class="w-full px-3 py-2 border rounded-xl outline-none" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Username *</label>
            <input type="text" v-model="newUser.username" required placeholder="e.g. j.mwangi" class="w-full px-3 py-2 border rounded-xl outline-none" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Official Email *</label>
            <input type="email" v-model="newUser.email" required placeholder="e.g. j.mwangi@parliament.go.ke" class="w-full px-3 py-2 border rounded-xl outline-none" />
          </div>

          <div v-if="auth.unit === 'SYSTEM_ADMIN' || auth.unit === 'ICT'">
            <label class="block font-semibold text-slate-700 mb-1">Department / Unit *</label>
            <select v-model="newUser.unit" class="w-full px-3 py-2 border rounded-xl outline-none">
              <option value="CLERK_LP">Clerks (Legal & Parliamentary Affairs)</option>
              <option value="MEDIA_RELATIONS">Media Relations</option>
              <option value="ICT">ICT Directorate</option>
              <option value="SECURITY">Parliamentary Security</option>
              <option value="HR_FINANCE">HR & Finance</option>
              <option value="CLERK_OFFICE">Office of the Clerk</option>
              <option value="AUDITOR">Internal Auditor</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Unit Role *</label>
            <select v-model="newUser.role" class="w-full px-3 py-2 border rounded-xl outline-none">
              <option value="STAFF">Regular Staff</option>
              <option value="SUPER_USER">Unit Super User</option>
              <option value="READ_ONLY">Read Only</option>
            </select>
          </div>

          <div class="flex justify-end space-x-2 pt-3 border-t">
            <button type="button" @click="showAddModal = false" class="px-3 py-1.5 border rounded-lg">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-1.5 bg-parliament-green text-white font-bold rounded-lg shadow-sm">Create Account</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reset Password Modal -->
    <div v-if="activeResetUser" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 border border-slate-200 text-xs">
        <h3 class="text-sm font-bold text-slate-900 mb-1">Reset Password</h3>
        <p class="text-slate-500 mb-3">User: {{ activeResetUser.username }} ({{ activeResetUser.full_name }})</p>

        <div v-if="resetSuccess" class="p-2 mb-3 rounded-lg bg-emerald-50 text-emerald-800">{{ resetSuccess }}</div>

        <div class="space-y-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Temporary Password</label>
            <input type="text" v-model="tempPassword" class="w-full px-3 py-2 border rounded-xl outline-none font-mono" />
          </div>

          <div class="flex justify-end space-x-2 pt-2 border-t">
            <button @click="activeResetUser = null" class="px-3 py-1.5 border rounded-lg">Cancel</button>
            <button @click="handleResetPassword" class="px-4 py-1.5 bg-slate-900 text-white font-bold rounded-lg">Apply Reset</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
