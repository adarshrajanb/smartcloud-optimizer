import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CheckCircle2,
  Cpu,
  Database,
  Gauge,
  Lock,
  MemoryStick,
  Server,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = "http://localhost:8000";

const RANGE_OPTIONS = [
  { id: "1d", label: "1 Day" },
  { id: "7d", label: "7 Days" },
  { id: "30d", label: "30 Days" },
];

const GRANULARITY_OPTIONS = {
  "1d": ["10m", "30m", "1h"],
  "7d": ["10m", "30m", "1h"],
  "30d": ["1d"],
};

const fallbackCustomer = {
  id: "cust-northwind",
  name: "Northwind Logistics",
  company: "Northwind Logistics Ltd.",
  industry: "Supply chain",
  budgetLimit: 45000,
};

const fallbackMetrics = {
  "1d": {
    "10m": Array.from({ length: 144 }, (_, index) => ({
      timestamp: new Date(Date.now() - (143 - index) * 10 * 60000).toISOString(),
      cpu: 36 + ((index * 7) % 22),
      memory: 44 + ((index * 5) % 18),
      disk: 28 + ((index * 11) % 15),
      network: 80 + ((index * 13) % 55),
    })),
    "30m": Array.from({ length: 48 }, (_, index) => ({
      timestamp: new Date(Date.now() - (47 - index) * 30 * 60000).toISOString(),
      cpu: 36 + ((index * 9) % 24),
      memory: 42 + ((index * 6) % 20),
      disk: 30 + ((index * 7) % 18),
      network: 90 + ((index * 9) % 58),
    })),
    "1h": Array.from({ length: 24 }, (_, index) => ({
      timestamp: new Date(Date.now() - (23 - index) * 60 * 60000).toISOString(),
      cpu: 34 + ((index * 8) % 26),
      memory: 40 + ((index * 5) % 19),
      disk: 30 + ((index * 6) % 17),
      network: 76 + ((index * 11) % 61),
    })),
  },
  "7d": {
    "10m": Array.from({ length: 1008 }, (_, index) => ({
      timestamp: new Date(Date.now() - (1007 - index) * 10 * 60000).toISOString(),
      cpu: 28 + ((index * 3) % 27),
      memory: 35 + ((index * 2) % 22),
      disk: 24 + ((index * 5) % 20),
      network: 68 + ((index * 7) % 65),
    })),
    "30m": Array.from({ length: 336 }, (_, index) => ({
      timestamp: new Date(Date.now() - (335 - index) * 30 * 60000).toISOString(),
      cpu: 30 + ((index * 4) % 28),
      memory: 38 + ((index * 3) % 24),
      disk: 26 + ((index * 8) % 18),
      network: 71 + ((index * 6) % 64),
    })),
    "1h": Array.from({ length: 168 }, (_, index) => ({
      timestamp: new Date(Date.now() - (167 - index) * 60 * 60000).toISOString(),
      cpu: 29 + ((index * 5) % 25),
      memory: 36 + ((index * 4) % 23),
      disk: 24 + ((index * 9) % 20),
      network: 70 + ((index * 8) % 62),
    })),
  },
  "30d": {
    "1d": Array.from({ length: 30 }, (_, index) => ({
      timestamp: new Date(Date.now() - (29 - index) * 24 * 60 * 60000).toISOString(),
      cpu: 27 + ((index * 7) % 31),
      memory: 34 + ((index * 5) % 23),
      disk: 25 + ((index * 6) % 22),
      network: 69 + ((index * 10) % 60),
    })),
  },
};

const fallbackVms = [
  {
    id: "vm-web-prod",
    name: "web-prod-01",
    customerId: "cust-northwind",
    region: "West Europe",
    resourceGroup: "prod-web-rg",
    status: "Healthy",
    currentSpend: 18400,
    projectedSpend: 13880,
    savings: 4520,
    autoScaleEnabled: true,
    specs: { cores: 8, ramGb: 32, storageGb: 512, os: "Ubuntu 22.04" },
    recommendation: {
      type: "downsize",
      title: "Night-time downsizing recommended",
      confidence: 94,
      reason: "Average CPU stayed at 18% between 7 PM and 5 AM, while memory remained below 42%.",
      formula: "₹18,400 current spend - ₹4,520 projected savings = ₹13,880 projected spend",
      billingImpact: "Projected monthly spend reduces by 24.6% if the scheduled automation remains approved.",
    },
    metrics: fallbackMetrics,
  },
  {
    id: "vm-analytics",
    name: "analytics-02",
    customerId: "cust-northwind",
    region: "Central US",
    resourceGroup: "analytics-rg",
    status: "At risk",
    currentSpend: 27250,
    projectedSpend: 29580,
    savings: 0,
    autoScaleEnabled: false,
    specs: { cores: 16, ramGb: 64, storageGb: 1024, os: "Windows Server 2022" },
    recommendation: {
      type: "upgrade",
      title: "Compute upgrade recommended",
      confidence: 89,
      reason: "P95 CPU is near 92% and memory remains above 80% for 3 consecutive workload windows.",
      formula: "Peak CPU 92% > 80% threshold and memory 81% -> add 4 vCPU and 16 GB RAM",
      billingImpact: "Projected monthly spend rises by ₹2,330 to avoid SLA risk and performance degradation.",
    },
    metrics: fallbackMetrics,
  },
  {
    id: "vm-batch",
    name: "batch-03",
    customerId: "cust-northwind",
    region: "Southeast Asia",
    resourceGroup: "batch-rg",
    status: "Idle",
    currentSpend: 9700,
    projectedSpend: 6200,
    savings: 3500,
    autoScaleEnabled: true,
    specs: { cores: 4, ramGb: 16, storageGb: 256, os: "Ubuntu 20.04" },
    recommendation: {
      type: "downsize",
      title: "Off-hours workload reduction recommended",
      confidence: 93,
      reason: "Batch windows finish before 6 AM and CPU stays below 22% during the overnight schedule.",
      formula: "₹9,700 current spend - ₹3,500 scheduled savings = ₹6,200 projected spend",
      billingImpact: "Savings are preserved while keeping the required nightly processing window intact.",
    },
    metrics: fallbackMetrics,
  },
];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function formatTimestamp(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en-IN", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem("smartcloud-auth") === "true";
  });
  const [loginForm, setLoginForm] = useState({
    email: "admin@northwind.com",
    password: "Admin@123",
  });
  const [loginError, setLoginError] = useState("");
  const [customer, setCustomer] = useState(fallbackCustomer);
  const [vms, setVms] = useState(fallbackVms);
  const [selectedVmId, setSelectedVmId] = useState("vm-web-prod");
  const [timeRange, setTimeRange] = useState("7d");
  const [granularity, setGranularity] = useState("30m");
  const [autoScaleEnabled, setAutoScaleEnabled] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadData = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/dashboard/cust-northwind`);
        if (!response.ok) throw new Error("Dashboard unavailable");

        const data = await response.json();
        if (data.customer) setCustomer(data.customer);
        if (Array.isArray(data.vms) && data.vms.length) {
          setVms(data.vms);
          setSelectedVmId(data.vms[0].id);
          setAutoScaleEnabled(data.vms[0].autoScaleEnabled);
        }
      } catch {
        setCustomer(fallbackCustomer);
        setVms(fallbackVms);
        setSelectedVmId("vm-web-prod");
        setAutoScaleEnabled(true);
      }
    };

    loadData();
  }, [isAuthenticated]);

  const selectedVm = useMemo(
    () => vms.find((vm) => vm.id === selectedVmId) || vms[0],
    [vms, selectedVmId],
  );

  useEffect(() => {
    if (!selectedVm) return;
    setAutoScaleEnabled(Boolean(selectedVm.autoScaleEnabled));
    const allowed = GRANULARITY_OPTIONS[timeRange] || ["30m"];
    if (!allowed.includes(granularity)) setGranularity(allowed[0]);
  }, [selectedVm, timeRange, granularity]);

  const chartData = useMemo(() => {
    if (!selectedVm || !selectedVm.metrics || !selectedVm.metrics[timeRange]) return [];
    const data = selectedVm.metrics[timeRange]?.[granularity] || [];
    return data.slice(0, 120).map((point) => ({
      ...point,
      timestampLabel: formatTimestamp(point.timestamp),
      cpu: Number(point.cpu || 0),
      memory: Number(point.memory || 0),
      disk: Number(point.disk || 0),
      network: Number(point.network || 0),
    }));
  }, [selectedVm, timeRange, granularity]);

  const totalCurrentSpend = useMemo(
    () => vms.reduce((sum, vm) => sum + Number(vm.currentSpend || 0), 0),
    [vms],
  );

  const totalProjectedSpend = useMemo(
    () => vms.reduce((sum, vm) => sum + Number(vm.projectedSpend || 0), 0),
    [vms],
  );

  const totalSavings = useMemo(
    () => vms.reduce((sum, vm) => sum + Number(vm.savings || 0), 0),
    [vms],
  );

  const recommendation = selectedVm?.recommendation || {
    type: "downsize",
    title: "No recommendation",
    reason: "Usage appears stable.",
    formula: "No cost change required.",
    billingImpact: "No projected billing impact.",
  };

  const handleLogin = (event) => {
    event.preventDefault();
    if (!loginForm.email || !loginForm.password || loginForm.password.length < 6) {
      setLoginError("Enter a valid email and password.");
      return;
    }

    setLoginError("");
    localStorage.setItem("smartcloud-auth", "true");
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("smartcloud-auth");
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-brand">
            <div className="brand-mark">SC</div>
            <div>
              <p className="eyebrow">SmartCloud</p>
              <h1>ResourceOps</h1>
            </div>
          </div>

          <div className="login-header">
            <h2>Welcome back</h2>
            <p>Sign in to manage VM spend and automated scaling.</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <label>
              <span>Email</span>
              <input
                type="email"
                value={loginForm.email}
                onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })}
                placeholder="name@company.com"
              />
            </label>

            <label>
              <span>Password</span>
              <input
                type="password"
                value={loginForm.password}
                onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
                placeholder="Enter password"
              />
            </label>

            {loginError && <div className="login-error">{loginError}</div>}

            <button type="submit" className="primary-button" style={{ width: "100%" }}>
              <Lock size={16} />
              Sign in
            </button>
          </form>

          <div className="login-footer">
            <span>Demo access</span>
            <strong>admin@northwind.com</strong>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SC</div>
          <div>
            <p className="eyebrow">SmartCloud</p>
            <h1>ResourceOps</h1>
          </div>
        </div>

        <div className="customer-card">
          <p className="eyebrow">Customer</p>
          <h3>{customer.company}</h3>
          <div className="meta-row">
            <span>{customer.industry}</span>
            <span>{vms.length} VMs</span>
          </div>
        </div>

        <div className="section-title-row">
          <h3>Virtual machines</h3>
          <span className="soft-badge">{vms.length}</span>
        </div>

        <div className="vm-list">
          {vms.map((vm) => (
            <button
              key={vm.id}
              type="button"
              className={`vm-item ${selectedVmId === vm.id ? "active" : ""}`}
              onClick={() => setSelectedVmId(vm.id)}
            >
              <div className="vm-name-row">
                <div>
                  <div className="vm-name">{vm.name}</div>
                  <div className="vm-region">{vm.region}</div>
                </div>
                <span className={`status-pill ${vm.recommendation?.type === "upgrade" ? "warning" : "success"}`}>
                  {vm.recommendation?.type === "upgrade" ? "Scale up" : "Scale down"}
                </span>
              </div>

              <div className="vm-specs">
                <span>{vm.specs?.cores} vCPU</span>
                <span>{vm.specs?.ramGb} GB RAM</span>
                <span>{vm.specs?.storageGb} GB</span>
              </div>
            </button>
          ))}
        </div>

        <button type="button" className="secondary-button" onClick={handleLogout}>
          Sign out
        </button>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations overview</p>
            <h2>{customer.company}</h2>
          </div>

          <div className="header-actions">
            <div className="inline-pill">
              <Database size={16} />
              Azure benchmark data
            </div>
            <button type="button" className="icon-button" aria-label="Notifications">
              <Bell size={18} />
            </button>
          </div>
        </header>

        <section className="summary-grid">
          <div className="summary-card">
            <div className="summary-meta">
              <span>Current spend</span>
              <Wallet size={16} />
            </div>
            <strong>{formatCurrency(totalCurrentSpend)}</strong>
          </div>

          <div className="summary-card">
            <div className="summary-meta">
              <span>Projected spend</span>
              <Gauge size={16} />
            </div>
            <strong>{formatCurrency(totalProjectedSpend)}</strong>
          </div>

          <div className="summary-card positive-card">
            <div className="summary-meta">
              <span>Projected savings</span>
              <TrendingDown size={16} />
            </div>
            <strong>{formatCurrency(totalSavings)}</strong>
          </div>

          <div className="summary-card neutral-card">
            <div className="summary-meta">
              <span>Automation</span>
              <ShieldCheck size={16} />
            </div>
            <strong>{autoScaleEnabled ? "Enabled" : "Manual"}</strong>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel vm-panel">
            <div className="section-title-row">
              <h3>VM details</h3>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={autoScaleEnabled}
                  onChange={(event) => setAutoScaleEnabled(event.target.checked)}
                />
                <span>Auto-scale approval</span>
              </label>
            </div>

            {selectedVm && (
              <>
                <div className="vm-header-card">
                  <div>
                    <p className="eyebrow">Selected VM</p>
                    <h3>{selectedVm.name}</h3>
                  </div>
                  <span className={`alert-pill ${recommendation.type === "upgrade" ? "warning" : "success"}`}>
                    {recommendation.type === "upgrade" ? "Upgrade recommended" : "Downsize recommended"}
                  </span>
                </div>

                <div className="data-grid">
                  <div className="metric-box">
                    <Cpu size={16} />
                    <span>Cores</span>
                    <strong>{selectedVm.specs?.cores}</strong>
                  </div>
                  <div className="metric-box">
                    <MemoryStick size={16} />
                    <span>RAM</span>
                    <strong>{selectedVm.specs?.ramGb} GB</strong>
                  </div>
                  <div className="metric-box">
                    <Server size={16} />
                    <span>Storage</span>
                    <strong>{selectedVm.specs?.storageGb} GB</strong>
                  </div>
                  <div className="metric-box">
                    <Wallet size={16} />
                    <span>Monthly spend</span>
                    <strong>{formatCurrency(selectedVm.currentSpend)}</strong>
                  </div>
                </div>

                <div className="detail-list">
                  <div>
                    <span>Region</span>
                    <strong>{selectedVm.region}</strong>
                  </div>
                  <div>
                    <span>Resource group</span>
                    <strong>{selectedVm.resourceGroup}</strong>
                  </div>
                  <div>
                    <span>Operating system</span>
                    <strong>{selectedVm.specs?.os}</strong>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="panel alert-panel">
            <div className="section-title-row">
              <h3>Recommendation</h3>
              {recommendation.type === "upgrade" ? (
                <ArrowUpRight className="icon-warning" size={18} />
              ) : (
                <ArrowDownRight className="icon-success" size={18} />
              )}
            </div>

            <div className={`alert-tag ${recommendation.type === "upgrade" ? "warning" : "success"}`}>
              {recommendation.type === "upgrade" ? "Bottleneck risk" : "Underutilized resources"}
            </div>

            <h4>{recommendation.title}</h4>
            <p>{recommendation.reason}</p>

            <div className="formula-box">
              <span>Cost logic</span>
              <strong>{recommendation.formula}</strong>
            </div>

            <div className="note-box">
              <CheckCircle2 size={16} />
              <span>{recommendation.billingImpact}</span>
            </div>
          </div>
        </section>

        <section className="panel chart-panel">
          <div className="section-title-row chart-header">
            <h3>Resource metrics</h3>
            <div className="chart-controls">
              <div className="segmented-control">
                {RANGE_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    className={timeRange === option.id ? "selected" : ""}
                    onClick={() => setTimeRange(option.id)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>

              <select value={granularity} onChange={(event) => setGranularity(event.target.value)}>
                {(GRANULARITY_OPTIONS[timeRange] || ["30m"]).map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="chart-area">
            <ResponsiveContainer width="100%" height={340}>
              <AreaChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="cpuFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#2f6fed" stopOpacity={0.22} />
                    <stop offset="95%" stopColor="#2f6fed" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="memoryFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#20b47a" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#20b47a" stopOpacity={0.02} />
                  </linearGradient>
                </defs>

                <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
                <XAxis dataKey="timestampLabel" tick={{ fill: "#64748b", fontSize: 10 }} minTickGap={30} />
                <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
                <Tooltip
                  formatter={(value, name) => [`${Number(value).toFixed(1)}%`, name]}
                  contentStyle={{
                    background: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    boxShadow: "0 8px 30px rgba(15, 23, 42, 0.08)",
                  }}
                />
                <Legend />
                <Area type="monotone" dataKey="cpu" stroke="#2f6fed" fill="url(#cpuFill)" name="CPU" strokeWidth={2.5} />
                <Area type="monotone" dataKey="memory" stroke="#20b47a" fill="url(#memoryFill)" name="Memory" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="stats-row">
            <div className="tiny-stat">
              <span>CPU peak</span>
              <strong>
                {Math.max(...(chartData.map((point) => Number(point.cpu || 0)) || [0]), 0).toFixed(0)}%
              </strong>
            </div>
            <div className="tiny-stat">
              <span>Memory peak</span>
              <strong>
                {Math.max(...(chartData.map((point) => Number(point.memory || 0)) || [0]), 0).toFixed(0)}%
              </strong>
            </div>
            <div className="tiny-stat">
              <span>Disk peak</span>
              <strong>
                {Math.max(...(chartData.map((point) => Number(point.disk || 0)) || [0]), 0).toFixed(0)}%
              </strong>
            </div>
            <div className="tiny-stat">
              <span>Network peak</span>
              <strong>
                {Math.max(...(chartData.map((point) => Number(point.network || 0)) || [0]), 0).toFixed(0)} MB/s
              </strong>
            </div>
          </div>
        </section>

        <section className="panel automation-panel">
          <div className="section-title-row">
            <h3>Automation summary</h3>
            <div className={`inline-pill ${autoScaleEnabled ? "good" : "neutral"}`}>
              {autoScaleEnabled ? "Approved" : "Pending"}
            </div>
          </div>

          <div className="insight-grid">
            <div>
              <span>Current spend</span>
              <strong>{formatCurrency(selectedVm?.currentSpend || 0)}</strong>
            </div>
            <div>
              <span>Projected spend</span>
              <strong>{formatCurrency(selectedVm?.projectedSpend || 0)}</strong>
            </div>
            <div>
              <span>Projected savings</span>
              <strong className="positive">{formatCurrency(selectedVm?.savings || 0)}</strong>
            </div>
          </div>

          <div className="automation-note">
            {autoScaleEnabled
              ? "Automation is approved. SmartCloud will automatically apply the recommended change when usage thresholds are crossed."
              : "Automation is not approved. The platform will notify the user and require approval before modifying the VM."}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
