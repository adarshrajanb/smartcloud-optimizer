<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="FinOps Cost Optimizer & Telemetry" />
    <div class="space-y-6">
      <!-- Interactive Telemetry & Workload Forecast Chart -->
      <StatisticsChart />

      <!-- Full VM Shutdown & Rightsizing Savings Simulator -->
      <VmShutdownSimulator />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import StatisticsChart from "@/components/ecommerce/StatisticsChart.vue";
import VmShutdownSimulator from "@/components/ecommerce/VmShutdownSimulator.vue";
</script>
