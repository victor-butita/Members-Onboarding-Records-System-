import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import MemberPortalView from '@/views/public/MemberPortalView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import StaffLayout from '@/components/layout/StaffLayout.vue'

import DashboardView from '@/views/dashboard/DashboardView.vue'
import InsightsView from '@/views/dashboard/InsightsView.vue'
import GazetteView from '@/views/gazette/GazetteView.vue'
import DeskCheckinView from '@/views/desk/DeskCheckinView.vue'
import ClearanceStationView from '@/views/clearance/ClearanceStationView.vue'
import MemberListView from '@/views/members/MemberListView.vue'
import MemberDetailView from '@/views/members/MemberDetailView.vue'
import ReportsView from '@/views/reports/ReportsView.vue'
import UsersView from '@/views/admin/UsersView.vue'
import AuditLogView from '@/views/admin/AuditLogView.vue'
import SettingsView from '@/views/admin/SettingsView.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const token = localStorage.getItem('mors_token')
      return token ? '/dashboard' : '/portal'
    }
  },
  {
    path: '/portal',
    name: 'MemberPortal',
    component: MemberPortalView,
    meta: { public: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/',
    component: StaffLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: DashboardView },
      { path: 'insights', name: 'Insights', component: InsightsView },
      { path: 'gazette', name: 'Gazette', component: GazetteView },
      { path: 'desk', name: 'DeskCheckin', component: DeskCheckinView },
      { path: 'clearance', name: 'Clearance', component: ClearanceStationView },
      { path: 'members', name: 'Members', component: MemberListView },
      { path: 'members/:id', name: 'MemberDetail', component: MemberDetailView },
      { path: 'reports', name: 'Reports', component: ReportsView },
      { path: 'admin/users', name: 'Users', component: UsersView },
      { path: 'admin/audit', name: 'AuditLog', component: AuditLogView },
      { path: 'admin/settings', name: 'Settings', component: SettingsView }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('mors_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
