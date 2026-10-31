<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import {
  Users, UserCheck, CheckCircle2, Clock, AlertTriangle, ArrowUpRight,
  TrendingUp, Building, Shield, Camera, Cpu, Briefcase, RefreshCw, AlertCircle
} from 'lucide-vue-next'

const stats = ref(null)
const isLoading = ref(true)
const error = ref('')

const fetchDashboard = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const res = await api.get('/dashboards/summary')
    stats.value = res.data
  } catch (err) {
    error.value = 'Failed to load dashboard metrics.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="space-y-6">
    
    <!-- Top Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Office of the Clerk · The National Assembly</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">Executive Onboarding Funnel & Overview</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="fetchDashboard" 
          class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
        >
          <RefreshCw class="w-3.5 h-3.5 text-slate-500" :class="{'animate-spin': isLoading}" />
          <span>Refresh Data</span>
        </button>
      </div>
    </div>

    <!-- Live System Alerts -->
    <div v-if="stats?.alerts?.length" class="space-y-2">
      <div 
        v-for="(a, idx) in stats.alerts" 
        :key="idx"
        class="p-3.5 rounded-xl border text-xs flex items-center space-x-2"
        :class="{
          'bg-amber-50 border-amber-200 text-amber-900': a.type === 'warning',
          'bg-emerald-50 border-emerald-200 text-emerald-900': a.type === 'success',
          'bg-blue-50 border-blue-200 text-blue-900': a.type === 'info'
        }"
      >
        <AlertCircle class="w-4 h-4 flex-shrink-0" />
        <span>{{ a.message }}</span>
      </div>
    </div>

    <!-- 4 Key Funnel Metric Cards -->
    <div v-if="stats" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <!-- Gazetted -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">1. Gazetted Members</div>
        <div class="text-3xl font-black text-slate-900 mt-2">{{ stats.funnel.total_gazetted }}</div>
        <div class="text-[11px] text-slate-500 mt-1">Official IEBC Notice (Target: 349)</div>
        <div class="absolute right-4 top-4 w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700">
          <Users class="w-5 h-5" />
        </div>
      </div>

      <!-- Online Submissions -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">2. Online Submissions</div>
        <div class="text-3xl font-black text-slate-900 mt-2">{{ stats.funnel.submitted_online }}</div>
        <div class="text-[11px] text-emerald-600 font-bold mt-1 flex items-center space-x-1">
          <span>{{ stats.funnel.submitted_online_pct }}% of House</span>
          <span class="text-slate-400 font-normal">(Target: 70%+)</span>
        </div>
        <div class="absolute right-4 top-4 w-10 h-10 rounded-xl bg-emerald-50 text-parliament-green flex items-center justify-center">
          <ArrowUpRight class="w-5 h-5" />
        </div>
      </div>

      <!-- Desk Checked-In -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">3. Desk Check-Ins (L&P)</div>
        <div class="text-3xl font-black text-slate-900 mt-2">{{ stats.funnel.desk_checked_in }}</div>
        <div class="text-[11px] text-blue-600 font-bold mt-1">
          <span>{{ stats.funnel.desk_checked_in_pct }}% Physically Reported</span>
        </div>
        <div class="absolute right-4 top-4 w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
          <UserCheck class="w-5 h-5" />
        </div>
      </div>

      <!-- Fully Cleared -->
      <div class="bg-white p-5 rounded-2xl border-2 border-parliament-gold/60 shadow-sm relative overflow-hidden">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">4. Fully Cleared</div>
        <div class="text-3xl font-black text-emerald-800 mt-2">{{ stats.funnel.fully_cleared }}</div>
        <div class="text-[11px] text-emerald-700 font-bold mt-1">
          <span>{{ stats.funnel.fully_cleared_pct }}% Cleared All 6 Units</span>
        </div>
        <div class="absolute right-4 top-4 w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center">
          <CheckCircle2 class="w-5 h-5" />
        </div>
      </div>

    </div>

    <!-- Funnel Progress Bar -->
    <div v-if="stats" class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
      <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">Onboarding Funnel Completion</h3>
      <div class="w-full bg-slate-100 h-4 rounded-full overflow-hidden flex">
        <div 
          class="bg-emerald-600 h-full transition-all duration-500" 
          :style="{ width: `${stats.funnel.fully_cleared_pct}%` }"
          title="Fully Cleared"
        ></div>
        <div 
          class="bg-blue-500 h-full transition-all duration-500" 
          :style="{ width: `${Math.max(0, stats.funnel.desk_checked_in_pct - stats.funnel.fully_cleared_pct)}%` }"
          title="Desk Verified"
        ></div>
        <div 
          class="bg-amber-400 h-full transition-all duration-500" 
          :style="{ width: `${Math.max(0, stats.funnel.submitted_online_pct - stats.funnel.desk_checked_in_pct)}%` }"
          title="Online Registered"
        ></div>
      </div>
      <div class="flex flex-wrap gap-4 text-xs mt-3 pt-2 border-t border-slate-100">
        <div class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-emerald-600"></span><span class="text-slate-600 font-medium">Fully Cleared: {{ stats.funnel.fully_cleared }}</span></div>
        <div class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-blue-500"></span><span class="text-slate-600 font-medium">Physical Desk Verified: {{ stats.funnel.desk_checked_in }}</span></div>
        <div class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-amber-400"></span><span class="text-slate-600 font-medium">Online Biodata Submitted: {{ stats.funnel.submitted_online }}</span></div>
      </div>
    </div>

    <!-- Unit Clearance Progress & Category Breakdown -->
    <div v-if="stats" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Unit Clearance Progress -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center justify-between">
          <span>Clearance Progress by Department / Unit</span>
          <span class="text-xs text-slate-400 font-normal">All 349 Members</span>
        </h3>
        
        <div class="space-y-4 mt-4">
          <div v-for="unit in stats.unit_progress" :key="unit.unit" class="text-xs">
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>{{ unit.unit_name }}</span>
              <span>{{ unit.completed }} / 349 ({{ unit.pct }}%)</span>
            </div>
            <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-parliament-green h-full rounded-full transition-all duration-500"
                :style="{ width: `${unit.pct}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100">
          Onboarding by Member Category
        </h3>

        <div class="divide-y divide-slate-100 mt-3 text-xs">
          <!-- Constituency MPs -->
          <div class="py-3">
            <div class="flex justify-between font-bold text-slate-900 mb-1">
              <span>Elected Constituency MPs (290)</span>
              <span class="text-parliament-green">{{ stats.category_breakdown.MP?.fully_cleared }} cleared</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-slate-600 bg-slate-50 p-2.5 rounded-xl">
              <div>Total: <strong>{{ stats.category_breakdown.MP?.total }}</strong></div>
              <div>Online: <strong>{{ stats.category_breakdown.MP?.submitted_online }}</strong></div>
              <div>Desk In: <strong>{{ stats.category_breakdown.MP?.checked_in }}</strong></div>
            </div>
          </div>

          <!-- County Woman Reps -->
          <div class="py-3">
            <div class="flex justify-between font-bold text-slate-900 mb-1">
              <span>County Woman Representatives (47)</span>
              <span class="text-purple-700">{{ stats.category_breakdown.WOMAN_REP?.fully_cleared }} cleared</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-slate-600 bg-slate-50 p-2.5 rounded-xl">
              <div>Total: <strong>{{ stats.category_breakdown.WOMAN_REP?.total }}</strong></div>
              <div>Online: <strong>{{ stats.category_breakdown.WOMAN_REP?.submitted_online }}</strong></div>
              <div>Desk In: <strong>{{ stats.category_breakdown.WOMAN_REP?.checked_in }}</strong></div>
            </div>
          </div>

          <!-- Nominated Members -->
          <div class="py-3">
            <div class="flex justify-between font-bold text-slate-900 mb-1">
              <span>Nominated Members (12)</span>
              <span class="text-blue-700">{{ stats.category_breakdown.NOMINATED?.fully_cleared }} cleared</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-slate-600 bg-slate-50 p-2.5 rounded-xl">
              <div>Total: <strong>{{ stats.category_breakdown.NOMINATED?.total }}</strong></div>
              <div>Online: <strong>{{ stats.category_breakdown.NOMINATED?.submitted_online }}</strong></div>
              <div>Desk In: <strong>{{ stats.category_breakdown.NOMINATED?.checked_in }}</strong></div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 14-Day Trend and Recent Activity Stream -->
    <div v-if="stats" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- 14-Day Trend Table / Mini Bar -->
      <div class="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center justify-between">
          <span class="flex items-center space-x-1.5">
            <TrendingUp class="w-4 h-4 text-parliament-green" />
            <span>14-Day Influx Trend (Online vs Physical Check-Ins)</span>
          </span>
          <span class="text-[11px] text-slate-400">Daily Trajectory</span>
        </h3>

        <div class="mt-4 overflow-x-auto">
          <div class="flex items-end gap-2 h-44 pt-6 px-2 min-w-[500px]">
            <div 
              v-for="day in stats.fourteen_day_trend" 
              :key="day.date" 
              class="flex-1 flex flex-col items-center gap-1 h-full justify-end group"
            >
              <div class="text-[9px] text-slate-400 font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                {{ day.online + day.desk }}
              </div>
              <div class="w-full flex items-end justify-center gap-0.5 h-32 bg-slate-50 rounded-t p-0.5">
                <!-- Online bar -->
                <div 
                  class="w-1/2 bg-amber-400 rounded-t transition-all hover:bg-amber-500" 
                  :style="{ height: `${Math.min(100, (day.online / 40) * 100)}%` }"
                  :title="`${day.date}: ${day.online} Online Submissions`"
                ></div>
                <!-- Desk bar -->
                <div 
                  class="w-1/2 bg-parliament-green rounded-t transition-all hover:bg-parliament-green-dark" 
                  :style="{ height: `${Math.min(100, (day.desk / 40) * 100)}%` }"
                  :title="`${day.date}: ${day.desk} Desk Check-ins`"
                ></div>
              </div>
              <span class="text-[9px] text-slate-500 font-medium whitespace-nowrap">{{ day.date }}</span>
            </div>
          </div>
          
          <div class="flex items-center justify-center space-x-6 text-xs text-slate-500 pt-3 border-t border-slate-100 mt-2">
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded bg-amber-400"></span><span>Online Pre-Registrations</span></div>
            <div class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded bg-parliament-green"></span><span>Desk Physical Check-Ins</span></div>
          </div>
        </div>
      </div>

      <!-- Recent Audit Log Feed -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center justify-between">
          <span>Live Activity Feed</span>
          <router-link to="/admin/audit" class="text-xs text-parliament-green hover:underline">View All</router-link>
        </h3>

        <div class="divide-y divide-slate-100 mt-2 text-xs">
          <div v-for="act in stats.recent_activity" :key="act.id" class="py-2.5">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-800">{{ act.user_name }}</span>
              <span class="text-[10px] text-slate-400 font-mono">{{ new Date(act.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
            </div>
            <p class="text-slate-600 text-[11px] mt-0.5 leading-snug line-clamp-2">{{ act.details }}</p>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>
