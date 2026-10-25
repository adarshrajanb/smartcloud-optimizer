<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="flex items-center text-gray-700 dark:text-gray-400 group"
      @click.prevent="toggleDropdown"
    >
      <span class="mr-2.5 overflow-hidden rounded-full h-10 w-10 bg-brand-500/10 border border-brand-500/20 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold text-sm">
        {{ currentCustomer.name.slice(0, 2).toUpperCase() }}
      </span>

      <div class="text-left hidden sm:block mr-2">
        <span class="block font-semibold text-gray-800 dark:text-white text-theme-sm leading-tight">
          {{ currentCustomer.name }}
        </span>
        <span class="block text-[11px] text-gray-500 dark:text-gray-400 font-normal">
          {{ currentCustomer.customerName }}
        </span>
      </div>

      <ChevronDownIcon :class="{ 'rotate-180': dropdownOpen }" class="w-4 h-4 transition-transform text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-200" />
    </button>

    <!-- Dropdown Start -->
    <div
      v-if="dropdownOpen"
      class="absolute right-0 mt-3 flex w-[280px] flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark z-50"
    >
      <div class="pb-3 border-b border-gray-100 dark:border-gray-800">
        <span class="block font-bold text-gray-800 text-sm dark:text-white">
          {{ currentCustomer.name }}
        </span>
        <span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          {{ currentCustomer.email }}
        </span>
        <div class="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-brand-50 dark:bg-brand-500/10 text-[10px] font-mono text-brand-700 dark:text-brand-300">
          Tenant: {{ currentCustomer.subscriptionId }}
        </div>
      </div>

      <!-- Switch Customer Section (Super Admin Only) -->
      <div v-if="isSuperAdmin" class="py-2 border-b border-gray-100 dark:border-gray-800">
        <div class="flex items-center justify-between mb-1.5 px-2">
          <span class="block text-[10px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
            Super Admin: Switch Tenant
          </span>
          <span class="text-[9px] px-1.5 py-0.2 rounded font-semibold bg-brand-100 text-brand-700">Root</span>
        </div>
        <button
          v-for="(prof, key) in CUSTOMER_PROFILES"
          :key="key"
          @click="handleSwitchCustomer(key)"
          :class="[
            'w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center justify-between transition-colors',
            currentCustomer.customerId === key
              ? 'bg-brand-500 text-white font-semibold'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5'
          ]"
        >
          <span>{{ prof.customerName }}</span>
          <span :class="currentCustomer.customerId === key ? 'text-white' : 'text-gray-400'" class="text-[10px]">
            {{ prof.vmCount }} VMs
          </span>
        </button>
      </div>

      <div class="pt-2">
        <button
          @click="handleSignOut"
          class="flex items-center w-full gap-2 px-2.5 py-2 text-xs font-medium text-error-600 rounded-lg hover:bg-error-50 dark:hover:bg-error-500/10 transition-colors"
        >
          <LogoutIcon class="w-4 h-4" />
          Sign out of Console
        </button>
      </div>
    </div>
    <!-- Dropdown End -->
  </div>
</template>

<script setup lang="ts">
import { ChevronDownIcon, LogoutIcon } from '@/icons'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFinOps, CUSTOMER_PROFILES } from '@/composables/useFinOps'

const router = useRouter()
const { currentCustomer, switchCustomer, logout, isSuperAdmin } = useFinOps()

const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
  dropdownOpen.value = false
}

const handleSwitchCustomer = async (key: string) => {
  await switchCustomer(key)
  closeDropdown()
}

const handleSignOut = () => {
  logout()
  closeDropdown()
  router.push('/signin')
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
