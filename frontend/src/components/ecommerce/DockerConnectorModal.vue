<template>
  <div>
    <!-- Top Docker Banner on Dashboard -->
    <div
      class="rounded-2xl border p-4 sm:px-6 sm:py-4 shadow-sm transition-all flex flex-col md:flex-row md:items-center justify-between gap-3"
      :class="
        dockerConnected
          ? 'bg-emerald-50/70 border-emerald-200 dark:bg-emerald-950/20 dark:border-emerald-800'
          : 'bg-white border-gray-200 dark:bg-white/[0.03] dark:border-gray-800'
      "
    >
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
          :class="
            dockerConnected
              ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
              : 'bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400'
          "
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
            <line x1="12" y1="22.08" x2="12" y2="12"></line>
          </svg>
        </div>

        <div>
          <div class="flex items-center gap-2">
            <h4 class="text-sm font-bold text-gray-900 dark:text-white">
              Docker Container Virtualization & Auto-Scaling Lab
            </h4>
            <span
              class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
              :class="
                dockerConnected
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
              "
            >
              {{ dockerConnected ? 'Live Connection Active' : 'Ready to Connect' }}
            </span>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {{
              dockerConnected
                ? `Live telemetry streaming from ${dockerHost}. Container utho-workload linked with autonomous dynamic auto-scaling.`
                : "Connect your local or remote Docker host to test live workload stress, bottleneck alerts, and dynamic auto-scaling."
            }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          v-if="dockerConnected"
          @click="selectDockerVm"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs transition-all flex items-center gap-1.5"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
          Select Docker VM
        </button>

        <button
          @click="openModal"
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all flex items-center gap-1.5"
          :class="
            dockerConnected
              ? 'border-emerald-300 text-emerald-800 bg-emerald-100/60 hover:bg-emerald-100 dark:border-emerald-700 dark:text-emerald-300'
              : 'border-brand-300 text-brand-600 bg-brand-50 hover:bg-brand-100 dark:border-brand-700 dark:text-brand-300 dark:bg-brand-500/10'
          "
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          {{ dockerConnected ? 'Open Stress & Scaling Lab' : 'Connect Docker Agent' }}
        </button>
      </div>
    </div>

    <!-- Modal Dialog -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 z-99999 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
    >
      <div
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-y-auto max-h-[92vh]"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2.5">
            <span class="p-2 rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              </svg>
            </span>
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">
                Docker Workload Stress & Auto-Scaling Lab
              </h3>
              <p class="text-xs text-gray-500">
                Live container simulation, CPU stress injection, and zero-downtime dynamic scaling
              </p>
            </div>
          </div>

          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Connection Settings -->
        <div class="my-5 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Docker Telemetry Agent Host / URL
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model="inputHost"
                type="text"
                placeholder="http://localhost:8001 or http://10.19.127.139:8001"
                class="flex-1 h-10 px-3.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent text-xs text-gray-900 dark:text-white placeholder:text-gray-400 focus:border-brand-500 focus:outline-hidden"
              />
              <button
                @click="handleConnect"
                :disabled="isConnecting"
                class="px-4 h-10 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold transition-all disabled:opacity-50 shrink-0 flex items-center gap-1.5"
              >
                <svg v-if="isConnecting" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ isConnecting ? 'Connecting...' : (dockerConnected ? 'Re-sync' : 'Connect') }}</span>
              </button>
            </div>
            <p class="text-[11px] text-gray-400 mt-1">
              Agent runs locally on <code class="font-mono">http://localhost:8001</code> or across LAN via machine IP.
            </p>
          </div>

          <!-- Connection Status Info Card -->
          <div
            v-if="connectionResult"
            class="p-3.5 rounded-xl border text-xs"
            :class="
              dockerConnected
                ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-950/30 text-emerald-800 dark:text-emerald-300'
                : 'bg-amber-50 border-amber-200 dark:bg-amber-950/30 text-amber-800 dark:text-amber-300'
            "
          >
            <div class="font-bold mb-0.5">{{ connectionResult }}</div>
            <div v-if="dockerHostInfo?.host" class="text-[11px] opacity-80">
              Host: {{ dockerHostInfo.host.platform }} • Cores: {{ dockerHostInfo.host.cpuCount }} • Docker CLI: Ready
            </div>
          </div>

          <!-- Interactive Live Stress & Auto-Scale Lab -->
          <div class="p-4 rounded-xl border border-brand-200 dark:border-brand-900/50 bg-brand-50/30 dark:bg-brand-950/20 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                  <span>⚡</span> Live Workload Stress & Auto-Scale Lab
                </span>
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold"
                  :class="isStressActive ? 'bg-red-500 text-white animate-pulse' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'"
                >
                  {{ isStressActive ? 'STRESS ACTIVE (High Load)' : 'WORKLOAD IDLE (Normal)' }}
                </span>
              </div>

              <!-- Auto-Scaler Toggle -->
              <div class="flex items-center gap-2">
                <span class="text-[11px] font-semibold text-gray-600 dark:text-gray-300">Auto-Scaler:</span>
                <button
                  @click="toggleAutoScaler"
                  class="px-2.5 py-1 rounded-md text-[11px] font-bold transition-all"
                  :class="autoscaleEnabled ? 'bg-emerald-600 text-white shadow-xs' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
                >
                  {{ autoscaleEnabled ? 'Active (Auto >80%)' : 'Disabled' }}
                </button>
              </div>
            </div>

            <!-- Live Gauge and Spec Status -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center">
              <div class="p-2.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xs">
                <div class="text-[10px] font-bold text-gray-400 uppercase">Normalized CPU</div>
                <div
                  class="text-base font-extrabold mt-0.5 transition-colors"
                  :class="liveCpu > 80 ? 'text-red-500' : (liveCpu > 65 ? 'text-amber-500' : 'text-emerald-600')"
                >
                  {{ liveCpu.toFixed(1) }}%
                </div>
                <div class="text-[9px] text-gray-400">
                  {{ liveRawCpu > 0 ? `Raw Load: ${liveRawCpu.toFixed(0)}%` : 'Target: < 70%' }}
                </div>
              </div>

              <div class="p-2.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xs">
                <div class="text-[10px] font-bold text-gray-400 uppercase">Allocated Cores</div>
                <div class="text-base font-extrabold text-brand-600 dark:text-brand-400 mt-0.5">
                  {{ liveCpus }} vCPUs
                </div>
                <div class="text-[9px] text-gray-400">
                  {{ liveCpus >= 8 ? 'Max (8 Cores)' : (liveCpus >= 6 ? 'Tier 2 (6 Cores)' : (liveCpus >= 4 ? 'Tier 1 (4 Cores)' : 'Baseline (2 Cores)')) }}
                </div>
              </div>

              <div class="p-2.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xs">
                <div class="text-[10px] font-bold text-gray-400 uppercase">Memory Quota</div>
                <div class="text-base font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">
                  {{ liveMemLimit }}
                </div>
                <div class="text-[9px] text-gray-400">{{ liveRam.toFixed(1) }}% Utilized</div>
              </div>

              <div class="p-2.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xs">
                <div class="text-[10px] font-bold text-gray-400 uppercase">Auto-Scale State</div>
                <div
                  class="text-xs font-extrabold mt-1 uppercase"
                  :class="liveCpus > 2 ? 'text-purple-600 dark:text-purple-400' : 'text-emerald-600 dark:text-emerald-400'"
                >
                  {{ liveCpus > 2 ? `🚀 Tier ${liveCpus}C` : '🌱 Baseline (2C)' }}
                </div>
                <div class="text-[9px] text-gray-400">Target &lt; 70% CPU</div>
              </div>
            </div>

            <!-- Action Buttons for Stress & Scaling -->
            <div class="space-y-2 pt-1">
              <div class="flex flex-wrap items-center gap-2">
                <button
                  v-if="!isStressActive"
                  @click="injectStress(4)"
                  :disabled="isActionLoading"
                  class="flex-1 py-2 px-3 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5"
                >
                  <span>⚡ Inject 4-Core Stress (400% Load)</span>
                </button>

                <button
                  v-if="!isStressActive"
                  @click="injectStress(8)"
                  :disabled="isActionLoading"
                  class="py-2 px-3 rounded-xl bg-orange-600 hover:bg-orange-700 text-white text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5 shrink-0"
                >
                  <span>🔥 Peak 8-Core Stress</span>
                </button>

                <button
                  v-else
                  @click="stopStress"
                  :disabled="isActionLoading"
                  class="flex-1 py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5"
                >
                  <span>⏹ Stop Stress & Cooldown</span>
                </button>
              </div>

              <!-- Instant Multi-Tier Manual Scaling -->
              <div class="pt-2 border-t border-brand-200/50 dark:border-brand-900/30">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-[11px] font-semibold text-gray-600 dark:text-gray-300">Live Scale Quota Override (Zero Downtime):</span>
                  <span class="text-[10px] text-gray-400">Max 8 Cores</span>
                </div>
                <div class="grid grid-cols-4 gap-1.5">
                  <button
                    v-for="tier in [
                      { cpus: 2, mem: '2g', label: '2 vCPUs' },
                      { cpus: 4, mem: '4g', label: '4 vCPUs' },
                      { cpus: 6, mem: '6g', label: '6 vCPUs' },
                      { cpus: 8, mem: '8g', label: '8 vCPUs' },
                    ]"
                    :key="tier.cpus"
                    @click="manualScale(tier.cpus, tier.mem)"
                    :disabled="isActionLoading"
                    class="py-1.5 px-2 rounded-lg text-xs font-semibold transition-all border text-center"
                    :class="liveCpus === tier.cpus
                      ? 'bg-brand-500 text-white border-brand-500 shadow-xs'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-brand-400'"
                  >
                    {{ tier.label }}
                  </button>
                </div>
              </div>
            </div>

            <p class="text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed">
              <strong>Autonomous Multi-Tier Logic:</strong> When 400% CPU stress load is detected on 2 cores, the autonomous auto-scaler dynamically upgrades the container to <strong>6 cores (6g RAM)</strong> so CPU utilization stabilizes at <strong>66.7%</strong> (safely under the 70% threshold). If load expands beyond 6 cores, it scales up to <strong>8 cores (8g RAM)</strong>. Stopping stress initiates an 8s cooldown and reverts back to 2 cores.
            </p>
          </div>

          <!-- Dynamic Scaling History Event Stream -->
          <div v-if="scaleHistory.length > 0" class="space-y-1.5">
            <h4 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider">
              Autonomous Dynamic Scaling Log
            </h4>
            <div class="max-h-36 overflow-y-auto space-y-1 rounded-xl border border-gray-200 dark:border-gray-800 p-2 bg-gray-50 dark:bg-gray-900/60 font-mono text-[11px]">
              <div
                v-for="(evt, idx) in scaleHistory.slice(0, 6)"
                :key="evt.id || idx"
                class="p-1.5 rounded flex items-center justify-between"
                :class="evt.type === 'AUTO_UPSCALE' ? 'bg-purple-100/70 text-purple-900 dark:bg-purple-950/40 dark:text-purple-300' : 'bg-emerald-100/70 text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300'"
              >
                <div class="flex items-center gap-1.5 truncate">
                  <span class="font-bold">{{ evt.type === 'AUTO_UPSCALE' ? '🚀 UPSCALE:' : '🔄 DOWNSCALE:' }}</span>
                  <span class="truncate">{{ evt.message }}</span>
                </div>
                <span class="text-[10px] opacity-75 shrink-0 ml-2">
                  {{ new Date(evt.timestamp).toLocaleTimeString() }}
                </span>
              </div>
            </div>
          </div>

          <!-- Quick Terminal Command Guide -->
          <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
            <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 mb-1.5">
              CLI Alternative Commands (PowerShell / Terminal):
            </h4>
            <div class="bg-gray-950 text-gray-200 rounded-xl p-3 font-mono text-[11px] space-y-1">
              <div class="text-gray-400"># Give stress to VM via CLI:</div>
              <div class="text-amber-400 select-all">docker exec -d utho-workload sh -c "while true; do :; done & while true; do :; done"</div>
              <div class="text-gray-400 mt-1"># Stop stress and cool down:</div>
              <div class="text-emerald-400 select-all">docker exec utho-workload pkill -f "while true"</div>
              <div class="text-gray-400 mt-1"># Watch live metrics and zero-downtime scaling:</div>
              <div class="text-cyan-400 select-all">docker stats utho-workload</div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
          <button
            @click="closeModal"
            class="px-4 py-2 text-xs font-semibold rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useFinOps } from '@/composables/useFinOps'

const {
  dockerHost,
  dockerConnected,
  dockerHostInfo,
  dockerContainers,
  connectDocker,
  scaleDockerContainer,
  switchCustomer,
  currentCustomer,
  showToast,
  vms,
  selectVm,
} = useFinOps()

const isModalOpen = ref(false)
const inputHost = ref(dockerHost.value || 'http://localhost:8001')
const isConnecting = ref(false)
const connectionResult = ref('')
const isActionLoading = ref(false)

// Live Lab State
const isStressActive = ref(false)
const liveCpu = ref(0.0)
const liveRawCpu = ref(0.0)
const liveRam = ref(0.0)
const liveCpus = ref(2.0)
const liveMemLimit = ref('2.0 GB')
const autoscaleEnabled = ref(true)
const autoscaleProfile = ref('baseline')
const scaleHistory = ref<any[]>([])

let pollTimer: any = null

const openModal = async () => {
  isModalOpen.value = true
  await handleConnect()
  startLivePolling()
}

const closeModal = () => {
  isModalOpen.value = false
  stopLivePolling()
}

const handleConnect = async () => {
  isConnecting.value = true
  connectionResult.value = ''
  try {
    const res = await connectDocker(inputHost.value)
    if (res.connected) {
      connectionResult.value = `Connected live to ${inputHost.value}! Discovered ${res.count} containers.`
      await fetchLiveTelemetry()
    } else {
      connectionResult.value = `Live agent at ${inputHost.value} not detected. Defaulted to simulated Model VM containers.`
    }
  } finally {
    isConnecting.value = false
  }
}

const fetchLiveTelemetry = async () => {
  try {
    const host = inputHost.value.replace(/\/$/, '')
    const res = await fetch(`${host}/metrics`)
    if (res.ok) {
      const data = await res.json()
      if (data.container) {
        liveCpu.value = data.container.cpuPercent || 0.0
        liveRawCpu.value = data.container.rawCpuPercent || (data.container.cpuPercent * (data.container.cpuLimit || 2.0))
        liveRam.value = data.container.ramPercent || 0.0
        liveCpus.value = data.container.cpuLimit || 2.0
        liveMemLimit.value = `${(data.container.ramLimitMb / 1024).toFixed(1)} GB`
      }
      if (data.stress) {
        isStressActive.value = data.stress.active
      }
      if (data.autoScale) {
        autoscaleEnabled.value = data.autoScale.enabled
        autoscaleProfile.value = data.autoScale.currentProfile
      }
    }

    const autoRes = await fetch(`${host}/autoscale`)
    if (autoRes.ok) {
      const autoData = await autoRes.json()
      scaleHistory.value = autoData.history || []
      autoscaleProfile.value = autoData.currentProfile || autoscaleProfile.value
    }
  } catch (err) {
    // Silent polling catch
  }
}

const startLivePolling = () => {
  stopLivePolling()
  pollTimer = setInterval(fetchLiveTelemetry, 1500)
}

const stopLivePolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const injectStress = async (workers: number = 4) => {
  isActionLoading.value = true
  try {
    const host = inputHost.value.replace(/\/$/, '')
    const res = await fetch(`${host}/stress/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workers }),
    })
    if (res.ok) {
      isStressActive.value = true
      showToast(`⚡ High CPU stress injected (${workers} parallel workers, ${workers * 100}% compute load)!`)
      await fetchLiveTelemetry()
    }
  } catch (err: any) {
    showToast('Failed to start stress: ' + err.message)
  } finally {
    isActionLoading.value = false
  }
}

const stopStress = async () => {
  isActionLoading.value = true
  try {
    const host = inputHost.value.replace(/\/$/, '')
    const res = await fetch(`${host}/stress/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    if (res.ok) {
      isStressActive.value = false
      showToast('⏹ Stress stopped. Workload returning to baseline.')
      await fetchLiveTelemetry()
    }
  } catch (err: any) {
    showToast('Failed to stop stress: ' + err.message)
  } finally {
    isActionLoading.value = false
  }
}

const toggleAutoScaler = async () => {
  try {
    const host = inputHost.value.replace(/\/$/, '')
    const nextVal = !autoscaleEnabled.value
    const res = await fetch(`${host}/autoscale`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: nextVal }),
    })
    if (res.ok) {
      autoscaleEnabled.value = nextVal
      showToast(`Auto-scaler ${nextVal ? 'Activated' : 'Paused'}.`)
    }
  } catch (err: any) {
    showToast('Failed to update auto-scaler: ' + err.message)
  }
}

const manualScale = async (cpus: number, memory: string) => {
  isActionLoading.value = true
  try {
    const res = await scaleDockerContainer('utho-workload', cpus, memory)
    if (res.success) {
      liveCpus.value = cpus
      liveMemLimit.value = `${parseInt(memory)} GB`
      await fetchLiveTelemetry()
    }
  } finally {
    isActionLoading.value = false
  }
}

const selectDockerVm = async () => {
  const dVm = vms.value.find((v: any) => v.id.startsWith('docker-'))
  if (dVm) {
    await selectVm(dVm.id)
    showToast(`Selected Docker Model VM: ${dVm.name}`)
  } else {
    showToast("Docker container is connected to your active fleet.")
  }
}

onUnmounted(() => {
  stopLivePolling()
})
</script>
