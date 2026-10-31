<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  Building2, User, LogOut, KeyRound, ExternalLink, ShieldCheck, 
  ChevronDown, X 
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const showUserMenu = ref(false)
const showPasswordModal = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')
const isSubmitting = ref(false)

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const handlePasswordChange = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'New passwords do not match.'
    return
  }
  if (newPassword.value.length < 8) {
    passwordError.value = 'New password must be at least 8 characters long.'
    return
  }
  
  isSubmitting.value = true
  try {
    await auth.changePassword(currentPassword.value, newPassword.value)
    passwordSuccess.value = 'Password changed successfully.'
    setTimeout(() => {
      showPasswordModal.value = false
      currentPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
      passwordSuccess.value = ''
    }, 1200)
  } catch (err) {
    passwordError.value = err.response?.data?.detail || 'Failed to update password.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <header class="bg-parliament-green text-white border-b-4 border-parliament-gold shadow-md sticky top-0 z-40 no-print">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Logo & Title -->
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full bg-white/10 border border-parliament-gold flex items-center justify-center p-1.5 shadow-inner">
          <Building2 class="w-6 h-6 text-parliament-gold" />
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-extrabold tracking-wider text-base uppercase text-white">MORS</span>
            <span class="text-xs bg-parliament-gold text-slate-900 font-bold px-2 py-0.5 rounded-full">14th Parliament</span>
          </div>
          <p class="text-[11px] text-emerald-100 font-medium tracking-tight">Members' Onboarding & Records System · Republic of Kenya</p>
        </div>
      </div>

      <!-- Quick Actions & User Profile -->
      <div class="flex items-center space-x-3">
        <!-- Portal Link -->
        <a 
          href="/portal" 
          target="_blank" 
          class="hidden md:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-900 text-xs font-semibold text-emerald-100 border border-emerald-700/50 transition-all"
        >
          <span>Member Portal</span>
          <ExternalLink class="w-3.5 h-3.5 text-parliament-gold" />
        </a>

        <!-- User Badge -->
        <div class="relative">
          <button 
            @click="showUserMenu = !showUserMenu"
            class="flex items-center space-x-2.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/20 transition-all"
          >
            <div class="w-7 h-7 rounded-full bg-parliament-gold text-slate-950 font-bold text-xs flex items-center justify-center">
              {{ auth.user?.full_name?.charAt(0) || 'U' }}
            </div>
            <div class="text-left hidden sm:block">
              <div class="text-xs font-bold text-white leading-none">{{ auth.user?.full_name }}</div>
              <div class="text-[10px] text-emerald-200 uppercase font-medium mt-0.5">
                {{ auth.user?.unit?.replace('_', ' ') }} · {{ auth.user?.role }}
              </div>
            </div>
            <ChevronDown class="w-3.5 h-3.5 text-emerald-200" />
          </button>

          <!-- Dropdown menu -->
          <div 
            v-if="showUserMenu" 
            class="absolute right-0 mt-2 w-56 rounded-xl bg-white text-slate-800 shadow-xl border border-slate-100 py-1.5 z-50 animate-in fade-in slide-in-from-top-1"
          >
            <div class="px-4 py-2 border-b border-slate-100">
              <p class="text-xs text-slate-500 font-medium">Signed in as</p>
              <p class="text-sm font-bold text-slate-900 truncate">{{ auth.user?.email }}</p>
            </div>

            <button 
              @click="showPasswordModal = true; showUserMenu = false"
              class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center space-x-2"
            >
              <KeyRound class="w-4 h-4 text-slate-500" />
              <span>Change Password</span>
            </button>

            <button 
              @click="handleLogout"
              class="w-full text-left px-4 py-2 text-xs font-medium text-red-600 hover:bg-red-50 flex items-center space-x-2"
            >
              <LogOut class="w-4 h-4 text-red-500" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- Password Change Modal -->
  <div v-if="showPasswordModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-100">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
        <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
          <KeyRound class="w-5 h-5 text-parliament-green" />
          <span>Change Account Password</span>
        </h3>
        <button @click="showPasswordModal = false" class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div v-if="passwordError" class="p-3 mb-4 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
        {{ passwordError }}
      </div>
      <div v-if="passwordSuccess" class="p-3 mb-4 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800">
        {{ passwordSuccess }}
      </div>

      <form @submit.prevent="handlePasswordChange" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Current Password</label>
          <input 
            type="password" 
            v-model="currentPassword" 
            required 
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" 
          />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">New Password (Min. 8 characters)</label>
          <input 
            type="password" 
            v-model="newPassword" 
            required 
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" 
          />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Confirm New Password</label>
          <input 
            type="password" 
            v-model="confirmPassword" 
            required 
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-parliament-green outline-none" 
          />
        </div>

        <div class="pt-2 flex justify-end space-x-2">
          <button 
            type="button" 
            @click="showPasswordModal = false" 
            class="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 font-semibold hover:bg-slate-50"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="px-4 py-2 rounded-lg bg-parliament-green hover:bg-parliament-green-dark text-white font-bold transition-all disabled:opacity-50"
          >
            {{ isSubmitting ? 'Updating...' : 'Save New Password' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
