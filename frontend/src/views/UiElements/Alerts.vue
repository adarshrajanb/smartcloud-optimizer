<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Bottlenecks & Capacity Alerts" />
    <div class="space-y-6">
      <div
        v-for="notif in notifications"
        :key="notif.id"
        :class="[
          'rounded-2xl border p-5 sm:p-6 shadow-sm',
          notif.type === 'bottleneck'
            ? 'border-error-200 bg-error-50/30 dark:border-error-900/40 dark:bg-error-950/20'
            : 'border-brand-200 bg-brand-50/20 dark:border-brand-900/40 dark:bg-brand-950/20'
        ]"
      >
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-3">
          <div class="flex items-center gap-2.5">
            <span
              :class="[
                'p-2 rounded-xl',
                notif.type === 'bottleneck'
                  ? 'bg-error-100 text-error-700 dark:bg-error-900/50 dark:text-error-300'
                  : 'bg-brand-100 text-brand-700 dark:bg-brand-900/50 dark:text-brand-300'
              ]"
            >
              <svg v-if="notif.type === 'bottleneck'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            </span>
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ notif.title }}</h3>
              <span class="text-xs text-gray-500 font-mono">Resource ID: {{ notif.id }}</span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Current: <strong>{{ formatAmount(notif.currentSpend) }}</strong></span>
            <span class="text-xs text-success-600 font-semibold">Projected: {{ formatAmount(notif.projectedSpend) }}</span>
          </div>
        </div>

        <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
          {{ notif.message }}
        </p>

        <div v-if="notif.formula" class="p-3 rounded-xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 text-xs font-mono text-gray-700 dark:text-gray-300">
          Calculation Model: {{ notif.formula }}
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import { useFinOps } from "@/composables/useFinOps";

const { notifications, formatAmount } = useFinOps();
</script>
