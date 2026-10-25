import { createClient, SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

export const isSupabaseConfigured = Boolean(
  supabaseUrl &&
  supabaseAnonKey &&
  supabaseUrl !== 'https://your-project.supabase.co' &&
  !supabaseUrl.includes('your-project')
)

// Initialize client if credentials are provided
export const supabase: SupabaseClient | null = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : null

export interface SupabaseAuthResult {
  success: boolean
  user?: any
  error?: string
  session?: any
}

export async function supabaseSignIn(email: string, password: string): Promise<SupabaseAuthResult> {
  if (!supabase || !isSupabaseConfigured) {
    return {
      success: false,
      error: 'Supabase URL or Anon Key not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your frontend/.env file.',
    }
  }

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      return { success: false, error: error.message }
    }

    return {
      success: true,
      user: data.user,
      session: data.session,
    }
  } catch (err: any) {
    return { success: false, error: err.message || 'An unexpected error occurred during sign in.' }
  }
}

export async function supabaseSignUp(
  email: string,
  password: string,
  metadata: { fullName?: string; company?: string; role?: string } = {}
): Promise<SupabaseAuthResult> {
  if (!supabase || !isSupabaseConfigured) {
    return {
      success: false,
      error: 'Supabase URL or Anon Key not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your frontend/.env file.',
    }
  }

  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: metadata.fullName || email.split('@')[0],
          company: metadata.company || 'Enterprise Cloud Client',
          customer_name: metadata.company || 'Enterprise Cloud Client',
          role: metadata.role || 'customer',
          assigned_vms: [],
        },
      },
    })

    if (error) {
      return { success: false, error: error.message }
    }

    return {
      success: true,
      user: data.user,
      session: data.session,
    }
  } catch (err: any) {
    return { success: false, error: err.message || 'An unexpected error occurred during sign up.' }
  }
}

export async function supabaseSignOut(): Promise<void> {
  if (supabase && isSupabaseConfigured) {
    try {
      await supabase.auth.signOut()
    } catch (err) {
      console.warn('Supabase sign out warning:', err)
    }
  }
}

export async function getSupabaseUser(): Promise<any | null> {
  if (!supabase || !isSupabaseConfigured) return null
  try {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  } catch (err) {
    return null
  }
}

/**
 * Syncs user account details (including password and assigned VMs) to Supabase table,
 * Supabase Auth user_metadata, and the backend persistent store for monitoring.
 */
export async function syncUserAccountToSupabase(payload: {
  userId: string
  email: string
  password?: string
  customerName?: string
  company?: string
  role?: string
  assignedVms?: any[]
}) {
  // 1. Sync directly to Supabase Auth metadata so it is bound to the cloud auth record
  if (supabase && isSupabaseConfigured) {
    try {
      await supabase.auth.updateUser({
        data: {
          customer_name: payload.customerName,
          company: payload.company,
          role: payload.role,
          assigned_vms: payload.assignedVms || [],
        },
      })
    } catch (e) {
      console.warn('Supabase user metadata update notice:', e)
    }

    // 2. Upsert into Supabase public.user_accounts table (for easy DB monitoring)
    try {
      const { error } = await supabase.from('user_accounts').upsert(
        {
          user_id: payload.userId,
          email_id: payload.email,
          password: payload.password || '••••••••',
          assigned_vms: payload.assignedVms || [],
          role: payload.role || 'customer',
          customer_name: payload.customerName || 'Enterprise Customer',
          company: payload.company || 'Cloud Enterprise',
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'user_id' }
      )
      if (error) {
        console.warn('Supabase user_accounts table notice (run supabase_schema.sql if not created):', error.message)
      }
    } catch (e) {
      console.warn('Supabase user_accounts table sync error:', e)
    }
  }

  // 3. Sync to backend persistent store on disk (survives laptop reboots)
  try {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    await fetch(`${apiBase}/api/users/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: payload.userId,
        email_id: payload.email,
        password: payload.password || '',
        customer_name: payload.customerName || 'Enterprise Customer',
        company: payload.company || 'Cloud Enterprise',
        role: payload.role || 'customer',
        assigned_vms: payload.assignedVms || [],
      }),
    })
  } catch (e) {
    console.warn('Backend user sync error:', e)
  }
}

/**
 * Persists a provisioned VM into Supabase public.vms table.
 */
export async function saveVmToSupabase(vm: any, userId: string, customerName: string) {
  if (supabase && isSupabaseConfigured) {
    try {
      const { error } = await supabase.from('vms').upsert(
        {
          id: vm.id,
          user_id: userId,
          customer_id: vm.customerId,
          customer_name: customerName || vm.customerName,
          name: vm.name,
          vm_size: vm.vmSize || vm.size,
          specs: vm.specs || { cores: vm.cores, ramGb: vm.ram, storageGb: vm.storage },
          status: vm.status || 'Healthy',
          region: vm.region || 'East US / Central India',
          hourly_rate: vm.hourlyRate,
          current_spend: vm.currentSpend,
          projected_spend: vm.projectedSpend,
          savings: vm.savings,
          auto_scale_enabled: vm.autoScaleEnabled ?? true,
          is_new: vm.isNew ?? true,
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'id' }
      )
      if (error) {
        console.warn('Supabase vms table notice:', error.message)
      }
    } catch (e) {
      console.warn('Supabase vms table sync error:', e)
    }
  }
}

/**
 * Fetches VMs directly from Supabase public.vms table.
 */
export async function loadVmsFromSupabase(userId: string, isSuperAdmin: boolean = false): Promise<any[] | null> {
  if (!supabase || !isSupabaseConfigured) return null
  try {
    let query = supabase.from('vms').select('*')
    if (!isSuperAdmin) {
      query = query.eq('user_id', userId)
    }
    const { data, error } = await query
    if (error || !data) {
      return null
    }
    return data.map((row) => ({
      id: row.id,
      name: row.name,
      customerId: row.customer_id,
      customerName: row.customer_name,
      userId: row.user_id,
      status: row.status,
      region: row.region,
      vmSize: row.vm_size,
      size: row.vm_size,
      cores: row.specs?.cores || 4,
      ram: row.specs?.ramGb || 16,
      storage: row.specs?.storageGb || 256,
      maxIops: row.specs?.maxIops || 6400,
      bandwidth: (row.specs?.cores || 4) * 1000,
      hourlyRate: Number(row.hourly_rate),
      currentSpend: Number(row.current_spend),
      projectedSpend: Number(row.projected_spend),
      savings: Number(row.savings),
      autoScaleEnabled: row.auto_scale_enabled,
      isNew: row.is_new,
      cpuUsage: 18.5,
      ramUsage: 28.0,
      diskUsage: 24,
    }))
  } catch (e) {
    console.warn('Supabase table lookup error:', e)
    return null
  }
}

/**
 * Loads user monitoring table data from Supabase, fallback to backend.
 */
export async function loadUserMonitoringData(): Promise<any[]> {
  if (supabase && isSupabaseConfigured) {
    try {
      const { data, error } = await supabase
        .from('user_accounts')
        .select('*')
        .order('created_at', { ascending: false })
      if (!error && data && data.length > 0) {
        return data
      }
    } catch (e) {
      console.warn('Supabase user_accounts table lookup:', e)
    }
  }

  try {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const res = await fetch(`${apiBase}/api/users/monitoring`)
    if (res.ok) {
      const json = await res.json()
      return json.users || []
    }
  } catch (e) {
    console.warn('Backend user monitoring fetch error:', e)
  }
  return []
}
