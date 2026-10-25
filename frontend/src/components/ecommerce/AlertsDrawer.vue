<template>
  <div v-if="isOpen" class="fixed inset-0 z-99999 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
    <div
      class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-4xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh] relative"
    >
      <!-- Header -->
      <div class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-800">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-error-50 dark:bg-error-950/40 text-error-600 dark:text-error-400 flex items-center justify-center">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              FinOps Alerts & Workload Insights
              <span class="text-xs px-2 py-0.5 rounded-full font-bold bg-error-100 text-error-700 dark:bg-error-950/60 dark:text-error-300">
                {{ alerts.length }} Critical Findings
              </span>
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Plain-language telemetry diagnosis: Spikes, 40% cost increase decomposition, capacity limits, and budget overruns.
            </p>
          </div>
        </div>

        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Alerts List -->
      <div class="mt-6 space-y-5">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          :class="[
            'p-5 rounded-2xl border transition-all space-y-3',
            alert.severity === 'CRITICAL'
              ? 'border-error-200 bg-error-50/20 dark:border-error-900/40 dark:bg-error-950/10'
              : alert.severity === 'HIGH'
              ? 'border-amber-200 bg-amber-50/20 dark:border-amber-900/40 dark:bg-amber-950/10'
              : alert.severity === 'WARNING'
              ? 'border-purple-200 bg-purple-50/20 dark:border-purple-900/40 dark:bg-purple-950/10'
              : 'border-blue-200 bg-blue-50/20 dark:border-blue-900/40 dark:bg-blue-950/10'
          ]"
        >
          <!-- Alert Title Bar -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                  alert.severity === 'CRITICAL'
                    ? 'bg-error-600 text-white'
                    : alert.severity === 'HIGH'
                    ? 'bg-amber-600 text-white'
                    : alert.severity === 'WARNING'
                    ? 'bg-purple-600 text-white'
                    : 'bg-blue-600 text-white'
                ]"
              >
                {{ alert.severity }}
              </span>
              <h4 class="font-bold text-gray-900 dark:text-white text-sm">
                {{ alert.title }}
              </h4>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span class="font-mono font-semibold text-gray-700 dark:text-gray-300">
                {{ alert.impactCost }}
              </span>
            </div>
          </div>

          <!-- Metadata Tag Row -->
          <div class="flex flex-wrap items-center gap-2 text-[11px] font-mono text-gray-500 dark:text-gray-400">
            <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">Resource: {{ alert.resourceName }}</span>
            <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800">Region: {{ alert.region }}</span>
            <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 uppercase">Env: {{ alert.environment }}</span>
            <span v-if="alert.savingsPotential > 0" class="px-2 py-0.5 rounded bg-success-100 dark:bg-success-900/40 text-success-700 dark:text-success-300 font-bold">
              Unlock ₹{{ alert.savingsPotential.toLocaleString() }}/mo
            </span>
          </div>

          <!-- 3-Part Plain-Language Diagnosis -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-gray-100 dark:border-gray-800/80 text-xs">
            <div class="p-3 rounded-xl bg-white/80 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/50">
              <span class="font-bold text-gray-900 dark:text-gray-100 block mb-1 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                1. What Happened
              </span>
              <p class="text-gray-600 dark:text-gray-300 leading-relaxed text-[11px]">
                {{ alert.whatHappened }}
              </p>
            </div>

            <div class="p-3 rounded-xl bg-white/80 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/50">
              <span class="font-bold text-gray-900 dark:text-gray-100 block mb-1 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                2. Why It Matters
              </span>
              <p class="text-gray-600 dark:text-gray-300 leading-relaxed text-[11px]">
                {{ alert.whyItMatters }}
              </p>
            </div>

            <div class="p-3 rounded-xl bg-white/80 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700/50">
              <span class="font-bold text-gray-900 dark:text-gray-100 block mb-1 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-success-500"></span>
                3. What To Do
              </span>
              <p class="text-gray-600 dark:text-gray-300 leading-relaxed text-[11px] whitespace-pre-line">
                {{ alert.whatToDo }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-xs font-semibold text-gray-700 dark:text-gray-200 transition-colors cursor-pointer"
        >
          Close Insights
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

defineProps<{
  isOpen: boolean
}>()

defineEmits<{
  (e: 'close'): void
}>()

const { fleetAlerts } = useFinOps()

const fallbackAlerts = [
  {
    id: 'alert-anomaly-staging-01',
    type: 'spike_anomaly',
    severity: 'CRITICAL',
    title: 'Unusual Spike: Runaway Regex Loop on Staging Worker (44 hrs @ 99.4% CPU)',
    resourceId: 'zenith-staging-worker-02',
    resourceName: 'staging-crawler-worker-02',
    region: 'Noida (North)',
    environment: 'staging',
    impactCost: '₹18,400 / month wasted compute',
    whatHappened: "Process 'python3 scraper_worker.py' entered an unhandled infinite regex evaluation loop on October 23. CPU utilization spiked from 12% to 99.4% and remained pegged for 44 consecutive hours.",
    whyItMatters: 'Consumes full Standard_D8s_v5 tier compute needlessly on a staging node, burning ₹18,400/month and blocking staging test suites.',
    whatToDo: '1. SSH into the node and kill PID 4108.\n2. Push regex patch.\n3. Downscale staging node to Standard_D2s_v5 to save ₹13,600/month.',
    savingsPotential: 13600,
  },
  {
    id: 'alert-cost-growth-decomp-02',
    type: 'cost_increase',
    severity: 'HIGH',
    title: 'Sudden Cost Growth Analysis: Why Monthly Bill Grew +40.0% in 6 Months',
    resourceId: 'fleet-wide',
    resourceName: 'ZenithFlow Fleet (56 Resources)',
    region: 'Multi-Region (Noida, Bangalore, Mumbai)',
    environment: 'all',
    impactCost: '+₹1,18,000 / month increase (₹2.95L → ₹4.13L)',
    whatHappened: 'Bill grew 40% across 3 specific root-cause drivers: (1) 24/7 unstopped Dev clusters on weekends: ₹45,200/mo, (2) Over-provisioned D8s/D16s cores: ₹60,200/mo, (3) 1.5 TB of unattached orphaned SSDs: ₹12,600/mo.',
    whyItMatters: 'Gross margins contracted by 4.2% due to unallocated infrastructure overhead. Cloud spend grew 3x faster than active customer accounts.',
    whatToDo: 'Apply one-click scheduled off-hours shutdown for Dev instances and purge orphaned disks/IPs.',
    savingsPotential: 118000,
  },
  {
    id: 'alert-capacity-checkout-03',
    type: 'capacity_limit',
    severity: 'WARNING',
    title: 'Capacity Warning: Production Checkout API Peaking at 94.8% CPU (p99)',
    resourceId: 'zenith-checkout-api-01',
    resourceName: 'checkout-order-prod-01',
    region: 'Mumbai (West)',
    environment: 'prod',
    impactCost: 'High SLA Breach & Cart Abandonment Risk',
    whatHappened: 'During daily peak lunch (13:00–14:30) and dinner (20:00–21:30) shopping hours, CPU saturation hits 88.4% (p95) and spikes to 94.8% (p99).',
    whyItMatters: 'CRITICAL FINOPS RULE: DO NOT DOWNSCALE. Even though 24-hr average CPU is only 48%, downsizing this VM will cause connection timeouts and drop conversions during flash promotions.',
    whatToDo: 'Configure HPA or dynamic burst-upscale to Standard_E16s_v5 during peak hours. Maintain baseline headroom.',
    savingsPotential: 0,
  },
  {
    id: 'alert-budget-overrun-04',
    type: 'budget_overrun',
    severity: 'ALERT',
    title: 'Projected Budget Overrun: Month-End Spend ₹5,52,100 Exceeds ₹4,50,000 Budget',
    resourceId: 'billing-account',
    resourceName: 'ZenithFlow Cloud Budget Account',
    region: 'All Regions',
    environment: 'all',
    impactCost: '₹1,02,100 over budget (+22.7%)',
    whatHappened: 'Current unmanaged 30-day run rate is trending at ₹5,52,100/month against board-approved budget limit of ₹4,50,000/month.',
    whyItMatters: 'Exceeding quarterly FinOps allocation triggers mandatory CTO escalation and cloud freeze.',
    whatToDo: 'Accept the active FinOps recommendations to reduce projected spend to ₹4,11,260/month, staying safely within budget with ₹38,740 buffer.',
    savingsPotential: 140840,
  },
]

const alerts = computed(() => (fleetAlerts.value && fleetAlerts.value.length > 0 ? fleetAlerts.value : fallbackAlerts))
</script>