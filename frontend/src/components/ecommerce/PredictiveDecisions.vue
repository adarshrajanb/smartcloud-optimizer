<template>
  <div v-if="selectedVmDetail" class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Card A: Off-Hours Scheduled Downscaling -->
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
                <h4 class="text-sm font-bold text-gray-900 dark:text-white">
                  Off-Hours Downscaling Recommendation
                </h4>
                <span class="text-[11px] text-gray-500 dark:text-gray-400">
                  Target Window: Weekdays 7:00 PM – 5:00 AM (10 hrs/night)
                </span>
              </div>
            </div>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400">
              Save {{ formatAmount(selectedVmDetail.savings) }}/mo
            </span>
          </div>

          <p v-if="selectedVmDetail.isNew" class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            <span class="font-semibold text-brand-600 dark:text-brand-400">Live AI Learning Mode:</span> This node was deployed recently. FinOps AI is collecting live operational telemetry without past history. Automated off-hours rightsizing is in standby mode and will calibrate its schedule upon collecting the initial 24-hour baseline.
          </p>
          <p v-else class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            Analysis of past telemetry shows compute utilization consistently drops below 18% during weekday nights. Downscaling to <strong>Standard_D2s_v5</strong> during this window maintains SLA while eliminating idle capacity waste.
          </p>

          <!-- Mathematical Formula & Calculation Steps -->
          <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 text-xs space-y-2">
            <div class="font-semibold text-gray-700 dark:text-gray-200 flex items-center justify-between">
              <span>Savings Calculation Formula:</span>
              <span class="text-[10px] text-gray-400">Itemized FinOps Model</span>
            </div>
            <div class="font-mono text-[11px] p-2 rounded bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-brand-600 dark:text-brand-400">
              ΔSavings = (Current_Rate − Target_Rate) × 10 hrs/day × 22 workdays/mo
            </div>
            <div class="space-y-1 text-[11px] text-gray-600 dark:text-gray-400">
              <div class="flex justify-between">
                <span>• Baseline Daytime Rate:</span>
                <span class="font-mono font-medium text-gray-800 dark:text-gray-200">{{ formatAmount(selectedVmDetail.hourlyRate) }}/hr</span>
              </div>
              <div class="flex justify-between">
                <span>• Off-Hours Target Rate:</span>
                <span class="font-mono font-medium text-gray-800 dark:text-gray-200">{{ formatAmount(selectedVmDetail.hourlyRate * 0.5) }}/hr</span>
              </div>
              <div class="flex justify-between">
                <span>• Off-Hours Duration:</span>
                <span class="font-mono font-medium text-gray-800 dark:text-gray-200">220 hrs/month (10 hrs × 22 days)</span>
              </div>
              <div class="flex justify-between pt-1 border-t border-gray-200 dark:border-gray-700 font-semibold text-success-600 dark:text-success-400">
                <span>• Net Projected Monthly Savings:</span>
                <span class="font-mono">{{ formatAmount(selectedVmDetail.savings) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center text-xs">
          <span class="text-gray-500">Current Spend: <strong class="text-gray-800 dark:text-gray-200">{{ formatAmount(selectedVmDetail.currentSpend) }}</strong></span>
          <span class="text-gray-500">Projected Spend: <strong class="text-success-600 dark:text-success-400">{{ formatAmount(selectedVmDetail.projectedSpend) }}</strong></span>
        </div>
      </div>

      <!-- Card B: Impending Bottleneck Prevention -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-xl bg-warning-50 dark:bg-warning-500/10 text-warning-600 dark:text-warning-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
              </span>
              <div>
                <h4 class="text-sm font-bold text-gray-900 dark:text-white">
                  Capacity Bottleneck Prevention Radar
                </h4>
                <span class="text-[11px] text-gray-500 dark:text-gray-400">
                  Saturation Risk Detection
                </span>
              </div>
            </div>
            <span
              :class="[
                'px-2.5 py-0.5 rounded-full text-xs font-bold',
                selectedVmDetail.status === 'Bottleneck Warning'
                  ? 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-400'
                  : 'bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400'
              ]"
            >
              {{ selectedVmDetail.status === 'Bottleneck Warning' ? 'Bottleneck Imminent' : 'Capacity Nominal' }}
            </span>
          </div>

          <div v-if="selectedVmDetail.status === 'Bottleneck Warning'" class="space-y-3">
            <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              Workload trend models project resource saturation (&gt;88% vCPU and Memory) during expected peak traffic window (1:00 PM – 5:30 PM). If not scaled, request latency may increase by up to 340%.
            </p>

            <div class="p-3 rounded-xl bg-error-50/50 dark:bg-error-950/20 border border-error-200 dark:border-error-900/40 text-xs space-y-1.5">
              <div class="flex justify-between font-semibold text-error-800 dark:text-error-300">
                <span>Recommended Upgrade Tier:</span>
                <span class="font-mono">Standard_D8s_v5 (8 Cores, 32 GB)</span>
              </div>
              <div class="flex justify-between text-error-700 dark:text-error-400 text-[11px]">
                <span>Incremental Prorated Cost:</span>
                <span class="font-mono">+{{ formatAmount(2330) }}/mo</span>
              </div>
              <div class="flex justify-between text-error-700 dark:text-error-400 text-[11px]">
                <span>Mitigation:</span>
                <span>Zero latency degradation; 100% SLA preserved</span>
              </div>
            </div>
          </div>

          <div v-else class="space-y-3">
            <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              Current headroom is adequate for baseline processing. Predictive monitors will automatically alert or scale if incoming requests exceed safe threshold limits.
            </p>
            <div class="p-3 rounded-xl bg-success-50/40 dark:bg-success-950/20 border border-success-200 dark:border-success-900/40 text-xs">
              <span class="font-semibold text-success-700 dark:text-success-300">Headroom Status:</span>
              <span class="text-gray-600 dark:text-gray-300 ml-1">Current vCPU at {{ selectedVmDetail.cpuUsage }}% (45% buffer available).</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
          <div v-if="selectedVmDetail.autoScaleEnabled" class="flex items-center gap-1.5 text-xs font-semibold text-success-600 dark:text-success-400">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Auto-Scale Enabled: Upgrade will trigger automatically
          </div>
          <div v-else class="flex items-center justify-between w-full">
            <span class="text-xs text-gray-500">Manual Approval Required</span>
            <button
              v-if="selectedVmDetail.status === 'Bottleneck Warning'"
              @click="handleManualUpgrade"
              class="px-3 py-1.5 rounded-lg bg-brand-500 text-white text-xs font-semibold hover:bg-brand-600 transition-all shadow-xs"
            >
              Approve 1-Click Tier Upgrade
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- CRITICAL BOTTOM SECTION: Customer Permission to Auto Upscale/Downscale & Dynamic Prorated Billing -->
    <div
      class="rounded-2xl border-2 border-brand-500/30 bg-gradient-to-r from-brand-50/50 via-white to-brand-50/30 dark:from-brand-950/30 dark:via-gray-900 dark:to-brand-950/20 p-6 shadow-md"
    >
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="space-y-1.5 max-w-2xl">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-brand-500 text-white">
              Customer Consent & SLA
            </span>
            <h3 class="text-base font-bold text-gray-900 dark:text-white">
              Automated Resource Upscaling & Downscaling Authorization
            </h3>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
            I hereby authorize <strong>SmartCloud Optimizer (CloudScale Technologies)</strong> to automatically adjust vCPU, RAM, and disk IOPS specifications for <strong>{{ selectedVmDetail.name }}</strong> based on predictive workload telemetry.
          </p>
          <div class="text-[11px] text-gray-500 dark:text-gray-400 space-y-0.5 pt-1">
            <p>• <strong>Prorated Billing Terms:</strong> All resource modifications are billed on a strict per-second prorated basis matching Microsoft Azure compute billing schedules.</p>
            <p>• <strong>Cost Transparency:</strong> Downscaling guarantees projected savings of {{ formatAmount(selectedVmDetail.savings) }}/mo; bottleneck upgrades only execute during detected saturation.</p>
          </div>
        </div>

        <!-- Toggle Switch Control -->
        <div class="flex flex-col items-center sm:items-end gap-2 shrink-0">
          <label class="relative inline-flex items-center cursor-pointer select-none">
            <input
              type="checkbox"
              :checked="selectedVmDetail.autoScaleEnabled"
              @change="toggleAutoScale(selectedVmDetail.id, !selectedVmDetail.autoScaleEnabled)"
              class="sr-only peer"
            />
            <div
              class="w-14 h-7 bg-gray-200 peer-focus:outline-hidden rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[3px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-brand-500 shadow-inner"
            ></div>
          </label>
          <span
            :class="[
              'text-xs font-bold',
              selectedVmDetail.autoScaleEnabled ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400'
            ]"
          >
            {{ selectedVmDetail.autoScaleEnabled ? 'Auto-Scaling Authorized' : 'Permission Not Granted' }}
          </span>
          <span class="text-[10px] text-gray-400">Syncs dynamically with Azure ARM</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFinOps } from '@/composables/useFinOps'

const { selectedVmDetail, toggleAutoScale, formatAmount, showToast } = useFinOps()

const handleManualUpgrade = () => {
  if (selectedVmDetail.value) {
    toggleAutoScale(selectedVmDetail.value.id, true)
    showToast(`Approved tier upgrade for ${selectedVmDetail.value.name}. Provisioning Standard_D8s_v5.`)
  }
}
</script>
