<template>
  <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03] shadow-sm">
    <!-- Header -->
    <div class="text-center max-w-2xl mx-auto mb-8 pt-2">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-500/10 border border-brand-200 dark:border-brand-500/20 text-brand-700 dark:text-brand-300 text-xs font-semibold mb-3">
        <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
        Tenant Cloud Provisioning
      </div>
      <h2 class="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
        Choose a VM Plan for {{ currentCustomer.customerName }}
      </h2>
      <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-2 leading-relaxed">
        Your organization tenant currently has 0 active virtual machines. Select a compute plan to provision your initial Azure instance and activate autonomous FinOps telemetry.
      </p>
    </div>

    <!-- Plans Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-6xl mx-auto mb-8">
      <!-- Plan 1: Starter -->
      <div
        class="rounded-2xl border p-6 flex flex-col justify-between transition-all hover:shadow-md relative bg-white dark:bg-gray-900"
        :class="selectedPlan === 'starter' ? 'border-brand-500 ring-2 ring-brand-500/20' : 'border-gray-200 dark:border-gray-800'"
      >
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Starter Tier</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
              Standard_B2s
            </span>
          </div>

          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
            Starter Cloud Node
          </h3>
          <p class="text-xs text-gray-500 mb-4">
            Best for lightweight web services, background workers, and staging environments.
          </p>

          <div class="mb-5 pb-5 border-b border-gray-100 dark:border-gray-800">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-extrabold text-gray-900 dark:text-white">{{ formatAmount(1850) }}</span>
              <span class="text-xs text-gray-400">/ month</span>
            </div>
            <span class="text-[11px] text-gray-400 block mt-0.5">{{ formatAmount(2.56) }}/hr compute rate</span>
          </div>

          <!-- Specs List -->
          <ul class="space-y-2.5 text-xs text-gray-600 dark:text-gray-300 mb-6">
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>2 vCPUs</strong> (Burstable AMD EPYC™)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>4 GB RAM</strong> High-speed DDR4
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>64 GB SSD</strong> (1,280 Max IOPS)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              1,000 Mbps Accelerated Networking
            </li>
            <li class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Off-hours scheduling: Saves ~₹650/mo
            </li>
          </ul>
        </div>

        <button
          @click="selectAndProvision('starter')"
          :disabled="isProvisioning"
          class="w-full py-2.5 px-4 rounded-xl text-xs font-bold border border-gray-300 dark:border-gray-700 hover:border-brand-500 hover:text-brand-600 text-gray-700 dark:text-gray-200 transition-all cursor-pointer disabled:opacity-50"
        >
          {{ isProvisioning && selectedPlan === 'starter' ? 'Provisioning...' : 'Provision Starter Node' }}
        </button>
      </div>

      <!-- Plan 2: Business (Recommended) -->
      <div
        class="rounded-2xl border-2 p-6 flex flex-col justify-between transition-all hover:shadow-lg relative bg-white dark:bg-gray-900 border-brand-500 shadow-md shadow-brand-500/10"
      >
        <!-- Most Popular Pill -->
        <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-brand-500 text-white text-[10px] font-bold uppercase tracking-wider shadow-sm">
          Recommended Choice
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">Business Tier</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-brand-50 dark:bg-brand-500/20 text-brand-700 dark:text-brand-300">
              Standard_D4s_v5
            </span>
          </div>

          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
            Business Performance Cluster
          </h3>
          <p class="text-xs text-gray-500 mb-4">
            Production web clusters, e-commerce APIs, and business-critical workloads.
          </p>

          <div class="mb-5 pb-5 border-b border-gray-100 dark:border-gray-800">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-extrabold text-brand-600 dark:text-brand-400">{{ formatAmount(7400) }}</span>
              <span class="text-xs text-gray-400">/ month</span>
            </div>
            <span class="text-[11px] text-gray-400 block mt-0.5">{{ formatAmount(10.27) }}/hr compute rate</span>
          </div>

          <!-- Specs List -->
          <ul class="space-y-2.5 text-xs text-gray-600 dark:text-gray-300 mb-6">
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>4 Dedicated vCPUs</strong> (Intel Xeon® Platinum)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>16 GB RAM</strong> High-Speed ECC
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>128 GB Premium SSD</strong> (6,400 Max IOPS)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              4,000 Mbps High Throughput Network
            </li>
            <li class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Off-hours scaling: Saves ~₹2,200/mo
            </li>
            <li class="flex items-center gap-2 text-brand-600 dark:text-brand-400 font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              Bottleneck proactive radar included
            </li>
          </ul>
        </div>

        <button
          @click="selectAndProvision('business')"
          :disabled="isProvisioning"
          class="w-full py-2.5 px-4 rounded-xl text-xs font-bold bg-brand-500 hover:bg-brand-600 text-white shadow-md shadow-brand-500/20 transition-all cursor-pointer disabled:opacity-50"
        >
          {{ isProvisioning && selectedPlan === 'business' ? 'Provisioning Instance...' : 'Provision Business Node' }}
        </button>
      </div>

      <!-- Plan 3: Enterprise -->
      <div
        class="rounded-2xl border p-6 flex flex-col justify-between transition-all hover:shadow-md relative bg-white dark:bg-gray-900"
        :class="selectedPlan === 'enterprise' ? 'border-brand-500 ring-2 ring-brand-500/20' : 'border-gray-200 dark:border-gray-800'"
      >
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Enterprise Tier</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
              Standard_E8s_v5
            </span>
          </div>

          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
            Enterprise Memory Node
          </h3>
          <p class="text-xs text-gray-500 mb-4">
            High memory databases, large in-memory caches, and heavy analytics pipelines.
          </p>

          <div class="mb-5 pb-5 border-b border-gray-100 dark:border-gray-800">
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-extrabold text-gray-900 dark:text-white">{{ formatAmount(18200) }}</span>
              <span class="text-xs text-gray-400">/ month</span>
            </div>
            <span class="text-[11px] text-gray-400 block mt-0.5">{{ formatAmount(25.27) }}/hr compute rate</span>
          </div>

          <!-- Specs List -->
          <ul class="space-y-2.5 text-xs text-gray-600 dark:text-gray-300 mb-6">
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>8 Dedicated vCPUs</strong> (High Performance)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>64 GB ECC RAM</strong> Enterprise Tier
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              <strong>256 GB Ultra SSD</strong> (12,800 Max IOPS)
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>
              8,000 Mbps Dedicated Networking
            </li>
            <li class="flex items-center gap-2 text-error-600 dark:text-error-400 font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-error-500"></span>
              Emergency burst upsizing ready
            </li>
          </ul>
        </div>

        <button
          @click="selectAndProvision('enterprise')"
          :disabled="isProvisioning"
          class="w-full py-2.5 px-4 rounded-xl text-xs font-bold border border-gray-300 dark:border-gray-700 hover:border-brand-500 hover:text-brand-600 text-gray-700 dark:text-gray-200 transition-all cursor-pointer disabled:opacity-50"
        >
          {{ isProvisioning && selectedPlan === 'enterprise' ? 'Provisioning...' : 'Provision Enterprise Node' }}
        </button>
      </div>
    </div>

    <!-- Custom VM Name & Settings Bar -->
    <div class="max-w-2xl mx-auto p-4 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 flex flex-col sm:flex-row items-center gap-3">
      <div class="flex-1 w-full">
        <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-300 mb-1">
          Custom Instance Hostname (Optional)
        </label>
        <input
          v-model="customVmName"
          type="text"
          :placeholder="`${slugCompany}-prod-01`"
          class="w-full h-9 px-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs font-mono text-gray-800 dark:text-white focus:border-brand-500 focus:outline-hidden"
        />
      </div>

      <div class="flex items-center gap-2 pt-2 sm:pt-4">
        <input
          type="checkbox"
          id="autoscaleConsent"
          v-model="consentAutoscale"
          class="w-4 h-4 text-brand-600 rounded border-gray-300 focus:ring-brand-500"
        />
        <label for="autoscaleConsent" class="text-xs text-gray-700 dark:text-gray-300 cursor-pointer select-none">
          Authorize dynamic rightsizing & off-hours scaling
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const emit = defineEmits<{ (e: 'provisioned'): void }>()

const { currentCustomer, formatAmount, provisionVm } = useFinOps()

const selectedPlan = ref<'starter' | 'business' | 'enterprise'>('business')
const isProvisioning = ref(false)
const customVmName = ref('')
const consentAutoscale = ref(true)

const slugCompany = computed(() => {
  const comp = currentCustomer.value?.company || currentCustomer.value?.customerName || 'cloud'
  return comp.toLowerCase().replace(/[^a-z0-9]/g, '') || 'app'
})

const selectAndProvision = async (plan: 'starter' | 'business' | 'enterprise') => {
  selectedPlan.value = plan
  isProvisioning.value = true
  try {
    const defaultName = `${slugCompany.value}-${plan}-01`
    const finalName = customVmName.value.trim() || defaultName
    await provisionVm(plan, finalName, 'East US / Central India')
    emit('provisioned')
  } finally {
    isProvisioning.value = false
  }
}
</script>
