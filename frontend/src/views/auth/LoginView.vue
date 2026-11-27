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
    errorMessage.value = err.response?.data?.detail || 'Incorrect email/username or password.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0c2418] lg:grid lg:grid-cols-[1.1fr_0.9fr]">
    <section class="hidden lg:flex flex-col justify-between p-12 text-white border-r border-white/10">
      <div>
        <div class="text-[11px] font-semibold tracking-[0.2em] uppercase text-parliament-gold">Republic of Kenya</div>
        <h1 class="font-serif text-4xl mt-4 leading-tight">The National Assembly</h1>
        <p class="mt-4 text-emerald-100/80 max-w-md text-sm leading-relaxed">
          One register for the 14th Parliament. Gazette the House, let Members submit their particulars, then verify and clear each department in turn.
        </p>
      </div>
      <ol class="space-y-3 text-sm text-emerald-50/90">
        <li class="flex gap-3"><span class="text-parliament-gold font-semibold">01</span> Upload the gazette notice</li>
        <li class="flex gap-3"><span class="text-parliament-gold font-semibold">02</span> Members complete the public portal</li>
        <li class="flex gap-3"><span class="text-parliament-gold font-semibold">03</span> Clerks verify documents and biodata</li>
        <li class="flex gap-3"><span class="text-parliament-gold font-semibold">04</span> Each department clears only its own station</li>
      </ol>
    </section>

    <div class="flex flex-col justify-center py-12 px-6 relative">
    <div class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
      <div class="text-center lg:text-left mb-2 lg:hidden">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-[#0c3d24] border border-parliament-gold mb-3">
          <Building2 class="w-7 h-7 text-parliament-gold" />
        </div>
        <div class="text-[11px] font-bold tracking-widest text-parliament-gold uppercase">Republic of Kenya</div>
        <h1 class="font-serif text-2xl text-white">The National Assembly</h1>
        <p class="mt-1 text-xs text-emerald-100/70">Members' Onboarding & Records System</p>
      </div>

      <!-- Login Card -->
      <div class="mt-8 bg-white py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-100">
        <div class="border-b border-slate-100 pb-4 mb-6">
          <h2 class="font-serif text-2xl text-slate-900">Staff sign in</h2>
          <p class="text-xs text-slate-500 mt-0.5">Authenticate with your assigned departmental email and password.</p>
        </div>

        <div v-if="errorMessage" class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start space-x-2">
          <AlertCircle class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4 text-xs">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Email Address / Username</label>
            <div class="relative">
              <input 
                type="text" 
                v-model="username" 
                required 
                placeholder="e.g. clerk.lp@parliament.go.ke or clerk.lp"
                class="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-parliament-green outline-none text-slate-900 font-medium"
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

          <div class="pt-2">
            <button 
              type="submit" 
              :disabled="isSubmitting"
              class="w-full py-2.5 bg-parliament-green hover:bg-parliament-green-dark text-white font-bold rounded-xl shadow-md transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{{ isSubmitting ? 'Authenticating...' : 'Sign In to Workspace' }}</span>
              <ArrowRight class="w-4 h-4" />
            </button>
          </div>
        </form>

        <div class="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
          <div class="text-[11px] text-slate-400 flex items-center space-x-1">
            <ShieldCheck class="w-3.5 h-3.5 text-parliament-gold" />
            <span>MORS Role-Based Access Control</span>
          </div>
          <router-link to="/portal" class="font-bold text-parliament-green hover:underline">
            Public Member Portal &rarr;
          </router-link>
        </div>

      </div>
    </div>
    </div>
  </div>
</template>
