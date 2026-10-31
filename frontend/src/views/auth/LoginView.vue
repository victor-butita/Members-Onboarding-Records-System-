<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Building2, Lock, User, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    await auth.login(username.value.trim(), password.value.trim())
    router.push('/dashboard')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Invalid username or password.'
  } finally {
    isSubmitting.value = false
  }
}

// Quick demo login helper
const quickLogin = (u, p) => {
  username.value = u
  password.value = p
  handleLogin()
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Background styling -->
    <div class="absolute inset-0 opacity-10 bg-[radial-gradient(#CBA135_1px,transparent_1px)] [background-size:16px_16px]"></div>
    
    <div class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
      <!-- Republic of Kenya Header -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-parliament-green border-2 border-parliament-gold shadow-xl mb-3">
          <Building2 class="w-9 h-9 text-parliament-gold" />
        </div>
        <div class="text-[11px] font-bold tracking-widest text-parliament-gold uppercase">Republic of Kenya</div>
        <h1 class="text-xl font-extrabold text-white tracking-tight">The National Assembly</h1>
        <p class="mt-1 text-xs text-slate-400">Members' Onboarding & Records System (MORS)</p>
      </div>

      <!-- Login Card -->
      <div class="mt-8 bg-white py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-100">
        <div class="border-b border-slate-100 pb-4 mb-6">
          <h2 class="text-base font-bold text-slate-900">Staff Portal Sign-In</h2>
          <p class="text-xs text-slate-500 mt-0.5">Please authenticate with your assigned unit credentials.</p>
        </div>

        <div v-if="errorMessage" class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start space-x-2">
          <AlertCircle class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4 text-xs">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Username / Staff ID</label>
            <div class="relative">
              <input 
                type="text" 
                v-model="username" 
                required 
                placeholder="e.g. clerk.lp"
                class="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-parliament-green outline-none text-slate-900"
              />
              <User class="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            </div>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Password</label>
            <div class="relative">
              <input 
                type="password" 
                v-model="password" 
                required 
                placeholder="••••••••"
                class="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-parliament-green outline-none text-slate-900"
              />
              <Lock class="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="w-full py-2.5 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{{ isSubmitting ? 'Authenticating...' : 'Sign In to Workspace' }}</span>
            <ArrowRight class="w-4 h-4" />
          </button>
        </form>

        <!-- Quick Switcher for Demo / Rehearsal -->
        <div class="mt-6 pt-5 border-t border-slate-100">
          <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
            <ShieldCheck class="w-3 h-3 text-parliament-gold" />
            <span>Mock Gazette Pilot Roles (Click to Fill & Sign In)</span>
          </div>
          
          <!-- Master Super Admin Button -->
          <button 
            type="button" 
            @click="quickLogin('admin', 'Password123!')" 
            class="w-full mb-2 p-2 rounded-xl bg-parliament-green/10 border-2 border-parliament-green text-parliament-green font-extrabold text-xs hover:bg-parliament-green hover:text-white transition-all flex items-center justify-between"
          >
            <span>👑 Super Administrator (Full All-Access)</span>
            <span class="text-[10px] uppercase font-mono font-bold">admin</span>
          </button>

          <div class="grid grid-cols-2 gap-1.5 text-[10px]">
            <button type="button" @click="quickLogin('clerk.lp', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              ⚖️ Clerks (L&P)
            </button>
            <button type="button" @click="quickLogin('clerk.office', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              🏛️ Clerk's Office
            </button>
            <button type="button" @click="quickLogin('media.lead', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              📸 Media Relations
            </button>
            <button type="button" @click="quickLogin('ict.lead', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              💻 ICT Admin
            </button>
            <button type="button" @click="quickLogin('security.lead', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              🛡️ Security Unit
            </button>
            <button type="button" @click="quickLogin('hr.finance', 'Password123!')" class="p-1.5 rounded-lg border border-slate-200 text-left hover:bg-slate-50 font-medium truncate">
              💼 HR & Finance
            </button>
          </div>
        </div>

        <div class="mt-6 text-center">
          <router-link to="/portal" class="text-xs font-bold text-parliament-green hover:underline">
            Go to Public Member Onboarding Portal &rarr;
          </router-link>
        </div>

      </div>
    </div>
  </div>
</template>
