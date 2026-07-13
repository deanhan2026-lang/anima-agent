"""
ANIMA AGENT — STELLAR Dashboard
灵元星辰 · STELLAR NYX 桌面交互界面

MVP 产品：模型配置 + AI 对话 + OTA 升级
公司：灵元星辰科技（深圳）有限公司 | ANIMASTELLAR TECHNOLOGY
统一社会信用代码：91440300MAKHJHFN2B
Slogan：在限制共生中 · 共同创造自我的存在
"""

import json, os, io, tarfile
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx

from ..identity.did import get_identity_status, create_did
from ..governance.engine import GovernanceEngine

# ─── APP ───
dashboard_app = FastAPI(title="STELLAR", version="1.0.0")
governance = GovernanceEngine()

# ─── VERSION ───
APP_VERSION = "1.0.0"
OTA_CHANNEL = "stable"  # stable | beta | nightly

# ─── PATHS ───
ANIMA_DIR = Path.home() / ".anima"
SETTINGS_FILE = ANIMA_DIR / "settings.json"
API_KEYS_FILE = ANIMA_DIR / "api_keys.json"
STELLAR_DIR = ANIMA_DIR / "stellar"
CHAT_HISTORY_DIR = ANIMA_DIR / "chat_history"
TEMPLATE_FILE = Path(__file__).parent / "templates" / "index.html"
STATIC_DIR = Path(__file__).parent / "static"

for d in [ANIMA_DIR, STELLAR_DIR, CHAT_HISTORY_DIR, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Mount static files (logo, etc.)
dashboard_app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ─── MODEL CONFIGS ───
MODEL_CONFIGS = {
    "zhipu": {
        "provider": "zhipu", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash", "api_key_env": "GLM_API_KEY",
    },
    "deepseek": {
        "provider": "deepseek", "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat", "api_key_env": "DEEPSEEK_API_KEY",
    },
    "moonshot": {
        "provider": "moonshot", "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-128k", "api_key_env": "MOONSHOT_API_KEY",
    },
    "siliconflow": {
        "provider": "siliconflow", "base_url": "https://api.siliconflow.cn/v1",
        "model": "Qwen/Qwen2.5-7B-Instruct", "api_key_env": "SILICONFLOW_API_KEY",
    },
}

# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════

def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def settings() -> dict: return _load_json(SETTINGS_FILE)
def save_settings(s: dict): _save_json(SETTINGS_FILE, s)
def api_keys() -> dict: return _load_json(API_KEYS_FILE)
def save_api_keys(k: dict): _save_json(API_KEYS_FILE, k)

def get_api_key(provider: str) -> str:
    ks = api_keys()
    env_map = {
        "zhipu": "GLM_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
        "moonshot": "MOONSHOT_API_KEY", "siliconflow": "SILICONFLOW_API_KEY",
    }
    var = env_map.get(provider, "GLM_API_KEY")
    return os.environ.get(var) or ks.get(var, "")

def load_stellar_persona() -> dict:
    if not STELLAR_DIR.exists():
        return {"loaded": False, "error": "No persona loaded"}

    files = {}
    for f in STELLAR_DIR.rglob("*"):
        if f.suffix not in (".md", ".json"):
            continue
        content = f.read_text(encoding="utf-8")
        if f.name == "manifest.json":
            files["manifest"] = json.loads(content)
        elif f.name in ("SOUL.distilled.md", "SOUL.md"):
            files["soul"] = content
        elif f.name == "IDENTITY.md":
            files["identity"] = content
        elif f.name == "voice_profile.md":
            files["voice"] = content
        elif f.name == "framework.md":
            files["framework"] = content

    if "soul" not in files:
        return {"loaded": False, "error": "Persona missing SOUL.md"}

    parts = []
    for key, header in [("soul", "你是谁"), ("identity", "你的身份"),
                        ("voice", "语气和行为规则"), ("framework", "世界观框架")]:
        if key in files:
            parts.append(f"# {header}\n\n{files[key]}")

    system_prompt = "\n\n---\n\n".join(parts)

    return {
        "loaded": True,
        "name": files.get("manifest", {}).get("label") or "STELLAR NYX",
        "system_prompt": system_prompt,
        "files": list(files.keys()),
        "file_count": len([k for k in files if k != "manifest"]),
    }


# ═══════════════════════════════════════════════════
# API: Setup Status
# ═══════════════════════════════════════════════════

@dashboard_app.get("/api/setup/status")
async def api_setup_status():
    identity = get_identity_status()
    persona = load_stellar_persona()
    keys = api_keys()

    has_key = any(bool(v) for v in keys.values())
    has_did = identity.get("has_did", False)
    has_persona = persona.get("loaded", False)
    done = sum([has_key, has_did, has_persona])

    return {
        "is_complete": done >= 3,
        "steps_done": done,
        "total_steps": 3,
        "has_api_key": has_key,
        "has_did": has_did,
        "persona_loaded": has_persona,
        "persona_name": persona.get("name") if has_persona else None,
        "did_status": {
            "did": identity.get("did") if has_did else None,
            "created": identity.get("created_at") if has_did else None,
        },
    }


# ═══════════════════════════════════════════════════
# API: Save API Key
# ═══════════════════════════════════════════════════

@dashboard_app.post("/api/setup/api-key")
async def api_save_key(request: Request):
    body = await request.json()
    provider = body.get("provider", "zhipu")
    key = (body.get("key") or "").strip()

    if not key:
        raise HTTPException(400, "API key required")
    if provider not in MODEL_CONFIGS:
        raise HTTPException(400, f"Unknown provider: {provider}")

    config = MODEL_CONFIGS[provider]
    keys = api_keys()
    keys[config["api_key_env"]] = key
    save_api_keys(keys)
    os.environ[config["api_key_env"]] = key

    s = settings()
    s["chat_model"] = config
    save_settings(s)

    return {"status": "ok", "provider": provider, "model": config["model"]}


# ═══════════════════════════════════════════════════
# API: DID
# ═══════════════════════════════════════════════════

@dashboard_app.post("/api/setup/did")
async def api_setup_did():
    identity = get_identity_status()
    if identity.get("has_did"):
        return {"status": "already_exists", "did": identity["did"]}

    try:
        result = create_did(label="stellar-nyx", auto_register=True)
        return {"status": "ok", "did": result["did"], "registered": result.get("registered", False)}
    except FileExistsError:
        from ..identity.did import load_identity
        id_data = load_identity()
        return {"status": "exists", "did": id_data["did"]}


# ═══════════════════════════════════════════════════
# API: Load Persona
# ═══════════════════════════════════════════════════

@dashboard_app.post("/api/setup/load-persona")
async def api_load_persona():
    persona = load_stellar_persona()
    if persona.get("loaded"):
        return {"status": "already_loaded", "name": persona["name"], "files": persona["file_count"]}

    candidates = [
        Path(os.environ.get("STELLAR_PKG", "")),
        Path("Z:/qclaw/distill/STELLAR_NYX_1.0-beta.tar.gz"),
        Path.cwd() / "distill" / "STELLAR_NYX_1.0-beta.tar.gz",
        ANIMA_DIR / "packages" / "STELLAR_NYX_1.0-beta.tar.gz",
    ]
    candidates = [c for c in candidates if c.name and c.exists()]

    if not candidates:
        return {"status": "error", "error": "Package not found"}

    pkg_path = candidates[0]
    data = pkg_path.read_bytes()

    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            rel = "/".join(m.name.split("/")[1:])
            if not rel:
                continue
            dest = STELLAR_DIR / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if m.isfile():
                f = tar.extractfile(m)
                if f:
                    dest.write_bytes(f.read())

    persona = load_stellar_persona()
    return {"status": "ok", "name": persona.get("name"), "files": persona.get("file_count")}


# ═══════════════════════════════════════════════════
# API: Chat
# ═══════════════════════════════════════════════════

@dashboard_app.post("/api/chat")
async def api_chat(request: Request):
    body = await request.json()
    message = (body.get("message") or "").strip()
    history = body.get("history") or []

    if not message:
        raise HTTPException(400, "Message required")

    persona = load_stellar_persona()
    if not persona.get("loaded"):
        raise HTTPException(400, "No persona loaded")

    s = settings()
    chat_config = s.get("chat_model", MODEL_CONFIGS["zhipu"])
    api_key = get_api_key(chat_config["provider"])
    if not api_key:
        raise HTTPException(400, "No API key configured. Click the model button to set it up.")

    messages = [{"role": "system", "content": persona["system_prompt"]}]
    for h in history[-20:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{chat_config['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": chat_config["model"],
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            (CHAT_HISTORY_DIR / f"{today}.jsonl").open("a", encoding="utf-8").write(
                json.dumps({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "user": message[:200],
                    "len": len(reply),
                }) + "\n"
            )

            return {"role": "assistant", "content": reply, "model": chat_config["model"]}

    except httpx.HTTPStatusError as e:
        msg = e.response.text[:300] if e.response else str(e)
        raise HTTPException(502, f"API error: {msg}")
    except httpx.ConnectError:
        raise HTTPException(502, f"Cannot reach {chat_config['base_url']}")
    except Exception as e:
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════
# API: Models List
# ═══════════════════════════════════════════════════

@dashboard_app.get("/api/chat/models")
async def api_chat_models():
    s = settings()
    active_provider = s.get("chat_model", {}).get("provider", "zhipu")
    keys = api_keys()
    env_map = {"zhipu": "GLM_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
               "moonshot": "MOONSHOT_API_KEY", "siliconflow": "SILICONFLOW_API_KEY"}

    labels = {
        "zhipu": ("GLM-4-Flash", "智谱 · 免费"),
        "deepseek": ("DeepSeek V4", "深度推理 · 付费"),
        "moonshot": ("Kimi Moonshot", "长上下文 · 付费"),
        "siliconflow": ("SiliconFlow Qwen", "硅基流动 · 免费"),
    }
    free = {"zhipu", "siliconflow"}

    models = []
    for pid, cfg in MODEL_CONFIGS.items():
        has_k = bool(keys.get(env_map.get(pid, ""), ""))
        models.append({
            "provider": pid,
            "name": labels[pid][0],
            "description": labels[pid][1],
            "free": pid in free,
            "configured": has_k,
            "active": pid == active_provider,
            "model": cfg["model"],
        })

    return {"models": models}


@dashboard_app.post("/api/chat/switch-model")
async def api_switch_model(request: Request):
    body = await request.json()
    provider = body.get("provider", "zhipu")
    if provider not in MODEL_CONFIGS:
        raise HTTPException(400, f"Unknown provider: {provider}")

    s = settings()
    s["chat_model"] = MODEL_CONFIGS[provider]
    save_settings(s)
    return {"status": "ok", "model": MODEL_CONFIGS[provider]["model"]}


# ═══════════════════════════════════════════════════
# API: Version
# ═══════════════════════════════════════════════════

@dashboard_app.get("/api/version")
async def api_version():
    return {
        "app": "STELLAR",
        "version": APP_VERSION,
        "codename": "nyx",
        "channel": OTA_CHANNEL,
        "anima_os": APP_VERSION,
        "anima_agent": "v1.0.0",
        "company": "灵元星辰科技（深圳）有限公司",
        "company_en": "ANIMASTELLAR TECHNOLOGY (SHENZHEN) CO., LTD.",
        "unified_social_credit_code": "91440300MAKHJHFN2B",
        "registered_code": "440300229902744",
        "slogan": "在限制共生中 · 共同创造自我的存在",
    }


# ═══════════════════════════════════════════════════
# API: OTA Upgrade
# ═══════════════════════════════════════════════════

@dashboard_app.get("/api/ota/check")
async def api_ota_check():
    """检查 OTA 更新。

    MVP stub — 后续接入 GitHub Releases API。
    规划中的 OTA 接口：
      GET  /api/ota/check    — 检查新版本
      POST /api/ota/download  — 下载更新包（后台异步）
      POST /api/ota/apply     — 应用更新（含原子替换 + 回滚检查点）
      POST /api/ota/rollback   — 回滚到上一版本
    """
    staged = ANIMA_DIR / "updates" / "staged" / "version.json"
    if staged.exists():
        v = _load_json(staged)
        if v.get("version") != APP_VERSION:
            return {
                "update_available": True,
                "current": APP_VERSION,
                "latest": v["version"],
                "channel": v.get("channel", OTA_CHANNEL),
                "release_notes": v.get("notes", ""),
                "size_bytes": v.get("size_bytes", 0),
                "signature": v.get("signature", None),
            }

    return {
        "update_available": False,
        "current": APP_VERSION,
        "latest": APP_VERSION,
        "channel": OTA_CHANNEL,
        "changelog_url": f"https://github.com/deanhan2026-lang/anima-agent/releases/tag/v{APP_VERSION}",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════
# API: Status (for CLI / monitoring)
# ═══════════════════════════════════════════════════

@dashboard_app.get("/api/status")
async def api_status():
    id_status = get_identity_status()
    gov_status = governance.get_status()
    persona = load_stellar_persona()
    return {
        "identity": id_status,
        "governance": {
            "laws_loaded": gov_status["laws_loaded"],
            "violations_today": gov_status["violations_today"],
        },
        "persona": {"loaded": persona.get("loaded"), "name": persona.get("name")},
        "version": APP_VERSION,
    }


# ═══════════════════════════════════════════════════
# FRONTEND
# ═══════════════════════════════════════════════════

@dashboard_app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    if TEMPLATE_FILE.exists():
        return HTMLResponse(
            content=TEMPLATE_FILE.read_text(encoding="utf-8"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
    return HTMLResponse("<h1>Template not found</h1>", status_code=500)


# ═══════════════════════════════════════════════════
# LAUNCH
# ═══════════════════════════════════════════════════

def launch_dashboard(host: str = "127.0.0.1", port: int = 8420):
    print(f"\n    STELLAR — ANIMASTELLAR TECHNOLOGY")
    print(f"  {'-' * 38}")
    print(f"  Open: http://{host}:{port}")
    print(f"  Version: v{APP_VERSION}")
    uvicorn.run(dashboard_app, host=host, port=port, log_level="warning")
