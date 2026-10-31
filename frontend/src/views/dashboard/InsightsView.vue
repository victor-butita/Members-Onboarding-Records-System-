<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { PieChart, Users, Sparkles, Award, RefreshCw, BarChart2 } from 'lucide-vue-next'

const insights = ref(null)
const isLoading = ref(true)

const fetchInsights = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/dashboards/insights')
    insights.value = res.data
  } catch (err) {
    console.error('Failed to load insights', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchInsights()
})
</script>

<template>
  <div class="space-y-6">
    
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[11px] font-bold text-parliament-gold uppercase tracking-wider">Demographic Profile & Analytics</div>
        <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">14th Parliament Composition Insights</h1>
      </div>
      <button 
        @click="fetchInsights" 
        class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center space-x-1.5 shadow-sm"
      >
        <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isLoading}" />
        <span>Refresh</span>
      </button>
    </div>

    <div v-if="insights" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <!-- Average & Median Age -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Average Age</div>
        <div class="text-3xl font-black text-slate-900 mt-2">{{ insights.avg_age }} <span class="text-sm font-normal text-slate-500">years</span></div>
        <div class="text-xs text-slate-500 mt-1">
          Median: <strong>{{ insights.median_age }}</strong> · Range: {{ insights.min_age }}–{{ insights.max_age }} yrs
        </div>
      </div>

      <!-- Female Representation -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Female Representation</div>
        <div class="text-3xl font-black text-purple-700 mt-2">{{ insights.female_share_pct }}%</div>
        <div class="text-xs text-slate-500 mt-1">
          <strong>{{ insights.gender_counts.FEMALE }}</strong> Women Members in 14th Parliament
        </div>
      </div>

      <!-- Youth Representation (< 35) -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Youth (< 35 Years)</div>
        <div class="text-3xl font-black text-blue-700 mt-2">{{ insights.under_35_pct }}%</div>
        <div class="text-xs text-slate-500 mt-1">
          <strong>{{ insights.under_35_count }}</strong> Members under age 35
        </div>
      </div>

      <!-- First-Term vs Returning -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">First-Term Members</div>
        <div class="text-3xl font-black text-emerald-700 mt-2">{{ insights.first_term_pct }}%</div>
        <div class="text-xs text-slate-500 mt-1">
          <strong>{{ insights.first_term_count }}</strong> New · <strong>{{ insights.returning_count }}</strong> Returning
        </div>
      </div>

    </div>

    <!-- Age Distribution & Party Breakdown -->
    <div v-if="insights" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Age Brackets -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center space-x-2">
          <BarChart2 class="w-4 h-4 text-parliament-green" />
          <span>Age Distribution Brackets</span>
        </h3>

        <div class="space-y-4 mt-4 text-xs">
          <div>
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>Youth (Under 35 years)</span>
              <span>{{ insights.age_brackets.under_35 }} members</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div class="bg-blue-500 h-full rounded-full" :style="{ width: `${(insights.age_brackets.under_35 / insights.total_members) * 100}%` }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>35 – 44 years</span>
              <span>{{ insights.age_brackets['35_44'] }} members</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div class="bg-emerald-500 h-full rounded-full" :style="{ width: `${(insights.age_brackets['35_44'] / insights.total_members) * 100}%` }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>45 – 54 years</span>
              <span>{{ insights.age_brackets['45_54'] }} members</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div class="bg-amber-500 h-full rounded-full" :style="{ width: `${(insights.age_brackets['45_54'] / insights.total_members) * 100}%` }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>55 – 64 years</span>
              <span>{{ insights.age_brackets['55_64'] }} members</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div class="bg-orange-500 h-full rounded-full" :style="{ width: `${(insights.age_brackets['55_64'] / insights.total_members) * 100}%` }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between font-semibold text-slate-700 mb-1">
              <span>Senior Members (65+ years)</span>
              <span>{{ insights.age_brackets['65_plus'] }} members</span>
            </div>
            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div class="bg-purple-500 h-full rounded-full" :style="{ width: `${(insights.age_brackets['65_plus'] / insights.total_members) * 100}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Party Breakdown -->
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center space-x-2">
          <Award class="w-4 h-4 text-parliament-gold" />
          <span>Political Party Representation</span>
        </h3>

        <div class="divide-y divide-slate-100 mt-2 text-xs">
          <div 
            v-for="(count, party) in insights.party_breakdown" 
            :key="party"
            class="py-2.5 flex items-center justify-between"
          >
            <span class="font-semibold text-slate-800">{{ party }}</span>
            <div class="flex items-center space-x-2">
              <span class="font-mono font-bold text-slate-900">{{ count }}</span>
              <span class="text-slate-400">({{ ((count / insights.total_members) * 100).toFixed(1) }}%)</span>
            </div>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>
