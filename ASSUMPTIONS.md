# SmartCloud Optimizer — FinOps Assumptions & Methodology Sheet

**Challenge**: UTHO Track — TRANSFINITTE 2026 Hackathon  
**Target Organization**: ZenithFlow Technologies Pvt Ltd (Mid-sized Indian B2B SaaS Enterprise)  
**Fleet**: 50–150 Provisioned Resources across Noida (North), Bangalore (South), and Mumbai (West)  

---

## 1. Cloud Infrastructure & Unit Pricing Baseline

All compute and storage costs are calibrated against official Microsoft Azure and Indian Cloud Datacenter pricing (Central India / Pune, South India / Chennai, West India / Mumbai) converted at an exchange rate of **₹84.00 per USD**.

| Resource SKU / Category | Hardware Specifications | Hourly Rate (USD) | Hourly Rate (INR) | Monthly 24/7 Cost (INR) |
| :--- | :--- | :--- | :--- | :--- |
| **Standard_B2s** | 2 vCPU, 4 GB RAM, 64 GB SSD | \$0.0416 / hr | ₹3.50 / hr | **₹2,550 / month** |
| **Standard_D2s_v5** | 2 vCPU, 8 GB RAM, 128 GB SSD | \$0.1120 / hr | ₹9.40 / hr | **₹6,900 / month** |
| **Standard_D4s_v5** | 4 vCPU, 16 GB RAM, 256 GB SSD | \$0.1580 / hr | ₹13.28 / hr | **₹9,700 / month** |
| **Standard_D8s_v5** | 8 vCPU, 32 GB RAM, 512 GB SSD | \$0.3000 / hr | ₹25.20 / hr | **₹18,400 / month** |
| **Standard_D16s_v5** | 16 vCPU, 64 GB RAM, 512 GB SSD | \$0.6260 / hr | ₹52.60 / hr | **₹38,400 / month** |
| **Standard_E8s_v5** | 8 vCPU, 64 GB RAM, 512 GB Ultra SSD | \$0.4370 / hr | ₹36.70 / hr | **₹26,800 / month** |
| **Standard_E16s_v5** | 16 vCPU, 128 GB RAM, 1 TB Ultra SSD | \$0.8740 / hr | ₹73.40 / hr | **₹53,600 / month** |
| **Premium Managed SSD** | 500 GB / 1 TB High-IOPS Block Storage | \$0.1000 / GB/mo | ₹8.40 / GB/mo | **₹4,200 / 500GB / mo** |
| **Unallocated Static IP** | Reserved IPv4 Address (Unattached) | \$0.0230 / hr | ₹1.92 / hr | **₹1,400 / month / IP** |

### Billable Hours Convention:
* **730 hours / month** is used as the standard cloud financial calendar constant:
  $$\text{Hours per month} = \frac{365 \text{ days} \times 24 \text{ hours}}{12 \text{ months}} = 730 \text{ hours}$$

---

## 2. Peak-Safe Rightsizing Engine (p95 & p99 Thresholds)

A central requirement of the UTHO problem statement is that **rightsizing must not rely solely on averages**. Sizing solely on average CPU risks severe downtime during traffic surges.

### Peak-Safe Governance Algorithm:
1. **Protection Condition**:
   $$\text{If } \text{p95\_CPU} \ge 75.0\% \quad \text{or} \quad \text{p99\_CPU} \ge 85.0\%$$
   * **Action**: Downsizing is **strictly prohibited**. The instance is classified as **Peak Protected** with a banner alert.
   * **Real-world Example**: `zenith-checkout-api-01` has a 24-hour average CPU of only 48.0%, but spikes to **88.4% (p95)** and **94.8% (p99)** during daily lunch (13:00–14:30) and dinner (20:00–21:30) flash promotions. Reducing this instance would cause connection pool starvation and drop customer checkouts.
2. **Rightsizing Candidate Condition**:
   $$\text{If } \text{p95\_CPU} < 35.0\% \quad \text{and} \quad \text{avg\_CPU} < 20.0\%$$
   * **Action**: Recommend downsizing by 50% capacity (e.g. Standard_D8s_v5 $\to$ Standard_D4s_v5).
   * **Safety Guarantee**: The target SKU ensures that historical p99 peaks will consume no more than 60% of the new tier's capacity, guaranteeing a $\ge 40\%$ headroom safety buffer.

---

## 3. Scheduled Off-Hours & Weekend Shutdown Model

Non-production environments (Development and Staging) do not need to run 24/7.

### Dev Cluster Idle Calculation:
* **Weekday Nocturnal Window**: 8:00 PM to 8:00 AM IST (12 idle hours / day $\times$ 5 weekdays = 60 hours).
* **Weekend Window**: Saturday 12:00 AM to Sunday 11:59 PM IST (48 idle hours).
* **Total Weekly Idle Time**: $60 + 48 = \mathbf{108 \text{ hours / week}}$.
* **Monthly Savings Ratio**:
  $$\text{Idle Time Ratio} = \frac{108 \text{ hours/week} \times 4.34 \text{ weeks}}{730 \text{ hours}} = \mathbf{64.2\% \text{ of the month}}$$
* **Net Financial Impact**: Shutting down dev nodes during non-working hours yields up to **58.8% net monthly savings** while preserving developer productivity.

### Batch Processing Window:
* Batch workloads (e.g., `zenith-nightly-recon-01`) execute exclusively between **01:00 AM and 04:30 AM** (3.5 hours/day).
* The remaining **20.5 hours/day** (85.4% of the day) are idle. Dynamic standby hibernation reduces monthly spend from ₹9,700 to ₹4,500.

---

## 4. Orphaned Resource Detection Criteria

Cloud providers continue charging for provisioned storage and reserved public IPs even when no virtual machine is attached to them.

1. **Unattached Block Volumes (EBS / Managed Disks)**:
   * **Detection Rule**: `attached_vm == null` AND `total_read_write_iops == 0` for $\ge 30$ consecutive days.
   * **Remediation**: Create a cold storage recovery snapshot (₹0.80/GB) and issue `az disk delete --yes`.
   * **Identified in ZenithFlow**:
     - `vol-noida-backup-snap-orphaned` (500 GB SSD, 45 days detached): ₹4,200/mo waste.
     - `vol-blr-staging-unattached-1tb` (1000 GB Ultra SSD, 60 days detached): ₹8,400/mo waste.
2. **Unallocated Static Public IPs**:
   * **Detection Rule**: Public IPv4 allocation not mapped to any running NIC or Load Balancer.
   * **Provider Penalty**: Charged at ₹1.92/hr idle penalty fee.
   * **Identified in ZenithFlow**: `ip-mumbai-legacy-gw-unallocated` (₹1,400/mo waste). Releasing it saves 100% of the cost.

---

## 5. Root Cause Decomposition: 40% Six-Month Bill Increase

The problem statement requires explaining why monthly cloud spend expanded by **+40.0%** over the previous 6 months (growing from ₹2,95,000 to ₹4,13,000+).

| Root Cause Category | Monthly Waste Generated | % of Total Bill Growth | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| **Dev 24/7 Weekend Idling** | ₹45,200 / month | 38.3% of surge | Enforce automated 8 PM–8 AM & weekend shutdown schedules |
| **Over-Provisioned Compute Sizing** | ₹60,200 / month | 51.0% of surge | Peak-safe rightsizing of D8s/D16s instances to D2s/D4s |
| **Orphaned Disks & Idle Public IPs** | ₹12,600 / month | 10.7% of surge | 1-click snapshot archive & automated resource deletion |
| **Total Unchecked Cloud Waste** | **₹1,18,000 / month** | **100.0%** | **SmartCloud Optimizer Autonomous Remediation Plan** |

---

## 6. Environmental, Social & Governance (ESG) Sustainability Model

Compute energy consumption and carbon emissions are calculated based on grid emission standards published by the **Central Electricity Authority (CEA) of India**:

* **Average Idle Server Draw**: **0.08 kWh** per idle vCPU-hour.
* **Indian National Grid Emission Factor**: **0.82 kg CO₂e / kWh**.
* **Formulas**:
  $$\text{Monthly kWh Saved} = \sum (\text{Optimized Cores} \times 0.08 \times 730 \times 0.45)$$
  $$\text{Monthly CO}_2\text{e Avoided (kg)} = \text{Monthly kWh Saved} \times 0.82$$
  $$\text{Tree Absorption Equivalent} = \frac{\text{Monthly CO}_2\text{e Avoided}}{21.7 \text{ kg CO}_2/\text{tree/year}}$$
* **ZenithFlow Fleet Impact**: Remediating over-provisioned nodes avoids **2,715 kg CO₂e / month**, saving **3,311 kWh** of electricity, equivalent to planting **125 mature trees**.

---

## 7. Assumptions & Engineering Simplifications

1. **Network Egress Fees**: In accordance with the hackathon brief, standard intra-region VNet traffic is modeled at ₹0, and internet egress is capped at base provider allowances.
2. **Storage Snapshot Warm-up**: Deleting orphaned volumes archives a cold snapshot before termination; cold storage snapshot cost is factored at 10% of active SSD cost.
3. **Prorated Hourly Granularity**: Billing updates reflect second-by-second prorated compute rates, consistent with Azure Resource Manager (ARM) billing meters.
