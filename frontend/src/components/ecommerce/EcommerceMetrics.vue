<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 md:gap-6">
    <!-- Card 1: Current Spend -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6 shadow-sm"
    >
      <div class="flex items-center justify-between">
        <div
          class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl dark:bg-gray-800 text-gray-800 dark:text-white"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="1" x2="12" y2="23"></line>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
          Azure On-Demand
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          {{ isAllNewFleet ? 'Monthly Plan Baseline' : 'Current Monthly Spend' }}
        </span>
        <h4 class="mt-1 font-bold text-gray-900 text-title-sm dark:text-white">
          {{ formatAmount(totalCurrentSpend) }}
        </h4>
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span v-if="isAllNewFleet" class="text-success-600 dark:text-success-400 font-semibold">
            MTD Billed: ₹0 (Live Telemetry Active)
          </span>
          <span v-else>
            Baseline fleet cost across {{ vms.length }} Azure VMs
          </span>
        </p>
      </div>
    </div>

    <!-- Card 2: Projected Spend with Automation -->
    <div
      class="rounded-2xl border border-brand-200 bg-brand-50/30 p-5 dark:border-brand-900/40 dark:bg-brand-500/[0.05] md:p-6 shadow-sm relative overflow-hidden"
    >
      <div class="flex items-center justify-between">
        <div
          class="flex items-center justify-center w-12 h-12 bg-brand-500 rounded-xl text-white shadow-md shadow-brand-500/20"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-brand-500 text-white shadow-xs">
          AI Auto-Scaling
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-semibold text-brand-700 dark:text-brand-300 uppercase tracking-wide">
          Projected Monthly Spend
        </span>
        <h4 class="mt-1 font-bold text-brand-900 text-title-sm dark:text-brand-100">
          {{ formatAmount(totalProjectedSpend) }}
        </h4>
        <p class="mt-2 text-xs text-brand-600 dark:text-brand-300">
          With automated off-hours rightsizing applied
        </p>
      </div>
    </div>

    <!-- Card 3: Projected Net Savings -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6 shadow-sm"
    >
      <div class="flex items-center justify-between">
        <div
          class="flex items-center justify-center w-12 h-12 bg-success-50 rounded-xl dark:bg-success-500/10 text-success-600 dark:text-success-400"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <span
          class="flex items-center gap-1 rounded-full bg-success-50 py-0.5 px-2.5 text-xs font-bold text-success-600 dark:bg-success-500/15 dark:text-success-400"
        >
          ↓ {{ savingsPercentage }}%
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          Projected Net Savings
        </span>
        <h4 class="mt-1 font-bold text-success-600 dark:text-success-400 text-title-sm">
          {{ formatAmount(totalSavings) }}
        </h4>
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Saved via 7 PM – 5 AM off-hours downscaling
        </p>
      </div>
    </div>

    <!-- Card 4: Fleet & Bottleneck Health -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6 shadow-sm"
    >
      <div class="flex items-center justify-between">
        <div
          class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl dark:bg-gray-800 text-gray-800 dark:text-white"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
            <line x1="6" y1="6" x2="6.01" y2="6"></line>
            <line x1="6" y1="18" x2="6.01" y2="18"></line>
          </svg>
        </div>
        <span
          :class="[
            'flex items-center gap-1 rounded-full py-0.5 px-2.5 text-xs font-bold',
            bottleneckCount > 0
              ? 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-400'
              : 'bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400'
          ]"
        >
          {{ bottleneckCount > 0 ? `${bottleneckCount} Bottleneck Risk` : 'Fleet Healthy' }}
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          Active VM Instances
        </span>
        <h4 class="mt-1 font-bold text-gray-900 text-title-sm dark:text-white">
          {{ vms.length }} VMs
        </h4>
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          {{ autoScaleActiveCount }} instances have auto-scaling enabled
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const {
  vms,
  totalCurrentSpend,
  totalProjectedSpend,
  totalSavings,
  savingsPercentage,
  bottleneckCount,
  autoScaleActiveCount,
  formatAmount,
} = useFinOps()

const isAllNewFleet = computed(() => vms.value.length > 0 && vms.value.every((v) => v.isNew))
</script>
