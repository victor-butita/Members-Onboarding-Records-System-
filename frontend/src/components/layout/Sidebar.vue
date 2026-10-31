<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard, PieChart, FileSpreadsheet, UserCheck, CheckSquare,
  Users, FileText, ShieldAlert, Settings, Shield, UserCog, History
} from 'lucide-vue-next'

const route = useRoute()
const auth = useAuthStore()

const navigationItems = computed(() => [
  {
    name: 'Executive Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
    show: true
  },
  {
    name: 'Demographic Insights',
    path: '/insights',
    icon: PieChart,
    show: true
  },
  {
    name: 'Gazette Processing',
    path: '/gazette',
    icon: FileSpreadsheet,
    show: auth.canAccessUnit(['ICT', 'CLERK_LP', 'CLERK_OFFICE'])
  },
  {
    name: 'Registration Desk (L&P)',
    path: '/desk',
    icon: UserCheck,
    show: auth.canAccessUnit(['CLERK_LP', 'CLERK_OFFICE', 'AUDITOR'])
  },
  {
    name: 'Unit Clearance Stations',
    path: '/clearance',
    icon: CheckSquare,
    show: auth.canAccessUnit(['MEDIA_RELATIONS', 'ICT', 'SECURITY', 'HR_FINANCE', 'CLERK_LP', 'CLERK_OFFICE', 'AUDITOR'])
  },
  {
    name: 'Members Register',
    path: '/members',
    icon: Users,
    show: true
  },
  {
    name: 'Statutory Reports (8)',
    path: '/reports',
    icon: FileText,
    show: true
  },
  {
    name: 'User Management',
    path: '/admin/users',
    icon: UserCog,
    show: auth.isSuperUser
  },
  {
    name: 'Audit Trail',
    path: '/admin/audit',
    icon: History,
    show: auth.canAccessUnit(['SYSTEM_ADMIN', 'ICT', 'CLERK_OFFICE', 'AUDITOR'])
  },
  {
    name: 'System Settings',
    path: '/admin/settings',
    icon: Settings,
    show: auth.canAccessUnit(['SYSTEM_ADMIN', 'ICT'])
  }
])
</script>

<template>
  <aside class="w-64 bg-slate-900 text-slate-300 min-h-[calc(100vh-4rem)] flex flex-col justify-between py-4 px-3 border-r border-slate-800 no-print flex-shrink-0">
    <div class="space-y-6">
      
      <!-- Unit badge -->
      <div class="px-3 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
        <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Active Workspace</div>
        <div class="text-xs font-extrabold text-parliament-gold truncate mt-0.5">
          {{ auth.user?.unit?.replace('_', ' ') }}
        </div>
        <div class="text-[10px] text-slate-400 mt-1 flex items-center space-x-1">
          <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>{{ auth.user?.role }} Role</span>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="space-y-1">
        <template v-for="item in navigationItems" :key="item.path">
          <router-link
            v-if="item.show"
            :to="item.path"
            class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group"
            :class="[
              route.path.startsWith(item.path)
                ? 'bg-parliament-green text-white font-bold shadow-md shadow-emerald-950/30'
                : 'text-slate-300 hover:bg-slate-800/90 hover:text-white'
            ]"
          >
            <component 
              :is="item.icon" 
              class="w-4 h-4 transition-colors"
              :class="route.path.startsWith(item.path) ? 'text-parliament-gold' : 'text-slate-400 group-hover:text-parliament-gold'" 
            />
            <span class="truncate">{{ item.name }}</span>
          </router-link>
        </template>
      </nav>

    </div>

    <!-- Bottom Help & Info -->
    <div class="p-3 bg-slate-800/50 rounded-xl border border-slate-700/40 text-[11px] space-y-1 text-slate-400">
      <div class="font-bold text-slate-200">Republic of Kenya</div>
      <div>The National Assembly</div>
      <div class="text-[10px] text-parliament-gold pt-1">MORS v3.0 (October 2026)</div>
    </div>
  </aside>
</template>
