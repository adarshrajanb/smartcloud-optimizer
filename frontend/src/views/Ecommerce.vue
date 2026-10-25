<template>
  <admin-layout>
    <div class="space-y-6">
      <!-- Top Action Bar: Persona Switcher, Alerts Trigger & Assumptions Sheet -->
      <div
        class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] shadow-xs"
      >
        <!-- Left: Persona Switcher -->
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold uppercase tracking-wider text-gray-400">View Persona:</span>
          <div class="inline-flex items-center p-0.5 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
            <button
              v-for="p in [
                { id: 'engineer', label: 'Cloud Engineer' },
                { id: 'finance', label: 'FinOps Lead' },
                { id: 'leadership', label: 'Leadership / CTO' }
              ]"
              :key="p.id"
              @click="currentPersona = (p.id as any)"
              :class="[
                currentPersona === p.id
                  ? 'bg-white dark:bg-gray-900 text-brand-600 dark:text-white font-bold shadow-xs'
                  : 'text-gray-500 hover:text-gray-800 dark:text-gray-400',
                'px-3 py-1.5 rounded-lg text-xs transition-all cursor-pointer'
              ]"
            >
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- Right: Alerts, Assumptions Sheet & Export Actions -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Alerts & Insights Button with Live Badge -->
          <button
            @click="showAlertsDrawer = true"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-error-500/30 bg-error-50 hover:bg-error-100 dark:border-error-500/20 dark:bg-error-950/40 dark:text-error-300 text-xs font-bold text-error-700 transition-all cursor-pointer shadow-2xs"
          >
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-error-500"></span>
            </span>
            Alerts & Insights
            <span class="px-1.5 py-0.2 rounded-full bg-error-600 text-white text-[10px]">4</span>
          </button>

          <!-- Assumptions Sheet Button -->
          <button
            @click="showAssumptionsModal = true"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700 text-xs font-semibold text-gray-700 dark:text-gray-200 transition-all cursor-pointer shadow-2xs"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            Assumptions Sheet
          </button>

          <!-- Download Terraform Plan -->
          <button
            @click="downloadTerraform"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-purple-500/30 bg-purple-50 hover:bg-purple-100 dark:border-purple-500/20 dark:bg-purple-950/40 dark:text-purple-300 text-xs font-semibold text-purple-700 transition-all cursor-pointer shadow-2xs"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Terraform
          </button>

          <!-- Download Azure CLI Script -->
          <button
            @click="downloadCliScript"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-blue-500/30 bg-blue-50 hover:bg-blue-100 dark:border-blue-500/20 dark:bg-blue-950/40 dark:text-blue-300 text-xs font-semibold text-blue-700 transition-all cursor-pointer shadow-2xs"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 17 10 11 4 5"></polyline>
              <line x1="12" y1="19" x2="20" y2="19"></line>
            </svg>
            Azure CLI
          </button>
        </div>
      </div>

      <!-- Live Docker Engine Workload Scaling Hub -->
      <docker-connector-modal />

      <!-- If Customer has 0 Resources: Show Provisioning Plans -->
      <vm-provisioning-plans v-if="vms.length === 0" />

      <!-- Live FinOps Infrastructure Dashboard -->
      <template v-else>
        <!-- Top FinOps High-Level Metrics (40% surge, budget safe, savings, ESG) -->
        <ecommerce-metrics />

        <!-- Active VM Hardware Specs & Spotlight -->
        <vm-specs-card />

        <!-- Interactive Telemetry & AI Forecast Chart (vCPU, RAM, Disk IOPS, Network In/Out) -->
        <statistics-chart />

        <!-- Environment Before vs After Table, Peak Safety Guarantee & Recommendation Toggles -->
        <predictive-decisions />

        <!-- Cloud VM Shutdown & What-If Savings Simulator -->
        <vm-shutdown-simulator />

        <!-- Customer Multi-Region Fleet Management Table with Multi-Filters -->
        <recent-orders />
      </template>

      <!-- Modal Drawers -->
      <alerts-drawer :is-open="showAlertsDrawer" @close="showAlertsDrawer = false" />
      <assumptions-modal :is-open="showAssumptionsModal" @close="showAssumptionsModal = false" />
    </div>
  </admin-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'
import DockerConnectorModal from '../components/ecommerce/DockerConnectorModal.vue'
import VmProvisioningPlans from '../components/ecommerce/VmProvisioningPlans.vue'
import EcommerceMetrics from '../components/ecommerce/EcommerceMetrics.vue'
import VmSpecsCard from '../components/ecommerce/VmSpecsCard.vue'
import StatisticsChart from '../components/ecommerce/StatisticsChart.vue'
import PredictiveDecisions from '../components/ecommerce/PredictiveDecisions.vue'
import VmShutdownSimulator from '../components/ecommerce/VmShutdownSimulator.vue'
import RecentOrders from '../components/ecommerce/RecentOrders.vue'
import AlertsDrawer from '../components/ecommerce/AlertsDrawer.vue'
import AssumptionsModal from '../components/ecommerce/AssumptionsModal.vue'
import { useFinOps } from '@/composables/useFinOps'

const showAlertsDrawer = ref(false)
const showAssumptionsModal = ref(false)

const {
  loadFleet,
  currentCustomer,
  vms,
  currentPersona,
  downloadTerraform,
  downloadCliScript,
} = useFinOps()

onMounted(async () => {
  await loadFleet(currentCustomer.value.customerId)
})
</script>