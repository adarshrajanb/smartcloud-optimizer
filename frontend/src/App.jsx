import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowDownCircle,
  ArrowUpCircle,
  Cpu,
  Database,
  Gauge,
  MemoryStick,
  ServerCog,
  ShieldCheck,
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

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatShortDate(value) {
  if (!value) return "";
  const date = new Date(value);
  return new Intl.DateTimeFormat("en-IN", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function App() {
  const [customers, setCustomers] = useState([]);
  const [vms, setVms] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState("");
  const [selectedVmId, setSelectedVmId] = useState("");
  const [timeRange, setTimeRange] = useState("7d");
  const [granularity, setGranularity] = useState("30m");
  const [autoScaleEnabled, setAutoScaleEnabled] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/customers`)
      .then((res) => res.json())
      .then((data) => {
        const customerList = data.customers || [];
        setCustomers(customerList);
        if (customerList[0]) setSelectedCustomerId(customerList[0].id);
      })
      .catch(() => {
        setCustomers([
          {
            id: "cust-northwind",
            name: "Northwind Logistics",
            company: "Northwind Logistics",
            budgetLimit: 45000,
          },
        ]);
        setSelectedCustomerId("cust-northwind");
      });
  }, []);

  useEffect(() => {
    if (!selectedCustomerId) return;
    fetch(`${API_BASE}/api/vms`)
      .then((res) => res.json())
      .then((data) => {
        const vmList = data.vms || [];
        setVms(vmList);
        if (vmList[0]) {
          setSelectedVmId(vmList[0].id);
          setAutoScaleEnabled(vmList[0].autoScaleEnabled);
        }
      })
      .catch(() => {
        setVms([
          {
            id: "vm-web-prod",
            name: "web-prod-01",
            customerId: "cust-northwind",
            region: "West Europe",
            resourceGroup: "prod-web-rg",
            currentSpend: 18400,
            projectedSpend: 13880,
            savings: 4520,
            autoScaleEnabled: true,
            specs: { cores: 8, ramGb: 32, storageGb: 512, os: "Ubuntu 22.04" },
            recommendation: {
              type: "downsize",
              title: "Downsize 2 vCPU / 8 GB for low-night usage",
              reason: "Average CPU usage is 18% after 7 pm.",
              formula: "₹18,400 current spend - ₹4,520 predicted savings = ₹13,880 projected spend",
              billingImpact: "Projected monthly billing reduces by 24.6%.",
            },
            metrics: {
              "1d": { "10m": [], "30m": [], "1h": [] },
              "7d": { "10m": [], "30m": [], "1h": [] },
              "30d": { "1d": [] },
            },
          },
          {
            id: "vm-analytics",
            name: "analytics-02",
            customerId: "cust-northwind",
            region: "Central US",
            resourceGroup: "analytics-rg",
            currentSpend: 27250,
            projectedSpend: 29580,
            savings: 0,
            autoScaleEnabled: false,
            specs: { cores: 16, ramGb: 64, storageGb: 1024, os: "Windows Server 2022" },
            recommendation: {
              type: "upgrade",
              title: "Upsize compute during evening batch window",
              reason: "P95 CPU is touching 92% and memory is above 80%.",
              formula: "Peak CPU 92% > 80% threshold and memory 81% -> add 4 vCPU and 16 GB RAM",
              billingImpact: "Projected spend rises by ₹2,330.",
            },
            metrics: {
              "1d": { "10m": [], "30m": [], "1h": [] },
              "7d": { "10m": [], "30m": [], "1h": [] },
              "30d": { "1d": [] },
            },
          },
        ]);
        setSelectedVmId("vm-web-prod");
      });
  }, [selectedCustomerId]);

  const currentCustomer = useMemo(
    () => customers.find((customer) => customer.id === selectedCustomerId) || customers[0],
    [customers, selectedCustomerId],
  );

  const selectedVm = useMemo(
    () => vms.find((vm) => vm.id === selectedVmId) || vms[0],
    [vms, selectedVmId],
  );

  useEffect(() => {
    if (!selectedVm) return;
    setAutoScaleEnabled(!!selectedVm.autoScaleEnabled);
    const allowedGranularity = GRANULARITY_OPTIONS[timeRange] || ["30m"];
    if (!allowedGranularity.includes(granularity)) {
      setGranularity(allowedGranularity[0]);
    }
  }, [selectedVm, timeRange, granularity]);

  const chartData = useMemo(() => {
    if (!selectedVm || !selectedVm.metrics || !selectedVm.metrics[timeRange]) return [];
    const selectedMetrics = selectedVm.metrics[timeRange]?.[granularity] || [];
    return selectedMetrics.slice(0, 120).map((point, index) => ({
      ...point,
      label: index,
      cpu: point.cpu,
      memory: point.memory,
      disk: point.disk,
      network: point.network,
      timestampLabel: formatShortDate(point.timestamp),
    }));
  }, [selectedVm, granularity, timeRange]);

  const totalCurrentSpend = useMemo(
    () => (vms || []).reduce((sum, vm) => sum + Number(vm.currentSpend || 0), 0),
    [vms],
  );

  const totalProjectedSpend = useMemo(
    () => (vms || []).reduce((sum, vm) => sum + Number(vm.projectedSpend || 0), 0),
    [vms],
  );

  const totalSavings = useMemo(
    () => (vms || []).reduce((sum, vm) => sum + Number(vm.savings || 0), 0),
    [vms],
  );

  const recommendationText = selectedVm?.recommendation || {
    title: "No recommendation",
    formula: "Cost model is stable",
    reason: "Usage pattern is within acceptable limits.",
    billingImpact: "No billing change expected.",
    type: "downsize",
  };

  return (
    <div className="app-shell">
      <div className="app-frame">
        <aside className="sidebar-panel">
          <div className="brand-block">
            <div className="brand-badge">SC</div>
            <div>
              <p className="eyebrow">FinOps</p>
              <h1>SmartCloud Optimizer</h1>
            </div>
          </div>

          <div className="customer-select">
            <label>Customer</label>
            <select
              value={selectedCustomerId}
              onChange={(event) => setSelectedCustomerId(event.target.value)}
            >
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.company || customer.name}
                </option>
              ))}
            </select>
          </div>

          <div className="section-header">
            <span>VM Inventory</span>
            <span className="pill">{vms.length}</span>
          </div>

          <div className="vm-list">
            {vms.map((vm) => (
              <button
                key={vm.id}
                type="button"
                className={`vm-card ${selectedVmId === vm.id ? "active" : ""}`}
                onClick={() => setSelectedVmId(vm.id)}
              >
                <div className="vm-name-row">
                  <div>
                    <div className="vm-title">{vm.name}</div>
                    <div className="vm-meta">{vm.region}</div>
                  </div>
                  <div className={`status-badge ${vm.recommendation?.type === "upgrade" ? "warning" : "safe"}`}>
                    {vm.recommendation?.type === "upgrade" ? "Scale up" : "Scale down"}
                  </div>
                </div>
                <div className="vm-specs">
                  <span>{vm.specs?.cores} vCPU</span>
                  <span>{vm.specs?.ramGb} GB RAM</span>
                  <span>{vm.specs?.storageGb} GB</span>
                </div>
              </button>
            ))}
          </div>
        </aside>

        <main className="main-panel">
          <header className="topbar">
            <div>
              <p className="eyebrow">Customer overview</p>
              <h2>{currentCustomer?.company || currentCustomer?.name}</h2>
            </div>
            <div className="summary-chip">
              <Database size={16} />
              Public Azure pricing benchmark
            </div>
          </header>

          <section className="summary-grid">
            <div className="summary-card">
              <div className="label-row">
                <span>Current spending</span>
                <Wallet size={16} />
              </div>
              <strong>{formatCurrency(totalCurrentSpend)}</strong>
            </div>
            <div className="summary-card">
              <div className="label-row">
                <span>Projected spend</span>
                <Gauge size={16} />
              </div>
              <strong>{formatCurrency(totalProjectedSpend)}</strong>
            </div>
            <div className="summary-card">
              <div className="label-row">
                <span>Projected savings</span>
                <ArrowDownCircle size={16} />
              </div>
              <strong className="positive">{formatCurrency(totalSavings)}</strong>
            </div>
            <div className="summary-card">
              <div className="label-row">
                <span>Automation</span>
                <ShieldCheck size={16} />
              </div>
              <strong>{autoScaleEnabled ? "Enabled" : "Manual"}</strong>
            </div>
          </section>

          <section className="content-grid">
            <div className="main-card information-card">
              <div className="section-title-row">
                <h3>VM details</h3>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={autoScaleEnabled}
                    onChange={(event) => setAutoScaleEnabled(event.target.checked)}
                  />
                  <span>Auto scale approval</span>
                </label>
              </div>

              {selectedVm ? (
                <>
                  <div className="vm-header-panel">
                    <div>
                      <p className="eyebrow">Selected VM</p>
                      <h4>{selectedVm.name}</h4>
                    </div>
                    <div className={`recommendation-type ${selectedVm.recommendation?.type === "upgrade" ? "warning" : "good"}`}>
                      {selectedVm.recommendation?.type === "upgrade" ? "Upgrade recommended" : "Downsize recommended"}
                    </div>
                  </div>

                  <div className="detail-grid">
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
                      <ServerCog size={16} />
                      <span>Storage</span>
                      <strong>{selectedVm.specs?.storageGb} GB</strong>
                    </div>
                    <div className="metric-box">
                      <Wallet size={16} />
                      <span>Monthly spend</span>
                      <strong>{formatCurrency(selectedVm.currentSpend)}</strong>
                    </div>
                  </div>

                  <div className="spec-summary">
                    <div>
                      <span>Region</span>
                      <strong>{selectedVm.region}</strong>
                    </div>
                    <div>
                      <span>Resource group</span>
                      <strong>{selectedVm.resourceGroup}</strong>
                    </div>
                    <div>
                      <span>OS</span>
                      <strong>{selectedVm.specs?.os}</strong>
                    </div>
                  </div>
                </>
              ) : null}
            </div>

            <div className="main-card notification-card">
              <div className="section-title-row">
                <h3>Recommendation</h3>
                {recommendationText.type === "upgrade" ? (
                  <ArrowUpCircle className="accent-warning" size={18} />
                ) : (
                  <ArrowDownCircle className="accent-success" size={18} />
                )}
              </div>

              <div className="notification-body">
                <div className={`notification-tag ${recommendationText.type === "upgrade" ? "warning" : "good"}`}>
                  {recommendationText.type === "upgrade" ? "Bottleneck risk" : "Underutilized resources"}
                </div>
                <h4>{recommendationText.title}</h4>
                <p>{recommendationText.reason}</p>
                <div className="formula-box">
                  <strong>Cost logic</strong>
                  <span>{recommendationText.formula}</span>
                </div>
                <div className="note-box">
                  <AlertTriangle size={16} />
                  <span>{recommendationText.billingImpact}</span>
                </div>
              </div>
            </div>
          </section>

          <section className="main-card chart-panel">
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

            <div className="chart-container">
              <ResponsiveContainer width="100%" height={330}>
                <AreaChart data={chartData} margin={{ top: 14, right: 12, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="cpuFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#34d399" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#34d399" stopOpacity={0.05} />
                    </linearGradient>
                    <linearGradient id="memoryFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.7} />
                      <stop offset="95%" stopColor="#60a5fa" stopOpacity={0.06} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                  <XAxis dataKey="timestampLabel" tick={{ fill: "#94a3b8", fontSize: 11 }} minTickGap={24} />
                  <YAxis domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <Tooltip
                    formatter={(value, name) => [`${Number(value).toFixed(1)}%`, name]}
                    labelFormatter={(label) => label}
                    contentStyle={{ background: "#020617", borderColor: "#334155", borderRadius: 12 }}
                  />
                  <Legend />
                  <Area type="monotone" dataKey="cpu" stroke="#34d399" fill="url(#cpuFill)" name="CPU" strokeWidth={2} />
                  <Area type="monotone" dataKey="memory" stroke="#60a5fa" fill="url(#memoryFill)" name="Memory" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="stats-row">
              <div className="tiny-stat">
                <span>CPU peak</span>
                <strong>{Math.max(...(chartData.map((point) => Number(point.cpu || 0)) || [0]), 0).toFixed(0)}%</strong>
              </div>
              <div className="tiny-stat">
                <span>Memory peak</span>
                <strong>{Math.max(...(chartData.map((point) => Number(point.memory || 0)) || [0]), 0).toFixed(0)}%</strong>
              </div>
              <div className="tiny-stat">
                <span>Disk peak</span>
                <strong>{Math.max(...(chartData.map((point) => Number(point.disk || 0)) || [0]), 0).toFixed(0)}%</strong>
              </div>
              <div className="tiny-stat">
                <span>Network peak</span>
                <strong>{Math.max(...(chartData.map((point) => Number(point.network || 0)) || [0]), 0).toFixed(0)} MB/s</strong>
              </div>
            </div>
          </section>

          <section className="main-card insight-panel">
            <div className="section-title-row">
              <h3>Automation summary</h3>
            </div>
            <div className="insight-grid">
              <div>
                <span className="insight-label">Current spend</span>
                <strong>{formatCurrency(selectedVm?.currentSpend || 0)}</strong>
              </div>
              <div>
                <span className="insight-label">Projected spend</span>
                <strong>{formatCurrency(selectedVm?.projectedSpend || 0)}</strong>
              </div>
              <div>
                <span className="insight-label">Savings</span>
                <strong className="positive">{formatCurrency(selectedVm?.savings || 0)}</strong>
              </div>
            </div>
            <div className="insight-footer">
              {autoScaleEnabled
                ? "Automation approved — SmartCloud will apply the recommended resource changes automatically when thresholds are crossed."
                : "Automation is not approved — the platform will notify the user and present the recommendation for approval before changes are applied."}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
