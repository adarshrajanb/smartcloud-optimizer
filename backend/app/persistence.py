import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("finops_persistence")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STORE_FILE = DATA_DIR / "fleet_store.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_store() -> Optional[Dict[str, Any]]:
    ensure_data_dir()
    if not STORE_FILE.exists():
        return None
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load fleet store from {STORE_FILE}: {e}")
        return None


def save_store(
    customers: Dict[str, Any],
    vm_state: Dict[str, Any],
    user_accounts: Dict[str, Any],
    audit_logs: List[Dict[str, Any]],
):
    ensure_data_dir()
    try:
        data = {
            "customers": customers,
            "vm_state": vm_state,
            "user_accounts": user_accounts,
            "audit_logs": audit_logs,
        }
        temp_file = STORE_FILE.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        if temp_file.exists():
            temp_file.replace(STORE_FILE)
    except Exception as e:
        logger.error(f"Failed to save fleet store to {STORE_FILE}: {e}")
