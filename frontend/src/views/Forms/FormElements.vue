<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="SLA Policies & Auto-Scaling Rules" />
    <div class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Rule 1 -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm">
          <div class="flex items-center gap-2.5 mb-3">
            <span class="p-2 rounded-xl bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 font-bold">
              01
            </span>
            <div>
              <h4 class="text-sm font-bold text-gray-900 dark:text-white">Weekday Off-Hours Downscale Policy</h4>
              <span class="text-xs text-gray-500">Scheduled Automation</span>
            </div>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            Triggers a non-disruptive downscale to the half-capacity instance tier (e.g., Standard_D4s $\rightarrow$ Standard_D2s) Monday through Friday between <strong>7:00 PM and 5:00 AM local time</strong>.
          </p>
          <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs font-mono text-gray-700 dark:text-gray-300 space-y-1">
            <div>• Execution: 19:00:00 UTC+5:30 (Scale Down)</div>
            <div>• Reversion: 05:00:00 UTC+5:30 (Scale Up)</div>
            <div>• SLA Target: 99.95% Availability</div>
          </div>
        </div>

        <!-- Rule 2 -->
        <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm">
          <div class="flex items-center gap-2.5 mb-3">
            <span class="p-2 rounded-xl bg-warning-50 dark:bg-warning-500/10 text-warning-600 dark:text-warning-400 font-bold">
              02
            </span>
            <div>
              <h4 class="text-sm font-bold text-gray-900 dark:text-white">Peak Saturation Spike Rule</h4>
              <span class="text-xs text-gray-500">Bottleneck Protection</span>
            </div>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            If continuous vCPU or RAM utilization exceeds <strong>85% for more than 5 consecutive minutes</strong>, system will immediately provision double capacity tier (e.g. Standard_D4s $\rightarrow$ Standard_D8s).
          </p>
          <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs font-mono text-gray-700 dark:text-gray-300 space-y-1">
            <div>• Evaluation Window: 5 Minutes (Rolling average)</div>
            <div>• Cooldown Period: 20 Minutes (Anti-flapping guard)</div>
            <div>• Billing Impact: Prorated by second during active surge</div>
          </div>
        </div>
      </div>

      <PredictiveDecisions />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import PredictiveDecisions from "@/components/ecommerce/PredictiveDecisions.vue";
</script>
