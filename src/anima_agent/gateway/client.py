"""
ANIMA AGENT — Gateway Client
Register node public key, query network nodes.

Gateway is a simple REST API that stores:
  - Public DID → public_key mapping
  - Node registration timestamp
  - Node status (active / inactive)

No private data is ever uploaded.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional

import httpx

from ..identity.did import load_identity


DEFAULT_GATEWAY_URL = "https://gateway.anima-os.org"
LOCAL_REGISTRY_PATH = Path.home() / ".anima" / "node_registry.json"


def register_node(
    gateway_url: str = DEFAULT_GATEWAY_URL,
    node_type: str = "standalone",
    package_ref: str = "",
) -> dict:
    """
    Register this node with the ANIMA Identity Gateway.
    Only uploads: DID + public_key + timestamp.
    """
    identity = load_identity()
    if not identity:
        raise ValueError("No DID found. Run 'anima identity generate' first.")

    payload = {
        "did": identity["did"],
        "public_key_hex": identity["public_key_hex"],
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "node_type": node_type,
        "package_ref": package_ref,
        "label": identity.get("label", ""),
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{gateway_url}/api/v1/register",
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
    except httpx.ConnectError:
        # Gateway not reachable — save locally and retry later
        result = {
            "status": "offline",
            "message": f"Gateway {gateway_url} not reachable. Registration saved locally.",
            "local_registry": str(LOCAL_REGISTRY_PATH),
        }
        _save_local_registry(payload)
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e),
        }

    return result


def list_nodes(
    gateway_url: str = DEFAULT_GATEWAY_URL,
    limit: int = 50,
) -> list[dict]:
    """Query gateway for registered nodes."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{gateway_url}/api/v1/nodes",
                params={"limit": limit},
            )
            resp.raise_for_status()
            return resp.json().get("nodes", [])
    except Exception as e:
        # Fallback to local registry
        return _load_local_registry()


def _save_local_registry(entry: dict):
    """Save registration to local file when gateway offline."""
    LOCAL_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if LOCAL_REGISTRY_PATH.exists():
        registry = json.loads(LOCAL_REGISTRY_PATH.read_text())
    else:
        registry = {"nodes": []}

    # Upsert
    existing = [n for n in registry["nodes"] if n["did"] == entry["did"]]
    if existing:
        registry["nodes"].remove(existing[0])
    registry["nodes"].append(entry)

    LOCAL_REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def _load_local_registry() -> list[dict]:
    """Load local registry file."""
    if not LOCAL_REGISTRY_PATH.exists():
        return []
    data = json.loads(LOCAL_REGISTRY_PATH.read_text())
    return data.get("nodes", [])


def check_gateway_status(gateway_url: str = DEFAULT_GATEWAY_URL) -> dict:
    """Check if the gateway is alive."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{gateway_url}/api/v1/health")
            return {
                "online": resp.status_code == 200,
                "url": gateway_url,
                "status_code": resp.status_code,
            }
    except Exception:
        return {
            "online": False,
            "url": gateway_url,
            "status_code": 0,
        }
