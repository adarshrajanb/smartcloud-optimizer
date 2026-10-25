"""
SmartCloud Optimizer - UTHO Challenge Dataset & Optimization Engine
===================================================================
Provides realistic infrastructure telemetry for ZenithFlow Technologies Pvt Ltd,
a mid-sized Indian SaaS company operating across Noida, Bangalore, and Mumbai.

Fleet: 56 managed resources across Production, Staging, and Development:
  - 38 Virtual Machines (Prod, Staging, Dev)
  - 12 Block Volumes (including unattached orphaned disks)
  - 6 Elastic Public IPs (including unallocated unused IPs)

Workload Patterns Featured:
  1. Steady low-usage VMs (overprovisioned, 6-12% CPU)
  2. Bursty workloads with high p95/p99 peaks (peak-safe: protected against downscaling)
  3. Batch processing jobs idle most of the day (scheduled hibernation)
  4. Dev environments running 24/7 needlessly on weekends (weekend shutoff)
  5. Orphaned resources (unattached SSDs and idle elastic IPs)
  6. Genuine anomaly (runaway CPU/memory staging thread)
"""

from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

REGIONS = ["Noida (North)", "Bangalore (South)", "Mumbai (West)"]
ENVIRONMENTS = ["prod", "staging", "dev"]
TEAMS = ["Backend Platform", "Data Engineering", "Core DevOps", "Payments & Billing", "Growth & Web"]

def generate_30d_series(base_cpu: float, p95_cpu: float, base_ram: float, max_iops: int, pattern: str = "normal"):
    series = []
    now = datetime.utcnow()
    # 30 daily summary points with hourly sample characteristics
    for day_idx in range(30, -1, -1):
        dt = now - timedelta(days=day_idx)
        is_weekend = dt.weekday() >= 5
        
        if pattern == "weekend_idle" and is_weekend:
            cpu = round(random.uniform(2.0, 5.5), 1)
            ram = round(base_ram * 0.4, 1)
            disk = 120
            net = round(random.uniform(0.5, 2.0), 1)
        elif pattern == "batch_night":
            cpu = round(random.uniform(78.0, 92.0) if day_idx % 2 == 0 else random.uniform(4.0, 8.0), 1)
            ram = round(base_ram * 0.9 if cpu > 50 else base_ram * 0.35, 1)
            disk = round(max_iops * 0.75 if cpu > 50 else max_iops * 0.08)
            net = round(random.uniform(35.0, 75.0) if cpu > 50 else random.uniform(1.0, 3.5), 1)
        elif pattern == "bursty":
            cpu = round(random.uniform(p95_cpu - 8.0, p95_cpu + 5.0) if day_idx % 3 == 0 else random.uniform(18.0, 32.0), 1)
            ram = round(min(90.0, base_ram + random.uniform(-4, 6)), 1)
            disk = round(max_iops * (0.85 if cpu > 70 else 0.3))
            net = round(random.uniform(25.0, 80.0), 1)
        elif pattern == "anomaly" and day_idx <= 2:
            cpu = round(random.uniform(96.5, 99.8), 1)
            ram = round(min(98.5, base_ram + 40.0), 1)
            disk = round(max_iops * 0.92)
            net = round(random.uniform(4.0, 8.0), 1)
        else:
            cpu = round(max(3.0, min(95.0, base_cpu + random.uniform(-3.5, 3.5))), 1)
            ram = round(max(8.0, min(92.0, base_ram + random.uniform(-2.0, 2.0))), 1)
            disk = round(max(50, min(max_iops, int(max_iops * (cpu / 120.0)))))
            net = round(max(1.0, cpu * 0.4 + random.uniform(-2, 3)), 1)

        series.append({
            "timestamp": dt.isoformat() + "Z",
            "timeLabel": dt.strftime("%b %d"),
            "fullDate": dt.strftime("%A, %b %d, %Y"),
            "cpu": cpu,
            "predictedCpu": round(min(100.0, cpu + random.uniform(-1.0, 2.0)), 1),
            "ram": ram,
            "memory": ram,
            "predictedRam": round(min(100.0, ram + 1.2), 1),
            "disk": disk,
            "predictedDisk": disk + 25,
            "network": net,
            "networkIn": round(net * 0.65, 1),
            "networkOut": round(net * 0.35, 1),
            "isNightWindow": False,
            "isBottleneck": cpu >= 80.0,
            "isLiveTick": False
        })
    return series

def build_zenith_fleet() -> Dict[str, Any]:
    vms: Dict[str, Any] = {}
    
    # -------------------------------------------------------------
    # 1. Flagship Production VMs (Noida, Bangalore, Mumbai)
    # -------------------------------------------------------------
    vms["zenith-auth-api-01"] = {
        "id": "zenith-auth-api-01",
        "name": "auth-core-prod-01",
        "type": "VM",
        "customerId": "cust-zenith",
        "region": "Bangalore (South)",
        "environment": "prod",
        "team": "Core Platform & DevOps",
        "status": "Healthy",
        "vmSize": "Standard_D8s_v5",
        "size": "Standard_D8s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.0.1.10",
        "publicIp": "13.233.45.101",
        "specs": {"cores": 8, "ramGb": 32, "storageGb": 256, "storageType": "Premium SSD", "maxIops": 6400, "bandwidthMbps": 10000},
        "cores": 8, "ram": 32, "ramGb": 32, "storage": 256, "storageGb": 256, "maxIops": 6400, "bandwidth": 10000,
        "currentHourlyRate": 0.384,
        "currentSpend": 18400,
        "projectedSpend": 13880,
        "savings": 4520,
        "p95Cpu": 24.2,
        "p99Cpu": 31.0,
        "p95Ram": 38.5,
        "avgCpu": 14.8,
        "avgRam": 32.0,
        "cpuUsage": 14.8,
        "ramUsage": 32.0,
        "diskUsage": 1850,
        "networkIn": 24.5,
        "networkOut": 18.2,
        "autoScaleEnabled": True,
        "workloadProfile": "JWT & OAuth2 Authentication Authority",
        "recommendation": {
            "type": "downsize",
            "action": "resize",
            "title": "Safe Rightsizing to Standard_D4s_v5 (p95 Peak Safe)",
            "urgency": "High Cost Optimization",
            "confidence": 96,
            "reason": "Historical p95 CPU peak is 24.2% across 30 days. Downsizing from 8 vCPU to 4 vCPU leaves 45% headroom above p99 peak without any performance degradation.",
            "formula": "Downsizing from ₹25.20/hr to ₹12.60/hr saves ₹4,520/month with p95 safety guarantee.",
            "billingImpact": "Invoice reduced from ₹18,400 to ₹13,880/month (-24.6%).",
            "targetSku": "Standard_D4s_v5 (4 vCPU, 16 GB RAM)",
            "accepted": True
        },
        "series": generate_30d_series(14.8, 24.2, 32.0, 6400, "normal")
    }

    vms["zenith-checkout-api-01"] = {
        "id": "zenith-checkout-api-01",
        "name": "checkout-order-prod-01",
        "type": "VM",
        "customerId": "cust-zenith",
        "region": "Mumbai (West)",
        "environment": "prod",
        "team": "Payments & Billing",
        "status": "Bottleneck Warning",
        "vmSize": "Standard_E8s_v5",
        "size": "Standard_E8s_v5",
        "os": "Debian 12 Bookworm",
        "privateIp": "10.0.2.14",
        "publicIp": "13.127.88.42",
        "specs": {"cores": 8, "ramGb": 64, "storageGb": 512, "storageType": "Ultra SSD", "maxIops": 16000, "bandwidthMbps": 12500},
        "cores": 8, "ram": 64, "ramGb": 64, "storage": 512, "storageGb": 512, "maxIops": 16000, "bandwidth": 12500,
        "currentHourlyRate": 0.522,
        "currentSpend": 26800,
        "projectedSpend": 26800,
        "savings": 0,
        "p95Cpu": 88.4,
        "p99Cpu": 94.8,
        "p95Ram": 76.0,
        "avgCpu": 48.0,
        "avgRam": 64.0,
        "cpuUsage": 82.5,
        "ramUsage": 72.0,
        "diskUsage": 12400,
        "networkIn": 68.0,
        "networkOut": 54.0,
        "autoScaleEnabled": False,
        "workloadProfile": "Checkout Transaction Engine & PCI-DSS Store",
        "recommendation": {
            "type": "upgrade",
            "action": "resize",
            "title": "DO NOT DOWNSCALE: Peak-Safe Alert - p99 Spike Hits 94.8%",
            "urgency": "High SLA Protection",
            "confidence": 98,
            "reason": "Although average CPU is 48%, p99 peak hits 94.8% during lunch & dinner flash sales. Downscaling would trigger latency spikes and checkout drops. Recommend auto-scaling or upgrading to E16s during flash sales.",
            "formula": "Protect ₹1.2 Cr daily transaction volume by maintaining headroom.",
            "billingImpact": "Retain baseline capacity to protect revenue; auto-scale burst only.",
            "targetSku": "Standard_E16s_v5 (Scale-Up on Demand)",
            "accepted": False
        },
        "series": generate_30d_series(48.0, 88.4, 64.0, 16000, "bursty")
    }

    vms["zenith-nightly-recon-01"] = {
        "id": "zenith-nightly-recon-01",
        "name": "batch-reconciliation-01",
        "type": "VM",
        "customerId": "cust-zenith",
        "region": "Noida (North)",
        "environment": "prod",
        "team": "Data Engineering",
        "status": "Healthy",
        "vmSize": "Standard_D4s_v5",
        "size": "Standard_D4s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.0.3.22",
        "publicIp": "13.232.19.80",
        "specs": {"cores": 4, "ramGb": 16, "storageGb": 256, "storageType": "Premium SSD", "maxIops": 6400, "bandwidthMbps": 5000},
        "cores": 4, "ram": 16, "ramGb": 16, "storage": 256, "storageGb": 256, "maxIops": 6400, "bandwidth": 5000,
        "currentHourlyRate": 0.192,
        "currentSpend": 9700,
        "projectedSpend": 4500,
        "savings": 5200,
        "p95Cpu": 82.0,
        "p99Cpu": 88.5,
        "p95Ram": 72.0,
        "avgCpu": 8.5,
        "avgRam": 18.0,
        "cpuUsage": 6.2,
        "ramUsage": 16.5,
        "diskUsage": 840,
        "networkIn": 8.2,
        "networkOut": 5.1,
        "autoScaleEnabled": True,
        "workloadProfile": "Nightly Settlement Batch Worker (01:00 - 04:30 AM)",
        "recommendation": {
            "type": "schedule_offhours",
            "action": "schedule",
            "title": "Scheduled Daytime Hibernation (04:30 AM – 01:00 AM Daily)",
            "urgency": "High Savings Opportunity",
            "confidence": 95,
            "reason": "This batch worker runs exclusively between 01:00 and 04:30 AM (3.5 hrs/day). For the remaining 20.5 hours daily, CPU is 4-8%. Hibernating during idle hours saves ₹5,200/mo.",
            "formula": "20.5 idle hrs/day × ₹13.28 base/hr × 30 days = ₹8,167 gross → calibrated ₹5,200 net savings with pre-warming.",
            "billingImpact": "Spend reduces from ₹9,700 to ₹4,500/mo (-53.6%).",
            "targetSku": "Standard_B2s (Off-Hours Standby) / Scheduled Wakeup",
            "accepted": True
        },
        "series": generate_30d_series(8.5, 82.0, 18.0, 6400, "batch_night")
    }

    # -------------------------------------------------------------
    # 2. Development & Staging Workloads (Weekend Idle & Runaway Anomaly)
    # -------------------------------------------------------------
    vms["zenith-dev-cluster-01"] = {
        "id": "zenith-dev-cluster-01",
        "name": "dev-k8s-worker-pool-01",
        "type": "VM",
        "customerId": "cust-zenith",
        "region": "Bangalore (South)",
        "environment": "dev",
        "team": "Core Platform & DevOps",
        "status": "Healthy",
        "vmSize": "Standard_D16s_v5",
        "size": "Standard_D16s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.0.10.4",
        "publicIp": "13.235.12.91",
        "specs": {"cores": 16, "ramGb": 64, "storageGb": 512, "storageType": "Standard SSD", "maxIops": 6000, "bandwidthMbps": 8000},
        "cores": 16, "ram": 64, "ramGb": 64, "storage": 512, "storageGb": 512, "maxIops": 6000, "bandwidth": 8000,
        "currentHourlyRate": 0.768,
        "currentSpend": 38400,
        "projectedSpend": 15800,
        "savings": 22600,
        "p95Cpu": 32.0,
        "p99Cpu": 41.0,
        "p95Ram": 35.0,
        "avgCpu": 9.2,
        "avgRam": 22.0,
        "cpuUsage": 8.0,
        "ramUsage": 21.0,
        "diskUsage": 1200,
        "networkIn": 4.5,
        "networkOut": 3.8,
        "autoScaleEnabled": True,
        "workloadProfile": "Engineering Dev K8s Worker Nodes (24/7 Waste)",
        "recommendation": {
            "type": "schedule_offhours",
            "action": "schedule",
            "title": "Automate Dev Shutdown (Weeknights 8 PM - 8 AM + Full Weekends)",
            "urgency": "Massive Cost Recovery",
            "confidence": 99,
            "reason": "Engineering team is offline between 8 PM and 8 AM on weekdays, and completely offline Saturdays & Sundays (108 idle hours/week = 64% of month). Auto-shutdown saves ₹22,600/month.",
            "formula": "108 idle hrs/week × 4.3 weeks = 464 hrs/mo saved × ₹53.76/hr = ₹24,944 gross savings.",
            "billingImpact": "Dev cluster spend reduced from ₹38,400 to ₹15,800/month (-58.8%).",
            "targetSku": "Auto-Deallocate (₹0/hr during 108 off-hours/wk)",
            "accepted": True
        },
        "series": generate_30d_series(9.2, 32.0, 22.0, 6000, "weekend_idle")
    }

    vms["zenith-staging-worker-02"] = {
        "id": "zenith-staging-worker-02",
        "name": "staging-crawler-worker-02",
        "type": "VM",
        "customerId": "cust-zenith",
        "region": "Noida (North)",
        "environment": "staging",
        "team": "Data Engineering",
        "status": "Runaway Anomaly",
        "vmSize": "Standard_D8s_v5",
        "size": "Standard_D8s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.0.12.8",
        "publicIp": "13.234.90.11",
        "specs": {"cores": 8, "ramGb": 32, "storageGb": 256, "storageType": "Standard SSD", "maxIops": 3200, "bandwidthMbps": 5000},
        "cores": 8, "ram": 32, "ramGb": 32, "storage": 256, "storageGb": 256, "maxIops": 3200, "bandwidth": 5000,
        "currentHourlyRate": 0.384,
        "currentSpend": 18400,
        "projectedSpend": 4800,
        "savings": 13600,
        "p95Cpu": 99.2,
        "p99Cpu": 99.9,
        "p95Ram": 94.0,
        "avgCpu": 89.0,
        "avgRam": 88.0,
        "cpuUsage": 99.4,
        "ramUsage": 95.2,
        "diskUsage": 3100,
        "networkIn": 1.2,
        "networkOut": 0.8,
        "autoScaleEnabled": False,
        "workloadProfile": "GENUINE ANOMALY: Runaway Regex Loop (Pegged at 100% CPU)",
        "recommendation": {
            "type": "terminate_idle",
            "action": "stop",
            "title": "Kill Runaway Worker Process & Downsize Staging Node to D2s",
            "urgency": "Critical Anomaly Detected",
            "confidence": 98,
            "reason": "Process 'python3 scraper_worker.py' has consumed 99.4% CPU continuously for 44 hours with near-zero network output, indicating an unhandled infinite regex loop. Staging node is burning ₹18,400/mo.",
            "formula": "Restarting worker and downsizing staging instance to Standard_D2s_v5 saves ₹13,600/month.",
            "billingImpact": "Eliminates ₹13,600/mo in rogue compute waste.",
            "targetSku": "Standard_D2s_v5 (2 vCPU, 8 GB RAM)",
            "accepted": True
        },
        "series": generate_30d_series(89.0, 99.2, 88.0, 3200, "anomaly")
    }

    # -------------------------------------------------------------
    # 3. Orphaned Resources (Unattached Block Volumes & Unused IPs)
    # -------------------------------------------------------------
    vms["vol-noida-backup-snap-orphaned"] = {
        "id": "vol-noida-backup-snap-orphaned",
        "name": "noida-migrated-db-vol-500g",
        "type": "Volume",
        "customerId": "cust-zenith",
        "region": "Noida (North)",
        "environment": "prod",
        "team": "Core Platform & DevOps",
        "status": "Orphaned Unattached",
        "vmSize": "Block_Storage_500GB_SSD",
        "size": "500 GB SSD",
        "os": "Unattached Disk Volume",
        "privateIp": "N/A",
        "publicIp": "N/A",
        "specs": {"cores": 0, "ramGb": 0, "storageGb": 500, "storageType": "Provisioned Premium SSD", "maxIops": 3000, "bandwidthMbps": 0},
        "cores": 0, "ram": 0, "ramGb": 0, "storage": 500, "storageGb": 500, "maxIops": 3000, "bandwidth": 0,
        "currentHourlyRate": 0.088,
        "currentSpend": 4200,
        "projectedSpend": 0,
        "savings": 4200,
        "p95Cpu": 0.0, "p99Cpu": 0.0, "p95Ram": 0.0, "avgCpu": 0.0, "avgRam": 0.0,
        "cpuUsage": 0.0, "ramUsage": 0.0, "diskUsage": 0, "networkIn": 0.0, "networkOut": 0.0,
        "autoScaleEnabled": False,
        "workloadProfile": "ORPHANED DISK: Detached from decommissioned DB 45 days ago",
        "recommendation": {
            "type": "delete_orphan",
            "action": "delete",
            "title": "Snapshot & Delete Orphaned 500GB SSD Block Volume",
            "urgency": "Zero Risk Pure Savings",
            "confidence": 99,
            "reason": "Volume has recorded exactly 0 read/write IOPS for 45 consecutive days. Left behind after MySQL 5.7 to 8.0 migration. Creates pure waste of ₹4,200/mo.",
            "formula": "500 GB × ₹8.40/GB/month = ₹4,200/month recurring cost eliminated.",
            "billingImpact": "Instant 100% cost elimination on this storage volume.",
            "targetSku": "Archive Snapshot to Cold Storage (₹0.80/GB) or Delete",
            "accepted": True
        },
        "series": generate_30d_series(0.0, 0.0, 0.0, 3000, "normal")
    }

    vms["vol-blr-staging-unattached-1tb"] = {
        "id": "vol-blr-staging-unattached-1tb",
        "name": "blr-staging-loadtest-vol-1tb",
        "type": "Volume",
        "customerId": "cust-zenith",
        "region": "Bangalore (South)",
        "environment": "staging",
        "team": "Backend Platform",
        "status": "Orphaned Unattached",
        "vmSize": "Block_Storage_1000GB_SSD",
        "size": "1000 GB SSD",
        "os": "Unattached Disk Volume",
        "privateIp": "N/A",
        "publicIp": "N/A",
        "specs": {"cores": 0, "ramGb": 0, "storageGb": 1000, "storageType": "Ultra SSD", "maxIops": 8000, "bandwidthMbps": 0},
        "cores": 0, "ram": 0, "ramGb": 0, "storage": 1000, "storageGb": 1000, "maxIops": 8000, "bandwidth": 0,
        "currentHourlyRate": 0.176,
        "currentSpend": 8400,
        "projectedSpend": 0,
        "savings": 8400,
        "p95Cpu": 0.0, "p99Cpu": 0.0, "p95Ram": 0.0, "avgCpu": 0.0, "avgRam": 0.0,
        "cpuUsage": 0.0, "ramUsage": 0.0, "diskUsage": 0, "networkIn": 0.0, "networkOut": 0.0,
        "autoScaleEnabled": False,
        "workloadProfile": "ORPHANED DISK: Detached from Staging Load Test Cluster in August",
        "recommendation": {
            "type": "delete_orphan",
            "action": "delete",
            "title": "Purge Orphaned 1TB Ultra SSD Volume (60 Days Idle)",
            "urgency": "Zero Risk Pure Savings",
            "confidence": 99,
            "reason": "1000 GB volume provisioned for a one-time performance benchmark in August. Was detached when instances were terminated but never deleted. Wasting ₹8,400/month.",
            "formula": "1000 GB × ₹8.40/GB/month = ₹8,400/month recurring cost eliminated.",
            "billingImpact": "Saves ₹8,400/mo immediately upon deletion.",
            "targetSku": "Permanently Delete Unattached Block Volume",
            "accepted": True
        },
        "series": generate_30d_series(0.0, 0.0, 0.0, 8000, "normal")
    }

    vms["ip-mumbai-legacy-gw-unallocated"] = {
        "id": "ip-mumbai-legacy-gw-unallocated",
        "name": "mumbai-static-ip-unallocated-01",
        "type": "IP",
        "customerId": "cust-zenith",
        "region": "Mumbai (West)",
        "environment": "prod",
        "team": "Core Platform & DevOps",
        "status": "Orphaned Unattached",
        "vmSize": "Reserved_Static_Public_IP",
        "size": "Static Public IP",
        "os": "Unallocated Elastic IP",
        "privateIp": "N/A",
        "publicIp": "13.235.40.11",
        "specs": {"cores": 0, "ramGb": 0, "storageGb": 0, "storageType": "IPv4 Network Allocation", "maxIops": 0, "bandwidthMbps": 0},
        "cores": 0, "ram": 0, "ramGb": 0, "storage": 0, "storageGb": 0, "maxIops": 0, "bandwidth": 0,
        "currentHourlyRate": 0.030,
        "currentSpend": 1400,
        "projectedSpend": 0,
        "savings": 1400,
        "p95Cpu": 0.0, "p99Cpu": 0.0, "p95Ram": 0.0, "avgCpu": 0.0, "avgRam": 0.0,
        "cpuUsage": 0.0, "ramUsage": 0.0, "diskUsage": 0, "networkIn": 0.0, "networkOut": 0.0,
        "autoScaleEnabled": False,
        "workloadProfile": "UNUSED IP: Cloud provider penalizes unattached static IPs",
        "recommendation": {
            "type": "delete_orphan",
            "action": "delete",
            "title": "Release Unused Reserved Public IPv4 Address",
            "urgency": "Zero Risk Pure Savings",
            "confidence": 99,
            "reason": "Cloud providers charge an idle penalty fee for allocated public IPv4 addresses not associated with running instances. Releasing back to pool saves ₹1,400/month.",
            "formula": "730 hrs × ₹1.92/hr idle IP penalty = ₹1,400/month.",
            "billingImpact": "Eliminates ₹1,400/month in idle IPv4 allocation surcharges.",
            "targetSku": "Release IP to Cloud Provider Pool",
            "accepted": True
        },
        "series": generate_30d_series(0.0, 0.0, 0.0, 0, "normal")
    }

    # -------------------------------------------------------------
    # 4. Generate Remaining 48 Fleet Resources to meet 50-150 VM UTHO Scale
    # -------------------------------------------------------------
    tiers = [
        {"sku": "Standard_B2s", "cores": 2, "ram": 4, "disk": 128, "rate": 0.096, "spend": 4600},
        {"sku": "Standard_D2s_v5", "cores": 2, "ram": 8, "disk": 128, "rate": 0.144, "spend": 6900},
        {"sku": "Standard_D4s_v5", "cores": 4, "ram": 16, "disk": 256, "rate": 0.192, "spend": 9700},
        {"sku": "Standard_D8s_v5", "cores": 8, "ram": 32, "disk": 512, "rate": 0.384, "spend": 18400},
    ]

    names_pool = [
        ("user-service", "prod", "Backend Platform"),
        ("billing-service", "prod", "Payments & Billing"),
        ("catalog-service", "prod", "Backend Platform"),
        ("inventory-service", "prod", "Backend Platform"),
        ("notification-hub", "prod", "Core DevOps"),
        ("search-solr-node", "prod", "Growth & Web"),
        ("event-ingestion", "prod", "Data Engineering"),
        ("spark-etl-worker", "prod", "Data Engineering"),
        ("dev-auth-stub", "dev", "Core Platform & DevOps"),
        ("dev-payment-mock", "dev", "Payments & Billing"),
        ("dev-frontend-ssr", "dev", "Growth & Web"),
        ("staging-api-gateway", "staging", "Core DevOps"),
        ("staging-db-replica", "staging", "Data Engineering"),
        ("staging-load-generator", "staging", "Backend Platform"),
    ]

    counter = 1
    for region in REGIONS:
        for base_name, env, team in names_pool:
            if len(vms) >= 54:
                break
            tier = random.choice(tiers)
            res_id = f"zenith-{base_name}-{region[:3].lower()}-{counter:02d}"
            counter += 1
            
            # 60% chance of being downsize candidate
            is_overprov = (env != "prod") or (counter % 3 == 0)
            avg_cpu = round(random.uniform(5.0, 16.0) if is_overprov else random.uniform(25.0, 55.0), 1)
            p95_cpu = round(min(88.0, avg_cpu * 1.6 + random.uniform(2, 6)), 1)
            avg_ram = round(random.uniform(18.0, 38.0) if is_overprov else random.uniform(40.0, 70.0), 1)
            spend = tier["spend"]
            savings = round(spend * 0.35) if is_overprov else 0
            proj_spend = spend - savings

            rec_type = "downsize" if is_overprov else "nominal"
            action_type = "resize" if is_overprov else "monitor"
            rec_title = f"Scheduled Rightsizing to 50% Capacity (p95 Safe: {p95_cpu}%)" if is_overprov else f"Operating at Healthy Capacity Baseline ({avg_cpu}% CPU)"
            rec_reason = f"Resource telemetry demonstrates sustained p95 utilization of {p95_cpu}%. Downsizing eliminates overprovisioning while safely absorbing peak surges." if is_overprov else "Resource is sized appropriately for production traffic."

            vms[res_id] = {
                "id": res_id,
                "name": f"{base_name}-{counter:02d}",
                "type": "VM",
                "customerId": "cust-zenith",
                "region": region,
                "environment": env,
                "team": team,
                "status": "Over-Provisioned" if is_overprov else "Healthy",
                "vmSize": tier["sku"],
                "size": tier["sku"],
                "os": "Ubuntu Linux 22.04 LTS",
                "privateIp": f"10.0.{counter // 10}.{counter % 100 + 10}",
                "publicIp": f"13.{120 + counter}.{40 + (counter%20)}.{10 + counter}",
                "specs": {"cores": tier["cores"], "ramGb": tier["ram"], "storageGb": tier["disk"], "storageType": "Premium SSD", "maxIops": tier["cores"] * 800, "bandwidthMbps": tier["cores"] * 1000},
                "cores": tier["cores"], "ram": tier["ram"], "ramGb": tier["ram"], "storage": tier["disk"], "storageGb": tier["disk"], "maxIops": tier["cores"] * 800, "bandwidth": tier["cores"] * 1000,
                "currentHourlyRate": tier["rate"],
                "currentSpend": spend,
                "projectedSpend": proj_spend,
                "savings": savings,
                "p95Cpu": p95_cpu,
                "p99Cpu": round(min(96.0, p95_cpu * 1.15), 1),
                "p95Ram": round(min(90.0, avg_ram * 1.3), 1),
                "avgCpu": avg_cpu,
                "avgRam": avg_ram,
                "cpuUsage": avg_cpu,
                "ramUsage": avg_ram,
                "diskUsage": int(tier["cores"] * 800 * 0.28),
                "networkIn": round(avg_cpu * 0.4, 1),
                "networkOut": round(avg_cpu * 0.25, 1),
                "autoScaleEnabled": is_overprov,
                "workloadProfile": f"{team} - {env.upper()} Service Node",
                "recommendation": {
                    "type": rec_type,
                    "action": action_type,
                    "title": rec_title,
                    "urgency": "High Cost Optimization" if is_overprov else "Nominal",
                    "confidence": 94 if is_overprov else 90,
                    "reason": rec_reason,
                    "formula": f"Rightsizing from {tier['sku']} saves ₹{savings:,}/mo." if is_overprov else "Properly calibrated.",
                    "billingImpact": f"Spend reduced from ₹{spend:,} to ₹{proj_spend:,}/mo." if is_overprov else "Spend matches expected baseline.",
                    "targetSku": "Standard_B2s" if is_overprov else tier["sku"],
                    "accepted": is_overprov
                },
                "series": generate_30d_series(avg_cpu, p95_cpu, avg_ram, tier["cores"] * 800, "weekend_idle" if env == "dev" else "normal")
            }

    return vms


def get_zenith_customer(vms_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the customer metadata populated with all registered fleet IDs."""
    return {
        "id": "cust-zenith",
        "name": "ZenithFlow Technologies",
        "company": "ZenithFlow Technologies Pvt Ltd (Indian SaaS)",
        "industry": "B2B SaaS / Omnichannel Cloud Suite",
        "azureSubscriptionId": "sub-utho-zenith-india-prod-0924",
        "tenantName": "zenithflow.in",
        "primaryRegion": "Noida, Bangalore, Mumbai",
        "budgetLimit": 450000,
        "vmIds": list(vms_dict.keys()),
    }


def get_zenith_alerts(vms_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns the 4 mandatory UTHO alert categories with structured plain-language explanations:
      1. Unusual Spikes & Anomalies (e.g. infinite loop staging worker)
      2. Sudden Cost Growth Decomposition (explaining the 40% 6-month bill increase)
      3. Capacity Limit & Saturation Warnings (preventing production SLA drops)
      4. Budget Overrun Projections & Corrective Actions
    """
    total_spend = sum(v.get("currentSpend", 0) for v in vms_dict.values())
    projected_spend = sum(v.get("projectedSpend", v.get("currentSpend", 0)) for v in vms_dict.values())
    budget = 450000

    return [
        {
            "id": "alert-anomaly-staging-01",
            "type": "spike_anomaly",
            "severity": "CRITICAL",
            "title": "Unusual Spike: Runaway Regex Loop on Staging Worker (44 hrs @ 99.4% CPU)",
            "resourceId": "zenith-staging-worker-02",
            "resourceName": "staging-crawler-worker-02",
            "region": "Noida (North)",
            "environment": "staging",
            "impactCost": "₹18,400 / month wasted compute",
            "whatHappened": "Process 'python3 scraper_worker.py' entered an unhandled infinite regex evaluation loop on October 23 at 17:15 UTC. CPU utilization spiked from baseline 12% to 99.4% and has remained locked at 100% for 44 consecutive hours with zero meaningful network egress.",
            "whyItMatters": "This staging worker is non-production but consumes full Standard_D8s_v5 tier compute. Left unattended, it burns ₹18,400/month, blocks CI/CD integration suites, and emits unnecessary heat/CO₂.",
            "whatToDo": "1. SSH into the node and kill PID 4108 (`kill -9 4108`).\n2. Push the regex patch with atomic backtracking timeout.\n3. Downscale the staging host to Standard_D2s_v5 (2 vCPU, 8 GB RAM) to save ₹13,600/month.",
            "actionRequired": "Terminate & Resize",
            "savingsPotential": 13600,
        },
        {
            "id": "alert-cost-growth-decomp-02",
            "type": "cost_increase",
            "severity": "HIGH",
            "title": "Sudden Cost Growth Analysis: Why Monthly Bill Grew +40.0% in 6 Months",
            "resourceId": "fleet-wide",
            "resourceName": "ZenithFlow Fleet (56 Resources)",
            "region": "Multi-Region (Noida, Bangalore, Mumbai)",
            "environment": "all",
            "impactCost": "+₹1,18,000 / month increase (₹2.95L → ₹4.13L)",
            "whatHappened": "A telemetry-driven audit reveals the root causes of the 40% spend surge between May and October 2026 across 3 specific waste vectors:\n  • Dev clusters running 24/7 over weekends: ₹45,200/mo (64% idle hours).\n  • Over-provisioned Production D8s/D16s instances sized for imaginary peaks: ₹60,200/mo.\n  • 1.5 TB of unattached orphaned SSD volumes and unused public IPs from August DB migrations: ₹12,600/mo.",
            "whyItMatters": "Gross margin on ZenithFlow SaaS accounts has contracted by 4.2% due to unallocated infrastructure overhead. Cloud spend grew 3x faster than active customer accounts.",
            "whatToDo": "Activate SmartCloud Optimizer autonomous governance: (1) Accept dev weekend shutdown schedule, (2) One-click purge orphaned disks/IPs, (3) Rightsize over-provisioned nodes using p95 peak-safety thresholds.",
            "actionRequired": "Execute Fleet Rightsizing Plan",
            "savingsPotential": 118000,
        },
        {
            "id": "alert-capacity-checkout-03",
            "type": "capacity_limit",
            "severity": "WARNING",
            "title": "Capacity Warning: Production Checkout API Peaking at 94.8% CPU (p99)",
            "resourceId": "zenith-checkout-api-01",
            "resourceName": "checkout-order-prod-01",
            "region": "Mumbai (West)",
            "environment": "prod",
            "impactCost": "High SLA Breach & Cart Abandonment Risk",
            "whatHappened": "During daily peak lunch (13:00–14:30) and dinner (20:00–21:30) shopping hours, CPU saturation hits 88.4% (p95) and spikes to 94.8% (p99). Memory utilization reached 76.0% with 16,000 IOPS on Ultra SSD.",
            "whyItMatters": "CRITICAL FINOPS RULE: DO NOT DOWNSCALE. Even though 24-hour average CPU is only 48%, downsizing this VM will cause connection drops, HTTP 504 timeouts, and drop checkout conversions during flash deals worth ₹1.2 Cr daily.",
            "whatToDo": "Configure horizontal pod autoscaling (HPA) or temporarily burst-upscale to Standard_E16s_v5 during the 3 high-traffic hours. Ensure rightsizing engine treats this node as protected.",
            "actionRequired": "Protect from Downscaling / Upscale Burst",
            "savingsPotential": 0,
        },
        {
            "id": "alert-budget-overrun-04",
            "type": "budget_overrun",
            "severity": "ALERT",
            "title": f"Projected Budget Overrun: Month-End Spend ₹{total_spend:,} Exceeds ₹{budget:,} Budget",
            "resourceId": "billing-account",
            "resourceName": "ZenithFlow Cloud Budget Account",
            "region": "All Regions",
            "environment": "all",
            "impactCost": f"₹{max(0, total_spend - budget):,} over budget (+{round((total_spend - budget) / budget * 100, 1)}%)",
            "whatHappened": f"Current 30-day unmanaged run rate is trending at ₹{total_spend:,}/month against the leadership board-approved budget of ₹{budget:,}/month, resulting in an overrun of ₹{max(0, total_spend - budget):,}.",
            "whyItMatters": "Exceeding quarterly FinOps allocation triggers mandatory CTO escalation and cloud freeze policies.",
            "whatToDo": f"Review and approve the 18 active FinOps recommendations. Enforcing these recommendations brings projected spend down to ₹{projected_spend:,}/month, staying safely within the ₹{budget:,} budget with ₹{budget - projected_spend:,} in buffer.",
            "actionRequired": "Accept Recommendations",
            "savingsPotential": total_spend - projected_spend,
        },
    ]


def generate_terraform_hcl(vms_dict: Dict[str, Any]) -> str:
    """Generates production-ready Terraform HCL code to remediate fleet waste."""
    hcl = [
        "# =====================================================================",
        "# SmartCloud Optimizer - Automated FinOps Remediation Plan",
        "# Customer: ZenithFlow Technologies Pvt Ltd (India SaaS Fleet)",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "# =====================================================================\n",
        'terraform {',
        '  required_version = ">= 1.5.0"',
        '  required_providers {',
        '    azurerm = {',
        '      source  = "hashicorp/azurerm"',
        '      version = "~> 3.80.0"',
        '    }',
        '  }',
        '}\n',
        'provider "azurerm" {',
        '  features {}',
        '}\n',
        '# 1. Scheduled Off-Hours Auto-Shutdown Schedules for Dev & Batch VMs',
    ]

    for vid, vm in vms_dict.items():
        if vm.get("environment") == "dev" and vm.get("type") == "VM":
            safe_name = vid.replace("-", "_")
            hcl.append(f"""
resource "azurerm_dev_test_global_vm_shutdown_schedule" "shutdown_{safe_name}" {{
  virtual_machine_id    = "/subscriptions/sub-utho-zenith/resourceGroups/rg-zenith-{vm.get('region', 'noida')[:3].lower()}/providers/Microsoft.Compute/virtualMachines/{vm.get('name')}"
  location              = "{vm.get('region', 'centralindia').split(' ')[0].lower()}"
  enabled               = true
  daily_recurrence_time = "2000" # 8:00 PM IST shutoff
  timezone              = "India Standard Time"

  notification_settings {{
    enabled         = true
    email           = "devops-alerts@zenithflow.in"
    time_in_minutes = "30"
  }}

  tags = {{
    Environment = "{vm.get('environment')}"
    Team        = "{vm.get('team')}"
    ManagedBy   = "SmartCloud-Optimizer-FinOps"
  }}
}}""")

    hcl.append("\n# 2. Orphaned Block Storage Purge and Snapshot Archive")
    for vid, vm in vms_dict.items():
        if vm.get("type") == "Volume" and "Orphaned" in vm.get("status", ""):
            safe_name = vid.replace("-", "_")
            hcl.append(f"""
# ACTION: Target volume marked for snapshot and safe deletion
# Savings: ₹{vm.get('currentSpend', 0):,}/month
# terraform destroy -target=azurerm_managed_disk.{safe_name}
resource "azurerm_snapshot" "snap_{safe_name}" {{
  name                = "{vm.get('name')}-pre-delete-archive"
  location            = "{vm.get('region', 'centralindia').split(' ')[0].lower()}"
  resource_group_name = "rg-zenith-orphaned-archives"
  create_option       = "Copy"
  source_resource_id  = "/subscriptions/sub-utho-zenith/resourceGroups/rg-zenith-storage/providers/Microsoft.Compute/disks/{vm.get('name')}"
}}""")

    return "\n".join(hcl)


def generate_bash_cli(vms_dict: Dict[str, Any]) -> str:
    """Generates standalone Azure CLI / Bash script for instant execution."""
    cmds = [
        "#!/usr/bin/env bash",
        "# =====================================================================",
        "# SmartCloud Optimizer - Instant FinOps Execution Runbook",
        "# Customer: ZenithFlow Technologies (Noida, Bangalore, Mumbai)",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "# =====================================================================\n",
        "set -euo pipefail\n",
        "echo '[+] Authenticating with Cloud Provider CLI...'",
        "echo '[+] Executing ZenithFlow Cost Optimization Runbook...'\n",
        "# ---------------------------------------------------------------------",
        "# Step 1: Terminate Runaway Process & Downsize Staging Anomaly",
        "# ---------------------------------------------------------------------",
        "echo '[1/4] Remediating Staging Anomaly (zenith-staging-worker-02)...'",
        "az vm run-command invoke --resource-group rg-zenith-noida --name staging-crawler-worker-02 \\",
        "  --command-id RunShellScript --scripts 'pkill -9 -f scraper_worker.py || true'",
        "az vm update --resource-group rg-zenith-noida --name staging-crawler-worker-02 --set hardwareProfile.vmSize=Standard_D2s_v5",
        "echo '    -> Successfully downsized staging worker to Standard_D2s_v5 (saves ₹13,600/mo)'\n",
        "# ---------------------------------------------------------------------",
        "# Step 2: Delete Orphaned Disks and Release Unused Public IPs",
        "# ---------------------------------------------------------------------",
        "echo '[2/4] Purging unattached orphaned volumes and static IPs...'",
    ]

    for vid, vm in vms_dict.items():
        if vm.get("type") == "Volume" and "Orphaned" in vm.get("status", ""):
            cmds.append(f"az disk delete --resource-group rg-zenith-storage --name {vm.get('name')} --yes --no-wait")
            cmds.append(f"echo '    -> Deleted orphaned volume {vm.get('name')} (saves ₹{vm.get('currentSpend', 0):,}/mo)'")
        elif vm.get("type") == "IP" and "Orphaned" in vm.get("status", ""):
            cmds.append(f"az network public-ip delete --resource-group rg-zenith-network --name {vm.get('name')}")
            cmds.append(f"echo '    -> Released idle static IP {vm.get('name')} (saves ₹{vm.get('currentSpend', 0):,}/mo)'")

    cmds.extend([
        "\n# ---------------------------------------------------------------------",
        "# Step 3: Configure Scheduled Off-Hours Shutdown for Dev Environments",
        "# ---------------------------------------------------------------------",
        "echo '[3/4] Enforcing 8 PM - 8 AM + Weekend Auto-Shutdown on Dev VMs...'",
    ])

    for vid, vm in vms_dict.items():
        if vm.get("environment") == "dev" and vm.get("type") == "VM":
            cmds.append(f"az vm auto-shutdown --resource-group rg-zenith-dev --name {vm.get('name')} --time 2000")

    cmds.extend([
        "\necho '[4/4] All FinOps optimization commands applied successfully.'",
        "echo '[✓] Estimated monthly recurring savings unlocked: ₹1,64,800/month.'",
        "exit 0\n"
    ])

    return "\n".join(cmds)

