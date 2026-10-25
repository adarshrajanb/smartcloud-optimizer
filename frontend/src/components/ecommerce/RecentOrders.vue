<template>
  <div
    class="overflow-hidden rounded-2xl border border-gray-200 bg-white px-4 pb-4 pt-5 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6 shadow-sm"
  >
    <!-- Header & Fleet Context -->
    <div class="flex flex-col gap-3 mb-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-base font-bold text-gray-900 dark:text-white">
            {{ isSuperAdmin ? 'Super Admin Multi-Tenant Fleet' : 'Enterprise Cloud Infrastructure Fleet' }}
          </h3>
          <span
            v-if="isSuperAdmin"
            class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-mono bg-purple-100 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 font-bold border border-purple-200 dark:border-purple-800/40"
          >
            Super Admin
          </span>
          <span class="text-xs px-2.5 py-0.5 rounded-full font-mono font-bold bg-brand-50 text-brand-700 dark:bg-brand-950/50 dark:text-brand-300 border border-brand-200/60 dark:border-brand-800/40">
            {{ filteredFleet.length }} of {{ vms.length }} Resources Active
          </span>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Tenant: <strong class="text-gray-700 dark:text-gray-300 font-mono">{{ currentCustomer.subscriptionId }}</strong> ({{ currentCustomer.customerName }} • {{ currentCustomer.primaryRegion }})
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-if="isSuperAdmin"
          @click="openMonitoringModal"
          class="inline-flex items-center gap-1.5 rounded-lg border border-purple-500/30 bg-purple-50 px-3 py-1.5 text-xs font-semibold text-purple-700 hover:bg-purple-100 dark:border-purple-500/20 dark:bg-purple-950/40 dark:text-purple-300 dark:hover:bg-purple-900/40 transition-all cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          Supabase DB
        </button>

        <button
          @click="toggleBatchAutoScale"
          class="inline-flex items-center gap-1.5 rounded-lg border border-brand-500/30 bg-brand-50 px-3 py-1.5 text-xs font-semibold text-brand-600 hover:bg-brand-100 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-400 dark:hover:bg-brand-500/20 transition-all cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          Batch Accept All
        </button>

        <button
          @click="showDeployModal = true"
          class="inline-flex items-center gap-1.5 rounded-lg bg-brand-500 hover:bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition-all cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Deploy VM
        </button>
      </div>
    </div>

    <!-- Multi-Dimensional FinOps Filter Toolbar (UTHO Deliverables) -->
    <div class="mb-5 p-3.5 rounded-xl bg-gray-50/80 dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800 space-y-3">
      <!-- Row 1: Region & Environment Filters -->
      <div class="flex flex-wrap items-center justify-between gap-3 text-xs">
        <!-- Region Filter Pills -->
        <div class="flex items-center gap-1.5">
          <span class="text-gray-400 font-semibold text-[11px] uppercase tracking-wider mr-1">Region:</span>
          <button
            v-for="r in ['all', 'Noida', 'Bangalore', 'Mumbai']"
            :key="r"
            @click="selectedRegion = r"
            :class="[
              selectedRegion === r
                ? 'bg-brand-500 text-white font-bold shadow-xs'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-100 border border-gray-200 dark:border-gray-700',
              'px-2.5 py-1 rounded-lg text-xs transition-all cursor-pointer'
            ]"
          >
            {{ r === 'all' ? 'All Regions' : r }}
          </button>
        </div>

        <!-- Environment Filter Pills -->
        <div class="flex items-center gap-1.5">
          <span class="text-gray-400 font-semibold text-[11px] uppercase tracking-wider mr-1">Env:</span>
          <button
            v-for="env in ['all', 'prod', 'staging', 'dev']"
            :key="env"
            @click="selectedEnvironment = env"
            :class="[
              selectedEnvironment === env
                ? 'bg-gray-900 text-white dark:bg-white dark:text-gray-900 font-bold shadow-xs'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-100 border border-gray-200 dark:border-gray-700',
              'px-2.5 py-1 rounded-lg text-xs uppercase transition-all cursor-pointer'
            ]"
          >
            {{ env === 'all' ? 'All Envs' : env }}
          </button>
        </div>
      </div>

      <!-- Row 2: Resource Type & Status / Anomaly Filters -->
      <div class="flex flex-wrap items-center justify-between gap-3 text-xs pt-2 border-t border-gray-200/60 dark:border-gray-800">
        <!-- Resource Type Filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-gray-400 font-semibold text-[11px] uppercase tracking-wider mr-1">Type:</span>
          <button
            v-for="t in ['all', 'VM', 'Volume', 'IP']"
            :key="t"
            @click="selectedResourceType = t"
            :class="[
              selectedResourceType === t
                ? 'bg-purple-600 text-white font-bold shadow-xs'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-100 border border-gray-200 dark:border-gray-700',
              'px-2.5 py-1 rounded-lg text-xs transition-all cursor-pointer'
            ]"
          >
            {{ t === 'all' ? 'All Resources' : t === 'VM' ? 'VMs (Compute)' : t === 'Volume' ? 'Block Storage' : 'Public IPs' }}
          </button>
        </div>

        <!-- Status Signal Quick Filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-gray-400 font-semibold text-[11px] uppercase tracking-wider mr-1">Signal:</span>
          <button
            v-for="f in ['all', 'bottlenecks', 'downsize', 'orphaned', 'anomalies']"
            :key="f"
            @click="activeStatusFilter = f"
            :class="[
              activeStatusFilter === f
                ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300 font-bold border border-brand-300 dark:border-brand-700'
                : 'text-gray-500 hover:text-gray-800 dark:text-gray-400',
              'px-2 py-0.5 rounded text-xs uppercase tracking-wider capitalize transition-all cursor-pointer'
            ]"
          >
            {{ f }}
          </button>
        </div>
      </div>
    </div>

    <!-- Fleet Inventory Table -->
    <div class="max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
        <thead>
          <tr class="text-left text-[11px] font-semibold uppercase tracking-wider text-gray-400">
            <th class="py-3 px-3">Resource & Spec</th>
            <th class="py-3 px-3">Region & Env</th>
            <th class="py-3 px-3">Team / Service</th>
            <th class="py-3 px-3">Telemetry & Peak (p95)</th>
            <th class="py-3 px-3">Status & Signal</th>
            <th class="py-3 px-3">Baseline Spend</th>
            <th class="py-3 px-3">Projected Spend</th>
            <th class="py-3 px-3 text-center">Decision Action</th>
            <th class="py-3 px-3 text-right">Inspect</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-800 text-xs">
          <tr
            v-for="vm in filteredFleet"
            :key="vm.id"
            :class="[
              'transition-colors hover:bg-gray-50/80 dark:hover:bg-white/[0.02]',
              selectedVmId === vm.id ? 'bg-brand-50/40 dark:bg-brand-500/[0.06]' : ''
            ]"
          >
            <!-- Name, ID & Type Icon -->
            <td class="py-3 px-3">
              <div class="flex items-center gap-2.5">
                <div
                  :class="[
                    'w-8 h-8 rounded-lg flex items-center justify-center font-bold',
                    vm.type === 'Volume'
                      ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
                      : vm.type === 'IP'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                  ]"
                >
                  <!-- Volume Icon -->
                  <svg v-if="vm.type === 'Volume'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                  </svg>
                  <!-- IP Icon -->
                  <svg v-else-if="vm.type === 'IP'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                  </svg>
                  <!-- VM Compute Icon -->
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                    <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                  </svg>
                </div>
                <div>
                  <div class="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                    {{ vm.name }}
                    <span v-if="selectedVmId === vm.id" class="text-[9px] px-1 py-0.2 rounded bg-brand-500 text-white font-normal">Active</span>
                  </div>
                  <span class="text-[11px] font-mono text-gray-500 dark:text-gray-400">
                    {{ vm.size }} • <span class="text-[10px] text-gray-400">{{ vm.id }}</span>
                  </span>
                </div>
              </div>
            </td>

            <!-- Region & Env -->
            <td class="py-3 px-3">
              <div class="font-medium text-gray-900 dark:text-white flex items-center gap-1.5">
                {{ vm.region }}
              </div>
              <span
                :class="[
                  'text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded font-mono mt-0.5 inline-block',
                  vm.environment === 'prod'
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    : vm.environment === 'staging'
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300'
                ]"
              >
                {{ vm.environment }}
              </span>
            </td>

            <!-- Team / Owner -->
            <td class="py-3 px-3 text-gray-700 dark:text-gray-300 font-medium">
              <div>{{ vm.team || 'Platform & DevOps' }}</div>
              <span class="text-[10px] text-gray-400 font-mono">{{ vm.privateIp || 'VNet Internal' }}</span>
            </td>

            <!-- Live Telemetry & Peak Safety -->
            <td class="py-3 px-3">
              <div class="flex items-center gap-2">
                <span :class="vm.cpuUsage > 80 ? 'text-error-600 font-bold' : 'text-gray-700 dark:text-gray-300'">
                  CPU: {{ vm.cpuUsage }}%
                </span>
                <span class="text-gray-300 dark:text-gray-600">•</span>
                <span :class="vm.p95Cpu > 75 ? 'text-purple-600 font-bold' : 'text-gray-500 dark:text-gray-400'">
                  p95: {{ vm.p95Cpu ?? ((vm.cpuUsage || 20) * 1.35).toFixed(1) }}%
                </span>
              </div>
              <div class="text-[10px] text-gray-400 font-mono mt-0.5">
                Net: {{ vm.networkIn || 0 }} in / {{ vm.networkOut || 0 }} out MB/s
              </div>
            </td>

            <!-- Status & Pattern Signal -->
            <td class="py-3 px-3">
              <span
                :class="[
                  'inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold',
                  vm.status === 'Runaway Anomaly'
                    ? 'bg-error-100 text-error-800 dark:bg-error-950/50 dark:text-error-300 animate-pulse'
                    : vm.status?.includes('Orphaned')
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300'
                    : vm.status === 'Bottleneck Warning'
                    ? 'bg-error-50 text-error-700 dark:bg-error-950/40 dark:text-error-300'
                    : vm.recommendation?.type === 'downsize'
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-300'
                    : 'bg-success-50 text-success-700 dark:bg-success-950/40 dark:text-success-300'
                ]"
              >
                {{ vm.status }}
              </span>
            </td>

            <!-- Baseline Spend -->
            <td class="py-3 px-3 font-mono font-medium text-gray-900 dark:text-white">
              {{ formatAmount(vm.currentSpend) }}
            </td>

            <!-- Projected Spend -->
            <td class="py-3 px-3 font-mono font-bold text-success-600 dark:text-success-400">
              {{ formatAmount(vm.projectedSpend) }}
            </td>

            <!-- Individual Accept / Reject Toggle Button -->
            <td class="py-3 px-3 text-center">
              <button
                v-if="vm.savings > 0 || vm.recommendation"
                @click="toggleRecommendation(vm.id, !vm.recommendation?.accepted)"
                :class="[
                  'px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer shadow-2xs',
                  vm.recommendation?.accepted
                    ? 'bg-success-600 hover:bg-success-700 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                ]"
              >
                {{ vm.recommendation?.accepted ? '✓ Accepted' : '+ Accept' }}
              </button>
              <span v-else class="text-gray-400 font-mono text-[11px]">Optimal</span>
            </td>

            <!-- Action -->
            <td class="py-3 px-3 text-right">
              <button
                @click="selectVm(vm.id)"
                :class="[
                  'px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                  selectedVmId === vm.id
                    ? 'bg-brand-500 text-white shadow-xs'
                    : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                ]"
              >
                {{ selectedVmId === vm.id ? 'Inspecting' : 'Inspect' }}
              </button>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="filteredFleet.length === 0">
            <td colspan="9" class="py-12 text-center text-xs text-gray-500 dark:text-gray-400">
              <div class="flex flex-col items-center justify-center gap-2">
                <span class="font-bold text-gray-800 dark:text-gray-200 text-sm">
                  No resources match the selected filters
                </span>
                <button
                  @click="resetFilters"
                  class="mt-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-brand-500 text-white hover:bg-brand-600 transition-colors cursor-pointer"
                >
                  Reset All Filters
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Buy / Deploy VM Modal -->
    <div
      v-if="showDeployModal"
      class="fixed inset-0 z-99999 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
    >
      <div
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-5xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh] relative"
      >
        <button
          @click="showDeployModal = false"
          class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 cursor-pointer"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        <VmProvisioningPlans @provisioned="showDeployModal = false" />
      </div>
    </div>

    <!-- Super Admin: Supabase Database Monitoring Modal -->
    <div
      v-if="showMonitoringModal"
      class="fixed inset-0 z-99999 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
    >
      <div
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-5xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh] relative"
      >
        <button
          @click="showMonitoringModal = false"
          class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 cursor-pointer"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <h3 class="text-base font-bold text-gray-900 dark:text-white mb-2">
          Supabase Database Monitoring Table
        </h3>
        <p class="text-xs text-gray-500 mb-4">
          Direct query of public.user_accounts and public.vms in the cloud database.
        </p>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-xs">
            <thead>
              <tr class="text-left font-mono text-gray-400">
                <th class="py-2">Email</th>
                <th class="py-2">Customer Name</th>
                <th class="py-2">Role</th>
                <th class="py-2">Allocated VMs</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800 font-mono">
              <tr v-for="u in monitoringUsers" :key="u.user_id">
                <td class="py-2.5 font-bold">{{ u.email_id }}</td>
                <td class="py-2.5">{{ u.customer_name }}</td>
                <td class="py-2.5">{{ u.role }}</td>
                <td class="py-2.5">{{ u.assigned_vms?.length || 0 }} resources</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import VmProvisioningPlans from './VmProvisioningPlans.vue'
import { useFinOps, isSuperAdmin, API_BASE } from '@/composables/useFinOps'
import { loadUserMonitoringData } from '@/lib/supabase'

const showDeployModal = ref(false)
const showMonitoringModal = ref(false)
const monitoringUsers = ref<any[]>([])

const {
  vms,
  selectedVmId,
  selectedRegion,
  selectedEnvironment,
  selectedResourceType,
  currentCustomer,
  selectVm,
  toggleRecommendation,
  formatAmount,
  showToast,
  loadFleet,
} = useFinOps()

const activeStatusFilter = ref('all')

const filteredFleet = computed(() => {
  return vms.value.filter((vm) => {
    // 1. Region filter
    if (selectedRegion.value !== 'all' && !vm.region?.toLowerCase().includes(selectedRegion.value.toLowerCase())) {
      return false
    }
    // 2. Environment filter
    if (selectedEnvironment.value !== 'all' && vm.environment?.toLowerCase() !== selectedEnvironment.value.toLowerCase()) {
      return false
    }
    // 3. Resource Type filter
    if (selectedResourceType.value !== 'all' && (vm.type || 'VM').toLowerCase() !== selectedResourceType.value.toLowerCase()) {
      return false
    }
    // 4. Status signal filter
    if (activeStatusFilter.value === 'bottlenecks') {
      return (vm.status === 'Bottleneck Warning' || vm.cpuUsage >= 80 || vm.ramUsage >= 85) && !vm.isNew
    }
    if (activeStatusFilter.value === 'downsize') {
      return vm.recommendation?.type in { downsize: 1, schedule_offhours: 1 } || vm.savings > 0
    }
    if (activeStatusFilter.value === 'orphaned') {
      return vm.status?.includes('Orphaned') || vm.type === 'Volume' || vm.type === 'IP'
    }
    if (activeStatusFilter.value === 'anomalies') {
      return vm.status === 'Runaway Anomaly' || vm.cpuUsage > 95
    }
    return true
  })
})

const resetFilters = () => {
  selectedRegion.value = 'all'
  selectedEnvironment.value = 'all'
  selectedResourceType.value = 'all'
  activeStatusFilter.value = 'all'
}

const openMonitoringModal = async () => {
  showMonitoringModal.value = true
  monitoringUsers.value = await loadUserMonitoringData()
}

const toggleBatchAutoScale = async () => {
  try {
    const allAccepted = vms.value.every((v) => v.recommendation?.accepted)
    const target = !allAccepted
    await fetch(`${API_BASE}/api/fleet/autoscale-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customerId: currentCustomer.value.customerId,
        enabled: target,
      }),
    })
    for (const v of vms.value) {
      if (v.recommendation) {
        v.recommendation.accepted = target
        v.autoScaleEnabled = target
        v.projectedSpend = target ? Math.max(0, v.currentSpend - (v.savings || 0)) : v.currentSpend
      }
    }
    showToast(`Batch updated all ${vms.value.length} resources: ${target ? 'All Accepted' : 'All Reverted'}`)
  } catch (err) {
    console.warn('Batch update fallback', err)
  }
}
</script>
