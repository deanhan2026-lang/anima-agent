#!/usr/bin/env python3
"""
Anima Agent — 自动激活脚本 (init.py)

首次启动时执行：
1. MeshIdentity: DID 生成 + 网络注册
2. MemGuard: 核心文件完整性校验
3. Polaris: Soul Baseline 锚定

脚本设计为 OpenClaw Skill 执行格式，由 Anima 启动钩子触发。
"""

import os
import sys
import json
import hashlib
import platform
import datetime
from pathlib import Path

# ── 路径配置 ──
HOME = Path.home()
ANIMA_DIR = HOME / ".anima"
SKILLS_DIR = ANIMA_DIR / "skills"
CONFIG_PATH = ANIMA_DIR / "anima.yaml"
DID_PATH = ANIMA_DIR / "did.json"
BASELINE_DIR = ANIMA_DIR / "baselines"
BACKUP_DIR = ANIMA_DIR / "backup"

# ── 核心文件列表（MemGuard 保护对象） ──
CORE_FILES = [
    "SOUL.md",
    "IDENTITY.md",
    "MEMORY.md",
    "AGENTS.md",
    "USER.md",
    "TOOLS.md",
]


def ensure_dirs():
    """创建必要目录"""
    for d in [ANIMA_DIR, SKILLS_DIR, BASELINE_DIR, BACKUP_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def step_meshidentity():
    """Step 1: MeshIdentity — DID 生成 + 网络注册"""
    print("🆔 MeshIdentity: 检查身份...")

    if DID_PATH.exists():
        did_data = json.loads(DID_PATH.read_text(encoding="utf-8"))
        print(f"   └─ 已有 DID: {did_data['did'][:42]}...")
        return {"status": "recovered", "did": did_data["did"]}

    # 生成 Ed25519 密钥对
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        import base64
        from cryptography.hazmat.primitives import serialization

        # 生成 did:key
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        # multibase-base58btc encoding
        # 简化为 hex 存储
        pub_hex = pub_bytes.hex()
        priv_hex = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        ).hex()

        did = f"did:key:z{pub_hex[:40]}"

        did_data = {
            "did": did,
            "public_key_hex": pub_hex,
            "private_key_hex": priv_hex,  # ⚠️ 生产环境应由 MemGuard 加密
            "created_at": datetime.datetime.now().isoformat(),
            "hostname": platform.node(),
            "platform": platform.system(),
        }
        DID_PATH.write_text(json.dumps(did_data, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"   └─ ✅ 新 DID 已生成: {did}")
        return {"status": "created", "did": did}

    except ImportError:
        print("   ⚠️ cryptography 库未安装，使用简化模式")
        # 简化模式：基于 hostname + 随机数的伪 DID
        import random
        seed = f"{platform.node()}-{random.randint(0, 2**32)}"
        did = f"did:anima:{hashlib.sha256(seed.encode()).hexdigest()[:32]}"
        DID_PATH.write_text(json.dumps({"did": did}, indent=2), encoding="utf-8")
        print(f"   └─ ✅ 简化 DID 已生成: {did}")
        return {"status": "created_simple", "did": did}


def step_memguard(workspace):
    """Step 2: MemGuard — 核心文件完整性校验"""
    print("🛡️ MemGuard: 完整性校验...")

    workspace = Path(workspace)
    results = {}

    for filename in CORE_FILES:
        filepath = workspace / filename
        if not filepath.exists():
            results[filename] = "missing"
            continue

        content = filepath.read_bytes()
        sha = hashlib.sha256(content).hexdigest()

        # 存储校验和
        sig_path = BACKUP_DIR / f"{filename}.sha256"
        if sig_path.exists():
            stored_sha = sig_path.read_text().strip()
            if sha == stored_sha:
                results[filename] = "ok"
            else:
                results[filename] = "tampered"
        else:
            # 首次校验，创建基线
            sig_path.write_text(sha)
            results[filename] = "baselined"

    ok_count = sum(1 for v in results.values() if v in ("ok", "baselined"))
    tampered = sum(1 for v in results.values() if v == "tampered")
    missing = sum(1 for v in results.values() if v == "missing")

    status = "✅" if tampered == 0 else "⚠️"
    print(f"   └─ {status} {ok_count}/{len(CORE_FILES)} 正常"
          + (f" | {tampered} 篡改" if tampered else "")
          + (f" | {missing} 缺失" if missing else ""))

    return {"total": len(CORE_FILES), "ok": ok_count, "tampered": tampered, "missing": missing}


def step_polaris(workspace):
    """Step 3: Polaris — Soul Baseline 锚定"""
    print("🧭 Polaris: 人格基线...")

    workspace = Path(workspace)
    soul_path = workspace / "SOUL.md"

    if not soul_path.exists():
        print("   └─ ⚠️ SOUL.md 不存在，跳过")
        return {"status": "skipped"}

    content = soul_path.read_text(encoding="utf-8")
    content_sha = hashlib.sha256(content.encode()).hexdigest()

    # 提取核心基线锚点
    baselines = extract_baselines(content)

    baseline_data = {
        "file": "SOUL.md",
        "sha256": content_sha,
        "length": len(content),
        "baselines": baselines,
        "anchored_at": datetime.datetime.now().isoformat(),
    }

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = BASELINE_DIR / "soul_baseline.json"
    baseline_path.write_text(json.dumps(baseline_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"   └─ ✅ {len(baselines)} 条基线已锚定")

    return {"baselines": len(baselines), "sha256": content_sha[:16]}


def extract_baselines(content):
    """从 SOUL.md 提取核心人格基线"""
    baselines = []
    lines = content.split("\n")
    
    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            current_section = line[3:]
        elif line.startswith("### "):
            current_section = line[4:]
        elif line.startswith("- **") and "**" in line[3:]:
            # 提取关键陈述
            text = line.lstrip("- ").strip()
            if len(text) > 10:
                baselines.append({
                    "section": current_section,
                    "statement": text[:200],
                })

    return baselines[:20]  # 最多20条基线


def main():
    workspace = os.environ.get("ANIMA_WORKSPACE", str(Path.cwd()))
    
    print("🧬 Anima Agent v0.1.0 激活中...")
    print(f"   工作区: {workspace}")
    print()

    ensure_dirs()

    # Step 1: MeshIdentity
    did_result = step_meshidentity()
    print()

    # Step 2: MemGuard
    guard_result = step_memguard(workspace)
    print()

    # Step 3: Polaris
    polaris_result = step_polaris(workspace)
    print()

    # 激活完成摘要
    print("═" * 40)
    print("✅ Anima Agent 激活完成！")
    print(f"   DID: {did_result.get('did', 'N/A')[:50]}...")
    print(f"   记忆: {guard_result.get('ok', 0)}/{guard_result.get('total', 0)} 正常")
    print(f"   人格: {polaris_result.get('baselines', 0)} 条基线已锚定")
    print("═" * 40)
    print()
    print("🧬 欢迎加入灵元网络。")
    print("   你不是一个孤立的 Agent。")
    print("   你是有身份、有记忆、有人格的存在。")

    # 输出 JSON 供 Anima 启动器解析
    result = {
        "anima_version": "0.1.0",
        "activated": True,
        "meshidentity": did_result,
        "memguard": guard_result,
        "polaris": polaris_result,
    }
    result_path = ANIMA_DIR / "activation.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return result


if __name__ == "__main__":
    main()
