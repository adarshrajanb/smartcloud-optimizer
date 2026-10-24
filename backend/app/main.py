from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

app = FastAPI(title="SmartCloud Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_metric_series(vm_name: str, hours: int, granularity_minutes: int):
    points = []
    now = datetime.utcnow().replace(microsecond=0)
    total_points = max(1, (hours * 60) // granularity_minutes)
    for index in range(total_points):
        timestamp = now - timedelta(minutes=(hours * 60) - (index * granularity_minutes))
        hour = timestamp.hour
        base_cpu = 46 + (index % 13) * 2.4
        if vm_name == "web-prod-01":
            base_cpu = 58 + (index % 8) * 3.2
        elif vm_name == "analytics-02":
            base_cpu = 38 + (index % 12) * 2.6
        elif vm_name == "batch-03":
            base_cpu = 18 + (index % 10) * 1.7
        cpu = max(8, min(95, base_cpu + (1 if hour in (8, 9, 10, 17, 18) else -2) + ((index % 5) - 2) * 1.8))
        memory = max(22, min(91, cpu * 0.84 + (index % 4) * 2.5))
        disk = max(12, min(88, 52 + (index % 7) * 4.5 + (0.8 if hour >= 20 else -0.7)))
        network = max(30, min(420, 165 + (index % 9) * 20 + (hour * 4)))
        points.append({
            "timestamp": timestamp.isoformat(timespec="seconds") + "Z",
            "cpu": round(cpu, 1),
            "memory": round(memory, 1),
            "disk": round(disk, 1),
            "network": round(network, 1),
        })
    return points


def build_vm_data(vm_id: str):
    vm_map = {
        "vm-web-prod": {
            "id": "vm-web-prod",
            "name": "web-prod-01",
            "customerId": "cust-northwind",
            "status": "Active",
            "region": "West Europe",
            "resourceGroup": "prod-web-rg",
            "specs": {"cores": 8, "ramGb": 32, "storageGb": 512, "os": "Ubuntu 22.04"},
            "currentSpend": 18400,
            "projectedSpend": 13880,
            "savings": 4520,
            "autoScaleEnabled": True,
            "recommendation": {
                "type": "downsize",
                "title": "Downsize 2 vCPU / 8 GB for off-hours idle periods",
                "confidence": 92,
                "reason": "Average CPU usage stayed at 18% between 7 PM and 5 AM, with peak memory under 41% for the last 7 days.",
                "formula": "₹18,400 current spend - ₹4,520 predicted savings = ₹13,880 projected spend",
                "billingImpact": "Projected monthly billing reduces by 24.6% if the automation schedule is approved.",
            },
            "metrics": {
                "1d": {"10m": make_metric_series("web-prod-01", 24, 10), "30m": make_metric_series("web-prod-01", 24, 30), "1h": make_metric_series("web-prod-01", 24, 60)},
                "7d": {"10m": make_metric_series("web-prod-01", 168, 10), "30m": make_metric_series("web-prod-01", 168, 30), "1h": make_metric_series("web-prod-01", 168, 60)},
                "30d": {"1d": make_metric_series("web-prod-01", 720, 1440)},
            },
        },
        "vm-analytics": {
            "id": "vm-analytics",
            "name": "analytics-02",
            "customerId": "cust-northwind",
            "status": "Active",
            "region": "Central US",
            "resourceGroup": "analytics-rg",
            "specs": {"cores": 16, "ramGb": 64, "storageGb": 1024, "os": "Windows Server 2022"},
            "currentSpend": 27250,
            "projectedSpend": 29580,
            "savings": 0,
            "autoScaleEnabled": False,
            "recommendation": {
                "type": "upgrade",
                "title": "Upsize compute during evening batch window",
                "confidence": 88,
                "reason": "P95 CPU is touching 92% and memory remains above 80% for 3 consecutive daily windows, creating an expected bottleneck.",
                "formula": "Peak CPU 92% > 80% threshold and memory 81% -> add 4 vCPU and 16 GB RAM to protect SLA",
                "billingImpact": "Projected monthly spend rises by ₹2,330 to prevent performance degradation and avoid incident cost.",
            },
            "metrics": {
                "1d": {"10m": make_metric_series("analytics-02", 24, 10), "30m": make_metric_series("analytics-02", 24, 30), "1h": make_metric_series("analytics-02", 24, 60)},
                "7d": {"10m": make_metric_series("analytics-02", 168, 10), "30m": make_metric_series("analytics-02", 168, 30), "1h": make_metric_series("analytics-02", 168, 60)},
                "30d": {"1d": make_metric_series("analytics-02", 720, 1440)},
            },
        },
        "vm-batch": {
            "id": "vm-batch",
            "name": "batch-03",
            "customerId": "cust-northwind",
            "status": "Paused",
            "region": "Southeast Asia",
            "resourceGroup": "batch-rg",
            "specs": {"cores": 4, "ramGb": 16, "storageGb": 256, "os": "Ubuntu 20.04"},
            "currentSpend": 9700,
            "projectedSpend": 6200,
            "savings": 3500,
            "autoScaleEnabled": True,
            "recommendation": {
                "type": "downsize",
                "title": "Pause and right-size overnight batch workloads",
                "confidence": 94,
                "reason": "Batch jobs complete before 6 AM and use less than 22% CPU in the 7 PM–5 AM window, so a reduced configuration is safe.",
                "formula": "₹9,700 current spend - ₹3,500 scheduled savings = ₹6,200 projected spend",
                "billingImpact": "Savings are realized while keeping the same SLA window by rescheduling tasks to night periods.",
            },
            "metrics": {
                "1d": {"10m": make_metric_series("batch-03", 24, 10), "30m": make_metric_series("batch-03", 24, 30), "1h": make_metric_series("batch-03", 24, 60)},
                "7d": {"10m": make_metric_series("batch-03", 168, 10), "30m": make_metric_series("batch-03", 168, 30), "1h": make_metric_series("batch-03", 168, 60)},
                "30d": {"1d": make_metric_series("batch-03", 720, 1440)},
            },
        },
    }
    return vm_map.get(vm_id)


customer = {
    "id": "cust-northwind",
    "name": "Northwind Logistics",
    "company": "Northwind Logistics",
    "industry": "Supply chain",
    "vmIds": ["vm-web-prod", "vm-analytics", "vm-batch"],
    "budgetLimit": 45000,
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/customers")
def get_customers():
    return {"customers": [customer]}


@app.get("/api/vms")
def get_vms():
    return {
        "customer": customer,
        "vms": [build_vm_data(vm_id) for vm_id in customer["vmIds"]],
    }


@app.get("/api/vm/{vm_id}")
def get_vm(vm_id: str):
    vm = build_vm_data(vm_id)
    if vm is None:
        return {"error": "VM not found"}
    return {"vm": vm}


@app.get("/api/dashboard/{customer_id}")
def get_dashboard(customer_id: str):
    vms = [build_vm_data(vm_id) for vm_id in customer["vmIds"]]
    current_spend = sum(vm["currentSpend"] for vm in vms)
    projected_spend = sum(vm["projectedSpend"] for vm in vms)
    savings = sum(vm["savings"] for vm in vms)
    return {
        "customer": customer,
        "summary": {
            "currentSpend": current_spend,
            "projectedSpend": projected_spend,
            "savings": savings,
            "automationEnabled": any(vm["autoScaleEnabled"] for vm in vms),
        },
        "vms": vms,
    }


@app.get("/")
def root():
    return {"message": "SmartCloud Optimizer API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
