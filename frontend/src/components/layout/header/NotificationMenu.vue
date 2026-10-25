<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="relative flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-dark-900 h-11 w-11 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
      @click="toggleDropdown"
      title="FinOps & Bottleneck Alerts"
    >
      <span
        v-if="notifications.length > 0"
        class="absolute right-0 top-0.5 z-1 h-2.5 w-2.5 rounded-full bg-error-500 flex"
      >
        <span
          class="absolute inline-flex w-full h-full bg-error-400 rounded-full opacity-75 -z-1 animate-ping"
        ></span>
      </span>
      <svg
        class="fill-current"
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M10.75 2.29248C10.75 1.87827 10.4143 1.54248 10 1.54248C9.58583 1.54248 9.25004 1.87827 9.25004 2.29248V2.83613C6.08266 3.20733 3.62504 5.9004 3.62504 9.16748V14.4591H3.33337C2.91916 14.4591 2.58337 14.7949 2.58337 15.2091C2.58337 15.6234 2.91916 15.9591 3.33337 15.9591H4.37504H15.625H16.6667C17.0809 15.9591 17.4167 15.6234 17.4167 15.2091C17.4167 14.7949 17.0809 14.4591 16.6667 14.4591H16.375V9.16748C16.375 5.9004 13.9174 3.20733 10.75 2.83613V2.29248ZM14.875 14.4591V9.16748C14.875 6.47509 12.6924 4.29248 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM8.00004 17.7085C8.00004 18.1228 8.33583 18.4585 8.75004 18.4585H11.25C11.6643 18.4585 12 18.1228 12 17.7085C12 17.2943 11.6643 16.9585 11.25 16.9585H8.75004C8.33583 16.9585 8.00004 17.2943 8.00004 17.7085Z"
          fill=""
        />
      </svg>
    </button>

    <!-- Dropdown Start -->
    <div
      v-if="dropdownOpen"
      class="absolute -right-[200px] sm:right-0 mt-3 flex h-[480px] w-[360px] flex-col rounded-2xl border border-gray-200 bg-white p-4 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark z-50"
    >
      <div
        class="flex items-center justify-between pb-3 mb-2 border-b border-gray-100 dark:border-gray-800"
      >
        <div>
          <h5 class="text-base font-bold text-gray-800 dark:text-white">FinOps & Scaling Alerts</h5>
          <span class="text-[11px] text-gray-500 dark:text-gray-400">
            {{ notifications.length }} active optimization recommendations
          </span>
        </div>

        <button @click="closeDropdown" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto space-y-3 pr-1">
        <div
          v-for="notif in notifications"
          :key="notif.id"
          @click="handleSelect(notif.id)"
          :class="[
            'p-3 rounded-xl border cursor-pointer transition-all hover:shadow-sm',
            notif.type === 'bottleneck'
              ? 'border-error-200 bg-error-50/50 dark:border-error-900/50 dark:bg-error-950/20'
              : 'border-brand-200 bg-brand-50/40 dark:border-brand-900/50 dark:bg-brand-950/20'
          ]"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              :class="[
                'text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full',
                notif.type === 'bottleneck'
                  ? 'bg-error-100 text-error-700 dark:bg-error-900/40 dark:text-error-300'
                  : 'bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
              ]"
            >
              {{ notif.type === 'bottleneck' ? 'Bottleneck Warning' : 'Off-Hours Downscale' }}
            </span>
            <span class="text-[10px] text-gray-400 font-mono">{{ notif.vmName }}</span>
          </div>

          <p class="text-xs font-semibold text-gray-800 dark:text-gray-100 mb-1 leading-snug">
            {{ notif.title }}
          </p>

          <p class="text-[11px] text-gray-600 dark:text-gray-300 mb-2 line-clamp-2">
            {{ notif.message }}
          </p>

          <div class="p-2 rounded bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 text-[10px] space-y-1">
            <div class="flex justify-between font-mono">
              <span class="text-gray-500">Current Spend:</span>
              <span class="font-bold text-gray-700 dark:text-gray-200">{{ formatAmount(notif.currentSpend) }}</span>
            </div>
            <div class="flex justify-between font-mono">
              <span class="text-gray-500">Projected Spend:</span>
              <span class="font-bold text-success-600 dark:text-success-400">{{ formatAmount(notif.projectedSpend) }}</span>
            </div>
            <div v-if="notif.formula" class="pt-1 text-[9px] text-gray-500 border-t border-gray-100 dark:border-gray-800 italic">
              Calc: {{ notif.formula }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const { notifications, formatAmount, selectVm } = useFinOps()

const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
  dropdownOpen.value = false
}

const handleSelect = (id: string) => {
  selectVm(id)
  closeDropdown()
}

const handleClickOutside = (event: Event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
