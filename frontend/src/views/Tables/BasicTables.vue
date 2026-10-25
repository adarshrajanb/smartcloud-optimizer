<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Azure VM Fleet" />
    <div class="space-y-6">
      <RecentOrders />
      <VmSpecsCard />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import RecentOrders from "@/components/ecommerce/RecentOrders.vue";
import VmSpecsCard from "@/components/ecommerce/VmSpecsCard.vue";
</script>
