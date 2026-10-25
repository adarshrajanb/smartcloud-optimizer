<template>
  <div v-if="isOpen" class="fixed inset-0 z-99999 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
    <div
      class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-3xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh] relative"
    >
      <!-- Header -->
      <div class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-800">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900 dark:text-white">
              FinOps Methodology & Assumptions Sheet
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Audit-grade calculation models, unit pricing, safety thresholds, and ESG formulas.
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

      <!-- Content -->
      <div class="mt-6 space-y-4 text-xs text-gray-600 dark:text-gray-300">
        <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 space-y-2">
          <h4 class="font-bold text-gray-900 dark:text-white text-sm flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-brand-500"></span>
            1. Cloud Unit Pricing & Proration Baseline
          </h4>
          <p class="leading-relaxed">
            All costs are benchmarked against official Microsoft Azure and Indian Cloud Datacenter pricing (Central India / Pune, South India / Chennai, West India / Mumbai) at reference exchange rate of <strong>₹84.00 per USD</strong>.
          </p>
          <ul class="list-disc pl-5 space-y-1 font-mono text-[11px] text-gray-500 dark:text-gray-400">
            <li>Standard Month Duration: <strong>730 hours / month</strong> (standard cloud financial calendar).</li>
            <li>Standard_B2s (2 vCPU, 4 GB RAM): ₹2.56/hr → ₹4,600 / month.</li>
            <li>Standard_D2s_v5 (2 vCPU, 8 GB RAM): ₹7.84/hr → ₹6,900 / month.</li>
            <li>Standard_D4s_v5 (4 vCPU, 16 GB RAM): ₹13.28/hr → ₹9,700 / month.</li>
            <li>Standard_D8s_v5 (8 vCPU, 32 GB RAM): ₹25.20/hr → ₹18,400 / month.</li>
            <li>Standard_D16s_v5 (16 vCPU, 64 GB RAM): ₹52.60/hr → ₹38,400 / month.</li>
            <li>Premium Managed SSD: <strong>₹8.40 / GB / month</strong>.</li>
            <li>Unallocated Idle Public IPv4 Penalty: <strong>₹1.92 / hour</strong> (₹1,400 / month).</li>
          </ul>
        </div>

        <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 space-y-2">
          <h4 class="font-bold text-gray-900 dark:text-white text-sm flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-purple-500"></span>
            2. Peak-Safe Sizing Rule (p95 & p99 Thresholds)
          </h4>
          <p class="leading-relaxed">
            Naive FinOps tools size instances by average CPU. SmartCloud Optimizer enforces a <strong>Strict Peak Safety Lock</strong>:
          </p>
          <div class="p-3 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 font-mono text-[11px] text-brand-600 dark:text-brand-400">
            IF (p95_CPU > 75.0% OR p99_CPU > 85.0%):
                PROHIBIT_DOWNSCALE(vm_id) -> Flag as SLA Protected
            ELSE IF (p95_CPU &lt; 35.0% AND avg_CPU &lt; 20.0%):
                RECOMMEND_RIGHTSIZE(vm_id, target_tier = tier // 2)
          </div>
          <p class="leading-relaxed text-[11px] text-gray-500 dark:text-gray-400">
            Example: <code>checkout-order-prod-01</code> has an average CPU of only 48%, but its p99 spike hits 94.8% during lunch/dinner flash sales. Our algorithm strictly protects this node from downsizing.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 space-y-2">
          <h4 class="font-bold text-gray-900 dark:text-white text-sm flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            3. Scheduled Off-Hours & Weekend Shutdown Model
          </h4>
          <p class="leading-relaxed">
            For development, staging, and batch processing workloads, infrastructure runs 24/7 needlessly:
          </p>
          <ul class="list-disc pl-5 space-y-1 text-[11px]">
            <li><strong>Development Clusters:</strong> Scheduled shutoff from 8:00 PM to 8:00 AM weekdays (12 hrs/night) + 48 hours full weekend = <strong>108 idle hours/week</strong> (64% of total time saved).</li>
            <li><strong>Batch Reconciliation Nodes:</strong> Active exclusively 01:00 AM – 04:30 AM (3.5 hrs/day). Standby hibernation saves 20.5 hrs/day.</li>
          </ul>
        </div>

        <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 space-y-2">
          <h4 class="font-bold text-gray-900 dark:text-white text-sm flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            4. Environmental, Social & Governance (ESG) Sustainability Model
          </h4>
          <p class="leading-relaxed">
            Energy and carbon metrics follow the <strong>Central Electricity Authority (CEA) of India</strong> CO₂ baseline:
          </p>
          <ul class="list-disc pl-5 space-y-1 font-mono text-[11px] text-gray-500 dark:text-gray-400">
            <li>Server compute power draw: <strong>0.08 kWh per vCPU-hour</strong> idle compute.</li>
            <li>Indian Grid Emission Factor: <strong>0.82 kg CO₂e per kWh</strong>.</li>
            <li>Carbon Abatement: <code>Monthly_CO2_kg = Monthly_kWh_Saved × 0.82</code></li>
            <li>Tree Equivalence: <strong>21.7 kg CO₂ absorbed per mature tree per year</strong>.</li>
          </ul>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-xs font-semibold text-white transition-colors cursor-pointer"
        >
          Understood & Acknowledged
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isOpen: boolean
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>