<template>
  <div
    class="overflow-hidden rounded-2xl border border-gray-200 bg-white px-4 pb-4 pt-5 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6 shadow-sm"
  >
    <div class="flex flex-col gap-3 mb-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-base font-bold text-gray-900 dark:text-white">
            {{ isSuperAdmin ? 'Super Admin Multi-Tenant Fleet' : 'Customer Azure VM Fleet' }}
          </h3>
          <span
            v-if="isSuperAdmin"
            class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-mono bg-purple-100 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 font-bold border border-purple-200 dark:border-purple-800/40"
          >
            Super Admin Mode
          </span>
          <span class="text-xs px-2 py-0.5 rounded font-mono bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
            {{ vms.length }} Managed Instances
          </span>
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          <span v-if="isSuperAdmin">
            Full cross-tenant visibility across all registered customers and assigned VMs.
          </span>
          <span v-else>
            Tenant: <strong class="text-gray-700 dark:text-gray-300 font-mono">{{ currentCustomer.subscriptionId }}</strong> ({{ currentCustomer.customerName }})
          </span>
        </p>
      </div>

      <!-- Fleet Filters & Action Buttons -->
      <div class="flex flex-wrap items-center gap-2">
        <div class="inline-flex items-center gap-0.5 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <button
            v-for="filter in ['all', 'bottlenecks', 'downsize', 'healthy']"
            :key="filter"
            @click="activeFilter = filter"
            :class="[
              activeFilter === filter
                ? 'shadow-xs text-brand-600 dark:text-white bg-white dark:bg-gray-800 font-semibold'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-800',
              'px-2.5 py-1 text-xs rounded-md uppercase tracking-wider capitalize transition-all',
            ]"
          >
            {{ filter }}
          </button>
        </div>

        <!-- Super Admin: Database Monitoring Table Modal -->
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
          Supabase Monitoring Table
        </button>

        <button
          @click="toggleBatchAutoScale"
          class="inline-flex items-center gap-1.5 rounded-lg border border-brand-500/30 bg-brand-50 px-3 py-1.5 text-xs font-semibold text-brand-600 hover:bg-brand-100 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-400 dark:hover:bg-brand-500/20 transition-all cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          Batch Enable All
        </button>

        <button
          @click="showDeployModal = true"
          class="inline-flex items-center gap-1.5 rounded-lg bg-brand-500 hover:bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition-all cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Buy / Deploy VM
        </button>
      </div>
    </div>

    <div class="max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
        <thead>
          <tr class="text-left text-[11px] font-semibold uppercase tracking-wider text-gray-400">
            <th class="py-3 px-3">Virtual Machine</th>
            <th v-if="isSuperAdmin" class="py-3 px-3">Customer / Owner</th>
            <th class="py-3 px-3">Hardware Specs</th>
            <th class="py-3 px-3">Live Telemetry</th>
            <th class="py-3 px-3">Status & Signal</th>
            <th class="py-3 px-3">Current Spend</th>
            <th class="py-3 px-3">Projected Spend</th>
            <th class="py-3 px-3 text-center">Auto-Scaling</th>
            <th class="py-3 px-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-800 text-xs">
          <tr
            v-for="vm in filteredVms"
            :key="vm.id"
            :class="[
              'transition-colors hover:bg-gray-50/80 dark:hover:bg-white/[0.02]',
              selectedVmId === vm.id ? 'bg-brand-50/40 dark:bg-brand-500/[0.06]' : ''
            ]"
          >
            <!-- Name & Size -->
            <td class="py-3 px-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center font-bold text-gray-700 dark:text-gray-300">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                    <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                  </svg>
                </div>
                <div>
                  <div class="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                    {{ vm.name }}
                    <span v-if="selectedVmId === vm.id" class="text-[9px] px-1 py-0.2 rounded bg-brand-500 text-white font-normal">Active</span>
                  </div>
                  <span class="text-[11px] font-mono text-gray-500 dark:text-gray-400">{{ vm.size }} • <span class="text-[10px] text-gray-400">{{ vm.id }}</span></span>
                </div>
              </div>
            </td>

            <!-- Customer / Owner Column (Prominently displayed for Super Admin) -->
            <td v-if="isSuperAdmin" class="py-3 px-3">
              <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                <span class="font-semibold text-gray-900 dark:text-white">
                  {{ vm.customerName || vm.ownerName || 'Enterprise Tenant' }}
                </span>
              </div>
              <span class="text-[11px] font-mono text-gray-400 block mt-0.5">
                {{ vm.customerId || vm.userId || 'cust-portal' }}
              </span>
            </td>

            <!-- Specs -->
            <td class="py-3 px-3 text-gray-600 dark:text-gray-300">
              <div class="font-medium text-gray-900 dark:text-white">{{ vm.cores }} vCPUs • {{ vm.ram }} GB RAM</div>
              <div class="text-[11px] text-gray-400">{{ vm.storage }} GB SSD • {{ vm.maxIops }} IOPS</div>
            </td>

            <!-- Live Usages -->
            <td class="py-3 px-3">
              <div class="flex items-center gap-2">
                <span :class="vm.cpuUsage > 80 ? 'text-error-600 font-bold' : 'text-gray-700 dark:text-gray-300'">
                  CPU: {{ vm.cpuUsage }}%
                </span>
                <span class="text-gray-400">•</span>
                <span class="text-gray-600 dark:text-gray-400">RAM: {{ vm.ramUsage }}%</span>
              </div>
              <div class="w-24 bg-gray-100 dark:bg-gray-800 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  :style="{ width: `${vm.cpuUsage}%` }"
                  :class="[
                    'h-full rounded-full',
                    vm.cpuUsage > 80 ? 'bg-error-500' : 'bg-brand-500'
                  ]"
                ></div>
              </div>
            </td>

            <!-- Status Signal -->
            <td class="py-3 px-3">
              <span
                v-if="vm.isNew"
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-success-50 text-success-700 dark:bg-success-950/40 dark:text-success-300 border border-success-200/60 dark:border-success-800/40"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-success-500 animate-pulse"></span>
                Newly Provisioned (Live)
              </span>
              <span
                v-else
                :class="[
                  'inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold',
                  vm.status === 'Bottleneck Warning'
                    ? 'bg-error-50 text-error-700 dark:bg-error-950/40 dark:text-error-300'
                    : vm.recommendation?.type === 'downsize'
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-300'
                    : 'bg-success-50 text-success-700 dark:bg-success-950/40 dark:text-success-300'
                ]"
              >
                {{ vm.status }}
              </span>
            </td>

            <!-- Current Spend -->
            <td class="py-3 px-3 font-mono font-medium text-gray-900 dark:text-white">
              {{ formatAmount(vm.currentSpend) }}
            </td>

            <!-- Projected Spend -->
            <td class="py-3 px-3 font-mono font-bold text-success-600 dark:text-success-400">
              {{ formatAmount(vm.projectedSpend) }}
            </td>

            <!-- Auto-Scale Permission Switch -->
            <td class="py-3 px-3 text-center">
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  :checked="vm.autoScaleEnabled"
                  @change="toggleAutoScale(vm.id, !vm.autoScaleEnabled)"
                  class="sr-only peer"
                />
                <div
                  class="w-9 h-5 bg-gray-200 peer-focus:outline-hidden rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-brand-500"
                ></div>
              </label>
            </td>

            <!-- Action -->
            <td class="py-3 px-3 text-right">
              <button
                @click="selectVm(vm.id)"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                  selectedVmId === vm.id
                    ? 'bg-brand-500 text-white shadow-xs'
                    : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                ]"
              >
                {{ selectedVmId === vm.id ? 'Inspecting' : 'Inspect Specs' }}
              </button>
            </td>
          </tr>

          <!-- Empty State when Filter Matches 0 Instances -->
          <tr v-if="filteredVms.length === 0">
            <td :colspan="isSuperAdmin ? 9 : 8" class="py-10 text-center text-xs text-gray-500 dark:text-gray-400">
              <div class="flex flex-col items-center justify-center gap-2">
                <div class="w-10 h-10 rounded-full bg-success-50 dark:bg-success-950/30 flex items-center justify-center text-success-600 dark:text-success-400">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="font-bold text-gray-800 dark:text-gray-200 text-sm">
                  {{
                    activeFilter === 'bottlenecks'
                      ? 'No Bottlenecked Instances Detected'
                      : activeFilter === 'downsize'
                      ? 'No Downsize Recommendations Needed'
                      : 'No Matching Instances in this View'
                  }}
                </span>
                <span class="text-xs text-gray-500 max-w-sm">
                  {{
                    activeFilter === 'bottlenecks'
                      ? 'All virtual machines are currently operating with healthy resource headroom.'
                      : activeFilter === 'downsize'
                      ? 'Your compute resources are properly allocated for current workload demands.'
                      : 'Switch back to "All" to inspect your entire fleet.'
                  }}
                </span>
                <button
                  @click="activeFilter = 'all'"
                  class="mt-1 px-3 py-1 rounded-lg text-xs font-semibold bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors cursor-pointer"
                >
                  View All {{ vms.length }} VMs
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
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-6xl w-full p-6 shadow-2xl overflow-y-auto max-h-[92vh] relative"
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

        <div class="mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-gray-100 dark:border-gray-800">
          <div>
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-lg bg-purple-100 dark:bg-purple-950/50 text-purple-600 dark:text-purple-300 font-bold">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z"></path>
                  <path d="M9 12h6"></path>
                  <path d="M9 16h6"></path>
                </svg>
              </span>
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">
                  Supabase User & VM Monitoring Table
                </h3>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  Direct database view: <code>public.user_accounts</code> • User ID, Email, Password & Assigned VMs
                </p>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="refreshMonitoring"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors cursor-pointer"
            >
              Refresh Table
            </button>
            <a
              href="/supabase_schema.sql"
              target="_blank"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-600 hover:bg-purple-700 text-white transition-colors"
            >
              View SQL Schema
            </a>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-xs">
            <thead>
              <tr class="text-left font-semibold text-gray-400 uppercase tracking-wider text-[11px] bg-gray-50/50 dark:bg-gray-800/20">
                <th class="py-3 px-3">User ID</th>
                <th class="py-3 px-3">Email ID</th>
                <th class="py-3 px-3">Password</th>
                <th class="py-3 px-3">Customer / Organization</th>
                <th class="py-3 px-3">Role</th>
                <th class="py-3 px-3">Assigned VMs</th>
                <th class="py-3 px-3 text-right">Created</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800 font-mono">
              <tr v-for="u in monitoringUsers" :key="u.user_id" class="hover:bg-gray-50/50 dark:hover:bg-white/[0.02]">
                <td class="py-3 px-3 text-purple-600 dark:text-purple-400 font-medium">
                  {{ u.user_id }}
                </td>
                <td class="py-3 px-3 text-gray-800 dark:text-gray-200 font-sans font-medium">
                  {{ u.email_id || u.email }}
                </td>
                <td class="py-3 px-3 text-amber-600 dark:text-amber-400">
                  {{ u.password || '••••••••' }}
                </td>
                <td class="py-3 px-3 text-gray-700 dark:text-gray-300 font-sans">
                  {{ u.customer_name || u.company || 'Enterprise' }}
                </td>
                <td class="py-3 px-3 font-sans">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                      u.role === 'super_admin'
                        ? 'bg-purple-100 text-purple-700 dark:bg-purple-950/50 dark:text-purple-300'
                        : 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300'
                    ]"
                  >
                    {{ u.role || 'customer' }}
                  </span>
                </td>
                <td class="py-3 px-3 font-sans">
                  <div v-if="Array.isArray(u.assigned_vms) && u.assigned_vms.length > 0" class="flex flex-wrap gap-1">
                    <span
                      v-for="(vmItem, idx) in u.assigned_vms"
                      :key="idx"
                      class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-[10px] font-mono text-gray-700 dark:text-gray-300"
                    >
                      {{ typeof vmItem === 'object' ? (vmItem.name || vmItem.id) : vmItem }}
                    </span>
                  </div>
                  <span v-else class="text-gray-400 italic text-[11px]">0 VMs allocated</span>
                </td>
                <td class="py-3 px-3 text-right text-gray-400 text-[11px]">
                  {{ u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Active' }}
                </td>
              </tr>
              <tr v-if="monitoringUsers.length === 0">
                <td colspan="7" class="py-8 text-center text-gray-400 italic">
                  No accounts synced yet. Sign in or register to record users into Supabase.
                </td>
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
  currentCustomer,
  selectVm,
  toggleAutoScale,
  formatAmount,
  showToast,
  loadFleet,
} = useFinOps()

const activeFilter = ref('all')

const filteredVms = computed(() => {
  if (activeFilter.value === 'bottlenecks') {
    return vms.value.filter(
      (v) => (v.status === 'Bottleneck Warning' || v.cpuUsage >= 80 || v.ramUsage >= 85) && !v.isNew
    )
  }
  if (activeFilter.value === 'downsize') {
    return vms.value.filter(
      (v) => !v.isNew && v.recommendation?.type === 'downsize' && v.status !== 'Bottleneck Warning' && v.cpuUsage < 80
    )
  }
  if (activeFilter.value === 'healthy') {
    return vms.value.filter(
      (v) => v.status !== 'Bottleneck Warning' && v.cpuUsage < 80 && v.ramUsage < 85
    )
  }
  return vms.value
})

const openMonitoringModal = async () => {
  showMonitoringModal.value = true
  await refreshMonitoring()
}

const refreshMonitoring = async () => {
  monitoringUsers.value = await loadUserMonitoringData()
}

const toggleBatchAutoScale = async () => {
  try {
    const allEnabled = vms.value.every((v) => v.autoScaleEnabled)
    const targetStatus = !allEnabled
    await fetch(`${API_BASE}/api/fleet/autoscale-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customerId: currentCustomer.value.customerId,
        enabled: targetStatus,
      }),
    })
    await loadFleet(currentCustomer.value.customerId)
    showToast(`Batch updated all ${vms.value.length} VMs to auto-scaling: ${targetStatus ? 'Enabled' : 'Disabled'}`)
  } catch (err) {
    console.warn('Batch update fallback', err)
  }
}
</script>