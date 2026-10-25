<template>
  <div
    v-if="selectedVmDetail"
    class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm"
  >
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-gray-100 dark:border-gray-800">
      <div>
        <div class="flex items-center gap-2.5">
          <span class="p-2 rounded-xl bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
              <line x1="6" y1="6" x2="6.01" y2="6"></line>
              <line x1="6" y1="18" x2="6.01" y2="18"></line>
            </svg>
          </span>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">
                {{ selectedVmDetail.name }}
              </h3>
              <span class="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                {{ selectedVmDetail.size }}
              </span>
              <span v-if="selectedVmDetail.isNew" class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-success-50 dark:bg-success-500/10 text-success-700 dark:text-success-400 border border-success-200 dark:border-success-500/20">
                <span class="w-1.5 h-1.5 rounded-full bg-success-500 animate-pulse"></span>
                Newly Provisioned (Live)
              </span>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              Resource ID: {{ selectedVmDetail.id }} • {{ selectedVmDetail.region }}
              <span v-if="isSuperAdmin || selectedVmDetail.customerName" class="ml-2 inline-flex items-center gap-1 font-semibold text-purple-600 dark:text-purple-400">
                • Owner: {{ selectedVmDetail.customerName || selectedVmDetail.ownerName || currentCustomer.customerName }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Quick VM Switcher Pills -->
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-xs text-gray-400 font-medium mr-1 hidden md:inline">Inspect:</span>
        <button
          v-for="vm in vms"
          :key="vm.id"
          @click="selectVm(vm.id)"
          :class="[
            'px-2.5 py-1 rounded-lg text-xs font-medium transition-all',
            selectedVmId === vm.id
              ? 'bg-brand-500 text-white shadow-xs font-semibold'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          ]"
        >
          {{ vm.name }}
        </button>
      </div>
    </div>

    <!-- Specifications Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3.5 my-5">
      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">vCPU Cores</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ selectedVmDetail.cores }} Cores</div>
        <span class="text-[10px] text-gray-500">AMD EPYC™ 7763</span>
      </div>

      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">System RAM</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ selectedVmDetail.ram }} GB</div>
        <span class="text-[10px] text-gray-500">DDR4 ECC High-Speed</span>
      </div>

      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Storage / Disk</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ selectedVmDetail.storage }} GB</div>
        <span class="text-[10px] text-gray-500">Premium SSD • {{ selectedVmDetail.maxIops }} IOPS</span>
      </div>

      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Bandwidth</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ selectedVmDetail.bandwidth }} Mbps</div>
        <span class="text-[10px] text-gray-500">Accelerated Networking</span>
      </div>

      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Hourly Rate</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ formatAmount(selectedVmDetail.hourlyRate) }}/hr</div>
        <span class="text-[10px] text-gray-500">{{ selectedVmDetail.isNew ? 'MTD Billed: ₹0 (Live)' : 'Azure PAYG Compute' }}</span>
      </div>

      <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Operating System</span>
        <div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5 truncate" :title="selectedVmDetail.os">
          {{ selectedVmDetail.os }}
        </div>
        <span class="text-[10px] text-gray-500 font-mono">{{ selectedVmDetail.ip }}</span>
      </div>
    </div>

    <!-- Live Telemetry Meters -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
      <div class="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="flex justify-between items-center mb-1.5">
          <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">Live CPU Utilization</span>
          <span class="text-xs font-bold font-mono text-gray-900 dark:text-white">{{ selectedVmDetail.cpuUsage }}%</span>
        </div>
        <div class="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
          <div
            :style="{ width: `${selectedVmDetail.cpuUsage}%` }"
            :class="[
              'h-full rounded-full transition-all duration-500',
              selectedVmDetail.cpuUsage > 80 ? 'bg-error-500' : 'bg-brand-500'
            ]"
          ></div>
        </div>
        <span class="text-[10px] text-gray-400 mt-1.5 block">Threshold: 85% peak limit</span>
      </div>

      <div class="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="flex justify-between items-center mb-1.5">
          <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">Live Memory (RAM)</span>
          <span class="text-xs font-bold font-mono text-gray-900 dark:text-white">{{ selectedVmDetail.ramUsage }}%</span>
        </div>
        <div class="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
          <div
            :style="{ width: `${selectedVmDetail.ramUsage}%` }"
            :class="[
              'h-full rounded-full transition-all duration-500',
              selectedVmDetail.ramUsage > 80 ? 'bg-error-500' : 'bg-brand-500'
            ]"
          ></div>
        </div>
        <span class="text-[10px] text-gray-400 mt-1.5 block">Allocated: {{ (selectedVmDetail.ram * selectedVmDetail.ramUsage / 100).toFixed(1) }} GB of {{ selectedVmDetail.ram }} GB</span>
      </div>

      <div class="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="flex justify-between items-center mb-1.5">
          <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">Disk IOPS</span>
          <span class="text-xs font-bold font-mono text-gray-900 dark:text-white">{{ selectedVmDetail.diskUsage }} IOPS</span>
        </div>
        <div class="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
          <div
            :style="{ width: `${Math.min(100, (selectedVmDetail.diskUsage / selectedVmDetail.maxIops) * 100)}%` }"
            class="h-full bg-brand-500 rounded-full transition-all duration-500"
          ></div>
        </div>
        <span class="text-[10px] text-gray-400 mt-1.5 block">Max Tier Provisioned: {{ selectedVmDetail.maxIops }} IOPS</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFinOps, isSuperAdmin } from '@/composables/useFinOps'

const { vms, selectedVmId, selectedVmDetail, selectVm, formatAmount, currentCustomer } = useFinOps()
</script>
