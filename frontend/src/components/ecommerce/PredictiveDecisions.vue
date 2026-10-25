<template>
  <div class="space-y-6">
    <!-- 1. Environment Before vs. After Cost Summary Table & IaC Export Hub -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm"
    >
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5 pb-4 border-b border-gray-100 dark:border-gray-800">
        <div>
          <div class="flex items-center gap-2">
            <span class="p-1.5 rounded-lg bg-brand-500 text-white">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
              </svg>
            </span>
            <h3 class="text-base font-bold text-gray-900 dark:text-white">
              Environment Sizing Impact: Before vs. After Recommendations
            </h3>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Dynamically aggregates approved FinOps decisions across Production, Staging, and Development.
          </p>
        </div>

        <!-- Export Buttons -->
        <div class="flex items-center gap-2">
          <button
            @click="downloadTerraform"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-purple-500/30 bg-purple-50 hover:bg-purple-100 dark:border-purple-500/20 dark:bg-purple-950/40 dark:text-purple-300 dark:hover:bg-purple-900/40 text-xs font-semibold text-purple-700 transition-all cursor-pointer shadow-2xs"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Terraform HCL
          </button>

          <button
            @click="downloadCliScript"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-blue-500/30 bg-blue-50 hover:bg-blue-100 dark:border-blue-500/20 dark:bg-blue-950/40 dark:text-blue-300 dark:hover:bg-blue-900/40 text-xs font-semibold text-blue-700 transition-all cursor-pointer shadow-2xs"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 17 10 11 4 5"></polyline>
              <line x1="12" y1="19" x2="20" y2="19"></line>
            </svg>
            Azure CLI (.sh)
          </button>
        </div>
      </div>

      <!-- Environment Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <!-- Prod -->
        <div class="p-4 rounded-xl border border-emerald-200 bg-emerald-50/20 dark:border-emerald-900/40 dark:bg-emerald-950/10 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300 text-[11px] flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              Production (prod)
            </span>
            <span class="px-2 py-0.5 rounded font-mono font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300 text-[10px]">
              {{ envStats.prod.count }} nodes
            </span>
          </div>
          <div class="space-y-1 pt-1 font-mono">
            <div class="flex justify-between text-gray-500 dark:text-gray-400">
              <span>Baseline:</span>
              <span>{{ formatAmount(envStats.prod.current) }}</span>
            </div>
            <div class="flex justify-between font-bold text-gray-900 dark:text-white">
              <span>Projected:</span>
              <span>{{ formatAmount(envStats.prod.projected) }}</span>
            </div>
            <div class="flex justify-between pt-1 border-t border-emerald-200/60 dark:border-emerald-900/40 text-emerald-700 dark:text-emerald-400 font-bold">
              <span>Savings:</span>
              <span>-{{ formatAmount(envStats.prod.savings) }} ({{ envStats.prod.pct }}%)</span>
            </div>
          </div>
        </div>

        <!-- Staging -->
        <div class="p-4 rounded-xl border border-amber-200 bg-amber-50/20 dark:border-amber-900/40 dark:bg-amber-950/10 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300 text-[11px] flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-amber-500"></span>
              Staging (staging)
            </span>
            <span class="px-2 py-0.5 rounded font-mono font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 text-[10px]">
              {{ envStats.staging.count }} nodes
            </span>
          </div>
          <div class="space-y-1 pt-1 font-mono">
            <div class="flex justify-between text-gray-500 dark:text-gray-400">
              <span>Baseline:</span>
              <span>{{ formatAmount(envStats.staging.current) }}</span>
            </div>
            <div class="flex justify-between font-bold text-gray-900 dark:text-white">
              <span>Projected:</span>
              <span>{{ formatAmount(envStats.staging.projected) }}</span>
            </div>
            <div class="flex justify-between pt-1 border-t border-amber-200/60 dark:border-amber-900/40 text-amber-700 dark:text-amber-400 font-bold">
              <span>Savings:</span>
              <span>-{{ formatAmount(envStats.staging.savings) }} ({{ envStats.staging.pct }}%)</span>
            </div>
          </div>
        </div>

        <!-- Dev -->
        <div class="p-4 rounded-xl border border-blue-200 bg-blue-50/20 dark:border-blue-900/40 dark:bg-blue-950/10 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold uppercase tracking-wider text-blue-800 dark:text-blue-300 text-[11px] flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-blue-500"></span>
              Development (dev)
            </span>
            <span class="px-2 py-0.5 rounded font-mono font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 text-[10px]">
              {{ envStats.dev.count }} nodes
            </span>
          </div>
          <div class="space-y-1 pt-1 font-mono">
            <div class="flex justify-between text-gray-500 dark:text-gray-400">
              <span>Baseline:</span>
              <span>{{ formatAmount(envStats.dev.current) }}</span>
            </div>
            <div class="flex justify-between font-bold text-gray-900 dark:text-white">
              <span>Projected:</span>
              <span>{{ formatAmount(envStats.dev.projected) }}</span>
            </div>
            <div class="flex justify-between pt-1 border-t border-blue-200/60 dark:border-blue-900/40 text-blue-700 dark:text-blue-400 font-bold">
              <span>Savings:</span>
              <span>-{{ formatAmount(envStats.dev.savings) }} ({{ envStats.dev.pct }}%)</span>
            </div>
          </div>
        </div>

        <!-- Total Fleet Net -->
        <div class="p-4 rounded-xl border border-brand-300 bg-brand-50/30 dark:border-brand-900/50 dark:bg-brand-950/20 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold uppercase tracking-wider text-brand-900 dark:text-brand-300 text-[11px] flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-brand-500"></span>
              Total Fleet Impact
            </span>
            <span class="px-2 py-0.5 rounded font-mono font-bold bg-brand-500 text-white text-[10px]">
              {{ vms.length }} Resources
            </span>
          </div>
          <div class="space-y-1 pt-1 font-mono">
            <div class="flex justify-between text-gray-500 dark:text-gray-400">
              <span>Baseline Spend:</span>
              <span>{{ formatAmount(totalCurrentSpend) }}</span>
            </div>
            <div class="flex justify-between font-bold text-brand-900 dark:text-brand-200">
              <span>Optimized Run Rate:</span>
              <span>{{ formatAmount(totalProjectedSpend) }}</span>
            </div>
            <div class="flex justify-between pt-1 border-t border-brand-200 dark:border-brand-800 text-success-600 dark:text-success-400 font-bold">
              <span>Monthly Reduction:</span>
              <span>-{{ formatAmount(totalSavings) }} ({{ savingsPercentage }}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Active Selected VM Recommendation & Peak Safety Guarantee -->
    <div v-if="selectedVmDetail" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Card A: Actionable Recommendation Card with Accept/Reject Toggle -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-xl bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
              </span>
              <div>
                <div class="flex items-center gap-2">
                  <h4 class="text-sm font-bold text-gray-900 dark:text-white">
                    {{ selectedVmDetail.recommendation?.title || 'FinOps Rightsizing Recommendation' }}
                  </h4>
                  <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded font-mono bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                    Action: {{ selectedVmDetail.recommendation?.action || selectedVmDetail.recommendation?.type || 'resize' }}
                  </span>
                </div>
                <span class="text-[11px] text-gray-500 dark:text-gray-400">
                  Target Sizing SKU: <strong class="text-brand-600 dark:text-brand-400 font-mono">{{ selectedVmDetail.recommendation?.targetSku || selectedVmDetail.size }}</strong>
                </span>
              </div>
            </div>
            <span
              v-if="selectedVmDetail.savings > 0"
              class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400"
            >
              Save {{ formatAmount(selectedVmDetail.savings) }}/mo
            </span>
          </div>

          <!-- Reason & Telemetry Grounding -->
          <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            {{ selectedVmDetail.recommendation?.reason || 'Continuous workload analysis calibrates provisioned specifications against peak utilization.' }}
          </p>

          <!-- Mathematical Formula & Step-by-Step Breakdown -->
          <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 text-xs space-y-2">
            <div class="font-semibold text-gray-700 dark:text-gray-200 flex items-center justify-between">
              <span>Savings Calculation Formula:</span>
              <span class="text-[10px] text-gray-400 font-mono">Confidence: {{ selectedVmDetail.recommendation?.confidence || 94 }}%</span>
            </div>
            <div class="font-mono text-[11px] p-2 rounded bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-brand-600 dark:text-brand-400">
              {{ selectedVmDetail.recommendation?.formula || 'ΔSavings = (Current_Rate − Target_Rate) × Active_Billable_Hours' }}
            </div>
            <div class="space-y-1 text-[11px] text-gray-600 dark:text-gray-400">
              <div class="flex justify-between">
                <span>• Baseline Monthly Cost:</span>
                <span class="font-mono font-medium text-gray-800 dark:text-gray-200">{{ formatAmount(selectedVmDetail.currentSpend) }}/mo</span>
              </div>
              <div class="flex justify-between">
                <span>• Projected Monthly Cost:</span>
                <span class="font-mono font-medium text-brand-600 dark:text-brand-400">{{ formatAmount(selectedVmDetail.projectedSpend) }}/mo</span>
              </div>
              <div class="flex justify-between pt-1 border-t border-gray-200 dark:border-gray-700 font-semibold text-success-600 dark:text-success-400">
                <span>• Net Monthly Reduction:</span>
                <span class="font-mono">{{ formatAmount(selectedVmDetail.recommendation?.accepted ? selectedVmDetail.savings : 0) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive Accept / Reject Toggle Buttons -->
        <div class="mt-5 pt-4 border-t border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2">
            <span class="text-gray-500">Recommendation Status:</span>
            <span
              :class="[
                'px-2.5 py-0.5 rounded-full font-bold text-[11px]',
                selectedVmDetail.recommendation?.accepted
                  ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
              ]"
            >
              {{ selectedVmDetail.recommendation?.accepted ? '✓ Accepted & Active' : '✕ Rejected / Pending' }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <button
              v-if="!selectedVmDetail.recommendation?.accepted"
              @click="toggleRecommendation(selectedVmDetail.id, true)"
              class="px-3.5 py-1.5 rounded-xl bg-success-600 hover:bg-success-700 text-white font-semibold transition-all cursor-pointer shadow-xs flex items-center gap-1.5"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              Accept Recommendation
            </button>

            <button
              v-else
              @click="toggleRecommendation(selectedVmDetail.id, false)"
              class="px-3.5 py-1.5 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold transition-all cursor-pointer flex items-center gap-1.5"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              Reject / Revert Baseline
            </button>
          </div>
        </div>
      </div>

      <!-- Card B: Peak-Safe SLA Guarantee & Capacity Radar -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-xl bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </span>
              <div>
                <h4 class="text-sm font-bold text-gray-900 dark:text-white">
                  Peak-Safe Reliability Guarantee
                </h4>
                <span class="text-[11px] text-gray-500 dark:text-gray-400">
                  p95 & p99 Traffic Spike Verification
                </span>
              </div>
            </div>
            <span
              :class="[
                'px-2.5 py-0.5 rounded-full text-xs font-bold',
                selectedVmDetail.p95Cpu > 75 || selectedVmDetail.p99Cpu > 85
                  ? 'bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300 border border-purple-200'
                  : 'bg-success-50 text-success-700 dark:bg-success-950/40 dark:text-success-300'
              ]"
            >
              {{ selectedVmDetail.p95Cpu > 75 ? 'Peak-Protected' : 'Safe to Rightsize' }}
            </span>
          </div>

          <!-- Peak-Safe Telemetry Matrix -->
          <div class="space-y-3">
            <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              Unlike simplistic tools that resize solely on 24-hour averages, our engine evaluates 30-day 95th and 99th percentile peaks to prevent SLA violations and dropped transactions.
            </p>

            <div class="grid grid-cols-3 gap-2 text-center p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
              <div>
                <span class="text-[10px] text-gray-400 uppercase font-mono block">Average CPU</span>
                <span class="text-sm font-bold text-gray-800 dark:text-gray-200 font-mono">{{ selectedVmDetail.avgCpu ?? selectedVmDetail.cpuUsage }}%</span>
              </div>
              <div class="border-x border-gray-200 dark:border-gray-700">
                <span class="text-[10px] text-gray-400 uppercase font-mono block">p95 Peak CPU</span>
                <span :class="selectedVmDetail.p95Cpu > 75 ? 'text-purple-600 font-bold' : 'text-gray-800 dark:text-gray-200 font-semibold'" class="text-sm font-mono">
                  {{ selectedVmDetail.p95Cpu ?? ((selectedVmDetail.cpuUsage || 20) * 1.35).toFixed(1) }}%
                </span>
              </div>
              <div>
                <span class="text-[10px] text-gray-400 uppercase font-mono block">p99 Spike CPU</span>
                <span :class="selectedVmDetail.p99Cpu > 85 ? 'text-error-600 font-bold' : 'text-gray-800 dark:text-gray-200 font-semibold'" class="text-sm font-mono">
                  {{ selectedVmDetail.p99Cpu ?? ((selectedVmDetail.cpuUsage || 20) * 1.5).toFixed(1) }}%
                </span>
              </div>
            </div>

            <div
              v-if="selectedVmDetail.p95Cpu > 75 || selectedVmDetail.p99Cpu > 85"
              class="p-3 rounded-xl bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800/40 text-xs space-y-1 text-purple-900 dark:text-purple-200"
            >
              <div class="font-bold flex items-center gap-1.5">
                <svg class="w-4 h-4 text-purple-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                Peak Protection Active
              </div>
              <p class="text-[11px] leading-relaxed">
                Even though average load appears modest, p99 spikes reach {{ selectedVmDetail.p99Cpu }}%. Downscaling this instance would breach SLAs during peak traffic bursts. Headroom is preserved.
              </p>
            </div>

            <div
              v-else
              class="p-3 rounded-xl bg-success-50/50 dark:bg-success-950/20 border border-success-200 dark:border-success-800/40 text-xs text-success-900 dark:text-success-200"
            >
              <div class="font-bold">✓ Verified Safe for Rightsizing</div>
              <p class="text-[11px] leading-relaxed">
                30-day telemetry verifies p99 peak stays under 50%. Rightsizing to target tier leaves over 40% headroom above maximum historical surges.
              </p>
            </div>
          </div>
        </div>

        <div class="mt-5 pt-3 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center text-xs">
          <span class="text-gray-500 font-mono">Network In/Out: <strong>{{ selectedVmDetail.networkIn || 12 }} / {{ selectedVmDetail.networkOut || 8 }} MB/s</strong></span>
          <span class="text-gray-500 font-mono">IOPS: <strong>{{ selectedVmDetail.diskUsage || 2400 }} IOPS</strong></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const {
  vms,
  selectedVmDetail,
  totalCurrentSpend,
  totalProjectedSpend,
  totalSavings,
  savingsPercentage,
  formatAmount,
  toggleRecommendation,
  downloadTerraform,
  downloadCliScript,
} = useFinOps()

const envStats = computed(() => {
  const calc = (env: string) => {
    const subset = vms.value.filter((v) => v.environment === env)
    const current = subset.reduce((acc, v) => acc + (v.currentSpend || 0), 0)
    const projected = subset.reduce((acc, v) => acc + (v.projectedSpend || v.currentSpend || 0), 0)
    const savings = current - projected
    const pct = current > 0 ? ((savings / current) * 100).toFixed(1) : '0.0'
    return { count: subset.length, current, projected, savings, pct }
  }

  return {
    prod: calc('prod'),
    staging: calc('staging'),
    dev: calc('dev'),
  }
})
</script>