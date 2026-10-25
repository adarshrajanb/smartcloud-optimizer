<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 md:gap-6">
    <!-- Card 1: Current Spend & 40% Growth Signal -->
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
        <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200/60 dark:border-amber-800/40">
          +40.0% (6-Mo Surge)
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          Current Monthly Spend
        </span>
        <h4 class="mt-1 font-bold text-gray-900 text-title-sm dark:text-white">
          {{ formatAmount(totalCurrentSpend) }}
        </h4>
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          50 resources in Noida, Bangalore & Mumbai
        </p>
      </div>
    </div>

    <!-- Card 2: Projected Spend & Budget Safeguard -->
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
        <span
          :class="[
            'inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold shadow-xs',
            totalProjectedSpend <= 450000
              ? 'bg-success-600 text-white'
              : 'bg-error-600 text-white'
          ]"
        >
          {{ totalProjectedSpend <= 450000 ? 'Within ₹4.5L Budget' : 'Budget Overrun Risk' }}
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
          Target: ₹4,50,000 / mo limit (with safety buffer)
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
          Monthly Cost Reduction
        </span>
        <h4 class="mt-1 font-bold text-success-600 dark:text-success-400 text-title-sm">
          {{ formatAmount(totalSavings) }}
        </h4>
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Annual Run-Rate Saved: <strong class="text-gray-700 dark:text-gray-300">{{ formatAmount(totalSavings * 12) }}</strong>
        </p>
      </div>
    </div>

    <!-- Card 4: Sustainability & ESG Carbon Impact -->
    <div
      class="rounded-2xl border border-emerald-200 bg-emerald-50/20 dark:border-emerald-900/30 dark:bg-emerald-950/10 p-5 md:p-6 shadow-sm"
    >
      <div class="flex items-center justify-between">
        <div
          class="flex items-center justify-center w-12 h-12 bg-emerald-100 rounded-xl dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5"></path>
            <path d="M2 12l10 5 10-5"></path>
          </svg>
        </div>
        <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
          🌿 ESG Impact
        </span>
      </div>

      <div class="mt-5">
        <span class="text-xs font-medium text-emerald-700 dark:text-emerald-300 uppercase tracking-wide">
          Clean Energy & CO₂ Avoided
        </span>
        <h4 class="mt-1 font-bold text-emerald-900 text-title-sm dark:text-emerald-100">
          {{ fleetSummary?.sustainability?.co2KgSavedMonthly ?? '2,715' }} kg CO₂e
        </h4>
        <p class="mt-2 text-xs text-emerald-700 dark:text-emerald-300">
          {{ fleetSummary?.sustainability?.kwhSavedMonthly ?? '3,311' }} kWh saved • ≈ {{ fleetSummary?.sustainability?.treesEquivalent ?? '125' }} trees planted
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFinOps } from '@/composables/useFinOps'

const {
  totalCurrentSpend,
  totalProjectedSpend,
  totalSavings,
  savingsPercentage,
  formatAmount,
  fleetSummary,
} = useFinOps()
</script>
