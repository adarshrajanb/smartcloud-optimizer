<template>
  <admin-layout>
    <PageBreadcrumb pageTitle="Customer FinOps Profile & Settings" />

    <div class="space-y-6">
      <!-- Tenant Overview Card -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6 shadow-sm"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold text-xl">
              {{ currentCustomer.name.slice(0, 2).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ currentCustomer.name }}</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ currentCustomer.role }} • {{ currentCustomer.company }}</p>
              <div class="mt-1 flex items-center gap-2">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                  Sub: {{ currentCustomer.subscriptionId }}
                </span>
                <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-success-50 text-success-700 dark:bg-success-950/40 dark:text-success-400">
                  Active Azure Tenant
                </span>
              </div>
            </div>
          </div>

          <!-- Switch Customer Button Group (Super Admin Only) -->
          <div v-if="isSuperAdmin" class="flex flex-col gap-1.5">
            <div class="flex items-center gap-1.5">
              <span class="text-[10px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
                Super Admin: Switch Customer Context
              </span>
              <span class="text-[9px] px-1 py-0.2 rounded font-semibold bg-brand-100 dark:bg-brand-500/20 text-brand-700 dark:text-brand-300">Root</span>
            </div>
            <div class="inline-flex rounded-lg border border-gray-200 dark:border-gray-800 p-0.5 bg-gray-100 dark:bg-gray-900">
              <button
                v-for="(prof, key) in CUSTOMER_PROFILES"
                :key="key"
                @click="switchCustomer(key)"
                :class="[
                  'px-3 py-1.5 rounded-md text-xs font-semibold transition-all',
                  currentCustomer.customerId === key
                    ? 'bg-brand-500 text-white shadow-xs'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                ]"
              >
                {{ prof.customerName.split(' ')[0] }}
              </button>
            </div>
          </div>
        </div>

        <!-- Configuration Fields -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-900 dark:text-white">Azure Subscription Details</h4>

            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Customer Enterprise</label>
              <input
                type="text"
                :value="currentCustomer.company"
                readonly
                class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs text-gray-700 dark:text-gray-300"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Azure Subscription ID</label>
              <input
                type="text"
                :value="currentCustomer.subscriptionId"
                readonly
                class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs font-mono text-gray-700 dark:text-gray-300"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Primary Azure Region</label>
              <input
                type="text"
                :value="currentCustomer.primaryRegion"
                readonly
                class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs text-gray-700 dark:text-gray-300"
              />
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="text-sm font-bold text-gray-900 dark:text-white">FinOps Governance & Preferences</h4>

            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Reporting Currency</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  @click="currency = 'INR'"
                  :class="[
                    'py-2 px-3 rounded-lg text-xs font-semibold border transition-all text-center',
                    currency === 'INR'
                      ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400'
                      : 'border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-400'
                  ]"
                >
                  Indian Rupee (₹ INR)
                </button>
                <button
                  type="button"
                  @click="currency = 'USD'"
                  :class="[
                    'py-2 px-3 rounded-lg text-xs font-semibold border transition-all text-center',
                    currency === 'USD'
                      ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400'
                      : 'border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-400'
                  ]"
                >
                  US Dollar ($ USD)
                </button>
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Monthly FinOps Budget Limit</label>
              <input
                type="text"
                :value="formatAmount(currentCustomer.budgetLimit)"
                readonly
                class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs font-mono text-gray-700 dark:text-gray-300"
              />
            </div>

            <div class="pt-2">
              <button
                type="button"
                @click="showToast('Preferences synchronized with Azure ARM FinOps connector.')"
                class="px-4 py-2.5 rounded-xl bg-brand-500 text-white text-xs font-semibold hover:bg-brand-600 transition-all shadow-xs"
              >
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </admin-layout>
</template>

<script setup lang="ts">
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import { useFinOps, CUSTOMER_PROFILES } from "@/composables/useFinOps";

const { currentCustomer, switchCustomer, currency, formatAmount, showToast, isSuperAdmin } = useFinOps();
</script>
