import { ref, computed } from 'vue'
import {
  isSupabaseConfigured,
  supabaseSignIn,
  supabaseSignUp,
  supabaseSignOut,
  syncUserAccountToSupabase,
  saveVmToSupabase,
  loadVmsFromSupabase,
} from '@/lib/supabase'

export const API_BASE = 'http://localhost:8000'

export interface CustomerProfile {
  id: string
  name: string
  email: string
  role: string
  customerId: string
  customerName: string
  company: string
  primaryRegion: string
  subscriptionId: string
  budgetLimit: number
  vmCount: number
}

export const CUSTOMER_PROFILES: Record<string, CustomerProfile> = {
  'cust-superadmin': {
    id: 'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    name: 'Super Admin',
    email: 'admin@smartcloud.com',
    role: 'FinOps Administrator (Super Admin)',
    customerId: 'cust-superadmin',
    customerName: 'SmartCloud Multi-Tenant HQ',
    company: 'SmartCloud Platform Lead',
    primaryRegion: 'Global Multi-Tenant',
    subscriptionId: 'sub-az-superadmin-root',
    budgetLimit: 500000,
    vmCount: 10,
  },
  'cust-northwind': {
    id: 'cust-northwind',
    name: 'Adarsh (FinOps Lead)',
    email: 'adarsh@northwindlogistics.com',
    role: 'Customer Cloud FinOps Lead',
    customerId: 'cust-northwind',
    customerName: 'Northwind Logistics SaaS',
    company: 'Northwind Logistics SaaS',
    primaryRegion: 'East US / Central India',
    subscriptionId: 'sub-az-9844-3101-prod',
    budgetLimit: 75000,
    vmCount: 4,
  },
  'cust-contoso': {
    id: 'cust-contoso',
    name: 'Dr. Sarah Lin',
    email: 'sarah@contosohealth.com',
    role: 'Customer Infrastructure Director',
    customerId: 'cust-contoso',
    customerName: 'Contoso HealthTech',
    company: 'Contoso Healthcare Systems',
    primaryRegion: 'West US 2 (Washington)',
    subscriptionId: 'sub-az-1102-4498-hipaa',
    budgetLimit: 160000,
    vmCount: 3,
  },
  'cust-fabrikam': {
    id: 'cust-fabrikam',
    name: 'Alex Vance',
    email: 'alex@fabrikamretail.com',
    role: 'Customer Director of Cloud',
    customerId: 'cust-fabrikam',
    customerName: 'Fabrikam Retail Inc.',
    company: 'Fabrikam Omnichannel Retail',
    primaryRegion: 'West Europe (Amsterdam)',
    subscriptionId: 'sub-az-8732-5510-retail',
    budgetLimit: 90000,
    vmCount: 3,
  },
  'cust-docker': {
    id: 'cust-docker',
    name: "Friend's Docker Host",
    email: 'friend@docker-model-vm.local',
    role: 'Remote Docker Virtualization Host',
    customerId: 'cust-docker',
    customerName: "Friend's Docker Model VM",
    company: "Docker Container Virtualization Host",
    primaryRegion: "Remote Host (Friend's Laptop)",
    subscriptionId: "sub-docker-model-laptop",
    budgetLimit: 50000,
    vmCount: 3,
  },
}

export const AUTH_STORAGE_KEY = 'smartcloud_session_auth'

function getSavedSession(): CustomerProfile | null {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const saved = localStorage.getItem(AUTH_STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        const matched = CUSTOMER_PROFILES[parsed.customerId || parsed.id]
        return matched || parsed
      }
    }
  } catch (err) {
    console.warn('Failed reading saved auth from localStorage', err)
  }
  return null
}

const savedProfile = getSavedSession()

function createFallbackSeries(range: string = '7d', gran: string = '30m', vm?: any) {
  const pts = []
  const count =
    range === '1d'
      ? gran === '10m'
        ? 96
        : gran === '1h'
        ? 24
        : 48
      : range === '7d'
      ? gran === '10m'
        ? 112
        : 84
      : 30

  const now = new Date()
  const baseCpu = vm?.cpuUsage ?? 44.5
  const baseRam = vm?.ramUsage ?? 54.0
  const baseDisk = vm?.diskUsage ?? 1200
  const stepMs =
    range === '30d'
      ? 86400000
      : range === '7d'
      ? gran === '10m'
        ? 5400000
        : 7200000
      : gran === '10m'
      ? 900000
      : gran === '1h'
      ? 3600000
      : 1800000

  for (let i = 0; i < count; i++) {
    const d = new Date(now.getTime() - (count - 1 - i) * stepMs)
    const timeLabel =
      range === '30d'
        ? d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        : range === '7d'
        ? d.toLocaleDateString('en-US', { weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false })
        : d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })

    const cpu = Math.round(Math.max(5, Math.min(99, baseCpu + Math.sin(i / 3) * 12)))
    const ram = Math.round(Math.max(15, Math.min(98, baseRam + Math.cos(i / 4) * 6)))
    const disk = Math.round(Math.max(100, baseDisk + Math.sin(i / 2) * 200))

    pts.push({
      timestamp: d.toISOString(),
      timeLabel,
      fullDate: d.toLocaleString(),
      cpu,
      predictedCpu: Math.round(Math.min(99, cpu + 2)),
      ram,
      predictedRam: Math.round(Math.min(98, ram + 1.5)),
      memory: ram,
      predictedMemory: Math.round(Math.min(98, ram + 1.5)),
      disk,
      predictedDisk: disk + 50,
      isNightWindow: d.getHours() >= 19 || d.getHours() < 5,
      isBottleneck: cpu > 85,
    })
  }
  return pts
}

function createInitialLiveSeries(vm?: any) {
  const now = new Date()
  const baseCpu = vm?.cpuUsage ?? 11.8
  const baseRam = vm?.ramUsage ?? 23.5
  const baseDisk = vm?.diskUsage ?? 24
  return [
    {
      timestamp: new Date(now.getTime() - 10000).toISOString(),
      timeLabel: new Date(now.getTime() - 10000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
      fullDate: new Date(now.getTime() - 10000).toLocaleString(),
      cpu: Math.max(5, Number((baseCpu - 3.3).toFixed(1))),
      predictedCpu: Math.max(5, Number((baseCpu - 2.8).toFixed(1))),
      ram: Math.max(10, Number((baseRam - 2.5).toFixed(1))),
      predictedRam: Math.max(10, Number((baseRam - 1.5).toFixed(1))),
      memory: Math.max(10, Number((baseRam - 2.5).toFixed(1))),
      predictedMemory: Math.max(10, Number((baseRam - 1.5).toFixed(1))),
      disk: Math.max(5, baseDisk - 6),
      predictedDisk: baseDisk,
      isNightWindow: false,
      isBottleneck: false,
      isLiveTick: true,
    },
    {
      timestamp: new Date(now.getTime() - 5000).toISOString(),
      timeLabel: new Date(now.getTime() - 5000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
      fullDate: new Date(now.getTime() - 5000).toLocaleString(),
      cpu: Math.max(5, Number((baseCpu + 2.4).toFixed(1))),
      predictedCpu: Math.max(5, Number((baseCpu + 2.7).toFixed(1))),
      ram: Math.max(10, Number((baseRam - 0.3).toFixed(1))),
      predictedRam: Math.max(10, Number((baseRam + 0.5).toFixed(1))),
      memory: Math.max(10, Number((baseRam - 0.3).toFixed(1))),
      predictedMemory: Math.max(10, Number((baseRam + 0.5).toFixed(1))),
      disk: Math.max(5, baseDisk + 8),
      predictedDisk: baseDisk + 11,
      isNightWindow: false,
      isBottleneck: false,
      isLiveTick: true,
    },
    {
      timestamp: now.toISOString(),
      timeLabel: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
      fullDate: now.toLocaleString(),
      cpu: baseCpu,
      predictedCpu: Math.round((baseCpu + 0.5) * 10) / 10,
      ram: baseRam,
      predictedRam: Math.round((baseRam + 0.5) * 10) / 10,
      memory: baseRam,
      predictedMemory: Math.round((baseRam + 0.5) * 10) / 10,
      disk: baseDisk,
      predictedDisk: baseDisk + 4,
      isNightWindow: false,
      isBottleneck: false,
      isLiveTick: true,
    },
  ]
}

let liveStreamInterval: any = null

function startLiveTelemetryStream() {
  if (liveStreamInterval) return
  liveStreamInterval = setInterval(async () => {
    if (!selectedVmDetail.value) return
    const vmId = selectedVmDetail.value.id
    try {
      const res = await fetch(`${API_BASE}/api/vm/${vmId}/live-tick`)
      if (res.ok) {
        const data = await res.json()
        const tick = data.tick
        if (selectedVmDetail.value && selectedVmDetail.value.id === vmId) {
          const s = selectedVmDetail.value.series ? [...selectedVmDetail.value.series, tick] : [tick]
          if (s.length > 50) s.shift()
          selectedVmDetail.value.series = s
          selectedVmDetail.value.cpuUsage = data.current.cpu
          selectedVmDetail.value.ramUsage = data.current.ram
          selectedVmDetail.value.diskUsage = data.current.disk
          if (data.vmStatus) {
            selectedVmDetail.value.status = data.vmStatus
          }
          if (data.current.cores) {
            selectedVmDetail.value.cores = data.current.cores
            if (selectedVmDetail.value.specs) selectedVmDetail.value.specs.cores = data.current.cores
          }
          if (data.current.ramGb) {
            selectedVmDetail.value.ram = data.current.ramGb
            if (selectedVmDetail.value.specs) selectedVmDetail.value.specs.ramGb = data.current.ramGb
          }

          const target = vms.value.find((v) => v.id === vmId)
          if (target) {
            target.cpuUsage = data.current.cpu
            target.ramUsage = data.current.ram
            target.diskUsage = data.current.disk
            target.series = s
            if (data.vmStatus) target.status = data.vmStatus
            if (data.current.cores) {
              target.cores = data.current.cores
              if (target.specs) target.specs.cores = data.current.cores
            }
            if (data.current.ramGb) {
              target.ram = data.current.ramGb
              if (target.specs) target.specs.ramGb = data.current.ramGb
            }
          }
        }
        return
      }
    } catch {
      // offline fallback
    }

    if (selectedVmDetail.value && selectedVmDetail.value.id === vmId) {
      const now = new Date()
      const lastCpu = selectedVmDetail.value.cpuUsage || 11.8
      const lastRam = selectedVmDetail.value.ramUsage || 23.5
      const newCpu = Math.round(Math.max(5, Math.min(95, lastCpu + (Math.random() * 2.4 - 1.2))) * 10) / 10
      const newRam = Math.round(Math.max(10, Math.min(90, lastRam + (Math.random() * 0.8 - 0.4))) * 10) / 10
      const newDisk = Math.round(Math.max(10, Math.min(100, 24 + (Math.random() * 10 - 4))))

      const tick = {
        timestamp: now.toISOString(),
        timeLabel: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
        fullDate: now.toLocaleString(),
        cpu: newCpu,
        predictedCpu: Math.round((newCpu + 1.0) * 10) / 10,
        ram: newRam,
        memory: newRam,
        predictedRam: Math.round((newRam + 1.0) * 10) / 10,
        predictedMemory: Math.round((newRam + 1.0) * 10) / 10,
        disk: newDisk,
        predictedDisk: newDisk + 4,
        network: Math.round((14 + Math.random() * 5) * 10) / 10,
        isNightWindow: false,
        isBottleneck: false,
        isLiveTick: true,
      }

      const s = selectedVmDetail.value.series ? [...selectedVmDetail.value.series, tick] : [tick]
      if (s.length > 50) s.shift()
      selectedVmDetail.value.series = s
      selectedVmDetail.value.cpuUsage = newCpu
      selectedVmDetail.value.ramUsage = newRam
      selectedVmDetail.value.diskUsage = newDisk

      const target = vms.value.find((v) => v.id === vmId)
      if (target) {
        target.cpuUsage = newCpu
        target.ramUsage = newRam
        target.diskUsage = newDisk
        target.series = s
      }
    }
  }, 2500)
}

// Global Singletons so state persists across routes and components
const isLoggedIn = ref(!!savedProfile)
const currentCustomer = ref<CustomerProfile>(savedProfile || CUSTOMER_PROFILES['cust-northwind'])
const vms = ref<any[]>([])
const selectedVmId = ref<string>('')
const selectedVmDetail = ref<any>(null)
const timeRange = ref<'1d' | '7d' | '30d'>('7d')
const granularity = ref<string>('30m')
const chartMetric = ref<'cpu' | 'ram' | 'disk'>('cpu')
const currency = ref<'INR' | 'USD'>('INR')
const toastMessage = ref<string>('')
const nightHoursWindow = ref<number>(10) // 7 PM - 5 AM off-hours
const isLoading = ref<boolean>(false)
const dockerHost = ref<string>('http://localhost:8001')
const dockerConnected = ref<boolean>(false)
const dockerHostInfo = ref<any>({})
const dockerContainers = ref<any[]>([])

export const isSuperAdmin = computed(() => {
  const email = currentCustomer.value?.email?.toLowerCase().trim() || ''
  const role = currentCustomer.value?.role?.toLowerCase() || ''
  const cid = currentCustomer.value?.customerId || ''
  return (
    email === 'admin@smartcloud.com' ||
    email === 'adarsh@northwindlogistics.com' ||
    email.includes('superadmin') ||
    email.startsWith('admin@') ||
    role.includes('super admin') ||
    role.includes('finops administrator') ||
    cid === 'cust-superadmin'
  )
})

export function useFinOps() {
  const fxRate = computed(() => (currency.value === 'INR' ? 1 : 0.012))
  const currencySymbol = computed(() => (currency.value === 'INR' ? '₹' : '$'))

  const formatAmount = (inrVal: number = 0) => {
    const val = (inrVal || 0) * fxRate.value
    if (currency.value === 'INR') {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }).format(val)
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val)
  }

  const showToast = (msg: string) => {
    toastMessage.value = msg
    setTimeout(() => {
      toastMessage.value = ''
    }, 3500)
  }

  // Load VM Fleet
  const loadFleet = async (
    custId: string = currentCustomer.value.customerId,
    forceAdmin: boolean = false,
    userId?: string
  ) => {
    isLoading.value = true
    try {
      const adminActive = forceAdmin || isSuperAdmin.value || custId === 'cust-superadmin' || custId === 'all'
      const uid = userId || currentCustomer.value.id || custId

      // 1. Try loading from Supabase cloud database
      if (isSupabaseConfigured) {
        try {
          const supaVms = await loadVmsFromSupabase(uid, adminActive)
          if (supaVms && supaVms.length > 0) {
            vms.value = supaVms
            currentCustomer.value.vmCount = supaVms.length
            selectedVmId.value = supaVms[0].id
            await loadVmDetails(supaVms[0].id, timeRange.value, granularity.value)
            startLiveTelemetryStream()
            return
          }
        } catch (e) {
          console.warn('Supabase fleet load error:', e)
        }
      }

      // 2. Fetch from Backend persistent API
      const endpoint = adminActive
        ? `${API_BASE}/api/vms?isSuperAdmin=true`
        : `${API_BASE}/api/vms?customerId=${custId}&userId=${uid}`

      const res = await fetch(endpoint)
      if (res.ok) {
        const data = await res.json()
        const fleetList = data.vms || []
        vms.value = fleetList
        currentCustomer.value.vmCount = fleetList.length
        if (fleetList.length > 0) {
          const firstId = fleetList[0].id
          selectedVmId.value = firstId
          await loadVmDetails(firstId, timeRange.value, granularity.value)
          startLiveTelemetryStream()
        } else {
          selectedVmDetail.value = null
        }
        try {
          localStorage.setItem(`smartcloud_vms_${custId}`, JSON.stringify(fleetList))
        } catch (e) {
          console.warn('LocalStorage save error:', e)
        }
        return
      }

      // 3. Fallback to localStorage if backend and supabase are offline
      const userFleetKey = `smartcloud_vms_${custId}`
      if (typeof window !== 'undefined' && window.localStorage) {
        const saved = localStorage.getItem(userFleetKey)
        if (saved) {
          try {
            const parsed = JSON.parse(saved)
            if (Array.isArray(parsed) && parsed.length > 0) {
              vms.value = parsed
              currentCustomer.value.vmCount = parsed.length
              selectedVmId.value = parsed[0].id
              await loadVmDetails(parsed[0].id, timeRange.value, granularity.value)
              return
            }
          } catch (e) {
            console.warn('Fleet cache parse error', e)
          }
        }
      }
    } catch (err) {
      console.warn('Backend unavailable or network error', err)
    } finally {
      isLoading.value = false
    }
  }

  // Load VM Details & Telemetry Series
  const loadVmDetails = async (
    vmId: string = selectedVmId.value,
    range: string = timeRange.value,
    gran: string = granularity.value
  ) => {
    if (!vmId) return
    try {
      const res = await fetch(`${API_BASE}/api/vm/${vmId}?range=${range}&granularity=${gran}`)
      if (res.ok) {
        const data = await res.json()
        selectedVmDetail.value = data.vm
        return
      }
    } catch (err) {
      console.warn('Could not load VM telemetry series from backend, using fallback series generator', err)
    }

    const found = vms.value.find((v) => v.id === vmId)
    if (found) {
      if (found.isNew) {
        selectedVmDetail.value = {
          ...found,
          hasHistoricalData: false,
          series: found.series && found.series.length > 0 ? found.series : createInitialLiveSeries(found),
        }
      } else {
        selectedVmDetail.value = {
          ...found,
          series: createFallbackSeries(range, gran, found),
        }
      }
    }
  }

  // Select VM
  const selectVm = async (vmId: string) => {
    selectedVmId.value = vmId
    await loadVmDetails(vmId, timeRange.value, granularity.value)
    startLiveTelemetryStream()
    showToast(`Inspecting ${selectedVmDetail.value?.name || vmId}`)
  }

  // Range and Granularity changes
  const setRangeAndGranularity = async (newRange: '1d' | '7d' | '30d') => {
    timeRange.value = newRange
    if (newRange === '30d') {
      granularity.value = '1d'
    } else if (granularity.value === '1d') {
      granularity.value = '30m'
    }
    await loadVmDetails(selectedVmId.value, timeRange.value, granularity.value)
  }

  const setSpecificGranularity = async (newGran: string) => {
    granularity.value = newGran
    await loadVmDetails(selectedVmId.value, timeRange.value, granularity.value)
  }

  // Toggle Auto-scale Permission for a single VM
  const toggleAutoScale = async (vmId: string, enabled: boolean) => {
    vms.value = vms.value.map((v) => {
      if (v.id === vmId) {
        const updatedSpend = enabled
          ? v.recommendation?.type === 'downsize'
            ? v.currentSpend - v.savings
            : v.currentSpend + 2330
          : v.currentSpend
        return {
          ...v,
          autoScaleEnabled: enabled,
          projectedSpend: updatedSpend,
        }
      }
      return v
    })

    if (selectedVmDetail.value && selectedVmDetail.value.id === vmId) {
      selectedVmDetail.value = {
        ...selectedVmDetail.value,
        autoScaleEnabled: enabled,
        projectedSpend: enabled
          ? selectedVmDetail.value.recommendation?.type === 'downsize'
            ? selectedVmDetail.value.currentSpend - selectedVmDetail.value.savings
            : selectedVmDetail.value.currentSpend + 2330
          : selectedVmDetail.value.currentSpend,
      }
    }

    try {
      await fetch(`${API_BASE}/api/vm/${vmId}/autoscale`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      })
      showToast(
        enabled
          ? `Auto-scaling authorized for ${vmId}. Dynamic prorated terms active.`
          : `Auto-scaling disabled for ${vmId}. Manual approval mode active.`
      )
    } catch (err) {
      console.warn('Could not post autoscale update', err)
    }
  }

  // Switch Customer Context
  const switchCustomer = async (newCustomerId: string) => {
    const prof = CUSTOMER_PROFILES[newCustomerId] || CUSTOMER_PROFILES['cust-northwind']
    currentCustomer.value = prof
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(prof))
    } catch (err) {
      console.warn('Could not update session in localStorage', err)
    }
    await loadFleet(prof.customerId)
    showToast(`Switched customer context to ${prof.customerName}`)
  }

  // Login
  const login = async (customerIdKey: string = 'cust-northwind') => {
    const key = customerIdKey.startsWith('cust-') ? customerIdKey : `cust-${customerIdKey}`
    const prof = CUSTOMER_PROFILES[key] || CUSTOMER_PROFILES['cust-northwind']
    currentCustomer.value = prof
    isLoggedIn.value = true
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(prof))
    } catch (err) {
      console.warn('Could not save session to localStorage', err)
    }
    await loadFleet(prof.customerId)
    showToast(`Welcome back, ${prof.name}! Accessing ${prof.customerName} resource portal.`)
  }

  // Supabase Authentication
  const loginWithSupabase = async (emailInput: string, passwordInput: string) => {
    isLoading.value = true
    try {
      if (isSupabaseConfigured) {
        const result = await supabaseSignIn(emailInput, passwordInput)
        if (!result.success) {
          showToast(`Supabase: ${result.error}`)
          return { success: false, error: result.error }
        }
        const user = result.user
        const trimmedEmail = emailInput.trim().toLowerCase()
        const isAdmin =
          trimmedEmail === 'admin@smartcloud.com' ||
          trimmedEmail === 'adarsh@northwindlogistics.com' ||
          trimmedEmail.includes('superadmin') ||
          trimmedEmail.startsWith('admin@') ||
          user.user_metadata?.role === 'super_admin'

        const companyName = user.user_metadata?.company || user.user_metadata?.customer_name || 'My Cloud Enterprise'
        const customerId = isAdmin ? 'cust-superadmin' : `cust-${user.id.substring(0, 8)}`

        const customProf: CustomerProfile = {
          id: user.id,
          name: isAdmin ? 'Super Admin' : (user.user_metadata?.full_name || emailInput.split('@')[0]),
          email: user.email || emailInput,
          role: isAdmin ? 'FinOps Administrator (Super Admin)' : 'Customer Cloud Lead',
          customerId,
          customerName: isAdmin ? 'SmartCloud Multi-Tenant HQ' : companyName,
          company: isAdmin ? 'SmartCloud Platform Lead' : companyName,
          primaryRegion: isAdmin ? 'Global Multi-Tenant' : 'East US / Central India',
          subscriptionId: isAdmin ? 'sub-az-superadmin-root' : `sub-az-${user.id.substring(0, 8)}`,
          budgetLimit: isAdmin ? 500000 : 50000,
          vmCount: 0,
        }

        CUSTOMER_PROFILES[customProf.customerId] = customProf
        currentCustomer.value = customProf
        isLoggedIn.value = true
        try {
          localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(customProf))
        } catch (e) {
          console.warn('Storage error', e)
        }

        // Load fleet - if admin, loads ALL VMs across all customer accounts!
        await loadFleet(customProf.customerId, isAdmin, user.id)

        // Sync credentials and assigned VMs into Supabase user_accounts table and backend for monitoring
        await syncUserAccountToSupabase({
          userId: user.id,
          email: user.email || emailInput,
          password: passwordInput,
          customerName: customProf.customerName,
          company: customProf.company,
          role: customProf.role,
          assignedVms: vms.value.map((v) => ({
            id: v.id,
            name: v.name,
            size: v.size,
            cores: v.cores,
            ram: v.ram,
            status: v.status,
            spend: v.currentSpend,
          })),
        })

        showToast(
          isAdmin
            ? 'Super Admin Mode Active: Full cross-tenant visibility enabled.'
            : currentCustomer.value.vmCount > 0
            ? `Welcome back, ${customProf.name}!`
            : `Welcome, ${customProf.name}! Select a cloud VM plan to provision your resources.`
        )
        return { success: true, user }
      } else {
        await login('cust-northwind')
        showToast('Demo Mode: Supabase not configured in .env. Signed in with demo profile.')
        return { success: true, demo: true }
      }
    } finally {
      isLoading.value = false
    }
  }

  // Provision / Buy a Virtual Machine for the customer
  const provisionVm = async (
    planId: 'starter' | 'business' | 'enterprise' = 'business',
    customName?: string,
    region: string = 'East US / Central India'
  ) => {
    isLoading.value = true
    const cid = currentCustomer.value.customerId
    const company = currentCustomer.value.company || 'cloud'
    const slug = company.toLowerCase().replace(/[^a-z0-9]/g, '') || 'vm'
    const defaultName = `${slug}-${planId}-01`
    const vmName = customName || defaultName

    // Generate random unique VM ID
    const randomVmId = `vm-${cid.replace('cust-', '').slice(0, 5)}-${Math.random().toString(36).substring(2, 7)}`

    let newVm: any = null

    try {
      const res = await fetch(`${API_BASE}/api/vms/provision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customerId: cid,
          planId,
          vmName,
          region,
          autoScaleEnabled: true,
          userId: currentCustomer.value.id || cid,
          customerName: currentCustomer.value.customerName,
          email: currentCustomer.value.email,
          vmId: randomVmId,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        newVm = data.vm
      }
    } catch (err) {
      console.warn('Provision backend call error, falling back to local creation', err)
    }

    if (!newVm) {
      const cores = planId === 'starter' ? 2 : planId === 'enterprise' ? 8 : 4
      const ram = planId === 'starter' ? 4 : planId === 'enterprise' ? 64 : 16
      const storage = planId === 'starter' ? 64 : planId === 'enterprise' ? 256 : 128
      const maxIops = planId === 'starter' ? 1280 : planId === 'enterprise' ? 12800 : 6400
      const sku =
        planId === 'starter'
          ? 'Standard_B2s'
          : planId === 'enterprise'
          ? 'Standard_E8s_v5'
          : 'Standard_D4s_v5'
      const spend = planId === 'starter' ? 1850 : planId === 'enterprise' ? 18200 : 7400
      const projSpend = planId === 'starter' ? 1200 : planId === 'enterprise' ? 20500 : 5200

      newVm = {
        id: randomVmId,
        name: vmName,
        customerId: cid,
        customerName: currentCustomer.value.customerName,
        userId: currentCustomer.value.id || cid,
        status: 'Healthy',
        region,
        resourceGroup: `rg-${cid.slice(0, 8)}-prod`,
        vmSize: sku,
        size: sku,
        os: 'Ubuntu Linux 22.04 LTS',
        ip: `20.84.112.${vms.value.length + 15}`,
        privateIp: `10.50.1.${vms.value.length + 10}`,
        cores,
        ram,
        storage,
        maxIops,
        bandwidth: cores * 1000,
        hourlyRate: planId === 'starter' ? 2.56 : planId === 'enterprise' ? 25.27 : 10.27,
        currentSpend: spend,
        projectedSpend: projSpend,
        savings: spend - projSpend,
        autoScaleEnabled: true,
        cpuUsage: 11.8,
        ramUsage: 23.5,
        diskUsage: Math.round(maxIops * 0.28),
        recommendation: {
          type: 'nominal',
          title: `FinOps Live Baseline Calibration for ${vmName}`,
          reason: `Node newly deployed under ${currentCustomer.value.customerName}. Live telemetry stream active.`,
          formula: `10 off-hours/day × 30 days = ₹${spend - projSpend} monthly savings`,
          steps: [
            { label: 'Provisioned Baseline', value: `₹${spend.toLocaleString()}/mo` },
            {
              label: 'Night Standby Target',
              value: `${Math.max(1, cores / 2)} vCPU / ${Math.max(2, ram / 2)} GB`,
            },
            { label: 'Projected Net Spend', value: `₹${projSpend.toLocaleString()}/mo` },
          ],
        },
      }
    }

    // Newly provisioned VMs do NOT have past historical data; only live streaming telemetry
    newVm.isNew = true
    newVm.hasHistoricalData = false
    newVm.uptime = 'Live (< 1m uptime)'
    newVm.mtdSpend = 0
    newVm.cpuUsage = newVm.cpuUsage ?? 11.8
    newVm.ramUsage = newVm.ramUsage ?? 23.5
    newVm.diskUsage = newVm.diskUsage ?? 24
    if (!newVm.series || newVm.series.length === 0 || !newVm.series[0]?.isLiveTick) {
      newVm.series = createInitialLiveSeries(newVm)
    }

    startLiveTelemetryStream()

    // Append to customer fleet
    vms.value = [...vms.value, newVm]
    selectedVmId.value = newVm.id
    selectedVmDetail.value = newVm
    currentCustomer.value.vmCount = vms.value.length

    // Save to Supabase public.vms table
    await saveVmToSupabase(newVm, currentCustomer.value.id || cid, currentCustomer.value.customerName)

    // Sync to user_accounts table & Supabase auth metadata for monitoring
    await syncUserAccountToSupabase({
      userId: currentCustomer.value.id || cid,
      email: currentCustomer.value.email || '',
      customerName: currentCustomer.value.customerName,
      company: currentCustomer.value.company,
      role: currentCustomer.value.role,
      assignedVms: vms.value.map((v) => ({
        id: v.id,
        name: v.name,
        size: v.size,
        cores: v.cores,
        ram: v.ram,
        status: v.status,
        spend: v.currentSpend,
      })),
    })

    // Persist to user's fleet key in localStorage
    try {
      const userFleetKey = `smartcloud_vms_${cid}`
      localStorage.setItem(userFleetKey, JSON.stringify(vms.value))
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(currentCustomer.value))
    } catch (e) {
      console.warn('Failed saving fleet to storage', e)
    }

    isLoading.value = false
    showToast(`VM "${vmName}" provisioned successfully! Random ID: ${newVm.id}`)
    return newVm
  }

  const signupWithSupabase = async (emailInput: string, passwordInput: string, metadata: any = {}) => {
    isLoading.value = true
    try {
      if (isSupabaseConfigured) {
        const result = await supabaseSignUp(emailInput, passwordInput, metadata)
        if (!result.success) {
          showToast(`Supabase: ${result.error}`)
          return { success: false, error: result.error }
        }
        showToast('Registration successful! Signing you in...')
        return await loginWithSupabase(emailInput, passwordInput)
      } else {
        showToast('Supabase credentials required in frontend/.env for cloud registration.')
        return { success: false, error: 'Supabase credentials missing in .env' }
      }
    } finally {
      isLoading.value = false
    }
  }

  // Connect Friend's Docker Host - Adds Docker container directly into active customer's fleet
  const connectDocker = async (hostUrl: string = dockerHost.value) => {
    isLoading.value = true
    dockerHost.value = hostUrl
    const currentCustId = currentCustomer.value.customerId
    try {
      const res = await fetch(`${API_BASE}/api/docker/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ host: hostUrl, customerId: currentCustId }),
      })
      if (res.ok) {
        const data = await res.json()
        dockerConnected.value = data.connected
        dockerContainers.value = data.containers || []
        dockerHostInfo.value = data.hostInfo || {}

        // Invalidate stale local cache key so fresh combined fleet is loaded from backend
        const userFleetKey = `smartcloud_vms_${currentCustId}`
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.removeItem(userFleetKey)
        }

        // DO NOT overwrite or delete the current user profile with cust-docker!
        // Instead, reload the active user's fleet with the newly attached Docker VM(s)
        await loadFleet(currentCustId)

        // Auto-select the newly added Docker container VM if found
        const attachedDockerVm = vms.value.find((v: any) => v.id.startsWith('docker-'))
        if (attachedDockerVm) {
          selectedVmId.value = attachedDockerVm.id
          await loadVmDetails(attachedDockerVm.id, timeRange.value, granularity.value)
        }

        showToast(data.message || `Docker container attached to ${currentCustomer.value.customerName}`)
        return { success: true, connected: data.connected, count: data.containersCount }
      }
    } catch (err: any) {
      console.warn('Docker connect error:', err)
      showToast(`Could not reach Docker host at ${hostUrl}`)
    } finally {
      isLoading.value = false
    }
    return { success: false, connected: false }
  }

  // Apply Scheduled Turn-Off / Rightsizing Policy to Selected VM
  const applyVmSchedulePolicy = async (payload: {
    vm_id: string
    action: string
    off_hours_duration: number
    start_time: string
    end_time: string
    days_mode: string
    weekend_shutdown: boolean
    simulated_monthly_savings: number
  }) => {
    try {
      const res = await fetch(`${API_BASE}/api/vm/${payload.vm_id}/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (res.ok) {
        const data = await res.json()
        showToast(data.message)
        const userFleetKey = `smartcloud_vms_${currentCustomer.value.customerId}`
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.removeItem(userFleetKey)
        }
        await loadFleet(currentCustomer.value.customerId)
        return { success: true }
      }
    } catch (err: any) {
      showToast('Failed to apply schedule: ' + err.message)
    }
    return { success: false }
  }

  const scaleDockerContainer = async (cid: string, cpus: number, memory: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/docker/scale`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ containerId: cid, cpus, memory }),
      })
      if (res.ok) {
        const data = await res.json()
        showToast(data.message)
        await loadFleet(currentCustomer.value?.id || 'cust-northwind')
        return { success: true, message: data.message }
      }
    } catch (err) {
      console.warn('Docker scale error:', err)
    }
    return { success: false }
  }

  // Logout
  const logout = async () => {
    isLoggedIn.value = false
    try {
      await supabaseSignOut()
      localStorage.removeItem(AUTH_STORAGE_KEY)
    } catch (err) {
      console.warn('Could not remove session from localStorage', err)
    }
    vms.value = []
    selectedVmDetail.value = null
    showToast('Signed out of SmartCloud Optimizer console.')
  }

  // Totals & Computed Metrics
  const totalCurrentSpend = computed(() => {
    return vms.value.reduce((acc, v) => acc + (v.currentSpend || 0), 0)
  })

  const totalProjectedSpend = computed(() => {
    return vms.value.reduce((acc, v) => acc + (v.projectedSpend || v.currentSpend || 0), 0)
  })

  const totalSavings = computed(() => {
    return Math.max(0, totalCurrentSpend.value - totalProjectedSpend.value)
  })

  const savingsPercentage = computed(() => {
    if (totalCurrentSpend.value === 0) return '0.0'
    return ((totalSavings.value / totalCurrentSpend.value) * 100).toFixed(1)
  })

  const bottleneckCount = computed(() => {
    return vms.value.filter(
      (v) => (v.status === 'Bottleneck Warning' || v.cpuUsage >= 80 || v.ramUsage >= 85) && !v.isNew
    ).length
  })

  const autoScaleActiveCount = computed(() => {
    return vms.value.filter((v) => v.autoScaleEnabled).length
  })

  const notifications = computed(() => {
    return vms.value.map((vm) => {
      if (vm.isNew) {
        return {
          id: vm.id,
          vmName: vm.name,
          type: 'healthy',
          title: `Live Stream Active: ${vm.name}`,
          message: 'Node is newly provisioned. FinOps AI is collecting live baseline telemetry.',
          currentSpend: vm.currentSpend,
          projectedSpend: vm.projectedSpend,
          savings: 0,
          formula: 'Live Baseline Learning Mode',
          steps: [],
          timestamp: 'Just now',
        }
      }
      const isBottleneck =
        vm.status === 'Bottleneck Warning' || vm.cpuUsage >= 80 || vm.ramUsage >= 85
      return {
        id: vm.id,
        vmName: vm.name,
        type: isBottleneck ? 'bottleneck' : 'downsize',
        title: isBottleneck
          ? `Bottleneck Alert: ${vm.name}`
          : `Off-Hours Downscale Opportunity: ${vm.name}`,
        message: vm.recommendation?.reason || 'Predictive analysis recommends sizing adjustment.',
        currentSpend: vm.currentSpend,
        projectedSpend: vm.projectedSpend,
        savings: vm.savings || 0,
        formula: vm.recommendation?.formula,
        steps: vm.recommendation?.steps || [],
        timestamp: 'Just now',
      }
    })
  })

  return {
    isLoggedIn,
    currentCustomer,
    vms,
    selectedVmId,
    selectedVmDetail,
    timeRange,
    granularity,
    chartMetric,
    currency,
    currencySymbol,
    fxRate,
    toastMessage,
    nightHoursWindow,
    isLoading,
    totalCurrentSpend,
    totalProjectedSpend,
    totalSavings,
    savingsPercentage,
    bottleneckCount,
    autoScaleActiveCount,
    notifications,
    formatAmount,
    showToast,
    loadFleet,
    loadVmDetails,
    selectVm,
    setRangeAndGranularity,
    setSpecificGranularity,
    toggleAutoScale,
    switchCustomer,
    login,
    logout,
    // Role-based Access
    isSuperAdmin,
    provisionVm,
    // Supabase Auth
    isSupabaseConfigured,
    loginWithSupabase,
    signupWithSupabase,
    // Docker Model VM Hub
    dockerHost,
    dockerConnected,
    dockerHostInfo,
    dockerContainers,
    connectDocker,
    scaleDockerContainer,
    // VM Shutdown & Rightsizing Simulator
    applyVmSchedulePolicy,
  }
}
