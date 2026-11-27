<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Menu, LogOut, KeyRound, ExternalLink, ChevronDown, X
} from 'lucide-vue-next'

defineEmits(['toggle-menu'])

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
  <header class="bg-[#0c3d24] text-white border-b-[3px] border-parliament-gold sticky top-0 z-40 no-print">
    <div class="h-16 px-3 sm:px-5 flex items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0">
        <button
          type="button"
          class="lg:hidden p-2 rounded-lg text-emerald-100 hover:bg-white/10"
          aria-label="Open menu"
          @click="$emit('toggle-menu')"
        >
          <Menu class="w-5 h-5" />
        </button>

        <div class="flex items-center gap-3 min-w-0">
          <img
            src="/brand/national-assembly-logo.png"
            alt="The National Assembly"
            class="h-10 w-10 shrink-0 rounded-full bg-white object-cover"
          />
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-serif text-[17px] leading-none text-white">MORS</span>
              <span class="hidden sm:inline text-[10px] uppercase tracking-[0.14em] text-parliament-gold font-semibold">14th Parliament</span>
            </div>
            <p class="hidden text-[11px] text-emerald-100/90 truncate sm:block">Members' Onboarding & Records</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <a
          href="/portal"
          target="_blank"
          class="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-emerald-50 border border-white/15 hover:bg-white/10"
        >
          <span>Member portal</span>
          <ExternalLink class="w-3.5 h-3.5 text-parliament-gold" />
        </a>

        <div class="relative">
          <button
            type="button"
            @click="showUserMenu = !showUserMenu"
            class="flex items-center gap-2.5 pl-1.5 pr-2.5 py-1.5 rounded-full bg-white/8 hover:bg-white/12 border border-white/15"
          >
            <div class="w-8 h-8 rounded-full bg-parliament-gold text-[#1a1404] font-semibold text-xs flex items-center justify-center">
              {{ auth.user?.full_name?.charAt(0) || 'U' }}
            </div>
            <div class="text-left hidden sm:block max-w-[180px]">
              <div class="text-xs font-semibold text-white leading-none truncate">{{ auth.user?.full_name }}</div>
              <div class="text-[10px] text-emerald-100/80 uppercase tracking-wide mt-1 truncate">
                {{ auth.user?.unit?.replaceAll('_', ' ') }}
              </div>
            </div>
            <ChevronDown class="w-3.5 h-3.5 text-emerald-100/80" />
          </button>

          <div
            v-if="showUserMenu"
            class="absolute right-0 mt-2 w-60 rounded-2xl bg-white text-slate-800 shadow-2xl border border-slate-100 py-1.5 z-50"
          >
            <div class="px-4 py-2.5 border-b border-slate-100">
              <p class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Signed in</p>
              <p class="text-sm font-semibold text-slate-900 truncate">{{ auth.user?.email }}</p>
            </div>
            <a
              href="/portal"
              class="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 md:hidden"
            >
              <ExternalLink class="w-4 h-4 text-slate-400" />
              <span>Member portal</span>
            </a>
            <button
              type="button"
              @click="showPasswordModal = true; showUserMenu = false"
              class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
            >
              <KeyRound class="w-4 h-4 text-slate-400" />
              <span>Change password</span>
            </button>
            <button
              type="button"
              @click="handleLogout"
              class="w-full text-left px-4 py-2.5 text-sm text-red-700 hover:bg-red-50 flex items-center gap-2"
            >
              <LogOut class="w-4 h-4" />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>

  <div v-if="showPasswordModal" class="fixed inset-0 bg-slate-950/55 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-100">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
        <h3 class="font-serif text-lg text-slate-900">Change password</h3>
        <button type="button" @click="showPasswordModal = false" class="text-slate-400 hover:text-slate-600">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div v-if="passwordError" class="p-3 mb-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700">
        {{ passwordError }}
      </div>
      <div v-if="passwordSuccess" class="p-3 mb-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800">
        {{ passwordSuccess }}
      </div>

      <form @submit.prevent="handlePasswordChange" class="space-y-4 text-sm">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Current password</label>
          <input type="password" v-model="currentPassword" required class="w-full px-3 py-2.5 border border-slate-200 rounded-xl" />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">New password</label>
          <input type="password" v-model="newPassword" required class="w-full px-3 py-2.5 border border-slate-200 rounded-xl" />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Confirm new password</label>
          <input type="password" v-model="confirmPassword" required class="w-full px-3 py-2.5 border border-slate-200 rounded-xl" />
        </div>
        <div class="pt-2 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button type="button" @click="showPasswordModal = false" class="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 font-semibold">
            Cancel
          </button>
          <button type="submit" :disabled="isSubmitting" class="px-4 py-2 rounded-xl bg-parliament-green text-white font-semibold disabled:opacity-50">
            {{ isSubmitting ? 'Updating...' : 'Save password' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
