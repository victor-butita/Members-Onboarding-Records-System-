<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  UserCog, UserPlus, KeyRound, CheckCircle2, AlertCircle, RefreshCw, X, Shield, Edit, Save
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

// Edit / Assign Role modal
const activeEditUser = ref(null)
const editUserData = ref({
  id: null,
  username: '',
  full_name: '',
  email: '',
  unit: '',
  role: '',
  is_active: true
})
const editError = ref('')
const editSuccess = ref('')

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

const openEditModal = (u) => {
  activeEditUser.value = u
  editUserData.value = {
    id: u.id,
    username: u.username,
    full_name: u.full_name,
    email: u.email,
    unit: u.unit,
    role: u.role,
    is_active: u.is_active
  }
  editError.value = ''
  editSuccess.value = ''
}

const handleUpdateUser = async () => {
  isSubmitting.value = true
  editError.value = ''
  editSuccess.value = ''
  try {
    await api.put(`/users/${editUserData.value.id}`, {
      full_name: editUserData.value.full_name,
      email: editUserData.value.email,
      unit: editUserData.value.unit,
      role: editUserData.value.role,
      is_active: editUserData.value.is_active
    })
    editSuccess.value = `Role and department updated for ${editUserData.value.username}.`
    setTimeout(() => {
      activeEditUser.value = null
      fetchUsers()
    }, 900)
  } catch (err) {
    editError.value = err.response?.data?.detail || 'Failed to update user.'
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
    
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">User Administration & Hierarchy</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Staff Accounts, Departments & Role Definitions</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="fetchUsers" 
          class="px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1 shadow-sm"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
          <span>Refresh</span>
        </button>
        <button 
          @click="showAddModal = true; addError = ''; addSuccess = ''"
          class="px-4 py-2 rounded-xl bg-parliament-green hover:bg-parliament-green-dark text-white text-xs font-bold flex items-center space-x-1.5 shadow-md"
        >
          <UserPlus class="w-4 h-4" />
          <span>Add Staff Account</span>
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs divide-y divide-slate-100">
          <thead class="bg-slate-50 text-slate-700 font-bold uppercase tracking-wider text-[11px]">
            <tr>
              <th class="py-3.5 px-4">Full Name</th>
              <th class="py-3.5 px-4">Email / Login ID</th>
              <th class="py-3.5 px-4">Department / Unit</th>
              <th class="py-3.5 px-4">Assigned Role</th>
              <th class="py-3.5 px-4">Status</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50/80 transition-colors">
              <td class="py-3 px-4 font-bold text-slate-900">
                <div>{{ u.full_name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">{{ u.username }}</div>
              </td>
              <td class="py-3 px-4 text-slate-600 font-medium">{{ u.email }}</td>
              <td class="py-3 px-4">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-200">
                  {{ u.unit.replace(/_/g, ' ') }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span 
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-bold"
                  :class="u.role === 'SUPER_USER' ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700'"
                >
                  {{ u.role }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span v-if="u.is_active" class="text-emerald-700 font-bold flex items-center space-x-1">
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Active</span>
                </span>
                <span v-else class="text-red-600 font-bold">Disabled</span>
              </td>
              <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="openEditModal(u)"
                    class="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 font-bold text-[11px] text-slate-700 flex items-center space-x-1 shadow-sm"
                    title="Change department or assign different role"
                  >
                    <Edit class="w-3.5 h-3.5 text-slate-500" />
                    <span>Define Role</span>
                  </button>
                  <button 
                    @click="activeResetUser = u"
                    class="px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 font-semibold text-[11px] flex items-center space-x-1"
                  >
                    <KeyRound class="w-3.5 h-3.5 text-slate-400" />
                    <span>Reset</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL 1: EDIT / ASSIGN ROLE TO DEPARTMENT -->
    <div v-if="activeEditUser" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200 text-xs">
        <div class="flex items-center justify-between pb-3 border-b mb-4">
          <div>
            <div class="text-[10px] font-bold text-parliament-gold uppercase">Role Definition & Assignment</div>
            <h3 class="text-sm font-bold text-slate-900">Edit Staff Account: {{ editUserData.username }}</h3>
          </div>
          <button @click="activeEditUser = null"><X class="w-5 h-5 text-slate-400 hover:text-slate-600" /></button>
        </div>

        <div v-if="editError" class="p-3 mb-3 rounded-lg bg-red-50 text-red-700">{{ editError }}</div>
        <div v-if="editSuccess" class="p-3 mb-3 rounded-lg bg-emerald-50 text-emerald-800">{{ editSuccess }}</div>

        <form @submit.prevent="handleUpdateUser" class="space-y-3.5">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Full Name *</label>
            <input type="text" v-model="editUserData.full_name" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Email Address *</label>
            <input type="email" v-model="editUserData.email" required class="w-full px-3 py-2 border rounded-xl outline-none focus:ring-2 focus:ring-parliament-green font-medium" />
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Assigned Department / Unit *</label>
            <select v-model="editUserData.unit" required class="w-full px-3 py-2 border rounded-xl outline-none bg-slate-50 font-medium">
              <option value="CLERK_LP">Clerks (Legal & Parliamentary Affairs)</option>
              <option value="MEDIA_RELATIONS">Media Relations</option>
              <option value="ICT">ICT Directorate</option>
              <option value="SECURITY">Parliamentary Security</option>
              <option value="HR_FINANCE">HR & Finance</option>
              <option value="CLERK_OFFICE">Office of the Clerk</option>
              <option value="AUDITOR">Internal Auditor</option>
              <option value="SYSTEM_ADMIN">System Administrator (Full All-Access)</option>
            </select>
            <p class="text-[10px] text-slate-500 mt-1">Staff will be strictly isolated to this department's clearance work queue.</p>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Assigned Role Authority *</label>
            <select v-model="editUserData.role" required class="w-full px-3 py-2 border rounded-xl outline-none bg-slate-50 font-medium">
              <option value="STAFF">Regular Staff (Departmental Operations)</option>
              <option value="SUPER_USER">Unit Lead / Super User</option>
              <option value="READ_ONLY">Read Only (Inspection / Auditing)</option>
            </select>
          </div>

          <div class="pt-1">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" v-model="editUserData.is_active" class="w-4 h-4 text-parliament-green rounded" />
              <span class="font-semibold text-slate-800">Account is Active and Allowed to Sign In</span>
            </label>
          </div>

          <div class="flex justify-end space-x-2 pt-4 border-t">
            <button type="button" @click="activeEditUser = null" class="px-3.5 py-1.5 border rounded-xl text-slate-600 hover:bg-slate-50">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="px-5 py-1.5 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-sm flex items-center space-x-1.5">
              <Save class="w-3.5 h-3.5" />
              <span>{{ isSubmitting ? 'Saving...' : 'Save Role Updates' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 2: CREATE USER MODAL -->
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
            <input type="text" v-model="newUser.full_name" required class="w-full px-3 py-2 border rounded-xl outline-none font-medium" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Username *</label>
            <input type="text" v-model="newUser.username" required placeholder="e.g. j.mwangi" class="w-full px-3 py-2 border rounded-xl outline-none font-mono" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Official Email *</label>
            <input type="email" v-model="newUser.email" required placeholder="e.g. j.mwangi@parliament.go.ke" class="w-full px-3 py-2 border rounded-xl outline-none" />
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Department / Unit *</label>
            <select v-model="newUser.unit" class="w-full px-3 py-2 border rounded-xl outline-none bg-slate-50 font-medium">
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
            <select v-model="newUser.role" class="w-full px-3 py-2 border rounded-xl outline-none bg-slate-50 font-medium">
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

    <!-- MODAL 3: RESET PASSWORD MODAL -->
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