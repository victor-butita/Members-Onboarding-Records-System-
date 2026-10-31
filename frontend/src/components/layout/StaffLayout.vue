<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'

const auth = useAuthStore()
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const isSubmitting = ref(false)

const handleForcePasswordChange = async () => {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }
  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  isSubmitting.value = true
  try {
    await auth.changePassword(currentPassword.value, newPassword.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update password.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans">
    <Navbar />

    <div class="flex flex-1">
      <Sidebar />
      <main class="flex-1 p-6 max-w-7xl overflow-x-hidden">
        <router-view />
      </main>
    </div>

    <!-- Mandatory Password Change Modal for First-Time Sign In -->
    <div v-if="auth.mustChangePassword" class="fixed inset-0 bg-slate-900/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border-2 border-parliament-gold">
        <div class="text-center mb-5">
          <div class="w-12 h-12 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center mx-auto mb-2 font-bold text-xl">!</div>
          <h2 class="text-lg font-extrabold text-slate-900">Mandatory First Sign-in Password Reset</h2>
          <p class="text-xs text-slate-600 mt-1">
            As a security requirement for the National Assembly MORS system, all new staff must choose their own private password before proceeding.
          </p>
        </div>

        <div v-if="error" class="p-3 mb-4 rounded-lg bg-red-50 text-red-700 border border-red-200 text-xs">
          {{ error }}
        </div>

        <form @submit.prevent="handleForcePasswordChange" class="space-y-3.5 text-xs">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Temporary Password</label>
            <input type="password" v-model="currentPassword" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" />
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">New Private Password (Min. 8 characters)</label>
            <input type="password" v-model="newPassword" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" />
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Confirm New Password</label>
            <input type="password" v-model="confirmPassword" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" />
          </div>

          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="w-full py-2.5 mt-2 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-lg transition-all shadow-md"
          >
            {{ isSubmitting ? 'Updating...' : 'Set Password and Continue' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
