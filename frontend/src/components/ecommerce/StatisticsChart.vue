<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white px-5 pb-5 pt-5 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6 sm:pt-6 shadow-sm"
  >
    <!-- Chart Header & Interactive Controls -->
    <div class="flex flex-col gap-4 mb-6 xl:flex-row xl:items-center xl:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            Resource Telemetry & AI Workload Forecast
          </h3>
          <span v-if="selectedVmDetail" class="text-xs px-2 py-0.5 rounded font-mono font-medium bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
            {{ selectedVmDetail.name }}
          </span>
        </div>
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Evaluates past telemetry patterns to identify off-hours drops (7 PM – 5 AM) and impending capacity bottlenecks.
        </p>
      </div>

      <!-- Controls Row -->
      <div class="flex flex-wrap items-center gap-2.5">
        <!-- Metric Switcher -->
        <div class="inline-flex items-center gap-0.5 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <button
            v-for="m in metricOptions"
            :key="m.id"
            @click="chartMetric = m.id"
            :class="[
              chartMetric === m.id
                ? 'shadow-xs text-brand-600 dark:text-white bg-white dark:bg-gray-800 font-semibold'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-800',
              'px-2.5 py-1.5 text-xs rounded-md transition-all',
            ]"
          >
            {{ m.label }}
          </button>
        </div>

        <!-- Time Range Switcher -->
        <div class="inline-flex items-center gap-0.5 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <button
            v-for="r in rangeOptions"
            :key="r.id"
            @click="handleRangeChange(r.id)"
            :class="[
              timeRange === r.id
                ? 'shadow-xs text-gray-900 dark:text-white bg-white dark:bg-gray-800 font-semibold'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-800',
              'px-2.5 py-1.5 text-xs rounded-md transition-all',
            ]"
          >
            {{ r.label }}
          </button>
        </div>

        <!-- Granularity Switcher -->
        <div class="inline-flex items-center gap-0.5 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <button
            v-for="g in availableGranularities"
            :key="g.id"
            @click="handleGranularityChange(g.id)"
            :class="[
              granularity === g.id
                ? 'shadow-xs text-brand-600 dark:text-white bg-white dark:bg-gray-800 font-semibold'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-800',
              'px-2.5 py-1.5 text-xs rounded-md transition-all',
            ]"
          >
            {{ g.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Live Stream Information Banner (Only for Newly Provisioned Nodes) -->
    <div
      v-if="selectedVmDetail?.isNew"
      class="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-blue-50/80 dark:bg-blue-950/20 border border-blue-200/80 dark:border-blue-800/40 mb-4 text-xs text-blue-900 dark:text-blue-200 shadow-2xs"
    >
      <div class="flex items-center gap-2.5">
        <span class="relative flex h-2.5 w-2.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-success-500"></span>
        </span>
        <span>
          <strong>Live Telemetry Stream Active:</strong> This node was just deployed. It only records live operational metrics from boot time. Historical telemetry prior to deployment is empty.
        </span>
      </div>
      <div class="flex items-center gap-2 text-[11px] font-mono">
        <span class="px-2 py-0.5 rounded bg-blue-100/80 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
          Uptime: &lt; 1 hr
        </span>
        <span class="px-2 py-0.5 rounded bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300 font-semibold">
          ● Live Tick: 3.5s
        </span>
      </div>
    </div>

    <!-- Telemetry Legend Banner -->
    <div class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800 mb-4 text-xs">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-brand-500 inline-block"></span>
          <span class="font-medium text-gray-700 dark:text-gray-300">Recorded Telemetry (Actual)</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3.5 h-0.5 border-t-2 border-dashed border-warning-500 inline-block"></span>
          <span class="font-medium text-gray-700 dark:text-gray-300">AI Predictive Forecast Curve</span>
        </div>
      </div>

      <div class="flex items-center gap-3 text-[11px] text-gray-500 dark:text-gray-400">
        <span class="inline-flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-brand-400"></span>
          Off-Hours Window: Weekdays 7 PM – 5 AM
        </span>
        <span class="inline-flex items-center gap-1 text-error-600 dark:text-error-400 font-medium">
          <span class="w-2 h-2 rounded-full bg-error-500"></span>
          Bottleneck Alert: &gt;85% Sustained Usage
        </span>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="max-w-full overflow-x-auto custom-scrollbar">
      <div class="min-w-[700px] xl:min-w-full">
        <VueApexCharts
          v-if="chartSeries.length > 0"
          type="area"
          height="340"
          :options="chartOptions"
          :series="chartSeries"
        />
        <div v-else class="h-[340px] flex items-center justify-center text-gray-400">
          Loading VM telemetry series...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useFinOps } from '@/composables/useFinOps'

const {
  selectedVmDetail,
  timeRange,
  granularity,
  chartMetric,
  setRangeAndGranularity,
  setSpecificGranularity,
} = useFinOps()

const metricOptions: Array<{ id: 'cpu' | 'ram' | 'disk'; label: string }> = [
  { id: 'cpu', label: 'vCPU %' },
  { id: 'ram', label: 'RAM %' },
  { id: 'disk', label: 'Disk IOPS' },
]

const rangeOptions: Array<{ id: '1d' | '7d' | '30d'; label: string }> = [
  { id: '1d', label: '1 Day' },
  { id: '7d', label: '7 Days' },
  { id: '30d', label: '30 Days' },
]

const availableGranularities = computed(() => {
  if (timeRange.value === '30d') {
    return [{ id: '1d', label: '1 Day' }]
  }
  return [
    { id: '10m', label: '10 Mins' },
    { id: '30m', label: '30 Mins' },
    { id: '1h', label: '1 Hour' },
  ]
})

const handleRangeChange = async (r: '1d' | '7d' | '30d') => {
  await setRangeAndGranularity(r)
}

const handleGranularityChange = async (g: string) => {
  await setSpecificGranularity(g)
}

// Chart Data Series Generation
const chartSeries = computed(() => {
  const seriesData = selectedVmDetail.value?.series || []
  if (seriesData.length === 0) return []

  const actualKey = chartMetric.value === 'cpu' ? 'cpu' : chartMetric.value === 'ram' ? 'ram' : 'disk'
  const forecastKey =
    chartMetric.value === 'cpu'
      ? 'predictedCpu'
      : chartMetric.value === 'ram'
      ? 'predictedRam'
      : 'predictedDisk'

  const actualPoints = seriesData.map((d: any) => {
    if (chartMetric.value === 'ram') {
      return Number(d.ram ?? d.memory ?? d.ramUsage ?? 0)
    }
    return Number(d[actualKey] ?? 0)
  })

  const forecastPoints = seriesData.map((d: any) => {
    if (chartMetric.value === 'ram') {
      return Number(d.predictedRam ?? d.predictedMemory ?? ((d.ram ?? d.memory ?? 45.0) + 1.5))
    }
    return Number(d[forecastKey] ?? d[actualKey] ?? 0)
  })

  return [
    {
      name: `Actual Telemetry (${metricOptions.find((m) => m.id === chartMetric.value)?.label})`,
      data: actualPoints,
    },
    {
      name: `AI Predictive Forecast`,
      data: forecastPoints,
    },
  ]
})

const categories = computed(() => {
  const seriesData = selectedVmDetail.value?.series || []
  return seriesData.map((d: any) => d.timeLabel || d.timestamp || '')
})

const chartOptions = computed(() => {
  const unit = chartMetric.value === 'disk' ? ' IOPS' : '%'
  const isNew = !!selectedVmDetail.value?.isNew

  return {
    chart: {
      type: 'area',
      height: 340,
      fontFamily: 'Outfit, sans-serif',
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: {
        enabled: isNew,
        dynamicAnimation: {
          speed: 400,
        },
      },
    },
    markers: {
      size: isNew ? [4, 3] : [0, 0],
      strokeWidth: 2,
    },
    stroke: {
      curve: 'smooth',
      width: [2.5, 2],
      dashArray: [0, 5],
    },
    colors: ['#465FFF', '#F59E0B'],
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.45,
        opacityTo: 0.05,
        stops: [0, 90, 100],
      },
    },
    dataLabels: { enabled: false },
    grid: {
      borderColor: '#E5E7EB',
      strokeDashArray: 3,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } },
    },
    xaxis: {
      categories: categories.value,
      labels: {
        rotate: isNew ? 0 : -45,
        rotateAlways: false,
        hideOverlappingLabels: true,
        style: {
          fontSize: '11px',
          colors: '#6B7280',
        },
      },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        formatter: (val: number) => `${Math.round(val)}${unit}`,
        style: {
          fontSize: '11px',
          colors: '#6B7280',
        },
      },
    },
    tooltip: {
      enabled: true,
      shared: true,
      intersect: false,
      theme: 'light',
      custom: function ({ series, seriesIndex, dataPointIndex, w }: any) {
        const seriesData = selectedVmDetail.value?.series || []
        const pt = seriesData[dataPointIndex] || {}
        const actualVal = series[0]?.[dataPointIndex]
        const forecastVal = series[1]?.[dataPointIndex]
        const timeHeader = pt.fullDate || pt.timeLabel || categories.value[dataPointIndex] || ''
        const metricLabel = metricOptions.find((m) => m.id === chartMetric.value)?.label || 'Usage'
        const isBottleneck = pt.isBottleneck || (Number(actualVal) >= 85)
        const isNight = pt.isNightWindow

        return `
          <div style="background:#ffffff; color:#111827; padding:12px 14px; border-radius:12px; border:1px solid #E5E7EB; box-shadow:0 10px 25px -5px rgba(0,0,0,0.1),0 8px 10px -6px rgba(0,0,0,0.1); font-family:Outfit,sans-serif; min-width:220px;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid #F3F4F6;">
              <span style="font-size:11px; font-weight:700; color:#374151;">${timeHeader}</span>
              ${
                isBottleneck
                  ? `<span style="font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; background:#FEE2E2; color:#B91C1C;">Bottleneck</span>`
                  : isNight
                  ? `<span style="font-size:10px; font-weight:600; padding:2px 6px; border-radius:4px; background:#EFF6FF; color:#1D4ED8;">Off-Hours</span>`
                  : ''
              }
            </div>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="display:flex; align-items:center; gap:6px; font-size:12px; color:#4B5563;">
                  <span style="width:10px; height:10px; border-radius:50%; background:#465FFF; display:inline-block;"></span>
                  Actual ${metricLabel}
                </span>
                <span style="font-size:12px; font-weight:700; font-family:monospace; color:#111827;">${actualVal !== undefined ? actualVal : '--'}${unit}</span>
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="display:flex; align-items:center; gap:6px; font-size:12px; color:#4B5563;">
                  <span style="width:10px; height:10px; border-radius:50%; background:#F59E0B; display:inline-block;"></span>
                  AI Forecast
                </span>
                <span style="font-size:12px; font-weight:700; font-family:monospace; color:#D97706;">${forecastVal !== undefined ? forecastVal : '--'}${unit}</span>
              </div>
            </div>
          </div>
        `
      },
    },
    legend: {
      show: false,
    },
  }
})
</script>
