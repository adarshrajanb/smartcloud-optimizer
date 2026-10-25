<template>
  <admin-layout>
    <div class="space-y-6">
      <!-- Friend's Docker Model VM Hub & Integration Bar -->
      <docker-connector-modal />

      <!-- If New Customer has 0 VMs: Show Cloud Compute Provisioning Plans -->
      <vm-provisioning-plans v-if="vms.length === 0" />

      <!-- If Customer has 1 or more VMs: Show Live FinOps Infrastructure Dashboard -->
      <template v-else>
        <!-- Top FinOps High-Level Metrics -->
        <ecommerce-metrics />

        <!-- Active VM Hardware Specs & Spotlight -->
        <vm-specs-card />

        <!-- Interactive Telemetry & AI Forecast Chart -->
        <statistics-chart />

        <!-- Predictive Downscaling & Bottleneck Alerts + Bottom Dynamic Billing Consent -->
        <predictive-decisions />

        <!-- Cloud VM Shutdown & Cost Savings Simulator -->
        <vm-shutdown-simulator />

        <!-- Customer Azure VM Fleet Management Table -->
        <recent-orders />
      </template>
    </div>
  </admin-layout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'
import DockerConnectorModal from '../components/ecommerce/DockerConnectorModal.vue'
import VmProvisioningPlans from '../components/ecommerce/VmProvisioningPlans.vue'
import EcommerceMetrics from '../components/ecommerce/EcommerceMetrics.vue'
import VmSpecsCard from '../components/ecommerce/VmSpecsCard.vue'
import StatisticsChart from '../components/ecommerce/StatisticsChart.vue'
import PredictiveDecisions from '../components/ecommerce/PredictiveDecisions.vue'
import VmShutdownSimulator from '../components/ecommerce/VmShutdownSimulator.vue'
import RecentOrders from '../components/ecommerce/RecentOrders.vue'
import { useFinOps } from '@/composables/useFinOps'

const { loadFleet, currentCustomer, vms } = useFinOps()

onMounted(async () => {
  if (vms.value.length === 0) {
    await loadFleet(currentCustomer.value.customerId)
  }
})
</script>
