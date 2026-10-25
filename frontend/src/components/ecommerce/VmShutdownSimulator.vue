<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6 shadow-sm space-y-6"
  >
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-gray-100 dark:border-gray-800">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path>
            <line x1="12" y1="2" x2="12" y2="12"></line>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-gray-900 dark:text-white">
              Cloud VM Shutdown & Cost Savings Simulator
            </h3>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300">
              Interactive FinOps
            </span>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Select any VM in your fleet and configure turn-off hours to model projected monthly and annual savings.
          </p>
        </div>
      </div>

      <!-- Quick Savings Badge -->
      <div class="flex items-center gap-2 shrink-0">
        <span class="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
          Save {{ formatAmount(calculatedMonthlySavings) }}/mo ({{ savingsPercent.toFixed(1) }}%)
        </span>
      </div>
    </div>

    <!-- Step 1: Choose VM & Optimization Strategy -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- VM Selector Card -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
          1. Choose Target VM for Simulation:
        </label>

        <!-- Dropdown & Quick Selector Pills -->
        <div class="space-y-2">
          <select
            v-model="targetVmId"
            @change="handleVmChange"
            class="w-full h-11 px-3.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-medium text-gray-900 dark:text-white focus:border-brand-500 focus:outline-hidden"
          >
            <option value="all">🌐 All Fleet VMs (Consolidated Savings Across Fleet)</option>
            <option v-for="vm in vms" :key="vm.id" :value="vm.id">
              {{ vm.name }} ({{ vm.size }} • {{ formatAmount(vm.hourlyRate) }}/hr) {{ vm.id.startsWith('docker-') ? '[Docker]' : '' }}
            </option>
          </select>

          <!-- Quick Selector Pills -->
          <div class="flex flex-wrap items-center gap-1.5 pt-1">
            <button
              @click="targetVmId = 'all'"
              :class="[
                'px-2.5 py-1 rounded-lg text-xs font-semibold transition-all',
                targetVmId === 'all'
                  ? 'bg-purple-600 text-white shadow-xs'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
              ]"
            >
              All VMs ({{ vms.length }})
            </button>
            <button
              v-for="vm in vms"
              :key="vm.id"
              @click="targetVmId = vm.id"
              :class="[
                'px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1',
                targetVmId === vm.id
                  ? 'bg-brand-500 text-white font-semibold shadow-xs'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
              ]"
            >
              <span v-if="vm.id.startsWith('docker-')" class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              {{ vm.name }}
            </button>
          </div>
        </div>

        <!-- Target VM Spec Snapshot -->
        <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 text-xs space-y-2">
          <div class="flex items-center justify-between font-bold text-gray-900 dark:text-white">
            <div class="flex items-center gap-1.5">
              <span>{{ targetVmInfo.name }}</span>
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                {{ targetVmInfo.size }}
              </span>
            </div>
            <span class="text-brand-600 dark:text-brand-400 font-mono font-bold">
              {{ formatAmount(targetVmInfo.hourlyRate) }}/hr
            </span>
          </div>

          <div class="grid grid-cols-3 gap-2 text-[11px] text-gray-500 dark:text-gray-400 pt-1 border-t border-gray-200 dark:border-gray-700">
            <div>
              <span class="block text-[10px] uppercase text-gray-400">Compute Specs</span>
              <strong class="text-gray-800 dark:text-gray-200">{{ targetVmInfo.cores }} vCPU • {{ targetVmInfo.ram }} GB</strong>
            </div>
            <div>
              <span class="block text-[10px] uppercase text-gray-400">Baseline Spend</span>
              <strong class="text-gray-800 dark:text-gray-200">{{ formatAmount(targetVmInfo.currentSpend) }}/mo</strong>
            </div>
            <div>
              <span class="block text-[10px] uppercase text-gray-400">Region / Host</span>
              <strong class="text-gray-800 dark:text-gray-200 truncate block">{{ targetVmInfo.region }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Strategy Selector -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
          2. Choose Off-Hours Optimization Strategy:
        </label>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <!-- Strategy A: Turn Off (100% compute savings) -->
          <div
            @click="strategy = 'shutdown'"
            class="p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col justify-between"
            :class="
              strategy === 'shutdown'
                ? 'border-purple-500 bg-purple-50/50 dark:bg-purple-950/30 dark:border-purple-500'
                : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/40 hover:border-gray-300'
            "
          >
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                  <span class="text-purple-600">🛑</span> Complete Turn Off
                </span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300">
                  100% Savings
                </span>
              </div>
              <p class="text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed">
                Deallocates VM completely during non-work hours. Compute cost drops to <strong>₹0.00/hr</strong> while stopped.
              </p>
            </div>
            <div class="text-[10px] text-purple-700 dark:text-purple-300 font-semibold mt-3">
              Best for: Dev, QA, Staging, Batch, Model VMs
            </div>
          </div>

          <!-- Strategy B: Rightsizing Downscale (50% savings) -->
          <div
            @click="strategy = 'downscale'"
            class="p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col justify-between"
            :class="
              strategy === 'downscale'
                ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/30 dark:border-brand-500'
                : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/40 hover:border-gray-300'
            "
          >
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                  <span class="text-brand-600">📉</span> Rightsizing Downscale
                </span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                  50% Savings
                </span>
              </div>
              <p class="text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed">
                Scales VM down to half-capacity (e.g. Standard_D4s $\rightarrow$ D2s) during off-hours while preserving 100% uptime SLA.
              </p>
            </div>
            <div class="text-[10px] text-brand-700 dark:text-brand-300 font-semibold mt-3">
              Best for: Production APIs, Customer Portals
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Configure Turn-Off Duration & Schedule -->
    <div class="p-4 rounded-xl bg-gray-50/70 dark:bg-gray-800/30 border border-gray-200 dark:border-gray-800 space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <label class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
          3. Set Duration in Which VM Will Be Turned Off:
        </label>
        <span class="text-xs font-mono font-bold text-purple-600 dark:text-purple-400">
          {{ offDurationHours }} Hours Turned Off per Day
        </span>
      </div>

      <!-- Duration Slider & Quick Presets -->
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <input
            type="range"
            min="1"
            max="24"
            step="1"
            v-model.number="offDurationHours"
            class="flex-1 accent-purple-600 cursor-pointer h-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
          />
          <span class="w-14 text-center font-mono font-bold text-sm text-gray-900 dark:text-white px-2 py-1 bg-white dark:bg-gray-800 border rounded-lg">
            {{ offDurationHours }}h
          </span>
        </div>

        <!-- Presets -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-[11px] text-gray-400">Presets:</span>
          <button
            v-for="p in durationPresets"
            :key="p.hours"
            @click="setPreset(p)"
            :class="[
              'px-2.5 py-1 rounded-md text-xs font-semibold transition-all',
              offDurationHours === p.hours
                ? 'bg-purple-600 text-white'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-purple-400'
            ]"
          >
            {{ p.label }} ({{ p.hours }}h)
          </button>
        </div>
      </div>

      <!-- Schedule Time Window & Days Mode -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <!-- Turn Off Time -->
        <div>
          <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-400 mb-1">
            Turn Off Time (Evening):
          </label>
          <input
            type="time"
            v-model="startTime"
            @change="syncFromTimes"
            class="w-full h-9 px-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs font-mono text-gray-900 dark:text-white"
          />
        </div>

        <!-- Turn On Time -->
        <div>
          <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-400 mb-1">
            Turn On / Boot Time (Morning):
          </label>
          <input
            type="time"
            v-model="endTime"
            @change="syncFromTimes"
            class="w-full h-9 px-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs font-mono text-gray-900 dark:text-white"
          />
        </div>

        <!-- Days Mode & Weekend Toggle -->
        <div class="flex flex-col justify-center">
          <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-400 mb-1">
            Weekly Schedule Mode:
          </label>
          <div class="flex items-center gap-2">
            <button
              @click="daysMode = 'weekdays'"
              :class="[
                'flex-1 h-9 rounded-lg text-xs font-semibold transition-all',
                daysMode === 'weekdays'
                  ? 'bg-brand-500 text-white shadow-xs'
                  : 'bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              Weekdays (22d)
            </button>
            <button
              @click="daysMode = 'daily'"
              :class="[
                'flex-1 h-9 rounded-lg text-xs font-semibold transition-all',
                daysMode === 'daily'
                  ? 'bg-brand-500 text-white shadow-xs'
                  : 'bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300'
              ]"
            >
              Every Day (30d)
            </button>
          </div>
        </div>
      </div>

      <!-- Full Weekend 48h Shutdown Toggle -->
      <div class="flex items-center justify-between p-3 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs">
        <div class="flex items-center gap-2.5">
          <span class="text-base">🛌</span>
          <div>
            <div class="font-bold text-gray-900 dark:text-white">
              Full Weekend 48-Hour Deallocation
            </div>
            <p class="text-[11px] text-gray-500">
              Turn off VM completely from Friday 8:00 PM through Monday 6:00 AM (+48 hrs every weekend)
            </p>
          </div>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" v-model="weekendShutdown" class="sr-only peer" />
          <div class="w-11 h-6 bg-gray-200 peer-focus:outline-hidden rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600 shadow-inner"></div>
        </label>
      </div>
    </div>

    <!-- Interactive 24-Hour Day Visualizer -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-xs">
        <span class="font-bold text-gray-700 dark:text-gray-300">
          24-Hour Daily Cycle Visualizer:
        </span>
        <div class="flex items-center gap-4 text-[11px]">
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-emerald-500"></span>
            Running / Active ({{ 24 - offDurationHours }}h)
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-purple-600"></span>
            {{ strategy === 'shutdown' ? 'Turned Off (₹0/hr)' : 'Rightsized 50%' }} ({{ offDurationHours }}h)
          </span>
        </div>
      </div>

      <!-- 24-Hour Bar -->
      <div class="h-6 rounded-lg overflow-hidden flex bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-[10px] font-mono text-white text-center font-bold">
        <div
          v-for="hour in 24"
          :key="hour"
          :style="{ width: `${100 / 24}%` }"
          :class="isHourTurnedOff(hour - 1) ? 'bg-purple-600 hover:bg-purple-700' : 'bg-emerald-500 hover:bg-emerald-600'"
          :title="`Hour ${hour - 1}:00 - ${isHourTurnedOff(hour - 1) ? 'Turned Off' : 'Active'}`"
          class="transition-colors cursor-pointer border-r border-black/10 last:border-r-0 flex items-center justify-center"
        >
          {{ (hour - 1) % 6 === 0 ? hour - 1 : '' }}
        </div>
      </div>
      <div class="flex justify-between text-[10px] font-mono text-gray-400 px-0.5">
        <span>00:00 (Midnight)</span>
        <span>06:00 (Morning)</span>
        <span>12:00 (Noon)</span>
        <span>18:00 (Evening)</span>
        <span>23:59 (Night)</span>
      </div>

      <!-- Schedule Breakdown Explanation -->
      <div class="p-2.5 rounded-lg bg-purple-50/70 dark:bg-purple-950/30 border border-purple-200/80 dark:border-purple-800/40 text-[11px] flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-purple-900 dark:text-purple-300">
        <div>
          <span class="font-bold">Schedule Breakdown: </span>
          <span v-if="weekendShutdown">
            {{ offDurationHours * 22 }} hrs (22 weekdays × {{ offDurationHours }}h) + 208 hrs (48h weekend deallocation × 4.33) = <strong>{{ monthlyOffHours }} hrs/mo</strong>
          </span>
          <span v-else>
            {{ daysMode === 'daily' ? '30 days' : '22 weekdays' }} × {{ offDurationHours }}h/night = <strong>{{ monthlyOffHours }} hrs/mo</strong>
          </span>
        </div>
        <span class="text-[10px] opacity-80 font-mono">
          {{ ((monthlyOffHours / 730) * 100).toFixed(1) }}% of total monthly compute eliminated
        </span>
      </div>
    </div>

    <!-- Step 4: FinOps Mathematical Results & Action -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
      <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 shadow-xs">
        <span class="text-[10px] font-bold text-gray-400 uppercase">Monthly Off Duration</span>
        <div class="text-base font-extrabold text-purple-600 dark:text-purple-400 mt-0.5">
          {{ monthlyOffHours }} hrs/mo
        </div>
        <span class="text-[10px] text-gray-400">{{ ((monthlyOffHours / 730) * 100).toFixed(1) }}% of Month Off</span>
      </div>

      <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 shadow-xs">
        <span class="text-[10px] font-bold text-gray-400 uppercase">Baseline Monthly Spend</span>
        <div class="text-base font-extrabold text-gray-800 dark:text-gray-200 mt-0.5">
          {{ formatAmount(targetVmInfo.currentSpend) }}
        </div>
        <span class="text-[10px] text-gray-400">730 hrs 24/7 Running</span>
      </div>

      <div class="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-200 dark:border-gray-800 shadow-xs">
        <span class="text-[10px] font-bold text-gray-400 uppercase">Simulated Monthly Spend</span>
        <div class="text-base font-extrabold text-brand-600 dark:text-brand-400 mt-0.5">
          {{ formatAmount(targetVmInfo.currentSpend - calculatedMonthlySavings) }}
        </div>
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">-{{ savingsPercent.toFixed(1) }}% Net Reduction</span>
      </div>

      <div class="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 shadow-xs">
        <span class="text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase">Projected Annual Savings</span>
        <div class="text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
          {{ formatAmount(calculatedMonthlySavings * 12) }}
        </div>
        <span class="text-[10px] text-emerald-700 dark:text-emerald-300 font-medium">Save {{ formatAmount(calculatedMonthlySavings) }}/mo</span>
      </div>
    </div>

    <!-- Mathematical Formula Display -->
    <div class="p-3 rounded-xl bg-gray-950 text-gray-200 font-mono text-[11px] space-y-1">
      <div class="text-gray-400"># FinOps Itemized Calculation Formula:</div>
      <div class="text-emerald-400 font-semibold">
        Monthly Savings = ({{ formatAmount(targetVmInfo.hourlyRate) }}/hr × {{ strategy === 'shutdown' ? '1.0' : '0.5' }}) × {{ monthlyOffHours }} hrs/month = {{ formatAmount(calculatedMonthlySavings) }}
      </div>
      <div class="text-gray-400">
        Annual Fleet ROI = {{ formatAmount(calculatedMonthlySavings) }}/mo × 12 months = {{ formatAmount(calculatedMonthlySavings * 12) }}/year
      </div>
    </div>

    <!-- Apply Policy Button -->
    <div class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-800">
      <div class="text-xs text-gray-500">
        Ready to enforce this shutdown schedule on <strong class="text-gray-900 dark:text-white">{{ targetVmInfo.name }}</strong>?
      </div>
      <button
        @click="handleApplyPolicy"
        :disabled="isApplying"
        class="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold transition-all shadow-md shadow-purple-600/20 disabled:opacity-50 flex items-center gap-2"
      >
        <svg v-if="isApplying" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ isApplying ? 'Enforcing Policy...' : 'Apply Scheduled Policy to VM' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const { vms, selectedVmId, formatAmount, showToast, applyVmSchedulePolicy } = useFinOps()

const targetVmId = ref<string>(selectedVmId.value || (vms.value[0]?.id ?? 'all'))
const strategy = ref<'shutdown' | 'downscale'>('shutdown')
const offDurationHours = ref<number>(10)
const startTime = ref<string>('20:00')
const endTime = ref<string>('06:00')
const daysMode = ref<'weekdays' | 'daily'>('weekdays')
const weekendShutdown = ref<boolean>(true)
const isApplying = ref<boolean>(false)

// Duration Presets
const durationPresets = [
  { label: 'Night Shift', hours: 8, start: '22:00', end: '06:00' },
  { label: 'Standard Off-Hours', hours: 10, start: '20:00', end: '06:00' },
  { label: 'Extended Off-Hours', hours: 12, start: '19:00', end: '07:00' },
  { label: 'Business Hours Only', hours: 16, start: '17:00', end: '09:00' },
]

// Keep targetVmId in sync when parent selectedVmId changes
watch(selectedVmId, (newId) => {
  if (newId && targetVmId.value !== 'all') {
    targetVmId.value = newId
  }
})

const handleVmChange = () => {
  // Triggered when dropdown changes
}

const setPreset = (preset: any) => {
  offDurationHours.value = preset.hours
  startTime.value = preset.start
  endTime.value = preset.end
}

const syncFromTimes = () => {
  const [sh, sm] = startTime.value.split(':').map(Number)
  const [eh, em] = endTime.value.split(':').map(Number)
  let diff = eh - sh + (em - sm) / 60
  if (diff <= 0) {
    diff += 24
  }
  offDurationHours.value = Math.max(1, Math.min(24, Math.round(diff)))
}

// Check if a given hour (0..23) falls into the turned-off window
const isHourTurnedOff = (hour: number) => {
  const [sh] = startTime.value.split(':').map(Number)
  const dur = offDurationHours.value
  const endH = (sh + dur) % 24
  if (sh < endH) {
    return hour >= sh && hour < endH
  } else {
    return hour >= sh || hour < endH
  }
}

// Target VM Info
const targetVmInfo = computed(() => {
  if (targetVmId.value === 'all') {
    const totalHourly = vms.value.reduce((acc, v) => acc + (v.hourlyRate || 25), 0)
    const totalSpend = vms.value.reduce((acc, v) => acc + (v.currentSpend || 18000), 0)
    const totalCores = vms.value.reduce((acc, v) => acc + (v.cores || 4), 0)
    const totalRam = vms.value.reduce((acc, v) => acc + (v.ram || 8), 0)
    return {
      name: `All Fleet VMs (${vms.value.length} Nodes)`,
      size: `${totalCores} Total vCPUs`,
      hourlyRate: totalHourly,
      currentSpend: totalSpend,
      cores: totalCores,
      ram: totalRam,
      region: 'Cross-Region Consolidated Fleet',
    }
  }

  const found = vms.value.find((v) => v.id === targetVmId.value) || vms.value[0]
  if (found) {
    return {
      name: found.name,
      size: found.size || 'Standard_D4s_v5',
      hourlyRate: found.hourlyRate || 28.5,
      currentSpend: found.currentSpend || 20805,
      cores: found.cores || 4,
      ram: found.ram || 16,
      region: found.region || 'East US',
    }
  }

  return {
    name: 'Standard Instance',
    size: 'Standard_D4s_v5',
    hourlyRate: 28.5,
    currentSpend: 20805,
    cores: 4,
    ram: 16,
    region: 'East US',
  }
})

// Calculate monthly turned-off hours
const monthlyOffHours = computed(() => {
  if (weekendShutdown.value) {
    // When Full Weekend 48h Deallocation is active, Saturday & Sunday are turned off 24/7 (48h/weekend = 208h/mo)
    // Weekdays are turned off for the daily scheduled duration (22 days * offDurationHours)
    const weekdayOff = offDurationHours.value * 22
    const weekendOff = Math.round(48 * 4.33) // 208 hours
    return Math.min(730, weekdayOff + weekendOff)
  } else {
    // Normal schedule without full weekend deallocation
    const daysCount = daysMode.value === 'daily' ? 30 : 22
    return Math.min(730, offDurationHours.value * daysCount)
  }
})

// Calculated Monthly Savings
const calculatedMonthlySavings = computed(() => {
  const rate = targetVmInfo.value.hourlyRate
  const factor = strategy.value === 'shutdown' ? 1.0 : 0.5
  return Math.round(rate * factor * monthlyOffHours.value)
})

const savingsPercent = computed(() => {
  if (targetVmInfo.value.currentSpend <= 0) return 0
  return Math.min(100, (calculatedMonthlySavings.value / targetVmInfo.value.currentSpend) * 100)
})

const handleApplyPolicy = async () => {
  isApplying.value = true
  try {
    const vmTargetList = targetVmId.value === 'all' ? vms.value.map((v) => v.id) : [targetVmId.value]
    for (const vid of vmTargetList) {
      const singleVmSavings =
        targetVmId.value === 'all'
          ? Math.round(calculatedMonthlySavings.value / vmTargetList.length)
          : calculatedMonthlySavings.value

      await applyVmSchedulePolicy({
        vm_id: vid,
        action: strategy.value,
        off_hours_duration: offDurationHours.value,
        start_time: startTime.value,
        end_time: endTime.value,
        days_mode: daysMode.value,
        weekend_shutdown: weekendShutdown.value,
        simulated_monthly_savings: singleVmSavings,
      })
    }
    showToast(
      `Enforced ${offDurationHours.value}h shutdown schedule! Projected to save ${formatAmount(calculatedMonthlySavings.value)}/month.`
    )
  } finally {
    isApplying.value = false
  }
}
</script>
