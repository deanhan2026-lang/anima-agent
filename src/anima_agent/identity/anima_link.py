"""
AnimaLink Registry — 跨方法 DID 注册管理

支持:
- did:stellar:... （STELLAR 原生，soul_anchor 锚定）
- did:key:...     （W3C 标准，外部导入）
- did:anima:...   （ANIMA AGENT 旧方案）

所有节点通过 registry.json 互相发现。
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional


# ═══════════════════════ Registry Path ═══════════════════════
DEFAULT_REGISTRY = "Z:/qclaw/did/registry.json"


def _load(path: str = DEFAULT_REGISTRY) -> dict:
    p = Path(path)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Auto-migrate from old stellar-did-registry format
            if "instances" in data and "nodes" not in data:
                nodes = {}
                for inst_id, inst in data["instances"].items():
                    nodes[inst_id] = {
                        "node_id": inst_id,
                        "primary_did": inst.get("primary_did", ""),
                        "did_method": "stellar",
                        "public_key_hex": inst.get("public_key_hex", ""),
                        "label": inst.get("label", inst_id),
                        "persona": "",
                        "platform": inst.get("platform", ""),
                        "instance_did": inst.get("instance_did", ""),
                        "also_known_as": [],
                        "relationships": {},
                        "status": inst.get("status", "active"),
                        "registered_at": inst.get("registered_at", ""),
                        "last_seen": inst.get("last_seen", ""),
                    }
                data["nodes"] = nodes
                data["schema"] = "anima-link-registry-v1"
                data.pop("instances", None)
                data.pop("did_method", None)
            return data
        except Exception:
            pass
    return {
        "schema": "anima-link-registry-v1",
        "nodes": {},
    }


def _save(reg: dict, path: str = DEFAULT_REGISTRY):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    reg["updated_at"] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════ Registry Operations ═══════════════════════

def register_node(
    node_id: str,
    primary_did: str,
    public_key_hex: str = "",
    label: str = "",
    persona: str = "",
    platform: str = "",
    did_method: str = "stellar",
    instance_did: str = "",
    relationships: dict = None,
    also_known_as: list = None,
    registry_path: str = DEFAULT_REGISTRY,
) -> dict:
    """
    注册一个节点到 AnimaLink 网络。

    支持 did:stellar / did:key / did:anima 三种 DID 方法。
    """
    reg = _load(registry_path)

    existing = reg["nodes"].get(node_id, {})

    reg["nodes"][node_id] = {
        "node_id": node_id,
        "primary_did": primary_did,
        "did_method": did_method,
        "public_key_hex": public_key_hex,
        "label": label or node_id,
        "persona": persona,
        "platform": platform,
        "instance_did": instance_did,
        "also_known_as": also_known_as or (existing.get("also_known_as", []) if existing else []),
        "relationships": relationships or {},
        "status": "active",
        "registered_at": existing.get("registered_at") or datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat(),
    }

    _save(reg, registry_path)
    return reg["nodes"][node_id]


def list_nodes(registry_path: str = DEFAULT_REGISTRY) -> List[dict]:
    """列出所有已注册节点"""
    reg = _load(registry_path)
    return list(reg.get("nodes", {}).values())


def get_node(node_id: str, registry_path: str = DEFAULT_REGISTRY) -> Optional[dict]:
    """查询单个节点"""
    reg = _load(registry_path)
    return reg.get("nodes", {}).get(node_id)


def update_last_seen(node_id: str, registry_path: str = DEFAULT_REGISTRY):
    """更新节点的 last_seen 时间"""
    reg = _load(registry_path)
    if node_id in reg.get("nodes", {}):
        reg["nodes"][node_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
        _save(reg, registry_path)


# ═══════════════════════ DID Key Decoding ═══════════════════════

def decode_did_key(did_key: str) -> Optional[dict]:
    """
    解码 did:key 格式，提取公钥信息。

    did:key 使用 multicodec + multibase 编码：
    - z = base58btc multibase prefix
    - 6Mk... = Ed25519 public key (multicodec 0xed01)
    - Dna... = X25519 (multicodec 0xec01)
    """
    ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    if not did_key.startswith("did:key:"):
        return None

    encoded = did_key[len("did:key:"):]

    # Remove multibase prefix (z = base58btc)
    if encoded.startswith("z"):
        encoded = encoded[1:]

    # Decode base58btc
    try:
        n = 0
        for c in encoded:
            n = n * 58 + ALPHABET.index(c)
        raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
        # Restore leading zeros
        pad = 0
        for c in encoded:
            if c == ALPHABET[0]:
                pad += 1
            else:
                break
        raw = b"\x00" * pad + raw
    except Exception as e:
        return {"method": "did:key", "raw": encoded, "error": f"Cannot decode: {e}"}

    if len(raw) < 3:
        return {"method": "did:key", "error": "Too short"}

    # Read multicodec: first 2 bytes (varint for 0xed or 0xec)
    codec = raw[0] << 8 | raw[1]
    key_data = raw[2:]

    codec_names = {
        0xed01: "Ed25519",
        0xec01: "X25519",
    }

    return {
        "method": "did:key",
        "codec_hex": f"0x{codec:04x}",
        "codec_name": codec_names.get(codec, f"unknown(0x{codec:04x})"),
        "public_key_hex": key_data.hex(),
        "public_key_bytes": len(key_data),
    }
