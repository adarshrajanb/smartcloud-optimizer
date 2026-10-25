from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import urllib.request
import uuid
from app.persistence import load_store, save_store

app = FastAPI(title="SmartCloud Optimizer FinOps API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class AutoScaleToggleRequest(BaseModel):
    enabled: bool


class BatchAutoScaleRequest(BaseModel):
    customer_id: str
    enabled: bool


class ProvisionVmRequest(BaseModel):
    customerId: str
    planId: str = "business"  # 'starter', 'business', 'enterprise'
    vmName: Optional[str] = None
    region: Optional[str] = "East US / Central India"
    autoScaleEnabled: Optional[bool] = True
    userId: Optional[str] = None
    customerName: Optional[str] = None
    email: Optional[str] = None
    vmId: Optional[str] = None


class SyncUserPayload(BaseModel):
    user_id: str
    email_id: str
    password: Optional[str] = ""
    customer_name: Optional[str] = "Enterprise Customer"
    company: Optional[str] = "Cloud Enterprise"
    role: Optional[str] = "customer"
    assigned_vms: Optional[List[Any]] = []


class DockerConnectPayload(BaseModel):
    host: str = "http://localhost:8001"
    customerId: Optional[str] = None


class DockerScalePayload(BaseModel):
    containerId: str
    cpus: float = 2.0
    memory: str = "4g"


DOCKER_HOST_STATE = {
    "host": "http://localhost:8001",
    "connected": False,
    "lastPing": None,
    "containers": [],
    "hostInfo": {},
}


# FinOps Audit Logs: Tracking All Optimization & Resource Changes
AUDIT_LOGS: List[Dict[str, Any]] = [
    {
        "id": "log-init-01",
        "timestamp": (datetime.utcnow() - timedelta(hours=36)).isoformat() + "Z",
        "action": "SCHEDULED_DOWNSCALE",
        "vmId": "vm-web-prod",
        "vmName": "web-prod-01",
        "previousSpend": 18400,
        "currentSpend": 13880,
        "costDelta": -4520,
        "previousSpec": "Standard_D8s_v5 (8 Cores, 32 GB)",
        "currentSpec": "Standard_D2s_v5 (2 Cores, 8 GB)",
        "reason": "Off-hours rightsizing applied (7:00 PM – 5:00 AM). Compute reduced during idle night window.",
        "status": "Enforced",
        "category": "Cost Reduction",
    },
    {
        "id": "log-init-02",
        "timestamp": (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z",
        "action": "SCHEDULED_HIBERNATION",
        "vmId": "vm-batch",
        "vmName": "batch-processor-03",
        "previousSpend": 9700,
        "currentSpend": 6200,
        "costDelta": -3500,
        "previousSpec": "Standard_D4s_v5 (4 Cores, 16 GB)",
        "currentSpec": "Standard_B2s (2 Cores, 4 GB standby)",
        "reason": "Dynamic hibernation enabled outside active reconciliation window (01:00 - 04:30 AM).",
        "status": "Enforced",
        "category": "Cost Reduction",
    },
    {
        "id": "log-init-03",
        "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z",
        "action": "OFF_HOURS_OPTIMIZATION",
        "vmId": "vm-api-gw",
        "vmName": "gateway-edge-04",
        "previousSpend": 9700,
        "currentSpend": 8500,
        "costDelta": -1200,
        "previousSpec": "Standard_D4s_v5 (4 Cores, 16 GB)",
        "currentSpec": "Standard_D2s_v5 (2 Cores, 8 GB)",
        "reason": "Traffic dropped by 60% during nocturnal window; auto-downscale active.",
        "status": "Enforced",
        "category": "Cost Reduction",
    },
]


def record_audit_log(
    action: str,
    vm_id: str,
    vm_name: str,
    prev_spend: float,
    cur_spend: float,
    prev_spec: str,
    cur_spec: str,
    reason: str,
    category: str = "Cost Optimization",
):
    log_entry = {
        "id": f"log-{int(datetime.utcnow().timestamp() * 1000)}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "vmId": vm_id,
        "vmName": vm_name,
        "previousSpend": round(prev_spend, 2),
        "currentSpend": round(cur_spend, 2),
        "costDelta": round(cur_spend - prev_spend, 2),
        "previousSpec": prev_spec,
        "currentSpec": cur_spec,
        "reason": reason,
        "status": "Enforced",
        "category": category,
    }
    AUDIT_LOGS.insert(0, log_entry)
    if len(AUDIT_LOGS) > 100:
        AUDIT_LOGS.pop()
    try:
        if 'persist_all' in globals():
            persist_all()
    except Exception:
        pass
    return log_entry


# Customer registry with distinct fleets
CUSTOMERS = {
    "cust-northwind": {
        "id": "cust-northwind",
        "name": "Northwind Logistics",
        "company": "Northwind Logistics SaaS",
        "industry": "Global Supply Chain & Freight",
        "azureSubscriptionId": "sub-az-9844-3101-prod",
        "tenantName": "northwindlogistics.onmicrosoft.com",
        "primaryRegion": "East US / Central India",
        "budgetLimit": 75000,
        "vmIds": ["vm-web-prod", "vm-analytics", "vm-batch", "vm-api-gw"],
    },
    "cust-contoso": {
        "id": "cust-contoso",
        "name": "Contoso HealthTech",
        "company": "Contoso Healthcare Systems",
        "industry": "Digital Health & Clinical Diagnostics",
        "azureSubscriptionId": "sub-az-1102-4498-hipaa",
        "tenantName": "contosohealth.onmicrosoft.com",
        "primaryRegion": "West US 2 (Washington)",
        "budgetLimit": 160000,
        "vmIds": ["vm-ehr-core", "vm-imaging-gpu", "vm-hl7-broker"],
    },
    "cust-fabrikam": {
        "id": "cust-fabrikam",
        "name": "Fabrikam Retail",
        "company": "Fabrikam Omnichannel Retail",
        "industry": "High-Volume E-Commerce & Retail",
        "azureSubscriptionId": "sub-az-8732-5510-retail",
        "tenantName": "fabrikamretail.onmicrosoft.com",
        "primaryRegion": "West Europe (Amsterdam)",
        "budgetLimit": 90000,
        "vmIds": ["vm-checkout-api", "vm-search-solr", "vm-rec-engine"],
    },
}

# Complete in-memory VM fleet state for all customers
VM_STATE = {
    # ================= Northwind Logistics VMs =================
    "vm-web-prod": {
        "id": "vm-web-prod",
        "name": "web-prod-01",
        "customerId": "cust-northwind",
        "status": "Healthy",
        "region": "East US (Virginia)",
        "resourceGroup": "rg-ecommerce-prod",
        "vmSize": "Standard_D8s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.0.1.14",
        "publicIp": "20.120.45.89",
        "specs": {
            "cores": 8,
            "ramGb": 32,
            "storageGb": 512,
            "storageType": "Premium SSD v2",
            "maxIops": 12800,
            "bandwidthMbps": 12500,
        },
        "currentHourlyRate": 0.384,
        "currentSpend": 18400,
        "projectedSpend": 13880,
        "savings": 4520,
        "autoScaleEnabled": True,
        "workloadProfile": "E-Commerce Frontend & Cart API",
        "recommendation": {
            "type": "downsize",
            "title": "Scheduled Downscale to Standard_D2s_v5 during Night Off-Hours (7 PM – 5 AM)",
            "urgency": "High Savings Opportunity",
            "confidence": 94,
            "reason": "Historical telemetry confirms CPU utilization stays under 18% and memory under 35% on weekdays between 19:00 and 05:00 UTC. The workload can comfortably run on 2 vCPU / 8 GB RAM during these 10 idle hours without SLA impact.",
            "formula": "Off-hours savings: 10 hrs/day × (₹25.60 baseline/hr - ₹6.40 downsized/hr) × 22 weekdays = ₹4,224 + weekend adjustments ≈ ₹4,520/month",
            "billingImpact": "Your monthly Azure invoice reduces from ₹18,400 to ₹13,880 (-24.6% reduction). Billing reflects prorated hourly compute under the Elastic SLA agreement.",
            "calculationSteps": [
                {"label": "Current 24/7 Provisioned Run Rate", "value": "730 hrs × ₹25.20/hr = ₹18,400/mo"},
                {"label": "Peak Business Hours (5 AM - 7 PM)", "value": "14 hrs/day × ₹25.20/hr = ₹352.80/day"},
                {"label": "Auto-Downscaled Hours (7 PM - 5 AM)", "value": "10 hrs/day × ₹6.30/hr = ₹63.00/day (saves ₹189.00/day)"},
                {"label": "Net Projected Spend with Automation", "value": "₹13,880/mo (Total Monthly Savings: ₹4,520)"},
            ],
            "targetSku": "Standard_D2s_v5 (2 vCPU, 8 GB RAM)",
        },
    },
    "vm-analytics": {
        "id": "vm-analytics",
        "name": "analytics-worker-02",
        "customerId": "cust-northwind",
        "status": "Bottleneck Warning",
        "region": "Central India (Pune)",
        "resourceGroup": "rg-analytics-pipeline",
        "vmSize": "Standard_E16s_v5",
        "os": "Windows Server 2022 Datacenter",
        "privateIp": "10.0.3.42",
        "publicIp": "52.172.90.11",
        "specs": {
            "cores": 16,
            "ramGb": 64,
            "storageGb": 1024,
            "storageType": "Ultra SSD",
            "maxIops": 25600,
            "bandwidthMbps": 20000,
        },
        "currentHourlyRate": 1.008,
        "currentSpend": 27250,
        "projectedSpend": 29580,
        "savings": 0,
        "autoScaleEnabled": False,
        "workloadProfile": "Real-time ETL & Spark Aggregator",
        "recommendation": {
            "type": "upgrade",
            "title": "Predictive Upsize to Standard_E32s_v5 to Prevent 14:00 - 18:00 UTC Bottleneck",
            "urgency": "Critical SLA Risk",
            "confidence": 91,
            "reason": "Predictive workload model forecasts CPU saturation at 93.8% and memory at 88.5% during daily ingestion bursts (14:00 – 18:00 UTC). Without additional compute, message queue lag exceeds 480 seconds, triggering HTTP 504 gateway timeouts.",
            "formula": "Elastic boost cost: 4 hrs/day × 30 days × (₹126.50 upsized/hr - ₹68.00 base/hr) = +₹2,330/mo vs estimated ₹3,20,000 downtime breach penalty",
            "billingImpact": "Spend temporarily increases by ₹2,330/mo only during high-load windows. When auto-scale permission is approved, the cluster automatically provisions extra cores 15 minutes before the spike and deallocates immediately after.",
            "calculationSteps": [
                {"label": "Current Flat-Rate Monthly Spend", "value": "₹27,250/mo (Standard_E16s_v5)"},
                {"label": "Predicted Ingestion Bottleneck Window", "value": "14:00 – 18:00 UTC daily (P95 CPU 93.8%)"},
                {"label": "Dynamic Burst Upsizing Cost", "value": "4 hrs/day × ₹58.25 delta = +₹2,330/mo"},
                {"label": "SLA & Outage Avoidance Value", "value": "Guarantees 99.95% API uptime & saves ~₹3,20,000 incident costs"},
            ],
            "targetSku": "Standard_E32s_v5 (32 vCPU, 128 GB RAM)",
        },
    },
    "vm-batch": {
        "id": "vm-batch",
        "name": "batch-processor-03",
        "customerId": "cust-northwind",
        "status": "Healthy",
        "region": "Southeast Asia (Singapore)",
        "resourceGroup": "rg-batch-jobs",
        "vmSize": "Standard_D4s_v5",
        "os": "Ubuntu Linux 20.04 LTS",
        "privateIp": "10.0.4.19",
        "publicIp": "None (Private VNet)",
        "specs": {
            "cores": 4,
            "ramGb": 16,
            "storageGb": 256,
            "storageType": "Standard SSD",
            "maxIops": 6400,
            "bandwidthMbps": 5000,
        },
        "currentHourlyRate": 0.192,
        "currentSpend": 9700,
        "projectedSpend": 6200,
        "savings": 3500,
        "autoScaleEnabled": True,
        "workloadProfile": "Nightly Reconciliation & Report Generation",
        "recommendation": {
            "type": "downsize",
            "title": "Dynamic Hibernation / Downscale Outside Active Job Windows",
            "urgency": "High Savings Opportunity",
            "confidence": 96,
            "reason": "Reconciliation batch executes exclusively between 01:00 and 04:30 AM. For the remaining 19.5 hours daily, CPU stays under 6%. Automation can scale the VM down to a minimal B2s instance outside processing windows.",
            "formula": "19.5 idle hrs/day × (₹13.28 base/hr - ₹3.12 standby/hr) = ₹198.12/day × 30 = ₹5,943 gross savings → calibrated ₹3,500 net monthly savings",
            "billingImpact": "Spend reduces from ₹9,700 to ₹6,200 (-36% reduction). Automatic wake-up ensures jobs start on schedule with zero delay.",
            "calculationSteps": [
                {"label": "Current 24/7 Provisioned Run Rate", "value": "₹9,700/mo (Standard_D4s_v5)"},
                {"label": "Active Processing Window", "value": "01:00 - 04:30 AM UTC (Compute utilized: 78%)"},
                {"label": "Standby Idle Hours Window", "value": "19.5 hours/day at < 6% CPU utilization"},
                {"label": "Net Projected Spend with Hibernation", "value": "₹6,200/mo (Monthly Savings: ₹3,500)"},
            ],
            "targetSku": "Standard_B2s (2 vCPU, 4 GB RAM standby)",
        },
    },
    "vm-api-gw": {
        "id": "vm-api-gw",
        "name": "gateway-edge-04",
        "customerId": "cust-northwind",
        "status": "Healthy",
        "region": "Central India (Pune)",
        "resourceGroup": "rg-ecommerce-prod",
        "vmSize": "Standard_D4s_v5",
        "os": "Debian Linux 12",
        "privateIp": "10.0.1.5",
        "publicIp": "20.198.112.50",
        "specs": {
            "cores": 4,
            "ramGb": 16,
            "storageGb": 128,
            "storageType": "Premium SSD",
            "maxIops": 6400,
            "bandwidthMbps": 8000,
        },
        "currentHourlyRate": 0.192,
        "currentSpend": 9700,
        "projectedSpend": 8500,
        "savings": 1200,
        "autoScaleEnabled": True,
        "workloadProfile": "Kong API Gateway & Rate Limiting",
        "recommendation": {
            "type": "downsize",
            "title": "Slight Night Downscale (7 PM - 5 AM)",
            "urgency": "Moderate Savings",
            "confidence": 89,
            "reason": "Traffic volume drops by 60% between 7 PM and 5 AM. Gateway CPU remains under 20% throughout night hours.",
            "formula": "Off-hours optimization saves ₹1,200 per month with zero connection dropouts.",
            "billingImpact": "Spend drops from ₹9,700 to ₹8,500/mo under autonomous elastic scaling.",
            "calculationSteps": [
                {"label": "Current Baseline Spend", "value": "₹9,700/mo"},
                {"label": "Off-hours Traffic Drop", "value": "60% throughput drop between 19:00 - 05:00 UTC"},
                {"label": "Optimized Run Rate", "value": "₹8,500/mo (Savings: ₹1,200)"},
            ],
            "targetSku": "Standard_D2s_v5 (2 vCPU, 8 GB RAM)",
        },
    },

    # ================= Contoso HealthTech VMs =================
    "vm-ehr-core": {
        "id": "vm-ehr-core",
        "name": "ehr-database-01",
        "customerId": "cust-contoso",
        "status": "Bottleneck Warning",
        "region": "West US 2 (Washington)",
        "resourceGroup": "rg-clinical-core",
        "vmSize": "Standard_E32s_v5",
        "os": "Red Hat Enterprise Linux 9",
        "privateIp": "10.20.1.8",
        "publicIp": "None (Internal Subnet)",
        "specs": {
            "cores": 32,
            "ramGb": 256,
            "storageGb": 2048,
            "storageType": "Ultra Disk SSD",
            "maxIops": 64000,
            "bandwidthMbps": 32000,
        },
        "currentHourlyRate": 2.016,
        "currentSpend": 74500,
        "projectedSpend": 79200,
        "savings": 0,
        "autoScaleEnabled": False,
        "workloadProfile": "Hospital Electronic Health Records & Epic Integration",
        "recommendation": {
            "type": "upgrade",
            "title": "Emergency Upsize to Standard_E48s_v5 for Clinical Shift Change (16:00 – 20:00 UTC)",
            "urgency": "Life-Critical Bottleneck",
            "confidence": 98,
            "reason": "During the shift-change window (16:00 – 20:00 UTC), simultaneous EHR doctor chart syncs drive CPU utilization to 96.4% and RAM to 91.2%, causing query latencies to spike from 120ms to 4,200ms. Upscaling compute during this 4-hour window guarantees patient record availability.",
            "formula": "4 shift hours/day × 30 days × (₹284.00 boost/hr - ₹186.25 base/hr) = +₹4,700/mo vs Zero Charting Outages",
            "billingImpact": "Increases spend by ₹4,700/mo strictly during active clinical shift changes when auto-scale permission is enabled.",
            "calculationSteps": [
                {"label": "Current 24/7 Provisioned Run Rate", "value": "₹74,500/mo (Standard_E32s_v5)"},
                {"label": "Peak Charting Ingestion Window", "value": "16:00 – 20:00 UTC (P95 CPU 96.4%)"},
                {"label": "Elastic Upsizing Surcharge", "value": "4 hrs/day × ₹39.16 delta = +₹4,700/mo"},
                {"label": "Clinical Availability Impact", "value": "Averts EHR query timeouts and HIPAA SLA penalties"},
            ],
            "targetSku": "Standard_E48s_v5 (48 vCPU, 384 GB RAM)",
        },
    },
    "vm-imaging-gpu": {
        "id": "vm-imaging-gpu",
        "name": "dicom-ai-infer-02",
        "customerId": "cust-contoso",
        "status": "Healthy",
        "region": "West US 2 (Washington)",
        "resourceGroup": "rg-clinical-ai",
        "vmSize": "Standard_NC8as_T4_v3",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.20.2.14",
        "publicIp": "52.183.210.4",
        "specs": {
            "cores": 8,
            "ramGb": 56,
            "storageGb": 1024,
            "storageType": "Premium SSD",
            "maxIops": 16000,
            "bandwidthMbps": 16000,
        },
        "currentHourlyRate": 1.45,
        "currentSpend": 52400,
        "projectedSpend": 38200,
        "savings": 14200,
        "autoScaleEnabled": True,
        "workloadProfile": "Radiology & DICOM AI Inference Cluster",
        "recommendation": {
            "type": "downsize",
            "title": "Automated GPU Deallocation & Downscale from 8 PM to 6 AM",
            "urgency": "Exceptional Savings",
            "confidence": 95,
            "reason": "Radiology scanning centers operate between 06:00 and 20:00 local time. During the 10 night hours, incoming DICOM volume drops by 94% and GPU utilization drops to 2.1%. Deallocating the GPU node and switching to an idle CPU standby node during night hours yields substantial savings.",
            "formula": "10 night hrs/day × (₹112.50 GPU/hr - ₹18.00 standby/hr) × 30 days = ₹14,200/month net savings",
            "billingImpact": "Monthly compute drops from ₹52,400 to ₹38,200 (-27.1% reduction) with automated warm wake-up before morning radiology rounds.",
            "calculationSteps": [
                {"label": "Current 24/7 Provisioned Run Rate", "value": "₹52,400/mo (Standard_NC8as_T4_v3)"},
                {"label": "Radiology Operating Window", "value": "06:00 – 20:00 UTC (Active scanning: 82%)"},
                {"label": "Night Deallocation Window (8 PM – 6 AM)", "value": "10 hrs/day at < 3% GPU load"},
                {"label": "Net Projected Spend with Scaling", "value": "₹38,200/mo (Savings: ₹14,200/mo)"},
            ],
            "targetSku": "Standard_D4s_v5 (4 vCPU, 16 GB standby)",
        },
    },
    "vm-hl7-broker": {
        "id": "vm-hl7-broker",
        "name": "hl7-fhir-broker-03",
        "customerId": "cust-contoso",
        "status": "Healthy",
        "region": "North Europe (Ireland)",
        "resourceGroup": "rg-integration-fhir",
        "vmSize": "Standard_D8s_v5",
        "os": "Debian Linux 12",
        "privateIp": "10.20.3.5",
        "publicIp": "51.144.89.22",
        "specs": {
            "cores": 8,
            "ramGb": 32,
            "storageGb": 512,
            "storageType": "Standard SSD",
            "maxIops": 8000,
            "bandwidthMbps": 10000,
        },
        "currentHourlyRate": 0.384,
        "currentSpend": 18400,
        "projectedSpend": 15800,
        "savings": 2600,
        "autoScaleEnabled": True,
        "workloadProfile": "HL7 v2 to FHIR v4 Message Transformation Gateway",
        "recommendation": {
            "type": "downsize",
            "title": "Night Message Buffer Downscale (7 PM - 5 AM)",
            "urgency": "Moderate Savings",
            "confidence": 91,
            "reason": "Off-peak patient lab result transfers decrease by 72% between 19:00 and 05:00 UTC. Reducing vCPU allocation from 8 to 4 during this period maintains zero backlog while trimming infrastructure waste.",
            "formula": "10 off-hours × 30 days × (₹25.20 - ₹12.60) = ₹2,600 monthly savings",
            "billingImpact": "Reduces spend from ₹18,400 to ₹15,800/mo.",
            "calculationSteps": [
                {"label": "Current Provisioned Spend", "value": "₹18,400/mo"},
                {"label": "Off-Peak Message Volume", "value": "72% drop in transaction rate between 7 PM - 5 AM"},
                {"label": "Optimized Run Rate", "value": "₹15,800/mo (Savings: ₹2,600)"},
            ],
            "targetSku": "Standard_D4s_v5 (4 vCPU, 16 GB RAM)",
        },
    },

    # ================= Fabrikam Retail VMs =================
    "vm-checkout-api": {
        "id": "vm-checkout-api",
        "name": "checkout-cluster-01",
        "customerId": "cust-fabrikam",
        "status": "Bottleneck Warning",
        "region": "West Europe (Amsterdam)",
        "resourceGroup": "rg-storefront-prod",
        "vmSize": "Standard_D16s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.30.1.20",
        "publicIp": "20.105.78.34",
        "specs": {
            "cores": 16,
            "ramGb": 64,
            "storageGb": 512,
            "storageType": "Premium SSD",
            "maxIops": 25600,
            "bandwidthMbps": 16000,
        },
        "currentHourlyRate": 0.768,
        "currentSpend": 36800,
        "projectedSpend": 39900,
        "savings": 0,
        "autoScaleEnabled": False,
        "workloadProfile": "Payment Gateway & Cart Checkout Microservices",
        "recommendation": {
            "type": "upgrade",
            "title": "Flash Sale Spike Protection Upscale to Standard_D32s_v5",
            "urgency": "Revenue Bottleneck Risk",
            "confidence": 93,
            "reason": "Retail promotions run daily between 18:00 and 21:00 UTC, where checkout transactions reach 1,800 requests/sec. Under current 16 vCPU capacity, thread pool saturation leads to 4.2% cart abandonment.",
            "formula": "3 peak hrs/day × 30 days × ₹34.40 burst = +₹3,100/mo vs ₹8,50,000 abandoned checkout recovery",
            "billingImpact": "Spend rises by ₹3,100/mo strictly during active 3-hour promotional windows.",
            "calculationSteps": [
                {"label": "Current Monthly Spend", "value": "₹36,800/mo"},
                {"label": "Promotional Flash Sale Peak", "value": "18:00 - 21:00 UTC daily (CPU 94.5%)"},
                {"label": "Dynamic Compute Upscale Cost", "value": "+₹3,100/mo for 32 vCPU tier"},
                {"label": "Revenue Recovery Value", "value": "Protects ₹8,50,000 cart transactions"},
            ],
            "targetSku": "Standard_D32s_v5 (32 vCPU, 128 GB RAM)",
        },
    },
    "vm-search-solr": {
        "id": "vm-search-solr",
        "name": "catalog-search-02",
        "customerId": "cust-fabrikam",
        "status": "Healthy",
        "region": "West Europe (Amsterdam)",
        "resourceGroup": "rg-storefront-prod",
        "vmSize": "Standard_E8s_v5",
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": "10.30.2.11",
        "publicIp": "None (Internal VNet)",
        "specs": {
            "cores": 8,
            "ramGb": 64,
            "storageGb": 1024,
            "storageType": "Premium SSD",
            "maxIops": 12800,
            "bandwidthMbps": 12500,
        },
        "currentHourlyRate": 0.504,
        "currentSpend": 22100,
        "projectedSpend": 15400,
        "savings": 6700,
        "autoScaleEnabled": True,
        "workloadProfile": "ElasticSearch / Solr Product Catalog Indexer",
        "recommendation": {
            "type": "downsize",
            "title": "Night Index Standby Downscale (10 PM - 6 AM)",
            "urgency": "High Savings",
            "confidence": 92,
            "reason": "Search queries drop to near zero after 22:00 CET. Downscaling during the 8-hour nighttime window maintains cached index reads without high memory reservation.",
            "formula": "8 night hrs/day × (₹30.24 - ₹8.10) × 30 days = ₹6,700/mo savings",
            "billingImpact": "Monthly spend reduces from ₹22,100 to ₹15,400 (-30.3%).",
            "calculationSteps": [
                {"label": "Current 24/7 Spend", "value": "₹22,100/mo"},
                {"label": "Night Query Volume", "value": "8-hour window from 10 PM to 6 AM (< 8% CPU)"},
                {"label": "Projected Spend with Schedule", "value": "₹15,400/mo (Savings: ₹6,700)"},
            ],
            "targetSku": "Standard_E4s_v5 (4 vCPU, 32 GB RAM)",
        },
    },
    "vm-rec-engine": {
        "id": "vm-rec-engine",
        "name": "recommendations-03",
        "customerId": "cust-fabrikam",
        "status": "Healthy",
        "region": "West Europe (Amsterdam)",
        "resourceGroup": "rg-storefront-prod",
        "vmSize": "Standard_D8s_v5",
        "os": "Debian Linux 12",
        "privateIp": "10.30.3.15",
        "publicIp": "20.105.90.14",
        "specs": {
            "cores": 8,
            "ramGb": 32,
            "storageGb": 512,
            "storageType": "Standard SSD",
            "maxIops": 8000,
            "bandwidthMbps": 10000,
        },
        "currentHourlyRate": 0.384,
        "currentSpend": 18400,
        "projectedSpend": 14200,
        "savings": 4200,
        "autoScaleEnabled": True,
        "workloadProfile": "Real-Time Collaborative Filtering & Product Recommendations",
        "recommendation": {
            "type": "downsize",
            "title": "Off-Hours Model Cache Downscale (7 PM - 5 AM)",
            "urgency": "Moderate Savings",
            "confidence": 90,
            "reason": "Recommendation scoring load drops by 78% between 19:00 and 05:00 UTC. Running on 2 vCPU during this window saves compute costs while keeping cache warm.",
            "formula": "10 hrs/day × (₹25.20 - ₹6.30) × 22 weekdays = ₹4,200 monthly savings",
            "billingImpact": "Spend drops from ₹18,400 to ₹14,200/mo under autonomous scheduling.",
            "calculationSteps": [
                {"label": "Current 24/7 Provisioned Run Rate", "value": "₹18,400/mo"},
                {"label": "Off-Hours Traffic Drop", "value": "78% lower inference load at night"},
                {"label": "Net Projected Spend", "value": "₹14,200/mo (Savings: ₹4,200)"},
            ],
            "targetSku": "Standard_D2s_v5 (2 vCPU, 8 GB RAM)",
        },
    },
}

USER_ACCOUNTS: Dict[str, Any] = {
    "d0a49394-eafe-41f1-ae07-4ae3045e0c65": {
        "user_id": "d0a49394-eafe-41f1-ae07-4ae3045e0c65",
        "email_id": "admin@smartcloud.com",
        "password": "Admin@123",
        "role": "super_admin",
        "customer_name": "Super Admin Platform Lead",
        "company": "SmartCloud Headquarters",
        "assigned_vms": ["vm-web-prod", "vm-analytics", "vm-batch", "vm-api-gw"],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
}


def persist_all():
    try:
        save_store(CUSTOMERS, VM_STATE, USER_ACCOUNTS, AUDIT_LOGS)
    except Exception as e:
        print(f"Error persisting fleet store: {e}")


# Initialize / restore persistent data across system reboots
_persisted = load_store()
if _persisted:
    if "customers" in _persisted and isinstance(_persisted["customers"], dict):
        CUSTOMERS.update(_persisted["customers"])
    if "vm_state" in _persisted and isinstance(_persisted["vm_state"], dict):
        VM_STATE.update(_persisted["vm_state"])
    if "user_accounts" in _persisted and isinstance(_persisted["user_accounts"], dict):
        USER_ACCOUNTS.update(_persisted["user_accounts"])
    if "audit_logs" in _persisted and isinstance(_persisted["audit_logs"], list) and len(_persisted["audit_logs"]) > 0:
        AUDIT_LOGS[:] = _persisted["audit_logs"]
else:
    persist_all()



def generate_time_series(vm_id: str, range_key: str = "7d", granularity_key: str = "30m") -> List[Dict[str, Any]]:
    """
    Generates realistic, lightning-fast Azure VM telemetry.
    Supports range: 1d, 7d, 30d
    Supports granularity: 10m, 30m, 1h, 1d
    Guaranteed to generate between 24 and 112 points for instant rendering.
    """
    now = datetime.utcnow().replace(microsecond=0)

    if range_key == "1d":
        if granularity_key == "10m":
            step_mins = 15  # 96 points
            lbl_format = "%H:%M"
        elif granularity_key == "1h":
            step_mins = 60  # 24 points
            lbl_format = "%H:%M"
        else:  # 30m
            step_mins = 30  # 48 points
            lbl_format = "%H:%M"
        total_points = (24 * 60) // step_mins
    elif range_key == "7d":
        if granularity_key == "10m":
            step_mins = 90  # 112 points
            lbl_format = "%a %H:%M"
        elif granularity_key == "1h":
            step_mins = 120  # 84 points
            lbl_format = "%a %H:%M"
        else:  # 30m
            step_mins = 120  # 84 points
            lbl_format = "%a %H:%M"
        total_points = (7 * 24 * 60) // step_mins
    else:  # "30d"
        step_mins = 1440  # 30 points (1 point per day)
        lbl_format = "%b %d"
        total_points = 30

    points = []

    for index in range(total_points):
        offset_minutes = (total_points - 1 - index) * step_mins
        timestamp = now - timedelta(minutes=offset_minutes)
        hour = timestamp.hour
        weekday = timestamp.weekday()
        is_weekday = weekday < 5
        is_night_window = (hour >= 19 or hour < 5)

        # Workload-specific telemetry profiles
        if vm_id in ("vm-web-prod", "vm-rec-engine"):
            if is_night_window and is_weekday:
                base_cpu = 14.0 + (index % 4) * 1.2
                base_mem = 31.0 + (index % 3) * 0.9
                base_disk = 18.0 + (index % 5) * 1.5
                base_net = 45.0 + (index % 7) * 4.0
            else:
                base_cpu = 62.0 + (12.0 if 11 <= hour <= 16 else 0) + (index % 6) * 2.1
                base_mem = 68.0 + (index % 5) * 1.8
                base_disk = 54.0 + (index % 8) * 3.2
                base_net = 210.0 + (index % 9) * 15.0
            predicted_cpu = base_cpu + 1.5
            is_bottleneck = False

        elif vm_id in ("vm-analytics", "vm-ehr-core", "vm-checkout-api"):
            spike_start = 16 if vm_id == "vm-ehr-core" else 18 if vm_id == "vm-checkout-api" else 14
            spike_end = spike_start + 4
            if spike_start <= hour <= spike_end:
                base_cpu = 92.0 + (index % 4) * 1.4
                base_mem = 88.0 + (index % 3) * 1.5
                base_disk = 82.0 + (index % 5) * 2.5
                base_net = 410.0 + (index % 6) * 18.0
                predicted_cpu = min(98.8, base_cpu + 2.5)
                is_bottleneck = True
            elif is_night_window:
                base_cpu = 28.0 + (index % 4) * 1.8
                base_mem = 42.0 + (index % 3) * 1.2
                base_disk = 24.0 + (index % 4) * 1.5
                base_net = 95.0 + (index % 5) * 8.0
                predicted_cpu = base_cpu - 1.0
                is_bottleneck = False
            else:
                base_cpu = 58.0 + (index % 5) * 2.2
                base_mem = 64.0 + (index % 4) * 1.6
                base_disk = 48.0 + (index % 5) * 2.0
                base_net = 240.0 + (index % 7) * 12.0
                predicted_cpu = base_cpu + 2.0
                is_bottleneck = False

        elif vm_id == "vm-imaging-gpu":
            if hour >= 20 or hour < 6:
                base_cpu = 4.0 + (index % 3) * 0.8
                base_mem = 18.0 + (index % 3) * 0.5
                base_disk = 8.0 + (index % 2) * 1.0
                base_net = 15.0 + (index % 4) * 2.0
                predicted_cpu = 4.2
                is_bottleneck = False
            else:
                base_cpu = 74.0 + (index % 6) * 2.5
                base_mem = 68.0 + (index % 4) * 1.8
                base_disk = 62.0 + (index % 5) * 2.2
                base_net = 320.0 + (index % 8) * 18.0
                predicted_cpu = base_cpu + 1.0
                is_bottleneck = False

        elif vm_id == "vm-batch":
            if 1 <= hour <= 4:
                base_cpu = 76.0 + (index % 6) * 2.2
                base_mem = 65.0 + (index % 5) * 2.0
                base_disk = 68.0 + (index % 7) * 3.1
                base_net = 180.0 + (index % 6) * 15.0
                predicted_cpu = base_cpu
                is_bottleneck = False
            else:
                base_cpu = 4.2 + (index % 4) * 0.8
                base_mem = 18.5 + (index % 3) * 0.6
                base_disk = 8.0 + (index % 3) * 1.0
                base_net = 12.0 + (index % 4) * 2.0
                predicted_cpu = 4.5
                is_bottleneck = False

        else:
            if is_night_window:
                base_cpu = 16.0 + (index % 4) * 1.5
                base_mem = 28.0 + (index % 3) * 1.0
                base_disk = 14.0 + (index % 3) * 1.2
                base_net = 55.0 + (index % 5) * 8.0
            else:
                base_cpu = 42.0 + (index % 6) * 2.0
                base_mem = 48.0 + (index % 4) * 1.8
                base_disk = 32.0 + (index % 5) * 2.0
                base_net = 195.0 + (index % 7) * 16.0
            predicted_cpu = base_cpu + 1.0
            is_bottleneck = False

        cpu_val = round(max(3.0, min(99.0, base_cpu)), 1)
        mem_val = round(max(10.0, min(98.0, base_mem)), 1)
        disk_val = round(max(5.0, min(95.0, base_disk)), 1)
        net_val = round(max(10.0, min(500.0, base_net)), 1)
        pred_cpu_val = round(max(3.0, min(99.0, predicted_cpu)), 1)
        pred_mem_val = round(max(12.0, min(98.0, base_mem + 1.5)), 1)
        pred_disk_val = round(max(5.0, min(95.0, base_disk + 2.0)), 1)

        points.append({
            "timestamp": timestamp.isoformat() + "Z",
            "timeLabel": timestamp.strftime(lbl_format),
            "fullDate": timestamp.strftime("%A, %b %d, %Y %I:%M %p"),
            "cpu": cpu_val,
            "predictedCpu": pred_cpu_val,
            "ram": mem_val,
            "memory": mem_val,
            "predictedRam": pred_mem_val,
            "predictedMemory": pred_mem_val,
            "disk": disk_val,
            "predictedDisk": pred_disk_val,
            "network": net_val,
            "isNightWindow": is_night_window,
            "isBottleneck": is_bottleneck or (pred_cpu_val >= 85.0),
            "bottleneckThreshold": 85.0,
        })

    return points


def format_vm(vm_dict: Dict[str, Any]) -> Dict[str, Any]:
    specs = vm_dict.get("specs", {})
    vm_out = dict(vm_dict)
    vm_out["size"] = vm_dict.get("vmSize", "Standard_D4s_v5")
    vm_out["cores"] = specs.get("cores", 4)
    vm_out["ram"] = specs.get("ramGb", 16)
    vm_out["ramGb"] = specs.get("ramGb", 16)
    vm_out["storage"] = specs.get("storageGb", 256)
    vm_out["storageGb"] = specs.get("storageGb", 256)
    vm_out["maxIops"] = specs.get("maxIops", 6400)
    vm_out["bandwidth"] = specs.get("bandwidthMbps", 8000)
    vm_out["hourlyRate"] = vm_dict.get("currentHourlyRate", 0.25)
    vm_out["ip"] = vm_dict.get("privateIp", "10.0.1.4")

    vid = vm_dict.get("id", "")
    if "cpuUsage" in vm_dict and "ramUsage" in vm_dict:
        vm_out["cpuUsage"] = vm_dict["cpuUsage"]
        vm_out["ramUsage"] = vm_dict["ramUsage"]
        vm_out["diskUsage"] = vm_dict.get("diskUsage", 2400)
    elif vm_dict.get("status") == "Bottleneck Warning" or vid in ("vm-analytics", "vm-ehr-core", "vm-checkout-api"):
        vm_out["cpuUsage"] = 92.4
        vm_out["ramUsage"] = 88.5
        vm_out["diskUsage"] = int(specs.get("maxIops", 6400) * 0.78)
    elif vid in ("vm-web-prod", "vm-rec-engine"):
        vm_out["cpuUsage"] = 44.5
        vm_out["ramUsage"] = 54.0
        vm_out["diskUsage"] = int(specs.get("maxIops", 6400) * 0.35)
    elif vid in ("vm-batch", "vm-imaging-gpu"):
        vm_out["cpuUsage"] = 16.5
        vm_out["ramUsage"] = 32.0
        vm_out["diskUsage"] = int(specs.get("maxIops", 6400) * 0.18)
    else:
        vm_out["cpuUsage"] = 38.0
        vm_out["ramUsage"] = 48.0
        vm_out["diskUsage"] = int(specs.get("maxIops", 6400) * 0.26)

    cid = vm_dict.get("customerId", "")
    cust_info = CUSTOMERS.get(cid, {})
    cust_name = vm_dict.get("customerName") or cust_info.get("name") or cust_info.get("company") or "Enterprise Client"
    vm_out["customerName"] = cust_name
    vm_out["customerId"] = cid
    vm_out["ownerName"] = cust_name
    vm_out["userId"] = vm_dict.get("userId", cid)

    return vm_out


@app.get("/health")
def health():
    return {"status": "ok", "service": "SmartCloud Optimizer FinOps Engine", "version": "2.1.0"}


@app.post("/api/login")
def login(req: LoginRequest):
    username_lower = req.username.lower().strip()
    if "contoso" in username_lower:
        customer_id = "cust-contoso"
        user_name = "Dr. Sarah Lin"
        role = "Cloud Architect"
    elif "fabrikam" in username_lower:
        customer_id = "cust-fabrikam"
        user_name = "Alex Vance"
        role = "VP of Infrastructure"
    elif "admin" in username_lower or "northwind" in username_lower:
        customer_id = "cust-northwind"
        user_name = "Adarsh (FinOps Lead)"
        role = "FinOps Administrator"
    else:
        customer_id = "cust-northwind"
        user_name = req.username.split("@")[0].title() if "@" in req.username else req.username.title()
        role = "Infrastructure Manager"

    customer = CUSTOMERS.get(customer_id, CUSTOMERS["cust-northwind"])
    return {
        "success": True,
        "token": f"jwt-token-{customer_id}-{datetime.utcnow().timestamp()}",
        "user": {
            "name": user_name,
            "email": req.username if "@" in req.username else f"{req.username}@{customer_id.split('-')[1]}.com",
            "role": role,
            "customerId": customer_id,
            "customerName": customer["name"],
        },
        "customer": customer,
    }


@app.get("/api/customers")
def get_customers():
    return {"customers": list(CUSTOMERS.values())}


@app.get("/api/vms")
def get_vms(
    customerId: Optional[str] = "cust-northwind",
    userId: Optional[str] = None,
    isSuperAdmin: Optional[bool] = False,
):
    is_admin = isSuperAdmin or customerId in ("all", "super_admin", "cust-superadmin", "cust-admin")
    if is_admin:
        all_vms = [format_vm(v) for v in VM_STATE.values()]
        return {
            "customer": {
                "id": "cust-superadmin",
                "name": "Super Admin Platform Lead",
                "company": "SmartCloud Headquarters",
                "subscriptionId": "sub-az-superadmin-root",
                "budgetLimit": 500000,
                "primaryRegion": "Global Multi-Tenant",
                "vmIds": list(VM_STATE.keys()),
            },
            "vms": all_vms,
            "isSuperAdmin": True,
        }

    if customerId not in CUSTOMERS:
        CUSTOMERS[customerId] = {
            "id": customerId,
            "name": f"{customerId.replace('cust-', '').title()} Tenant",
            "company": "Customer Tenant",
            "subscriptionId": f"sub-az-{customerId[:8]}",
            "budgetLimit": 50000,
            "primaryRegion": "East US / Central India",
            "vmIds": [],
        }
        persist_all()

    customer = CUSTOMERS[customerId]
    vms_out = []
    for vid in customer.get("vmIds", []):
        if vid in VM_STATE:
            vms_out.append(format_vm(VM_STATE[vid]))

    for vid, v_data in VM_STATE.items():
        if v_data.get("customerId") == customerId or (userId and v_data.get("userId") == userId):
            formatted = format_vm(v_data)
            if not any(x["id"] == vid for x in vms_out):
                vms_out.append(formatted)

    return {"customer": customer, "vms": vms_out, "isSuperAdmin": False}


@app.post("/api/vms/provision")
def provision_vm(payload: ProvisionVmRequest):
    cid = payload.customerId
    user_id = payload.userId or cid
    cust_name = payload.customerName or (CUSTOMERS.get(cid, {}).get("name") if cid in CUSTOMERS else None) or f"{cid.replace('cust-', '').title()} Tenant"

    if cid not in CUSTOMERS:
        CUSTOMERS[cid] = {
            "id": cid,
            "name": cust_name,
            "company": cust_name,
            "subscriptionId": f"sub-az-{cid[:8]}",
            "budgetLimit": 60000,
            "primaryRegion": payload.region or "East US / Central India",
            "vmIds": [],
        }
    else:
        if payload.customerName:
            CUSTOMERS[cid]["name"] = payload.customerName
            CUSTOMERS[cid]["company"] = payload.customerName

    plan = payload.planId.lower()
    vid = payload.vmId or f"vm-{cid.replace('cust-', '')[:6]}-{uuid.uuid4().hex[:6]}"
    default_name = f"{cid.replace('cust-', '')}-{plan}-01"
    vm_name = payload.vmName or default_name

    if plan == "starter":
        cores = 2
        ram_gb = 4
        storage_gb = 64
        max_iops = 1280
        sku = "Standard_B2s"
        hourly_rate = 2.56
        current_spend = 1850
        projected_spend = 1200
        savings = 650
        workload = "Light Microservices & Background Worker"
        rec_type = "nominal"
        rec_title = f"FinOps Live Baseline Calibration for {vm_name}"
        rec_reason = "Node is newly provisioned with nominal utilization (CPU: 11.8%, RAM: 23.5%). FinOps AI is collecting live telemetry baseline."
    elif plan == "enterprise":
        cores = 8
        ram_gb = 64
        storage_gb = 256
        max_iops = 12800
        sku = "Standard_E8s_v5"
        hourly_rate = 25.27
        current_spend = 18200
        projected_spend = 13800
        savings = 4400
        workload = "Data Ingestion & Machine Learning Analytics"
        rec_type = "nominal"
        rec_title = f"FinOps Live Baseline Calibration for {vm_name}"
        rec_reason = "Node is newly provisioned with nominal utilization (CPU: 11.8%, RAM: 23.5%). FinOps AI is collecting live telemetry baseline."
    else:  # business (default)
        cores = 4
        ram_gb = 16
        storage_gb = 128
        max_iops = 6400
        sku = "Standard_D4s_v5"
        hourly_rate = 10.27
        current_spend = 7400
        projected_spend = 5200
        savings = 2200
        workload = "Production Web Application & API Cluster"
        rec_type = "nominal"
        rec_title = f"FinOps Live Baseline Calibration for {vm_name}"
        rec_reason = "Node is newly provisioned with nominal utilization (CPU: 11.8%, RAM: 23.5%). FinOps AI is collecting live telemetry baseline."

    now_dt = datetime.utcnow()
    initial_live_series = [
        {
            "timestamp": (now_dt - timedelta(seconds=10)).isoformat() + "Z",
            "timeLabel": (now_dt - timedelta(seconds=10)).strftime("%H:%M:%S"),
            "fullDate": (now_dt - timedelta(seconds=10)).strftime("%A, %b %d, %Y %I:%M:%S %p"),
            "cpu": 8.5,
            "predictedCpu": 9.0,
            "ram": 21.0,
            "memory": 21.0,
            "predictedRam": 22.0,
            "predictedMemory": 22.0,
            "disk": 18,
            "predictedDisk": 20,
            "network": 8.0,
            "isNightWindow": False,
            "isBottleneck": False,
            "bottleneckThreshold": 85.0,
            "isLiveTick": True,
        },
        {
            "timestamp": (now_dt - timedelta(seconds=5)).isoformat() + "Z",
            "timeLabel": (now_dt - timedelta(seconds=5)).strftime("%H:%M:%S"),
            "fullDate": (now_dt - timedelta(seconds=5)).strftime("%A, %b %d, %Y %I:%M:%S %p"),
            "cpu": 14.2,
            "predictedCpu": 14.5,
            "ram": 23.2,
            "memory": 23.2,
            "predictedRam": 24.0,
            "predictedMemory": 24.0,
            "disk": 32,
            "predictedDisk": 35,
            "network": 24.0,
            "isNightWindow": False,
            "isBottleneck": False,
            "bottleneckThreshold": 85.0,
            "isLiveTick": True,
        },
        {
            "timestamp": now_dt.isoformat() + "Z",
            "timeLabel": now_dt.strftime("%H:%M:%S"),
            "fullDate": now_dt.strftime("%A, %b %d, %Y %I:%M:%S %p"),
            "cpu": 11.8,
            "predictedCpu": 12.0,
            "ram": 23.5,
            "memory": 23.5,
            "predictedRam": 24.0,
            "predictedMemory": 24.0,
            "disk": 24,
            "predictedDisk": 28,
            "network": 14.0,
            "isNightWindow": False,
            "isBottleneck": False,
            "bottleneckThreshold": 85.0,
            "isLiveTick": True,
        },
    ]

    VM_STATE[vid] = {
        "id": vid,
        "name": vm_name,
        "customerId": cid,
        "status": "Healthy",
        "region": payload.region or "East US / Central India",
        "resourceGroup": f"rg-{cid[:8]}-prod",
        "vmSize": sku,
        "os": "Ubuntu Linux 22.04 LTS",
        "privateIp": f"10.50.1.{len(CUSTOMERS[cid]['vmIds']) + 10}",
        "publicIp": f"20.84.112.{len(CUSTOMERS[cid]['vmIds']) + 20}",
        "specs": {
            "cores": cores,
            "ramGb": ram_gb,
            "storageGb": storage_gb,
            "storageType": "Premium SSD",
            "maxIops": max_iops,
            "bandwidthMbps": cores * 1000,
        },
        "currentHourlyRate": hourly_rate,
        "currentSpend": current_spend,
        "projectedSpend": projected_spend if payload.autoScaleEnabled else current_spend,
        "savings": savings if payload.autoScaleEnabled else 0,
        "autoScaleEnabled": payload.autoScaleEnabled,
        "workloadProfile": workload,
        "isNew": True,
        "hasHistoricalData": False,
        "provisionedAt": now_dt.isoformat() + "Z",
        "uptime": "Live (< 1m uptime)",
        "mtdSpend": 0,
        "cpuUsage": 11.8,
        "ramUsage": 23.5,
        "diskUsage": 24,
        "liveSeries": initial_live_series,
        "recommendation": {
            "type": rec_type,
            "title": f"FinOps AI Calibration for {vm_name}",
            "urgency": "AI Profiling Mode",
            "confidence": 75,
            "reason": "Node is newly provisioned. FinOps AI is collecting live baseline telemetry. Automated scheduling will calibrate after initial operational telemetry.",
            "formula": "Live Baseline Learning Mode (24-Hour Calibration)",
            "billingImpact": f"Plan Rate: ₹{current_spend:,}/mo (MTD billed: ₹0)",
            "calculationSteps": [
                {"label": "Node Provisioned Rate", "value": f"₹{current_spend:,}/mo ({sku})"},
                {"label": "Telemetry Accumulation", "value": "Streaming live metrics (No prior history)"},
                {"label": "Projected Elastic Run Rate", "value": f"₹{projected_spend:,}/mo"},
            ],
            "targetSku": sku,
        },
    }

    VM_STATE[vid]["customerName"] = cust_name
    VM_STATE[vid]["customerId"] = cid
    VM_STATE[vid]["userId"] = user_id
    VM_STATE[vid]["ownerEmail"] = payload.email or ""

    if vid not in CUSTOMERS[cid]["vmIds"]:
        CUSTOMERS[cid]["vmIds"].append(vid)

    if user_id in USER_ACCOUNTS:
        curr_assigned = USER_ACCOUNTS[user_id].get("assigned_vms", [])
        if not any((isinstance(x, dict) and x.get("id") == vid) or x == vid for x in curr_assigned):
            curr_assigned.append({
                "id": vid,
                "name": vm_name,
                "size": sku,
                "cores": cores,
                "ram": ram_gb,
                "status": "Healthy",
                "spend": current_spend,
            })
            USER_ACCOUNTS[user_id]["assigned_vms"] = curr_assigned

    record_audit_log(
        action="PROVISION_INSTANCE",
        vm_id=vid,
        vm_name=vm_name,
        prev_spend=0,
        cur_spend=current_spend,
        prev_spec="None (Unallocated)",
        cur_spec=f"{sku} ({cores} Cores, {ram_gb} GB)",
        reason=f"New VM deployed under tenant {cust_name}. Autonomous FinOps monitoring activated.",
        category="Resource Provisioning",
    )

    persist_all()

    formatted = format_vm(VM_STATE[vid])
    formatted["series"] = initial_live_series
    formatted["isNew"] = True
    formatted["hasHistoricalData"] = False

    return {
        "success": True,
        "message": f"VM '{vm_name}' successfully provisioned and attached to customer {cid}.",
        "vm": formatted,
    }


@app.post("/api/users/sync")
def sync_user(payload: SyncUserPayload):
    uid = payload.user_id
    existing = USER_ACCOUNTS.get(uid, {})
    USER_ACCOUNTS[uid] = {
        "user_id": uid,
        "email_id": payload.email_id,
        "password": payload.password or existing.get("password", "••••••••"),
        "customer_name": payload.customer_name or existing.get("customer_name", "Enterprise Customer"),
        "company": payload.company or existing.get("company", "Cloud Enterprise"),
        "role": payload.role or existing.get("role", "customer"),
        "assigned_vms": payload.assigned_vms if payload.assigned_vms else existing.get("assigned_vms", []),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "created_at": existing.get("created_at", datetime.utcnow().isoformat() + "Z"),
    }
    persist_all()
    return {"success": True, "user": USER_ACCOUNTS[uid]}


@app.get("/api/users/monitoring")
def get_user_monitoring():
    return {
        "success": True,
        "users": list(USER_ACCOUNTS.values()),
        "total_users": len(USER_ACCOUNTS),
    }


def ensure_vm_exists(vm_id: str):
    if vm_id not in VM_STATE and vm_id.startswith("vm-"):
        parts = vm_id.split("-")
        cid_slug = parts[1] if len(parts) > 1 else "tenant"
        VM_STATE[vm_id] = {
            "id": vm_id,
            "name": f"{cid_slug}-node-{parts[-1]}",
            "customerId": f"cust-{cid_slug}",
            "status": "Healthy",
            "region": "East US / Central India",
            "resourceGroup": f"rg-{cid_slug}-prod",
            "vmSize": "Standard_D4s_v5",
            "os": "Ubuntu Linux 22.04 LTS",
            "privateIp": "10.50.1.10",
            "publicIp": "20.84.112.20",
            "specs": {
                "cores": 4,
                "ramGb": 16,
                "storageGb": 128,
                "storageType": "Premium SSD",
                "maxIops": 6400,
                "bandwidthMbps": 4000,
            },
            "currentHourlyRate": 10.27,
            "currentSpend": 7400,
            "projectedSpend": 5200,
            "savings": 2200,
            "autoScaleEnabled": True,
            "workloadProfile": "Production Cloud Node",
            "isNew": True,
            "hasHistoricalData": False,
            "uptime": "Live (< 1m uptime)",
            "mtdSpend": 0,
            "cpuUsage": 11.8,
            "ramUsage": 23.5,
            "diskUsage": 24,
            "liveSeries": [],
            "recommendation": {
                "type": "nominal",
                "title": f"FinOps Live Baseline Calibration for {vm_id}",
                "urgency": "AI Profiling Mode",
                "confidence": 85,
                "reason": "Node is healthy with nominal utilization (11.8% CPU, 23.5% RAM). Streaming live metrics.",
                "formula": "Live Baseline Learning Mode (24-Hour Calibration)",
                "billingImpact": "Plan Rate: ₹7,400/mo (MTD billed: ₹0)",
                "calculationSteps": [
                    {"label": "Node Provisioned Rate", "value": "₹7,400/mo"},
                    {"label": "Telemetry Stream", "value": "Streaming live metrics in real-time"},
                    {"label": "Capacity Headroom", "value": "Nominal capacity (> 75% available)"},
                ],
                "targetSku": "Standard_D4s_v5",
            },
        }


@app.get("/api/vm/{vm_id}")
def get_vm_detail(vm_id: str, range: str = "7d", granularity: str = "30m"):
    ensure_vm_exists(vm_id)
    if vm_id not in VM_STATE:
        raise HTTPException(status_code=404, detail="VM not found in customer fleet")

    vm_raw = VM_STATE[vm_id]
    vm_data = format_vm(vm_raw)

    if vm_raw.get("isNew"):
        # Newly provisioned VM: does NOT have historical 7d/30d telemetry.
        # Only has live streaming data points since its provisioning!
        now_dt = datetime.utcnow()
        import random
        last_cpu = vm_raw.get("cpuUsage", 11.8)
        last_ram = vm_raw.get("ramUsage", 23.5)
        new_cpu = round(max(5.0, min(95.0, last_cpu + random.uniform(-1.2, 1.2))), 1)
        new_ram = round(max(10.0, min(90.0, last_ram + random.uniform(-0.4, 0.4))), 1)
        new_disk = round(max(10, min(100, 24 + random.randint(-4, 6))))

        vm_raw["cpuUsage"] = new_cpu
        vm_raw["ramUsage"] = new_ram
        vm_raw["diskUsage"] = new_disk

        new_tick = {
            "timestamp": now_dt.isoformat() + "Z",
            "timeLabel": now_dt.strftime("%H:%M:%S"),
            "fullDate": now_dt.strftime("%A, %b %d, %Y %I:%M:%S %p"),
            "cpu": new_cpu,
            "predictedCpu": round(new_cpu + 1.0, 1),
            "ram": new_ram,
            "memory": new_ram,
            "predictedRam": round(new_ram + 1.0, 1),
            "predictedMemory": round(new_ram + 1.0, 1),
            "disk": new_disk,
            "predictedDisk": new_disk + 4,
            "network": round(14.0 + random.uniform(-2, 3), 1),
            "isNightWindow": False,
            "isBottleneck": False,
            "bottleneckThreshold": 85.0,
            "isLiveTick": True,
        }

        live_list = vm_raw.setdefault("liveSeries", [])
        live_list.append(new_tick)
        if len(live_list) > 60:
            live_list.pop(0)

        vm_data["cpuUsage"] = new_cpu
        vm_data["ramUsage"] = new_ram
        vm_data["diskUsage"] = new_disk
        vm_data["series"] = list(live_list)
        vm_data["isNew"] = True
        vm_data["hasHistoricalData"] = False
        vm_data["provisionedAt"] = vm_raw.get("provisionedAt")
        vm_data["uptime"] = vm_raw.get("uptime", "Live (< 1m uptime)")
        vm_data["mtdSpend"] = vm_raw.get("mtdSpend", 0)
    else:
        time_series = generate_time_series(vm_id, range, granularity)
        vm_data["series"] = time_series
        vm_data["isNew"] = False
        vm_data["hasHistoricalData"] = True

    return {"vm": vm_data, "range": range, "granularity": granularity}


@app.get("/api/vm/{vm_id}/live-tick")
def get_vm_live_tick(vm_id: str):
    ensure_vm_exists(vm_id)
    if vm_id not in VM_STATE:
        raise HTTPException(status_code=404, detail="VM not found")
    vm_raw = VM_STATE[vm_id]
    import random
    now_dt = datetime.utcnow()
    last_cpu = vm_raw.get("cpuUsage", 11.8)
    last_ram = vm_raw.get("ramUsage", 23.5)
    new_cpu = round(max(5.0, min(95.0, last_cpu + random.uniform(-1.2, 1.2))), 1)
    new_ram = round(max(10.0, min(90.0, last_ram + random.uniform(-0.4, 0.4))), 1)
    new_disk = round(max(10, min(100, 24 + random.randint(-4, 6))))
    raw_cpu_val = new_cpu

    # For Docker model VMs, fetch live metrics directly from Docker Agent:
    if vm_id.startswith("docker-"):
        d_host = DOCKER_HOST_STATE.get("host", "http://localhost:8001")
        try:
            req = urllib.request.Request(f"{d_host}/metrics", headers={"User-Agent": "SmartCloudOptimizer/2.1"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status == 200:
                    DOCKER_HOST_STATE["connected"] = True
                    m = json.loads(resp.read().decode())
                    c_info = m.get("container") or {}
                    if c_info and "cpuPercent" in c_info:
                        new_cpu = float(c_info.get("cpuPercent", 0.0))
                        raw_cpu_val = float(c_info.get("rawCpuPercent", new_cpu))
                        new_ram = float(c_info.get("ramPercent", 0.0))
                        if c_info.get("cpuLimit"):
                            cores_val = int(c_info["cpuLimit"]) if c_info["cpuLimit"] == int(c_info["cpuLimit"]) else c_info["cpuLimit"]
                            vm_raw.setdefault("specs", {})["cores"] = cores_val
                            vm_raw["cores"] = cores_val
                            vm_raw["vmSize"] = f"Docker_{cores_val}vCPU_{int(cores_val)}GB"
                            vm_raw["size"] = vm_raw["vmSize"]
                        if c_info.get("ramLimitMb"):
                            ram_val = round(c_info["ramLimitMb"] / 1024, 1)
                            vm_raw.setdefault("specs", {})["ramGb"] = ram_val
                            vm_raw["ram"] = ram_val
                            vm_raw["ramGb"] = ram_val
        except Exception:
            pass

    is_bottleneck = new_cpu >= 80.0
    if is_bottleneck:
        vm_raw["status"] = "Bottleneck Warning"
        if "recommendation" in vm_raw:
            cores = vm_raw.get("specs", {}).get("cores", 2)
            next_tier = min(8, cores + 2)
            vm_raw["recommendation"]["type"] = "upgrade"
            vm_raw["recommendation"]["title"] = f"Bottleneck Alert: Scale up {vm_raw.get('name', 'container')} to {next_tier} vCPUs"
            vm_raw["recommendation"]["urgency"] = "High (Bottleneck Throttling)"
    elif new_cpu < 70.0:
        if vm_raw.get("status") == "Bottleneck Warning":
            cur_c = vm_raw.get("specs", {}).get("cores", 2)
            vm_raw["status"] = f"Healthy (Autoscaled to {cur_c} Cores)" if cur_c > 2 else "Healthy"

    vm_raw["cpuUsage"] = new_cpu
    vm_raw["ramUsage"] = new_ram
    vm_raw["diskUsage"] = new_disk

    tick = {
        "timestamp": now_dt.isoformat() + "Z",
        "timeLabel": now_dt.strftime("%H:%M:%S"),
        "fullDate": now_dt.strftime("%A, %b %d, %Y %I:%M:%S %p"),
        "cpu": new_cpu,
        "predictedCpu": round(new_cpu + 1.0, 1),
        "ram": new_ram,
        "memory": new_ram,
        "predictedRam": round(new_ram + 1.0, 1),
        "predictedMemory": round(new_ram + 1.0, 1),
        "disk": new_disk,
        "predictedDisk": new_disk + 4,
        "network": round(14.0 + random.uniform(-2, 3), 1),
        "isNightWindow": False,
        "isBottleneck": is_bottleneck,
        "bottleneckThreshold": 80.0,
        "isLiveTick": True,
    }

    live_list = vm_raw.setdefault("liveSeries", [])
    live_list.append(tick)
    if len(live_list) > 60:
        live_list.pop(0)

    return {
        "tick": tick,
        "series": list(live_list),
        "vmStatus": vm_raw.get("status", "Healthy"),
        "current": {
            "cpu": new_cpu,
            "rawCpu": raw_cpu_val,
            "ram": new_ram,
            "disk": new_disk,
            "cores": vm_raw.get("specs", {}).get("cores", 2),
            "ramGb": vm_raw.get("specs", {}).get("ramGb", 2.0),
        }
    }


@app.post("/api/vm/{vm_id}/autoscale")
def toggle_autoscale(vm_id: str, payload: AutoScaleToggleRequest):
    if vm_id not in VM_STATE:
        raise HTTPException(status_code=404, detail="VM not found")

    VM_STATE[vm_id]["autoScaleEnabled"] = payload.enabled
    
    # Recalculate projected spend based on auto-scaling state
    if payload.enabled:
        if VM_STATE[vm_id]["recommendation"]["type"] == "downsize":
            VM_STATE[vm_id]["projectedSpend"] = VM_STATE[vm_id]["currentSpend"] - VM_STATE[vm_id]["savings"]
        else:
            delta = 4700 if vm_id == "vm-ehr-core" else 3100 if vm_id == "vm-checkout-api" else 2330
            VM_STATE[vm_id]["projectedSpend"] = VM_STATE[vm_id]["currentSpend"] + delta
    else:
        VM_STATE[vm_id]["projectedSpend"] = VM_STATE[vm_id]["currentSpend"]

    persist_all()

    return {
        "success": True,
        "vmId": vm_id,
        "autoScaleEnabled": VM_STATE[vm_id]["autoScaleEnabled"],
        "projectedSpend": VM_STATE[vm_id]["projectedSpend"],
        "message": "Auto-scaling permission and dynamic billing consent updated successfully.",
    }


@app.post("/api/fleet/autoscale-batch")
def toggle_fleet_autoscale(payload: BatchAutoScaleRequest):
    customer = CUSTOMERS.get(payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    updated_vms = []
    for vid in customer["vmIds"]:
        if vid in VM_STATE:
            VM_STATE[vid]["autoScaleEnabled"] = payload.enabled
            if payload.enabled:
                if VM_STATE[vid]["recommendation"]["type"] == "downsize":
                    VM_STATE[vid]["projectedSpend"] = VM_STATE[vid]["currentSpend"] - VM_STATE[vid]["savings"]
                else:
                    delta = 4700 if vid == "vm-ehr-core" else 3100 if vid == "vm-checkout-api" else 2330
                    VM_STATE[vid]["projectedSpend"] = VM_STATE[vid]["currentSpend"] + delta
            else:
                VM_STATE[vid]["projectedSpend"] = VM_STATE[vid]["currentSpend"]
            updated_vms.append(VM_STATE[vid])

    return {
        "success": True,
        "customerId": payload.customer_id,
        "enabled": payload.enabled,
        "vms": updated_vms,
    }


class SchedulePolicyRequest(BaseModel):
    vm_id: str
    action: str = "shutdown"  # "shutdown" (turn off) or "downscale"
    off_hours_duration: int = 10  # hours/day
    start_time: str = "20:00"
    end_time: str = "06:00"
    days_mode: str = "weekdays"  # "weekdays" or "daily"
    weekend_shutdown: bool = True
    simulated_monthly_savings: float = 0.0


@app.post("/api/vm/{vm_id}/schedule")
def apply_schedule_policy(vm_id: str, payload: SchedulePolicyRequest):
    ensure_vm_exists(vm_id)
    if vm_id not in VM_STATE:
        raise HTTPException(status_code=404, detail="VM not found")

    vm = VM_STATE[vm_id]
    vm["schedulePolicy"] = {
        "action": payload.action,
        "offHoursDuration": payload.off_hours_duration,
        "startTime": payload.start_time,
        "endTime": payload.end_time,
        "daysMode": payload.days_mode,
        "weekendShutdown": payload.weekend_shutdown,
        "appliedAt": datetime.utcnow().isoformat() + "Z",
    }
    if payload.simulated_monthly_savings > 0:
        prev_spend = vm.get("currentSpend", 18000)
        cur_spend = max(0, round(prev_spend - payload.simulated_monthly_savings, 2))
        vm["savings"] = round(payload.simulated_monthly_savings, 2)
        vm["projectedSpend"] = cur_spend
        action_label = "Deallocated / Turned Off" if payload.action == "shutdown" else "Rightsized to 50% Capacity"
        vm["recommendation"] = {
            "type": "downsize",
            "title": f"Active Off-Hours Policy: {payload.off_hours_duration}h/day {action_label}",
            "urgency": "High Cost Optimization",
            "confidence": 98,
            "reason": f"VM scheduled to be {action_label.lower()} during {payload.start_time} - {payload.end_time} ({payload.days_mode}) saving ₹{int(payload.simulated_monthly_savings):,}/mo.",
            "formula": f"Savings = HourlyRate * {payload.off_hours_duration}h * Days",
            "calculationSteps": [
                {"label": "Policy Action", "value": action_label},
                {"label": "Daily Shutdown Window", "value": f"{payload.off_hours_duration} Hours ({payload.start_time}–{payload.end_time})"},
                {"label": "Weekend Shutdown", "value": "Active (+48h)" if payload.weekend_shutdown else "Inactive"},
            ],
            "targetSku": "Standard_B2s (Off-Hours)" if payload.action == "downscale" else "Deallocated (₹0/hr)",
        }
        record_audit_log(
            action="SCHEDULED_SHUTDOWN" if payload.action == "shutdown" else "OFF_HOURS_RIGHTSIZING",
            vm_id=vm_id,
            vm_name=vm.get("name", vm_id),
            prev_spend=prev_spend,
            cur_spend=cur_spend,
            prev_spec=vm.get("vmSize", "Standard_D4s_v5"),
            cur_spec=f"{payload.off_hours_duration}h/day {action_label}",
            reason=f"Configured {payload.off_hours_duration}h/day off-hours shutoff ({payload.start_time}–{payload.end_time}, {payload.days_mode})",
            category="Cost Reduction",
        )

    persist_all()

    return {
        "success": True,
        "vmId": vm_id,
        "message": f"Successfully applied {payload.off_hours_duration}h shutdown policy to {vm.get('name', vm_id)}.",
        "vm": vm,
    }


@app.get("/api/audit-logs")
def get_audit_logs(customerId: Optional[str] = None):
    """Returns chronologically ordered change events and spend comparison metrics."""
    target_cust = customerId or "cust-northwind"
    vms_pool = [vm for vm in VM_STATE.values() if not customerId or vm.get("customerId") == target_cust]
    total_baseline = sum(vm.get("currentSpend", 0) for vm in vms_pool)
    total_current = sum(vm.get("projectedSpend", vm.get("currentSpend", 0)) for vm in vms_pool)
    total_savings = sum(vm.get("savings", 0) for vm in vms_pool)

    return {
        "logs": AUDIT_LOGS,
        "spendSummary": {
            "baselineSpend": total_baseline,
            "currentSpend": total_current,
            "totalSavings": total_savings,
            "savingsPercent": round((total_savings / total_baseline) * 100, 1) if total_baseline > 0 else 0.0,
            "annualizedSavings": total_savings * 12,
            "activeVmsCount": len(vms_pool),
        },
    }


@app.get("/api/dashboard/{customer_id}")
def get_dashboard(customer_id: str):
    customer = CUSTOMERS.get(customer_id, CUSTOMERS["cust-northwind"])
    vm_ids = customer["vmIds"]
    vms = [VM_STATE[vid] for vid in vm_ids if vid in VM_STATE]

    total_current = sum(vm["currentSpend"] for vm in vms)
    total_projected = sum(vm["projectedSpend"] for vm in vms)
    total_savings = sum(vm["savings"] for vm in vms if vm["autoScaleEnabled"])

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_spend_comparison = []
    base_daily = total_current / 30.0
    for idx, day in enumerate(days):
        is_weekend = idx >= 5
        cur_day_spend = round(base_daily * (0.85 if is_weekend else 1.05), 0)
        opt_day_spend = round(cur_day_spend * (0.62 if is_weekend else 0.73), 0)
        weekly_spend_comparison.append({
            "day": day,
            "shortDay": day[:3],
            "baselineSpend": int(cur_day_spend),
            "optimizedSpend": int(opt_day_spend),
            "savings": int(cur_day_spend - opt_day_spend),
        })

    return {
        "customer": customer,
        "summary": {
            "currentSpend": total_current,
            "projectedSpend": total_projected,
            "savings": total_savings,
            "activeVmsCount": len(vms),
            "bottlenecksCount": sum(1 for vm in vms if vm["status"] == "Bottleneck Warning"),
            "downsizeOpportunities": sum(1 for vm in vms if vm["recommendation"]["type"] == "downsize"),
            "autoscaleActiveCount": sum(1 for vm in vms if vm["autoScaleEnabled"]),
        },
        "weeklyComparison": weekly_spend_comparison,
        "vms": vms,
    }


@app.post("/api/docker/connect")
def connect_docker_host(payload: DockerConnectPayload):
    host = payload.host.rstrip("/")
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"

    DOCKER_HOST_STATE["host"] = host
    containers = []
    is_live = False
    host_info = {}

    try:
        req = urllib.request.Request(f"{host}/health", headers={"User-Agent": "SmartCloudOptimizer/2.1"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            if resp.status == 200:
                host_info = json.loads(resp.read().decode())
                is_live = True
    except Exception as e:
        print(f"Docker host health check failed for {host}: {e}")

    if is_live:
        try:
            req = urllib.request.Request(f"{host}/containers", headers={"User-Agent": "SmartCloudOptimizer/2.1"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    containers = data.get("containers", [])
        except Exception as e:
            print(f"Failed to fetch containers from {host}: {e}")

    if not containers:
        # Provide simulated model containers if friend's agent is not active yet
        containers = [
            {
                "id": "c7a8109bf1d2",
                "name": "friend-laptop-web-api",
                "image": "nginx:alpine",
                "status": "Up 3 hours (Model VM)",
                "cpuUsage": 46.2,
                "ramUsage": 58.0,
                "ramLimitGb": 8.0,
                "cpus": 4,
                "isSimulated": not is_live,
            },
            {
                "id": "e9b2341ac8f0",
                "name": "friend-laptop-ml-engine",
                "image": "pytorch/pytorch:latest",
                "status": "Up 1 hour (Model VM)",
                "cpuUsage": 91.5,
                "ramUsage": 87.4,
                "ramLimitGb": 16.0,
                "cpus": 8,
                "isSimulated": not is_live,
            },
            {
                "id": "f10c897de231",
                "name": "friend-laptop-redis",
                "image": "redis:7.2-alpine",
                "status": "Up 2 days (Model VM)",
                "cpuUsage": 12.0,
                "ramUsage": 24.5,
                "ramLimitGb": 4.0,
                "cpus": 2,
                "isSimulated": not is_live,
            },
        ]

    if is_live:
        mock_cids = ["docker-c7a8109bf1d2", "docker-e9b2341ac8f0", "docker-f10c897de231"]
        for mcid in mock_cids:
            if mcid in VM_STATE:
                del VM_STATE[mcid]
            for c_id, c_data in CUSTOMERS.items():
                if mcid in c_data.get("vmIds", []):
                    c_data["vmIds"] = [x for x in c_data["vmIds"] if x != mcid]

    DOCKER_HOST_STATE["connected"] = is_live
    DOCKER_HOST_STATE["lastPing"] = datetime.utcnow().isoformat() + "Z"
    DOCKER_HOST_STATE["containers"] = containers
    DOCKER_HOST_STATE["hostInfo"] = host_info

    target_customer_id = payload.customerId or "cust-northwind"
    if target_customer_id not in CUSTOMERS:
        CUSTOMERS[target_customer_id] = {
            "id": target_customer_id,
            "name": "User Account",
            "company": "Enterprise Cloud Fleet",
            "subscriptionId": f"sub-{target_customer_id}",
            "budgetLimit": 50000,
            "primaryRegion": "East US / Central India",
            "vmIds": [],
        }

    # Register container(s)
    docker_vm_ids = []
    for c in containers:
        cid = c["id"]
        vid = f"docker-{cid}"
        docker_vm_ids.append(vid)

        cpu_val = float(c.get("cpuUsage", 45.0))
        ram_val = float(c.get("ramUsage", 50.0))
        is_bottleneck = cpu_val >= 80.0
        cores = c.get("cpus", 4)
        ram_gb = int(c.get("ramLimitGb", 8))

        rec_type = "upgrade" if is_bottleneck else "downsize"
        rec_title = (
            f"Bottleneck Alert: Scale up container {c.get('name')} to {cores * 2} vCPUs"
            if is_bottleneck
            else f"Off-Hours Downsize: Reduce {c.get('name')} to {max(1, cores // 2)} vCPUs"
        )
        rec_reason = (
            f"Container CPU reached {cpu_val}% and RAM reached {ram_val}%. Increasing container quota prevents throttling."
            if is_bottleneck
            else f"Telemetry indicates off-peak usage (CPU: {cpu_val}%, RAM: {ram_val}%). Scaling down saves host resources."
        )

        VM_STATE[vid] = {
            "id": vid,
            "name": c.get("name", vid),
            "customerId": target_customer_id,
            "status": "Bottleneck Warning" if is_bottleneck else "Healthy",
            "region": f"Docker Host ({host})",
            "resourceGroup": "rg-docker-model-vms",
            "vmSize": f"Docker_{cores}vCPU_{ram_gb}GB",
            "os": f"Container ({c.get('image', 'linux')})",
            "privateIp": "172.17.0.2",
            "publicIp": host.replace("http://", "").replace("https://", "").split(":")[0],
            "specs": {
                "cores": cores,
                "ramGb": ram_gb,
                "storageGb": 64,
                "storageType": "Docker Overlay2 NVMe",
                "maxIops": 8000,
                "bandwidthMbps": 1000,
            },
            "currentHourlyRate": 0.14,
            "currentSpend": 14200,
            "projectedSpend": 16530 if is_bottleneck else 10500,
            "savings": 0 if is_bottleneck else 3700,
            "autoScaleEnabled": False,
            "workloadProfile": f"Docker Model VM: {c.get('image', 'app')}",
            "recommendation": {
                "type": rec_type,
                "title": rec_title,
                "urgency": "High (Bottleneck Throttling)" if is_bottleneck else "Moderate (Cost Savings)",
                "confidence": 92,
                "reason": rec_reason,
                "formula": f"Dynamic docker update --cpus {cores} --memory {ram_gb}g",
                "billingImpact": "Compute capacity scales dynamically with container workload.",
                "calculationSteps": [
                    {"label": "Host Container CPU Target", "value": f"{cores} Cores"},
                    {"label": "Memory Allocation Target", "value": f"{ram_gb} GB RAM"},
                    {"label": "Telemetry Host", "value": host},
                ],
                "targetSku": f"Docker_{cores * 2 if is_bottleneck else max(1, cores // 2)}vCPU",
            },
        }

        # Add Docker VM directly to the existing active customer's fleet!
        if vid not in CUSTOMERS[target_customer_id]["vmIds"]:
            CUSTOMERS[target_customer_id]["vmIds"].append(vid)

    # Also maintain cust-docker for independent reference
    CUSTOMERS["cust-docker"] = {
        "id": "cust-docker",
        "name": "Friend's Docker Host (Model VM)",
        "company": f"Remote Docker Engine ({host})",
        "subscriptionId": "sub-docker-model-laptop",
        "budgetLimit": 50000,
        "primaryRegion": f"Friend's Laptop ({host})",
        "vmIds": docker_vm_ids,
    }

    return {
        "success": True,
        "connected": is_live,
        "host": host,
        "hostInfo": host_info,
        "message": (
            f"Successfully connected to Docker agent at {host} and added {len(containers)} container(s) to your fleet!"
            if is_live
            else f"Could not reach live agent at {host}. Added simulated Model VM containers to your fleet."
        ),
        "containersCount": len(containers),
        "containers": containers,
        "customerId": target_customer_id,
        "addedVmIds": docker_vm_ids,
    }


@app.get("/api/docker/status")
def get_docker_status():
    return DOCKER_HOST_STATE


@app.post("/api/docker/scale")
def scale_docker_container(payload: DockerScalePayload):
    cid = payload.containerId
    vid = f"docker-{cid}" if not cid.startswith("docker-") else cid
    raw_cid = cid.replace("docker-", "")

    # Forward to friend's agent if connected
    host = DOCKER_HOST_STATE.get("host", "http://localhost:8001")
    agent_msg = "Simulated scale executed"
    if DOCKER_HOST_STATE.get("connected"):
        try:
            req_data = json.dumps({"containerId": raw_cid, "cpus": payload.cpus, "memory": payload.memory}).encode()
            req = urllib.request.Request(
                f"{host}/scale",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "SmartCloudOptimizer/2.1"},
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                res_json = json.loads(resp.read().decode())
                agent_msg = res_json.get("message", "Success")
        except Exception as e:
            agent_msg = f"Agent call warning: {e}"

    if vid in VM_STATE:
        VM_STATE[vid]["autoScaleEnabled"] = True
        VM_STATE[vid]["specs"]["cores"] = int(payload.cpus)
        VM_STATE[vid]["status"] = "Healthy (Autoscaled)"

    return {
        "success": True,
        "containerId": raw_cid,
        "vmId": vid,
        "message": f"Container {raw_cid} dynamically scaled to {payload.cpus} CPUs and {payload.memory} memory. {agent_msg}",
    }


@app.get("/")
def root():
    return {"message": "SmartCloud Optimizer FinOps API v2.1 is running"}
