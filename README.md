# SmartCloud Optimizer — Azure FinOps & VM Resource Scaler

SmartCloud Optimizer is a professional FinOps dashboard and autonomous resource scaling platform for Microsoft Azure Virtual Machines.

Based on historical and predictive time-series workload patterns (such as off-hours idle drops between 7:00 PM and 5:00 AM on weekdays, or high-throughput batch bursts), SmartCloud Optimizer dynamically schedules rightsizing, eliminates server bottlenecks, and reduces cloud compute spend by up to 38%.

---

## Key Features

1. **Enterprise FinOps UI Theme**:
   - Crisp, modern aesthetic modeled after top cloud management consoles (custom pastel summary cards, royal blue navigation, interactive Recharts spline & grouped bar visualizations).
   - Instant currency switcher: **INR (₹)** and **USD ($)**.

2. **Authentication & Multi-Tenant Support**:
   - Full login system with fast 1-click demo profiles:
     - **Northwind Logistics SaaS** (E-Commerce fleet with high off-hours night downsize potential)
     - **Contoso HealthTech** (Healthcare analytics fleet with critical ingestion bottleneck risk)
   - Profile management, tenant switcher, and session sign out.

3. **Customer VM Fleet & Specification Inspector**:
   - Live inventory of all Azure VMs owned by the customer.
   - Deep hardware specifications upon selecting any VM:
     - **vCPU Cores**, **RAM (GB)**, **Storage (GB SSD & IOPS)**, **Bandwidth (Mbps)**, **OS**, **Region**, **Private/Public IP**, and **Hourly Rate**.
   - Real-time gauge metrics for live CPU %, RAM %, and Disk IOPS.

4. **Resource Metrics & Granular Telemetry**:
   - Time ranges: **1 Day**, **7 Days**, **30 Days**.
   - Custom granularities:
     - **1 Day**: `10 Mins`, `30 Mins`, `1 Hour`
     - **7 Days**: `10 Mins`, `30 Mins`, `1 Hour`
     - **30 Days**: `1 Day`
   - AI Predictive Demand overlay, visible 85% Bottleneck danger threshold, and highlighted 7:00 PM – 5:00 AM off-hours window.

5. **Bottleneck & Scale-Down Predictive Notifications**:
   - **Bottleneck Prevention**:
     - Detects forecasted spikes (e.g. 93.8% CPU peak).
     - If Auto-Scale permission is approved: Automatically upscales SKU to prevent service degradation.
     - If Auto-Scale permission is not approved: Dispatches alert explaining the bottleneck and providing a 1-click upgrade option.
   - **Underutilization Downsizing**:
     - Detects idle night periods (7 PM - 5 AM) and provides itemized cost formulas showing exactly how much monthly money is saved.
   - **Transparent Mathematical Calculation**:
     - Itemized breakdown showing baseline 24/7 spend, peak business hours, downscaled off-hours, and net savings formula.
   - **Interactive Scenario Simulator**:
     - "Simulate Traffic Surge (Bottleneck)" and "Simulate 7 PM – 5 AM Night Drop" buttons to test real-time dynamic behavior.

6. **Autonomous Scaling & Dynamic Billing Consent (Bottom Section)**:
   - Dedicated agreement switch allowing the customer to grant permission for automated scaling.
   - Transparent billing explanation: Invoices are calculated on prorated hourly consumption rather than static flat-rate allocation.

---

## Tech Stack

- **Frontend**: React 18, Vite, Recharts, Lucide Icons, Plus Jakarta Sans typography.
- **Backend**: Python 3.11, FastAPI, Pydantic, Uvicorn.

---

## Quickstart

### 1. Start Backend API
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend Dev Server
```bash
cd frontend
npm install
npm run dev
```

Open:
- **Frontend Dashboard**: `http://localhost:5173`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
