<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Lock, User, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)
const slide = ref(0)

const slides = [
  {
    src: '/brand/parliament-clock.jpg',
    title: 'Parliament Buildings',
    caption: 'The National Assembly, Nairobi'
  },
  {
    src: '/brand/parliament-entrance.jpg',
    title: 'Main entrance',
    caption: 'Parliament Road'
  },
  {
    src: '/brand/chamber.jpg',
    title: 'The Chamber',
    caption: 'Where the House sits'
  },
  {
    src: '/brand/parliament-banner.jpg',
    title: 'Clock tower',
    caption: 'Parliament of Kenya'
  }
]

let timer
onMounted(() => {
  timer = setInterval(() => {
    slide.value = (slide.value + 1) % slides.length
  }, 5500)
})
onUnmounted(() => clearInterval(timer))

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
  <div class="min-h-screen lg:grid lg:grid-cols-2 bg-[#f4f1ea]">
    <section class="relative hidden lg:block min-h-screen overflow-hidden bg-[#0c2418]">
      <img
        v-for="(item, index) in slides"
        :key="item.src"
        :src="item.src"
        :alt="item.title"
        class="absolute inset-0 h-full w-full object-cover transition-opacity duration-700"
        :class="index === slide ? 'opacity-100' : 'opacity-0'"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-[#07140f] via-[#07140f]/50 to-[#07140f]/20"></div>

      <div class="relative z-10 flex h-full flex-col justify-between p-10 text-white">
        <div class="flex items-center gap-4">
          <img
            src="/brand/national-assembly-logo.png"
            alt="The National Assembly of the Republic of Kenya"
            class="h-16 w-16 rounded-full bg-white object-cover shadow-lg"
          />
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-[0.22em] text-parliament-gold">Republic of Kenya</div>
            <div class="font-serif text-2xl leading-tight">The National Assembly</div>
          </div>
        </div>

        <div class="max-w-md">
          <p class="font-serif text-4xl leading-tight">{{ slides[slide].title }}</p>
          <p class="mt-2 text-sm text-white/80">{{ slides[slide].caption }}</p>
          <div class="mt-6 flex gap-2">
            <button
              v-for="(item, index) in slides"
              :key="item.src"
              type="button"
              class="h-1.5 rounded-full transition-all"
              :class="index === slide ? 'w-8 bg-parliament-gold' : 'w-4 bg-white/40'"
              :aria-label="item.title"
              @click="slide = index"
            />
          </div>
        </div>
      </div>
    </section>

    <div class="flex min-h-screen flex-col justify-center px-6 py-12">
      <div class="mx-auto w-full max-w-md">
        <div class="mb-8 flex flex-col items-center text-center">
          <img
            src="/brand/national-assembly-logo.png"
            alt="The National Assembly of the Republic of Kenya"
            class="h-24 w-24 rounded-full bg-white object-cover shadow-md ring-4 ring-white"
          />
          <div class="mt-4 text-[11px] font-semibold uppercase tracking-[0.2em] text-parliament-gold-dark">Republic of Kenya</div>
          <h1 class="font-serif text-3xl text-slate-900">The National Assembly</h1>
          <p class="mt-1 text-sm text-slate-500">Members' Onboarding & Records System</p>
        </div>

        <div class="rounded-3xl border border-[#e6e0d4] bg-white px-6 py-8 shadow-card sm:px-8">
          <h2 class="font-serif text-2xl text-slate-900">Staff sign in</h2>
          <p class="mt-1 text-sm text-slate-500">Use the email and password issued for your department.</p>

          <div v-if="errorMessage" class="mt-4 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
            <AlertCircle class="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
            <span>{{ errorMessage }}</span>
          </div>

          <form @submit.prevent="handleLogin" class="mt-6 space-y-4 text-sm">
            <div>
              <label class="mb-1.5 block font-semibold text-slate-700">Email or username</label>
              <div class="relative">
                <input
                  v-model="username"
                  type="text"
                  required
                  placeholder="name@parliament.go.ke"
                  class="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-3 text-slate-900"
                />
                <User class="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
              </div>
            </div>
            <div>
              <label class="mb-1.5 block font-semibold text-slate-700">Password</label>
              <div class="relative">
                <input
                  v-model="password"
                  type="password"
                  required
                  placeholder="Password"
                  class="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-3 text-slate-900"
                />
                <Lock class="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
              </div>
            </div>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-parliament-green py-3 font-semibold text-white hover:bg-parliament-green-dark disabled:opacity-50"
            >
              <span>{{ isSubmitting ? 'Signing in...' : 'Sign in to workspace' }}</span>
              <ArrowRight class="h-4 w-4" />
            </button>
          </form>

          <div class="mt-6 flex items-center justify-between border-t border-slate-100 pt-4 text-xs">
            <span class="flex items-center gap-1 text-slate-400">
              <ShieldCheck class="h-3.5 w-3.5 text-parliament-gold" />
              Department access
            </span>
            <router-link to="/portal" class="font-semibold text-parliament-green hover:underline">
              Member portal
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
