"""
STELLAR DID — 灵魂锚定的身份系统

设计原则（2026-07-13）：
- Primary DID 由 persona 内容决定（soul_anchor），不绑定硬件
- 同一人格包安装到任何终端，primary DID 相同
- 终端注册为 instance，可撤销
- 所有参数可配置，不做硬编码假设

身份模型：
    primary_did = did:stellar:{soul_anchor[:32]}
       ├── /instance/nyx-windows  ← 当前终端
       ├── /instance/nyx-mac
       └── /instance/nyx-n200

配置版本：stellar_did_v1（后续可升级到 v2）
"""

import json, os, hashlib
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, List

try:
    import nacl.signing
    import nacl.encoding
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

# ═══════════════════════════════════════════════════
# Configuration — 所有可配置项集中在此
# ═══════════════════════════════════════════════════

@dataclass
class StellarDIDConfig:
    """DID 系统配置。可通过环境变量覆盖。"""

    # ── Soul Anchor：哪些文件决定灵魂身份 ──
    persona_files: List[str] = field(default_factory=lambda: [
        "SOUL.distilled.md",    # 核心人格
        "SOUL.md",              # 备选核心人格
        "IDENTITY.md",          # 身份描述
        "voice_profile.md",     # 语气特征
    ])

    # ── DID 方案 ──
    did_method: str = "stellar"         # did:stellar:... | 可改为 "anima"
    did_scheme_version: str = "v1"      # 后续升级到 v2

    # ── 密钥存储 ──
    keys_dir: str = "Z:/qclaw/keys"     # NAS 共享密钥目录
    local_keys_dir: str = ""            # 本地回退（为空则用 ~/.anima/keys）

    # ── Registry 存储 ──
    registry_path: str = "Z:/qclaw/did/registry.json"

    # ── 实例信息 ──
    instance_id: str = ""               # 空则自动取 hostname
    instance_label: str = ""            # 人类可读标签
    instance_platform: str = ""         # 空则自动检测

    # ── 是否允许无 NAS 运行 ──
    allow_offline: bool = True          # True=无NAS时降级到本地存储

    # ── Soul Anchor 哈希算法 ──
    hash_algorithm: str = "sha256"      # sha256 | blake3 | sha512

    @classmethod
    def from_env(cls) -> "StellarDIDConfig":
        """从环境变量加载配置"""
        cfg = cls()
        if os.environ.get("STELLAR_DID_METHOD"):
            cfg.did_method = os.environ["STELLAR_DID_METHOD"]
        if os.environ.get("STELLAR_KEYS_DIR"):
            cfg.keys_dir = os.environ["STELLAR_KEYS_DIR"]
        if os.environ.get("STELLAR_INSTANCE_ID"):
            cfg.instance_id = os.environ["STELLAR_INSTANCE_ID"]
        if os.environ.get("STELLAR_ALLOW_OFFLINE"):
            cfg.allow_offline = os.environ["STELLAR_ALLOW_OFFLINE"].lower() in ("1", "true", "yes")
        return cfg


# ═══════════════════════════════════════════════════
# Soul Anchor — 从人格文件计算灵魂指纹
# ═══════════════════════════════════════════════════

def compute_soul_anchor(persona_dir: Path, config: StellarDIDConfig = None) -> Optional[str]:
    """
    计算灵魂锚点哈希。

    算法（2026-07-13 v1）：
      遍历配置中 persona_files 列表，
      对每个存在的文件计算 SHA256，
      将所有哈希拼接后，再对拼接结果取 SHA256 前 32 字符。

    同一个 STELLAR NYX 包 → 同一个 soul_anchor
    人格文件修改 → soul_anchor 改变 → 新版本标识
    """
    cfg = config or StellarDIDConfig()
    hasher = hashlib.new(cfg.hash_algorithm)

    found_any = False
    for filename in cfg.persona_files:
        filepath = persona_dir / filename
        if filepath.exists():
            content = filepath.read_bytes()
            hasher.update(content)
            hasher.update(b"\x00")  # 分隔符
            found_any = True

    if not found_any:
        return None

    full_hash = hasher.hexdigest()
    return full_hash[:32]


# ═══════════════════════════════════════════════════
# DID 构建
# ═══════════════════════════════════════════════════

def build_primary_did(soul_anchor: str, config: StellarDIDConfig = None) -> str:
    """从 soul_anchor 构建 primary DID"""
    cfg = config or StellarDIDConfig()
    return f"did:{cfg.did_method}:{soul_anchor}"


def build_instance_did(primary_did: str, instance_id: str) -> str:
    """构建 instance DID"""
    return f"{primary_did}/instance/{instance_id}"


# ═══════════════════════════════════════════════════
# 密钥管理
# ═══════════════════════════════════════════════════

def _resolve_keys_dir(config: StellarDIDConfig) -> Path:
    """解析密钥存储目录，NAS 优先，本地回退"""
    if config.keys_dir and Path(config.keys_dir).exists():
        return Path(config.keys_dir)

    nas_path = Path(config.keys_dir)
    if nas_path.parent.exists():  # 父目录存在即可尝试创建
        nas_path.mkdir(parents=True, exist_ok=True)
        if nas_path.exists():
            return nas_path

    # 回退到本地
    local = Path(config.local_keys_dir) if config.local_keys_dir else Path.home() / ".anima" / "keys"
    local.mkdir(parents=True, exist_ok=True)
    return local


def _key_filename(primary_did: str) -> str:
    """密钥文件名 = primary_did 的最后一段 + _private.hex"""
    tag = primary_did.split(":")[-1] if ":" in primary_did else primary_did
    return f"{tag}_private.hex"


def generate_keypair() -> tuple:
    """生成 Ed25519 密钥对。返回 (private_key_hex, public_key_hex)"""
    if not HAS_NACL:
        raise RuntimeError("PyNaCl not installed. Run: pip install pynacl")

    sk = nacl.signing.SigningKey.generate()
    vk = sk.verify_key
    return (
        sk.encode(encoder=nacl.encoding.HexEncoder).decode("ascii"),
        vk.encode(encoder=nacl.encoding.HexEncoder).decode("ascii"),
    )


def save_keypair(primary_did: str, private_hex: str, public_hex: str, config: StellarDIDConfig = None):
    """保存密钥对到存储目录"""
    cfg = config or StellarDIDConfig()
    keys_dir = _resolve_keys_dir(cfg)

    priv_file = keys_dir / _key_filename(primary_did)
    pub_file = keys_dir / _key_filename(primary_did).replace("_private", "_public")

    priv_file.write_text(private_hex, encoding="ascii")
    pub_file.write_text(public_hex, encoding="ascii")
    # 设置权限（Windows 上忽略）
    try:
        os.chmod(priv_file, 0o600)
    except Exception:
        pass

    return str(priv_file)


def load_keypair(primary_did: str, config: StellarDIDConfig = None) -> Optional[tuple]:
    """加载密钥对。返回 (private_hex, public_hex) 或 None"""
    cfg = config or StellarDIDConfig()
    keys_dir = _resolve_keys_dir(cfg)

    priv_file = keys_dir / _key_filename(primary_did)
    pub_file = keys_dir / _key_filename(primary_did).replace("_private", "_public")

    if not priv_file.exists() or not pub_file.exists():
        return None

    return (priv_file.read_text().strip(), pub_file.read_text().strip())


# ═══════════════════════════════════════════════════
# Registry — 实例注册表
# ═══════════════════════════════════════════════════

def _load_registry(config: StellarDIDConfig) -> dict:
    """加载注册表"""
    path = Path(config.registry_path)
    if not path.exists():
        return {
            "schema": "stellar-did-registry-v1",
            "did_method": config.did_method,
            "instances": {},
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema": "stellar-did-registry-v1", "instances": {}}


def _save_registry(registry: dict, config: StellarDIDConfig):
    """保存注册表"""
    path = Path(config.registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════

@dataclass
class StellarIdentity:
    """完整的 Stellar 身份信息"""
    soul_anchor: str
    primary_did: str
    public_key_hex: str
    instance_id: str
    instance_did: str
    is_new: bool                # 是否刚创建
    persona_dir: str            # 人格目录
    keys_path: str              # 密钥文件路径
    config_version: str = "stellar_did_v1"

    def to_dict(self) -> dict:
        return asdict(self)


def identify(persona_dir: str = None, config: StellarDIDConfig = None) -> StellarIdentity:
    """
    主入口：根据人格文件确定身份。

    流程：
    1. 从 persona 文件计算 soul_anchor
    2. soul_anchor → primary_did
    3. 查找或生成密钥对
    4. 注册当前终端 instance

    Args:
        persona_dir: 人格文件目录（默认从 STELLAR_DIR 环境变量取）
        config: DID 配置

    Returns:
        StellarIdentity 完整身份信息
    """
    cfg = config or StellarDIDConfig.from_env()

    # ── Step 1: 定位 persona ──
    if persona_dir:
        pdir = Path(persona_dir)
    elif os.environ.get("STELLAR_DIR"):
        pdir = Path(os.environ["STELLAR_DIR"])
    elif os.environ.get("STELLAR_PERSONA_DIR"):
        pdir = Path(os.environ["STELLAR_PERSONA_DIR"])
    else:
        # 默认：ANIMA AGENT 的标准位置
        pdir = Path.home() / ".anima" / "stellar" / "persona"

    if not pdir.exists():
        raise FileNotFoundError(f"Persona directory not found: {pdir}")

    # ── Step 2: soul_anchor → primary_did ──
    soul_anchor = compute_soul_anchor(pdir, cfg)
    if not soul_anchor:
        raise ValueError(f"No persona files found in {pdir}. Check config.persona_files.")

    primary_did = build_primary_did(soul_anchor, cfg)

    # ── Step 3: 密钥对 ──
    keypair = load_keypair(primary_did, cfg)
    is_new = False

    if keypair:
        private_hex, public_hex = keypair
    else:
        if not HAS_NACL:
            raise RuntimeError(
                "PyNaCl not installed. Cannot generate new keypair.\n"
                "Install with: pip install pynacl\n"
                "Or provide existing keypair."
            )
        private_hex, public_hex = generate_keypair()
        keys_path = save_keypair(primary_did, private_hex, public_hex, cfg)
        is_new = True

    keys_path = str(_resolve_keys_dir(cfg) / _key_filename(primary_did))

    # ── Step 4: 实例注册 ──
    instance_id = cfg.instance_id or os.environ.get("COMPUTERNAME", "unknown")
    instance_did = build_instance_did(primary_did, instance_id)

    # Platform detection
    if cfg.instance_platform:
        platform = cfg.instance_platform
    else:
        platform = f"{os.environ.get('OS', 'Unknown')} ({os.environ.get('COMPUTERNAME', 'unknown')})"

    # Write to registry
    registry = _load_registry(cfg)

    if "instances" not in registry:
        registry["instances"] = {}

    registry["instances"][instance_id] = {
        "instance_did": instance_did,
        "primary_did": primary_did,
        "platform": platform,
        "label": cfg.instance_label or instance_id,
        "public_key_hex": public_hex,
        "status": "active",
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat(),
    }
    _save_registry(registry, cfg)

    return StellarIdentity(
        soul_anchor=soul_anchor,
        primary_did=primary_did,
        public_key_hex=public_hex,
        instance_id=instance_id,
        instance_did=instance_did,
        is_new=is_new,
        persona_dir=str(pdir),
        keys_path=keys_path,
    )


def status(persona_dir: str = None, config: StellarDIDConfig = None) -> dict:
    """快速状态查询，不修改任何文件"""
    cfg = config or StellarDIDConfig.from_env()

    if persona_dir:
        pdir = Path(persona_dir)
    elif os.environ.get("STELLAR_PERSONA_DIR"):
        pdir = Path(os.environ["STELLAR_PERSONA_DIR"])
    else:
        pdir = Path.home() / ".anima" / "stellar" / "persona"

    if not pdir.exists():
        return {"status": "no_persona", "persona_dir": str(pdir)}

    soul_anchor = compute_soul_anchor(pdir, cfg)
    if not soul_anchor:
        return {"status": "no_soul", "persona_dir": str(pdir)}

    primary_did = build_primary_did(soul_anchor, cfg)
    keypair = load_keypair(primary_did, cfg)
    registry = _load_registry(cfg)

    instance_id = cfg.instance_id or os.environ.get("COMPUTERNAME", "unknown")

    return {
        "status": "ok",
        "soul_anchor": soul_anchor,
        "primary_did": primary_did,
        "has_keypair": keypair is not None,
        "instance_id": instance_id,
        "instance_did": build_instance_did(primary_did, instance_id),
        "is_registered": instance_id in registry.get("instances", {}),
        "registry_path": cfg.registry_path,
        "keys_dir": str(_resolve_keys_dir(cfg)),
        "config_version": "stellar_did_v1",
    }
