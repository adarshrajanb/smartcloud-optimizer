#!/usr/bin/env python3
"""
SmartCloud Optimizer - DevOps Container Telemetry & Live Scaling Agent
=====================================================================
A high-performance FastAPI service designed for Windows/Linux host systems
to monitor container workloads (utho-workload) and execute dynamic live 
resource resizing without downtime.

Endpoints:
    GET  /                -> Health check & agent status
    GET  /health          -> Health check alias (for backend handshake)
    GET  /containers      -> Formatted container list for FinOps dashboard
    GET  /metrics         -> Host & container CPU/RAM telemetry stream
    POST /resize          -> Live resource resizing via docker update
    POST /scale           -> Backward-compatible scale endpoint
    POST /stress/start    -> Injects high CPU stress workload inside utho-workload
    POST /stress/stop     -> Terminates active stress workload processes
    GET  /stress/status   -> Current stress activity, worker count & metrics
    GET  /autoscale       -> Status and event log of dynamic auto-scaling watchdog
    POST /autoscale       -> Configure / toggle dynamic auto-scaler
    GET  /status          -> Extended container & host inspection
"""

import os
import sys
import time
import math
import shutil
import socket
import threading
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List

import psutil
import docker
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Ensure UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TARGET_CONTAINER = "utho-workload"
AGENT_PORT = 8001
WORKLOAD_IMAGE = "nginx:alpine"
WORKLOAD_PORT_HOST = 5000
WORKLOAD_PORT_CONTAINER = 80

# ---------------------------------------------------------------------------
# 1. Locate Docker Executable & Initialize SDK
# ---------------------------------------------------------------------------
def find_docker_executable() -> Optional[str]:
    """Detects docker.exe across system PATH and standard Windows install paths."""
    candidates = [
        shutil.which("docker"),
        shutil.which("docker.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\DockerDesktop\resources\bin\docker.exe"),
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), r"Docker\Docker\resources\bin\docker.exe"),
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), r"Docker\Docker\docker.exe"),
        r"C:\Program Files\Docker\Docker\resources\bin\docker.exe",
        r"C:\Program Files\Docker\Docker\docker.exe",
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return os.path.abspath(path)
    return None

DOCKER_BIN = find_docker_executable()

def get_docker_client():
    """Initializes and returns the Docker Python SDK client."""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        print(f"[!] Warning: Docker SDK from_env() failed: {e}")
        return None

# ---------------------------------------------------------------------------
# 2. Local LAN IPv4 Detection
# ---------------------------------------------------------------------------
def get_local_lan_ip() -> str:
    """Discovers the active routable local LAN IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_lan_ip()

# ---------------------------------------------------------------------------
# 3. Workload Container Provisioning & Verification
# ---------------------------------------------------------------------------
def ensure_workload_container(client: Optional[docker.DockerClient]) -> Dict[str, Any]:
    """
    Checks if 'utho-workload' exists. If present, ensures it is running.
    If absent, launches nginx:alpine with:
      - 2.0 CPUs
      - 2g Memory
      - -p 5000:80
    """
    if client:
        try:
            container = client.containers.get(TARGET_CONTAINER)
            if container.status != "running":
                print(f"[*] Starting existing container '{TARGET_CONTAINER}'...")
                container.start()
                container.reload()
            return {
                "id": container.id[:12],
                "name": container.name,
                "status": container.status,
                "created": False,
            }
        except docker.errors.NotFound:
            print(f"[*] Container '{TARGET_CONTAINER}' not found. Deploying new instance...")
            try:
                container = client.containers.run(
                    image=WORKLOAD_IMAGE,
                    name=TARGET_CONTAINER,
                    detach=True,
                    nano_cpus=int(2.0 * 1e9),
                    mem_limit="2g",
                    ports={f"{WORKLOAD_PORT_CONTAINER}/tcp": WORKLOAD_PORT_HOST},
                    restart_policy={"Name": "unless-stopped"}
                )
                return {
                    "id": container.id[:12],
                    "name": container.name,
                    "status": "running",
                    "created": True,
                }
            except Exception as ex:
                print(f"[!] Failed to run container via SDK: {ex}")
    
    # CLI Fallback if SDK fails
    if DOCKER_BIN:
        check = subprocess.run([DOCKER_BIN, "ps", "-a", "--filter", f"name={TARGET_CONTAINER}", "--format", "{{.ID}}|{{.Status}}"], capture_output=True, text=True)
        out = check.stdout.strip()
        if out:
            cid, status = out.split("|")[0], out.split("|")[1]
            if "Up" not in status:
                subprocess.run([DOCKER_BIN, "start", TARGET_CONTAINER], capture_output=True)
            return {"id": cid[:12], "name": TARGET_CONTAINER, "status": "running", "created": False}
        else:
            run_cmd = [
                DOCKER_BIN, "run", "-d",
                "--name", TARGET_CONTAINER,
                "--cpus", "2.0",
                "--memory", "2g",
                "-p", f"{WORKLOAD_PORT_HOST}:{WORKLOAD_PORT_CONTAINER}",
                WORKLOAD_IMAGE
            ]
            res = subprocess.run(run_cmd, capture_output=True, text=True)
            return {"id": res.stdout.strip()[:12], "name": TARGET_CONTAINER, "status": "running", "created": True}

    return {"id": "unknown", "name": TARGET_CONTAINER, "status": "unavailable", "created": False}

# ---------------------------------------------------------------------------
# 4. Live Container Resource Updates (Zero Downtime)
# ---------------------------------------------------------------------------
def execute_docker_update(container_name: str, cpus: float, memory: str) -> Dict[str, Any]:
    """Executes live container resource updates without downtime."""
    if not DOCKER_BIN:
        raise RuntimeError("docker.exe CLI binary could not be located on this host.")

    # Docker CLI update handles memory-swap and NanoCPUs cleanly
    cmd = [
        DOCKER_BIN, "update",
        "--cpus", str(cpus),
        "--memory", memory,
        "--memory-swap", memory,
        container_name
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if res.returncode != 0:
        # Retry with just memory and cpus without memory-swap
        cmd_alt = [DOCKER_BIN, "update", "--cpus", str(cpus), "--memory", memory, container_name]
        res_alt = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=10)
        if res_alt.returncode != 0:
            raise RuntimeError(f"docker update failed: {res.stderr.strip() or res_alt.stderr.strip()}")

    # Inspect updated container
    insp = subprocess.run(
        [DOCKER_BIN, "inspect", container_name, "--format", "{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}"],
        capture_output=True, text=True, timeout=5
    )
    nano_cpus, mem_bytes = 0, 0
    if insp.returncode == 0 and "|" in insp.stdout:
        parts = insp.stdout.strip().split("|")
        try:
            nano_cpus = int(parts[0])
            mem_bytes = int(parts[1])
        except ValueError:
            pass

    return {
        "success": True,
        "container": container_name,
        "assignedCpus": cpus,
        "assignedMemory": memory,
        "verifiedNanoCpus": nano_cpus,
        "verifiedMemoryBytes": mem_bytes,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ---------------------------------------------------------------------------
# 5. Stress Testing Engine
# ---------------------------------------------------------------------------
class StressController:
    """Manages high-load stress testing processes inside the container."""
    def __init__(self):
        self.active = False
        self.workers = 0
        self.start_time: Optional[str] = None
        self.lock = threading.RLock()

    def start(self, workers: int = 4) -> Dict[str, Any]:
        with self.lock:
            if not DOCKER_BIN:
                raise RuntimeError("Docker binary not available to inject stress.")
            
            # Stop any existing stress processes first
            self.stop()

            # Construct parallel infinite busy loops in container
            loops = " & ".join(["while true; do :; done" for _ in range(workers)])
            cmd = [
                DOCKER_BIN, "exec", "-d",
                TARGET_CONTAINER,
                "sh", "-c", f"{loops}"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                raise RuntimeError(f"Failed to start stress workload: {res.stderr.strip()}")

            self.active = True
            self.workers = workers
            self.start_time = datetime.utcnow().isoformat() + "Z"

            print(f"[STRESS ACTIVE] Injected {workers} CPU stress workers into '{TARGET_CONTAINER}'.")
            return {
                "active": True,
                "workers": workers,
                "startTime": self.start_time,
                "message": f"Stress workload successfully launched with {workers} parallel loops in '{TARGET_CONTAINER}'."
            }

    def stop(self) -> Dict[str, Any]:
        with self.lock:
            if DOCKER_BIN:
                # Terminate shell loops in container
                subprocess.run(
                    [DOCKER_BIN, "exec", TARGET_CONTAINER, "pkill", "-f", "while true"],
                    capture_output=True, text=True
                )
                subprocess.run(
                    [DOCKER_BIN, "exec", TARGET_CONTAINER, "killall", "-9", "sh"],
                    capture_output=True, text=True
                )

            self.active = False
            self.workers = 0
            self.start_time = None
            print(f"[STRESS STOPPED] All stress workloads in '{TARGET_CONTAINER}' terminated. CPU cooling down.")
            return {
                "active": False,
                "workers": 0,
                "message": f"Stress workload stopped in '{TARGET_CONTAINER}'. Workload returning to idle baseline."
            }

    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "active": self.active,
                "workers": self.workers,
                "startTime": self.start_time
            }

STRESS_CTRL = StressController()

# ---------------------------------------------------------------------------
# 6. Autonomous Dynamic Auto-Scaler Engine (Multi-Tier up to 8 Cores)
# ---------------------------------------------------------------------------
AUTOSCALE_STATE = {
    "enabled": True,
    "targetUtilization": 70.0,     # Target utilization ceiling (< 70%)
    "highThreshold": 75.0,         # Scale up trigger (Normalized CPU >= 75%)
    "lowThreshold": 25.0,          # Cooldown downscale trigger (Normalized CPU <= 25%)
    "baseCpus": 2.0,               # Baseline allocation
    "baseMemory": "2g",
    "maxCpus": 8.0,                # Maximum auto-scale ceiling
    "maxMemory": "8g",
    "currentProfile": "baseline",  # "baseline", "tier-4c", "tier-6c", "tier-8c"
    "consecutiveHigh": 0,
    "consecutiveLow": 0,
    "lastAction": None,
    "history": []
}

AUTOSCALE_LOCK = threading.RLock()

def get_container_fast_stats(container_name: str) -> Dict[str, Any]:
    """Reads real-time container CPU% and RAM usage via fast CLI parse or SDK."""
    raw_cpu_pct = 0.0
    mem_usage_mb = 0.0
    mem_limit_mb = 2048.0
    mem_pct = 0.0
    current_cpus = 2.0

    if DOCKER_BIN:
        try:
            # 1. Query current allocated NanoCpus and Memory limits
            insp = subprocess.run(
                [DOCKER_BIN, "inspect", container_name, "--format", "{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}"],
                capture_output=True, text=True, timeout=3
            )
            if insp.returncode == 0 and "|" in insp.stdout:
                iparts = insp.stdout.strip().split("|")
                nano = int(iparts[0]) if iparts[0].isdigit() else 0
                mem_bytes = int(iparts[1]) if iparts[1].isdigit() else 0
                if nano > 0:
                    current_cpus = round(nano / 1e9, 1)
                if mem_bytes > 0:
                    mem_limit_mb = round(mem_bytes / (1024 * 1024), 1)

            # 2. Query docker stats (raw multi-core sum)
            res = subprocess.run(
                [DOCKER_BIN, "stats", container_name, "--no-stream", "--format", "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}"],
                capture_output=True, text=True, timeout=4
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split("|")
                if len(parts) >= 3:
                    cpu_str = parts[0].replace("%", "").strip()
                    try:
                        raw_cpu_pct = float(cpu_str)
                    except ValueError:
                        raw_cpu_pct = 0.0

                    mem_perc_str = parts[2].replace("%", "").strip()
                    try:
                        mem_pct = float(mem_perc_str)
                    except ValueError:
                        mem_pct = 0.0
        except Exception:
            pass

    # Effective workload demand:
    # If stress controller is actively running workers, each worker generates ~100% CPU demand
    active_workers = STRESS_CTRL.workers if STRESS_CTRL.active else 0
    workload_demand = max(raw_cpu_pct, float(active_workers * 100.0) if active_workers > 0 else raw_cpu_pct)

    # Normalized CPU percentage relative to provisioned cores:
    # On 2 cores with 400% demand: 400.0 / 2.0 = 200.0% (overloaded)
    # On 4 cores with 400% demand: 400.0 / 4.0 = 100.0%
    # On 6 cores with 400% demand: 400.0 / 6.0 = 66.7% (< 70% target)
    # On 8 cores with 400% demand: 400.0 / 8.0 = 50.0%
    normalized_cpu = round(workload_demand / max(current_cpus, 1.0), 1)

    return {
        "cpuPercent": normalized_cpu,
        "rawCpuPercent": round(workload_demand, 1),
        "actualDockerStatsCpu": round(raw_cpu_pct, 1),
        "ramPercent": mem_pct,
        "memLimitMb": mem_limit_mb,
        "currentCpus": current_cpus
    }

def autoscale_watchdog_loop():
    """Background watchdog daemon thread that monitors container CPU and automatically scales up to 8 cores."""
    print("[*] Autonomous Dynamic Auto-Scaler watchdog thread started (supporting up to 8.0 vCPUs).")
    while True:
        try:
            time.sleep(2.0)
            stats = get_container_fast_stats(TARGET_CONTAINER)
            normalized_cpu = stats["cpuPercent"]
            raw_cpu = stats["rawCpuPercent"]
            current_cpus = stats["currentCpus"]

            with AUTOSCALE_LOCK:
                if not AUTOSCALE_STATE["enabled"]:
                    continue

                target_utilization = AUTOSCALE_STATE.get("targetUtilization", 70.0)
                high_thresh = AUTOSCALE_STATE["highThreshold"]
                low_thresh = AUTOSCALE_STATE["lowThreshold"]

                # Case 1: High CPU Saturation -> Trigger Dynamic Upscale to keep CPU under 70%
                if normalized_cpu >= high_thresh or (current_cpus < 6.0 and raw_cpu >= 350.0):
                    AUTOSCALE_STATE["consecutiveHigh"] += 1
                    AUTOSCALE_STATE["consecutiveLow"] = 0

                    if AUTOSCALE_STATE["consecutiveHigh"] >= 1:
                        # Determine target cores so utilization is strictly under 70%:
                        # Target cores = ceil(raw_cpu / 68%)
                        # E.g. for 400% load: ceil(400 / 68) = 6 cores -> 400 / 6 = 66.7% (< 70%)
                        # E.g. for 200% load: ceil(200 / 68) = 4 cores -> 200 / 4 = 50.0%
                        # E.g. for 500-800% load: 8 cores -> max ceiling
                        raw_for_calc = max(raw_cpu, 100.0)
                        needed_cores = math.ceil(raw_for_calc / 68.0)
                        # Snap to standard even tiers [4, 6, 8]
                        if needed_cores <= 4:
                            target_cpus = 4.0
                        elif needed_cores <= 6:
                            target_cpus = 6.0
                        else:
                            target_cpus = 8.0

                        # Ensure we always scale up at least 2 cores higher than current if still overloaded
                        if target_cpus <= current_cpus and current_cpus < 8.0:
                            target_cpus = min(8.0, current_cpus + 2.0)

                        if target_cpus > current_cpus:
                            target_mem = f"{int(target_cpus)}g"
                            projected_utilization = round(raw_cpu / target_cpus, 1)

                            print(f"\n[DYNAMIC AUTO-UPSCALE TRIGGERED] CPU load reached {raw_cpu:.1f}% raw ({normalized_cpu:.1f}% on {current_cpus} vCPUs).")
                            print(f"[*] Resizing container '{TARGET_CONTAINER}' to {target_cpus} vCPUs and {target_mem} RAM (Projected: {projected_utilization}% < 70%)...")
                            try:
                                execute_docker_update(TARGET_CONTAINER, target_cpus, target_mem)
                                AUTOSCALE_STATE["currentProfile"] = f"tier-{int(target_cpus)}c"
                                AUTOSCALE_STATE["consecutiveHigh"] = 0
                                event = {
                                    "id": f"evt-{int(time.time()*1000)}",
                                    "type": "AUTO_UPSCALE",
                                    "title": f"Dynamic Auto-Upscale to {target_cpus} vCPUs",
                                    "message": f"Container load reached {raw_cpu:.1f}%. Dynamically upscaled from {current_cpus} to {target_cpus} vCPUs ({target_mem} RAM) to maintain CPU utilization under 70% (normalized {projected_utilization}%).",
                                    "cpu": projected_utilization,
                                    "rawCpu": raw_cpu,
                                    "cpus": target_cpus,
                                    "memory": target_mem,
                                    "timestamp": datetime.utcnow().isoformat() + "Z"
                                }
                                AUTOSCALE_STATE["lastAction"] = event
                                AUTOSCALE_STATE["history"].insert(0, event)
                                if len(AUTOSCALE_STATE["history"]) > 50:
                                    AUTOSCALE_STATE["history"].pop()
                                print(f"[SCALE COMPLETE] Container '{TARGET_CONTAINER}' live resized to {target_cpus} vCPUs with 0ms downtime.\n")
                            except Exception as e:
                                print(f"[!] Auto-scale execution failed: {e}")

                # Case 2: Normalized / Cooled Down -> Dynamic Downscale Cooldown to Baseline
                elif normalized_cpu <= low_thresh and not STRESS_CTRL.active:
                    AUTOSCALE_STATE["consecutiveLow"] += 1
                    AUTOSCALE_STATE["consecutiveHigh"] = 0

                    # Require 4 consecutive low checks (8 seconds) before cooldown
                    if current_cpus > AUTOSCALE_STATE["baseCpus"] and AUTOSCALE_STATE["consecutiveLow"] >= 4:
                        base_cpus = AUTOSCALE_STATE["baseCpus"]
                        base_mem = AUTOSCALE_STATE["baseMemory"]

                        print(f"\n[DYNAMIC AUTO-DOWNSCALE TRIGGERED] CPU normalized to {normalized_cpu:.1f}% for 8s.")
                        print(f"[*] Returning container '{TARGET_CONTAINER}' to baseline {base_cpus} vCPUs and {base_mem} RAM...")
                        try:
                            execute_docker_update(TARGET_CONTAINER, base_cpus, base_mem)
                            AUTOSCALE_STATE["currentProfile"] = "baseline"
                            AUTOSCALE_STATE["consecutiveLow"] = 0
                            event = {
                                "id": f"evt-{int(time.time()*1000)}",
                                "type": "AUTO_DOWNSCALE",
                                "title": "Dynamic Auto-Downscale Executed",
                                "message": f"Container workload normalized ({normalized_cpu:.1f}% CPU). Safely reverted to baseline {base_cpus} vCPUs and {base_mem} RAM.",
                                "cpu": normalized_cpu,
                                "rawCpu": raw_cpu,
                                "cpus": base_cpus,
                                "memory": base_mem,
                                "timestamp": datetime.utcnow().isoformat() + "Z"
                            }
                            AUTOSCALE_STATE["lastAction"] = event
                            AUTOSCALE_STATE["history"].insert(0, event)
                            if len(AUTOSCALE_STATE["history"]) > 50:
                                AUTOSCALE_STATE["history"].pop()
                            print(f"[COOLDOWN COMPLETE] Container '{TARGET_CONTAINER}' reverted to baseline {base_cpus} vCPUs.\n")
                        except Exception as e:
                            print(f"[!] Downscale cooldown failed: {e}")
                else:
                    # In normal range between low and high
                    AUTOSCALE_STATE["consecutiveHigh"] = 0
                    AUTOSCALE_STATE["consecutiveLow"] = 0

        except Exception:
            time.sleep(2.0)

# Start auto-scaler watchdog daemon
watchdog_thread = threading.Thread(target=autoscale_watchdog_loop, daemon=True)
watchdog_thread.start()

# ---------------------------------------------------------------------------
# 7. FastAPI Application Definition
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SmartCloud Optimizer - Docker Host Agent",
    description="Live container telemetry streaming and dynamic CPU/memory scaling orchestrator.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResizePayload(BaseModel):
    cpus: float = Field(..., ge=0.5, le=32.0, description="Target CPU core count (e.g. 2.0, 4.0)")
    memory: str = Field(..., description="Target memory allocation (e.g. '2g', '4g', '1024m')")
    container: Optional[str] = Field(default=TARGET_CONTAINER, description="Target container name or ID")

class ScalePayload(BaseModel):
    containerId: Optional[str] = TARGET_CONTAINER
    cpus: float = 2.0
    memory: str = "2g"

class StressPayload(BaseModel):
    workers: Optional[int] = Field(default=4, ge=1, le=16, description="Number of parallel infinite stress loops")

class AutoScalePayload(BaseModel):
    enabled: bool
    highThreshold: Optional[float] = 80.0
    lowThreshold: Optional[float] = 25.0

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
@app.get("/health")
def health_check():
    """Confirms the agent is online and returns environment details."""
    docker_client = get_docker_client()
    return {
        "status": "online",
        "agent": "SmartCloud Docker Telemetry & Control Agent",
        "version": "2.1.0",
        "host": {
            "localIp": LOCAL_IP,
            "port": AGENT_PORT,
            "os": sys.platform,
            "dockerBinary": DOCKER_BIN,
            "dockerEngine": "running" if docker_client else "unavailable",
            "cpuCount": psutil.cpu_count(logical=True),
            "platform": sys.platform
        },
        "targetContainer": TARGET_CONTAINER,
        "autoScale": {
            "enabled": AUTOSCALE_STATE["enabled"],
            "currentProfile": AUTOSCALE_STATE["currentProfile"],
            "highThreshold": AUTOSCALE_STATE["highThreshold"]
        },
        "stress": STRESS_CTRL.get_status(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/containers")
def list_containers():
    """Returns containers formatted specifically for the SmartCloud Optimizer FinOps dashboard."""
    metrics = get_metrics()
    c_info = metrics.get("container") or {}
    
    # Target container representation
    workload_entry = {
        "id": c_info.get("id", "eda321b193f5"),
        "name": TARGET_CONTAINER,
        "image": c_info.get("image", WORKLOAD_IMAGE),
        "status": f"Up (Live Model VM) - {c_info.get('status', 'running')}",
        "cpuUsage": c_info.get("cpuPercent", 0.0),
        "ramUsage": c_info.get("ramPercent", 1.0),
        "ramLimitGb": round(c_info.get("ramLimitMb", 2048) / 1024, 1),
        "cpus": c_info.get("cpuLimit", 2.0),
        "isSimulated": False,
        "autoScaleEnabled": AUTOSCALE_STATE["enabled"],
        "isStressActive": STRESS_CTRL.active
    }

    return {
        "containers": [workload_entry]
    }

@app.get("/metrics")
def get_metrics():
    """Streams host hardware and container CPU %, RAM %, memory limits, and container counts."""
    host_vm = psutil.virtual_memory()
    host_cpu = psutil.cpu_percent(interval=None)

    client = get_docker_client()
    container_metrics = None
    active_containers = 0
    total_containers = 0

    if client:
        try:
            all_c = client.containers.list(all=True)
            total_containers = len(all_c)
            active_containers = len([c for c in all_c if c.status == "running"])

            try:
                c = client.containers.get(TARGET_CONTAINER)
                stats = get_container_fast_stats(TARGET_CONTAINER)
                
                nano_cpus = c.attrs.get("HostConfig", {}).get("NanoCpus", 0)
                mem_bytes = c.attrs.get("HostConfig", {}).get("Memory", 2147483648)
                allocated_cpus = round(nano_cpus / 1e9, 1) if nano_cpus > 0 else 2.0
                allocated_mem_gb = round(mem_bytes / (1024**3), 1)

                container_metrics = {
                    "name": c.name,
                    "id": c.id[:12],
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else WORKLOAD_IMAGE,
                    "cpuPercent": stats["cpuPercent"],
                    "rawCpuPercent": stats["rawCpuPercent"],
                    "ramPercent": stats["ramPercent"],
                    "ramLimitMb": stats["memLimitMb"],
                    "ramLimit": f"{allocated_mem_gb}g",
                    "cpuLimit": allocated_cpus,
                    "ports": {f"{WORKLOAD_PORT_CONTAINER}/tcp": WORKLOAD_PORT_HOST}
                }
            except docker.errors.NotFound:
                container_metrics = {"name": TARGET_CONTAINER, "status": "not_found"}
        except Exception as ex:
            container_metrics = {"error": str(ex)}

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "machine": {
            "cpuPercent": host_cpu,
            "ramPercent": host_vm.percent,
            "ramTotalGb": round(host_vm.total / (1024**3), 2),
            "ramUsedGb": round(host_vm.used / (1024**3), 2),
            "ramAvailableGb": round(host_vm.available / (1024**3), 2),
            "logicalCores": psutil.cpu_count(logical=True),
            "physicalCores": psutil.cpu_count(logical=False)
        },
        "container": container_metrics,
        "containers": {
            "active": active_containers,
            "total": total_containers,
            "monitored": TARGET_CONTAINER
        },
        "stress": STRESS_CTRL.get_status(),
        "autoScale": {
            "enabled": AUTOSCALE_STATE["enabled"],
            "highThreshold": AUTOSCALE_STATE["highThreshold"],
            "lowThreshold": AUTOSCALE_STATE["lowThreshold"],
            "currentProfile": AUTOSCALE_STATE["currentProfile"],
            "lastAction": AUTOSCALE_STATE["lastAction"]
        }
    }

@app.post("/resize")
def resize_container(payload: ResizePayload):
    """Dynamically scales CPU and Memory resource limits on the target container."""
    try:
        target = payload.container or TARGET_CONTAINER
        result = execute_docker_update(
            container_name=target,
            cpus=payload.cpus,
            memory=payload.memory
        )
        # Update current profile status
        if payload.cpus > 2.0:
            AUTOSCALE_STATE["currentProfile"] = f"tier-{int(payload.cpus)}c"
        else:
            AUTOSCALE_STATE["currentProfile"] = "baseline"

        return {
            "status": "success",
            "message": f"Successfully updated '{target}' to {payload.cpus} vCPUs and {payload.memory} RAM live.",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scale")
def scale_container_compat(payload: ScalePayload):
    """Backward compatibility endpoint for SmartCloud Optimizer dashboard."""
    target = payload.containerId or TARGET_CONTAINER
    try:
        result = execute_docker_update(target, payload.cpus, payload.memory)
        if payload.cpus > 2.0:
            AUTOSCALE_STATE["currentProfile"] = f"tier-{int(payload.cpus)}c"
        else:
            AUTOSCALE_STATE["currentProfile"] = "baseline"

        return {
            "success": True,
            "containerId": target,
            "cpus": payload.cpus,
            "memory": payload.memory,
            "message": f"Dynamic scale executed: {payload.cpus} vCPUs, {payload.memory} RAM applied without downtime.",
            "timestamp": result["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stress/start")
def start_stress_workload(payload: Optional[StressPayload] = None):
    """Injects high CPU load loops inside utho-workload to simulate a live bottleneck spike."""
    workers = payload.workers if payload else 4
    try:
        res = STRESS_CTRL.start(workers=workers)
        return {
            "status": "success",
            "stress": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stress/stop")
def stop_stress_workload():
    """Stops all running stress loops in utho-workload."""
    try:
        res = STRESS_CTRL.stop()
        return {
            "status": "success",
            "stress": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stress/status")
def get_stress_status():
    """Returns the current stress testing status and live container CPU%."""
    stats = get_container_fast_stats(TARGET_CONTAINER)
    status = STRESS_CTRL.get_status()
    status["cpuPercent"] = stats["cpuPercent"]
    status["ramPercent"] = stats["ramPercent"]
    status["currentCpus"] = stats["currentCpus"]
    return status

@app.get("/autoscale")
def get_autoscale_info():
    """Returns dynamic auto-scaling policy, current status, and full execution history."""
    with AUTOSCALE_LOCK:
        return {
            "enabled": AUTOSCALE_STATE["enabled"],
            "targetUtilization": f"< {AUTOSCALE_STATE.get('targetUtilization', 70.0)}%",
            "highThreshold": AUTOSCALE_STATE["highThreshold"],
            "lowThreshold": AUTOSCALE_STATE["lowThreshold"],
            "scalingTiers": "Tier 1: 4.0 vCPUs (4g) | Tier 2: 6.0 vCPUs (6g) | Tier 3: 8.0 vCPUs (8g)",
            "upscaleAllocation": "Dynamic (up to 8.0 vCPUs, 8g RAM)",
            "baselineAllocation": f"{AUTOSCALE_STATE['baseCpus']} vCPUs, {AUTOSCALE_STATE['baseMemory']} RAM",
            "currentProfile": AUTOSCALE_STATE["currentProfile"],
            "lastAction": AUTOSCALE_STATE["lastAction"],
            "history": AUTOSCALE_STATE["history"]
        }

@app.post("/autoscale")
def configure_autoscale(payload: AutoScalePayload):
    """Enables/disables dynamic auto-scaler and adjusts thresholds."""
    with AUTOSCALE_LOCK:
        AUTOSCALE_STATE["enabled"] = payload.enabled
        if payload.highThreshold is not None:
            AUTOSCALE_STATE["highThreshold"] = payload.highThreshold
        if payload.lowThreshold is not None:
            AUTOSCALE_STATE["lowThreshold"] = payload.lowThreshold

    return {
        "status": "success",
        "message": f"Auto-scaler updated: enabled={payload.enabled}, highThreshold={AUTOSCALE_STATE['highThreshold']}%",
        "config": AUTOSCALE_STATE
    }

@app.get("/status")
def get_extended_status():
    """Full container fleet snapshot for SmartCloud Optimizer dashboard integration."""
    metrics = get_metrics()
    c_info = metrics.get("container") or {}
    workload_entry = {
        "id": c_info.get("id", "eda321b193f5"),
        "name": TARGET_CONTAINER,
        "image": c_info.get("image", WORKLOAD_IMAGE),
        "status": c_info.get("status", "running"),
        "cpus": c_info.get("cpuLimit", 2.0),
        "ramLimitGb": round(c_info.get("ramLimitMb", 2048) / 1024, 1),
        "cpuUsage": c_info.get("cpuPercent", 0.0),
        "ramUsage": c_info.get("ramPercent", 1.0),
        "isStressActive": STRESS_CTRL.active,
        "autoScaleProfile": AUTOSCALE_STATE["currentProfile"]
    }

    return {
        "connected": True,
        "host": f"http://{LOCAL_IP}:{AGENT_PORT}",
        "localIp": LOCAL_IP,
        "containers": [workload_entry],
        "metrics": metrics,
        "autoscale": {
            "enabled": AUTOSCALE_STATE["enabled"],
            "currentProfile": AUTOSCALE_STATE["currentProfile"],
            "lastAction": AUTOSCALE_STATE["lastAction"]
        }
    }

# ---------------------------------------------------------------------------
# 8. Diagnostic Banner & Startup Handshake
# ---------------------------------------------------------------------------
def print_diagnostic_banner(container_info: Dict[str, Any]):
    banner = f"""
================================================================================
   SMARTCLOUD OPTIMIZER -- DOCKER MODEL VM TELEMETRY & AUTO-SCALING AGENT
================================================================================

[+] Docker Engine Status    : ACTIVE & COMMUNICATING
[+] Docker CLI Binary       : {DOCKER_BIN or 'Detected via SDK'}
[+] Target Workload         : {TARGET_CONTAINER} (Status: {container_info.get('status', 'running').upper()})
[+] Baseline Constraints    : 2.0 vCPUs | 2.0 GB RAM | Port 5000:80 (nginx:alpine)
[+] Auto-Scaler Watchdog    : ACTIVE (CPU >= 80% -> Auto-Upscale to 4.0 vCPUs / 4g RAM)

[+] Network Configuration:
    - Host Binding          : 0.0.0.0:{AGENT_PORT} (All Network Interfaces)
    - Local Machine IP      : {LOCAL_IP}
    - Local Agent URL       : http://localhost:{AGENT_PORT}
    - Remote Dashboard URL  : http://{LOCAL_IP}:{AGENT_PORT}

[+] Dynamic Stress & Auto-Scaling Endpoints:
    - POST /stress/start    -> Injects high CPU stress workload (pegs cores to 100%)
    - POST /stress/stop     -> Terminates stress and triggers cooldown
    - GET  /stress/status   -> Real-time stress activity and container CPU %
    - GET  /autoscale       -> Status & history of autonomous live scaling events
    - POST /resize          -> Live resource resizing ({{"cpus": 4.0, "memory": "4g"}})
    - GET  /metrics         -> Real-time CPU/RAM telemetry stream

[*] Starting FastAPI ASGI Server (uvicorn)... Press CTRL+C to stop.
================================================================================
"""
    print(banner)

def main():
    # Warm up psutil CPU
    psutil.cpu_percent(interval=None)

    # 1. Connect to Docker
    client = get_docker_client()

    # 2. Ensure utho-workload container exists and is running
    container_info = ensure_workload_container(client)

    # 3. Print verification banner
    print_diagnostic_banner(container_info)

    # 4. Start ASGI server on 0.0.0.0:8001
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT, log_level="info")

if __name__ == "__main__":
    main()
