-- =========================================================================
-- SmartCloud Optimizer - Supabase Production Schema & Monitoring Table
-- Run this in your Supabase Dashboard SQL Editor:
-- https://supabase.com/dashboard/project/odfdeuuyqxewzaaoambi/sql/new
-- =========================================================================

-- 1. Create User Accounts & Monitoring Table
CREATE TABLE IF NOT EXISTS public.user_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    email_id TEXT NOT NULL,
    password TEXT NOT NULL,
    assigned_vms JSONB DEFAULT '[]'::jsonb,
    role TEXT DEFAULT 'customer',
    customer_name TEXT DEFAULT 'Enterprise Customer',
    company TEXT DEFAULT 'Cloud Enterprise',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Virtual Machines Table
CREATE TABLE IF NOT EXISTS public.vms (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    customer_id TEXT,
    customer_name TEXT,
    name TEXT NOT NULL,
    vm_size TEXT,
    specs JSONB,
    status TEXT DEFAULT 'Healthy',
    region TEXT DEFAULT 'East US / Central India',
    hourly_rate NUMERIC DEFAULT 10.27,
    current_spend NUMERIC DEFAULT 7400,
    projected_spend NUMERIC DEFAULT 5200,
    savings NUMERIC DEFAULT 2200,
    auto_scale_enabled BOOLEAN DEFAULT true,
    is_new BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable Row Level Security (RLS) with open read/write policies for anon & authenticated roles
ALTER TABLE public.user_accounts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public full access to user_accounts" ON public.user_accounts;
CREATE POLICY "Public full access to user_accounts" ON public.user_accounts
    FOR ALL TO anon, authenticated
    USING (true)
    WITH CHECK (true);

ALTER TABLE public.vms ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public full access to vms" ON public.vms;
CREATE POLICY "Public full access to vms" ON public.vms
    FOR ALL TO anon, authenticated
    USING (true)
    WITH CHECK (true);

-- 4. Seed Super Admin Account in user_accounts table for monitoring
INSERT INTO public.user_accounts (user_id, email_id, password, role, customer_name, company, assigned_vms)
VALUES (
    'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    'admin@smartcloud.com',
    'Admin@123',
    'super_admin',
    'Super Admin Platform Lead',
    'SmartCloud Headquarters',
    '[
        {"id": "vm-web-prod", "name": "web-prod-01", "size": "Standard_D8s_v5", "cores": 8, "ram": 32, "status": "Healthy"},
        {"id": "vm-analytics", "name": "analytics-worker-02", "size": "Standard_E16s_v5", "cores": 16, "ram": 64, "status": "Bottleneck Warning"},
        {"id": "vm-batch", "name": "batch-processor-03", "size": "Standard_D4s_v5", "cores": 4, "ram": 16, "status": "Healthy"},
        {"id": "vm-api-gw", "name": "gateway-edge-04", "size": "Standard_D4s_v5", "cores": 4, "ram": 16, "status": "Healthy"}
    ]'::jsonb
)
ON CONFLICT (user_id) DO UPDATE SET
    email_id = EXCLUDED.email_id,
    password = EXCLUDED.password,
    role = EXCLUDED.role,
    customer_name = EXCLUDED.customer_name,
    company = EXCLUDED.company,
    assigned_vms = EXCLUDED.assigned_vms,
    updated_at = NOW();

-- 5. Seed Northwind Logistics standard VMs into vms table
INSERT INTO public.vms (id, user_id, customer_id, customer_name, name, vm_size, specs, status, region, hourly_rate, current_spend, projected_spend, savings, auto_scale_enabled)
VALUES
(
    'vm-web-prod',
    'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    'cust-northwind',
    'Northwind Logistics SaaS',
    'web-prod-01',
    'Standard_D8s_v5',
    '{"cores": 8, "ramGb": 32, "storageGb": 512, "maxIops": 12800}'::jsonb,
    'Healthy',
    'East US (Virginia)',
    0.384,
    18400,
    13880,
    4520,
    true
),
(
    'vm-analytics',
    'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    'cust-northwind',
    'Northwind Logistics SaaS',
    'analytics-worker-02',
    'Standard_E16s_v5',
    '{"cores": 16, "ramGb": 64, "storageGb": 1024, "maxIops": 25600}'::jsonb,
    'Bottleneck Warning',
    'Central India (Pune)',
    1.008,
    27250,
    29580,
    0,
    false
),
(
    'vm-batch',
    'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    'cust-northwind',
    'Northwind Logistics SaaS',
    'batch-processor-03',
    'Standard_D4s_v5',
    '{"cores": 4, "ramGb": 16, "storageGb": 256, "maxIops": 6400}'::jsonb,
    'Healthy',
    'Southeast Asia (Singapore)',
    0.192,
    9700,
    6200,
    3500,
    true
),
(
    'vm-api-gw',
    'd0a49394-eafe-41f1-ae07-4ae3045e0c65',
    'cust-northwind',
    'Northwind Logistics SaaS',
    'gateway-edge-04',
    'Standard_D4s_v5',
    '{"cores": 4, "ramGb": 16, "storageGb": 256, "maxIops": 6400}'::jsonb,
    'Healthy',
    'Central India (Pune)',
    0.192,
    9700,
    8500,
    1200,
    true
)
ON CONFLICT (id) DO NOTHING;
