<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard, PieChart, FileSpreadsheet, UserCheck, CheckSquare,
  Users, FileText, Settings, UserCog, History
} from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const route = useRoute()
const auth = useAuthStore()

watch(() => route.path, () => emit('close'))

const navigationItems = computed(() => [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, show: true },
  { name: 'Insights', path: '/insights', icon: PieChart, show: true },
  { name: 'Gazette', path: '/gazette', icon: FileSpreadsheet, show: auth.canAccessUnit(['ICT', 'CLERK_LP', 'CLERK_OFFICE']) },
  { name: 'Registration desk', path: '/desk', icon: UserCheck, show: auth.canAccessUnit(['CLERK_LP', 'CLERK_OFFICE', 'AUDITOR']) },
  { name: 'Unit clearance', path: '/clearance', icon: CheckSquare, show: auth.canAccessUnit(['MEDIA_RELATIONS', 'ICT', 'SECURITY', 'HR_FINANCE', 'CLERK_OFFICE', 'AUDITOR']) },
  { name: 'Members', path: '/members', icon: Users, show: true },
  { name: 'Reports', path: '/reports', icon: FileText, show: true },
  { name: 'Staff & roles', path: '/admin/users', icon: UserCog, show: auth.isSuperUser },
  { name: 'Audit trail', path: '/admin/audit', icon: History, show: auth.canAccessUnit(['SYSTEM_ADMIN', 'ICT', 'CLERK_OFFICE', 'AUDITOR']) },
  { name: 'Settings', path: '/admin/settings', icon: Settings, show: auth.canAccessUnit(['SYSTEM_ADMIN', 'ICT']) }
])

const unitLabel = computed(() => (auth.user?.unit || '').replaceAll('_', ' '))
</script>

<template>
  <div v-if="open" class="fixed inset-0 bg-[#06140e]/50 z-40 lg:hidden" @click="emit('close')"></div>

  <aside
    class="fixed lg:static z-50 inset-y-0 left-0 w-[16.25rem] bg-[#10241b] text-slate-300 flex flex-col border-r border-black/20 no-print transform transition-transform duration-200 lg:translate-x-0"
    :class="props.open ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="px-4 pt-5 pb-3">
      <div class="rounded-2xl bg-white/[0.04] border border-white/10 px-3.5 py-3">
        <div class="text-[10px] uppercase tracking-[0.16em] text-parliament-gold font-semibold">Workspace</div>
        <div class="text-sm font-semibold text-white mt-1 truncate">{{ unitLabel }}</div>
        <div class="text-[11px] text-emerald-100/70 mt-0.5">{{ auth.user?.role?.replaceAll('_', ' ') }}</div>
      </div>
    </div>

    <nav class="flex-1 px-3 pb-4 space-y-0.5 overflow-y-auto">
      <template v-for="item in navigationItems" :key="item.path">
        <router-link
          v-if="item.show"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-colors"
          :class="route.path.startsWith(item.path)
            ? 'bg-white/10 text-white shadow-[inset_3px_0_0_#CBA135]'
            : 'text-slate-300 hover:bg-white/5 hover:text-white'"
        >
          <component :is="item.icon" class="w-4 h-4 shrink-0" :class="route.path.startsWith(item.path) ? 'text-parliament-gold' : 'text-slate-400'" />
          <span class="truncate">{{ item.name }}</span>
        </router-link>
      </template>
    </nav>

    <div class="px-4 py-4 border-t border-white/10 text-[11px] text-slate-400">
      <div class="font-semibold text-slate-200">Republic of Kenya</div>
      <div>The National Assembly</div>
    </div>
  </aside>
</template>
