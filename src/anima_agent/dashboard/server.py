"""
ANIMA AGENT — Desktop Dashboard Server

FastAPI backend + embedded HTML/JS frontend.
Launched via 'anima dashboard'.
"""

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from ..identity.did import get_identity_status, load_identity
from ..governance.engine import GovernanceEngine
from ..models.router import get_model_list, get_route, classify_request
from ..gateway.client import check_gateway_status, list_nodes


dashboard_app = FastAPI(title="ANIMA AGENT Dashboard", version="1.0.0")
governance = GovernanceEngine()


# ─── API ROUTES ───

@dashboard_app.get("/api/status")
async def api_status():
    """Aggregate status for dashboard."""
    id_status = get_identity_status()
    gov_status = governance.get_status()
    models = get_model_list()
    gw = check_gateway_status()

    return {
        "identity": id_status,
        "governance": {
            "laws_loaded": gov_status["laws_loaded"],
            "violations_today": gov_status["violations_today"],
        },
        "models": {
            "total": len(models),
            "free_count": len([m for m in models if m["is_free"]]),
            "list": models,
        },
        "gateway": gw,
    }


@dashboard_app.get("/api/network/nodes")
async def api_nodes(limit: int = 20):
    """Get registered nodes."""
    nodes = list_nodes(limit=limit)
    return {"nodes": nodes, "total": len(nodes)}


@dashboard_app.post("/api/route")
async def api_route(request: Request):
    """Test model routing."""
    body = await request.json()
    query = body.get("query", "")
    route = get_route(query)
    return route


# ─── STATIC ASSETS ───

TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


@dashboard_app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the dashboard HTML."""
    return get_dashboard_html()


def get_dashboard_html() -> str:
    """Inline dashboard HTML (single file, no build step)."""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ANIMA AGENT v1.0</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
  background: #0a0a0f; color: #e0e0e0; min-height: 100vh;
}
.header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 24px 32px; border-bottom: 1px solid #2a2a40;
  display: flex; justify-content: space-between; align-items: center;
}
.header h1 { font-size: 24px; color: #e94560; }
.header .version { color: #666; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px; padding: 24px; }
.card {
  background: #141420; border: 1px solid #2a2a40; border-radius: 12px;
  padding: 20px; transition: border-color 0.2s;
}
.card:hover { border-color: #e94560; }
.card-title { font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }
.card-value { font-size: 32px; font-weight: 700; }
.did-box {
  font-family: monospace; font-size: 13px; background: #0d0d18;
  padding: 12px; border-radius: 8px; word-break: break-all;
  color: #4fc3f7; margin-top: 8px;
}
.tag {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; margin-right: 4px; margin-bottom: 4px;
}
.tag-green { background: #1b5e20; color: #81c784; }
.tag-red { background: #b71c1c; color: #ef9a9a; }
.tag-blue { background: #0d47a1; color: #64b5f6; }
.tag-yellow { background: #4a3800; color: #ffe082; }
.model-lane { margin-bottom: 12px; padding: 8px 12px; background: #1a1a28; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
.model-name { font-weight: 600; }
.route-input { margin-top: 16px; display: flex; gap: 8px; }
.route-input input {
  flex: 1; padding: 8px 12px; background: #0d0d18; border: 1px solid #2a2a40;
  border-radius: 8px; color: #e0e0e0; font-size: 14px;
}
.route-input button {
  padding: 8px 16px; background: #e94560; border: none; border-radius: 8px;
  color: #fff; cursor: pointer; font-weight: 600;
}
.route-result { margin-top: 12px; font-size: 13px; color: #4fc3f7; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-online { background: #4caf50; }
.status-offline { background: #f44336; }
.loading { color: #666; font-style: italic; }
.empty { color: #555; text-align: center; padding: 24px; }
.laws-grid { display: grid; grid-template-columns: 1fr; gap: 8px; }
.law-item { padding: 8px 12px; background: #1a1a28; border-radius: 6px; font-size: 13px; display: flex; justify-content: space-between; }
.law-id { color: #e94560; font-weight: 700; margin-right: 8px; }
.node-item { padding: 8px 12px; background: #1a1a28; border-radius: 6px; font-size: 12px; margin-bottom: 4px; font-family: monospace; }
.footer { text-align: center; padding: 24px; color: #444; font-size: 12px; border-top: 1px solid #1a1a28; margin-top: 24px; }
.footer .company { color: #e94560; font-weight: 600; }
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>ANIMA AGENT</h1>
    <span class="version">v1.0 · AI Identity Sovereign Runtime</span>
  </div>
  <div style="text-align:right">
    <div style="font-size:13px;color:#888;">Status</div>
    <div><span class="status-dot status-online"></span>Running</div>
  </div>
</div>
<div class="grid">
  <!-- IDENTITY CARD -->
  <div class="card">
    <div class="card-title">🆔 Identity</div>
    <div id="identity-content"><span class="loading">Loading...</span></div>
  </div>

  <!-- GOVERNANCE CARD -->
  <div class="card">
    <div class="card-title">⚖️ Governance</div>
    <div id="gov-content"><span class="loading">Loading...</span></div>
  </div>

  <!-- MODELS CARD -->
  <div class="card">
    <div class="card-title">🤖 Models</div>
    <div id="models-content"><span class="loading">Loading...</span></div>
  </div>

  <!-- GATEWAY CARD -->
  <div class="card">
    <div class="card-title">🌐 Gateway</div>
    <div id="gateway-content"><span class="loading">Loading...</span></div>
  </div>

  <!-- NETWORK NODES CARD -->
  <div class="card" style="grid-column: 1 / -1;">
    <div class="card-title">🔗 Network Nodes</div>
    <div id="nodes-content"><span class="loading">Loading...</span></div>
  </div>
</div>
<div class="footer"><span class="company">ANIMASTELLAR TECHNOLOGY</span> · 2026 · Built on OpenClaw · <a href="https://github.com/animastellar/anima-os" style="color:#4fc3f7;">github.com/animastellar/anima-os</a></div>

<script>
async function load() {
  const res = await fetch('/api/status');
  const data = await res.json();
  renderIdentity(data.identity);
  renderGovernance(data.governance);
  renderModels(data.models);
  renderGateway(data.gateway);
  loadNodes();
}

function renderIdentity(id) {
  const el = document.getElementById('identity-content');
  if (!id.has_did) {
    el.innerHTML = '<div class="empty">No DID — run <code>anima identity generate</code></div>';
    return;
  }
  el.innerHTML = `
    <div class="card-value" style="font-size:16px;">${escapeHtml(id.did)}</div>
    <div style="margin-top:12px;font-size:13px;color:#888;">
      Key: ${id.public_key_hex?.substring(0,16)}...<br>
      Created: ${id.created_at?.substring(0,19)}<br>
      Type: <span class="tag tag-blue">${id.node_type}</span>
    </div>
  `;
}

function renderGovernance(gov) {
  const el = document.getElementById('gov-content');
  el.innerHTML = `
    <div class="card-value" style="color:#e94560;">G001–G008</div>
    <div style="margin-top:8px;font-size:13px;">
      Laws: <span class="tag tag-green">${gov.laws_loaded} loaded</span>
      Violations: <span class="tag tag-red">${gov.violations_today}</span>
    </div>
    <div style="margin-top:12px;font-size:12px;color:#888;">
      G001 核心范式 · G002 透明追溯 · G003 三角分工<br>
      G004 否决权 · G005 数据分类 · G006 自主权<br>
      G007 记忆完整 · G008 永恒平等
    </div>
  `;
}

function renderModels(models) {
  const el = document.getElementById('models-content');
  let html = `<div style="font-size:13px;color:#888;margin-bottom:8px;">
    ${models.total} registered · ${models.free_count} free</div>`;
  models.list.forEach(m => {
    const tierColors = {default:'tag-green',reasoning:'tag-blue',long_context:'tag-yellow',fallback:'tag-red'};
    html += `<div class="model-lane">
      <span class="model-name">${m.name}</span>
      <span>
        <span class="tag ${tierColors[m.tier]||'tag-blue'}">${m.tier}</span>
        ${m.is_free ? '<span class="tag tag-green">FREE</span>' : '<span class="tag tag-yellow">PAID</span>'}
      </span>
    </div>`;
  });

  html += `<div class="route-input">
    <input id="route-query" placeholder="Test routing... (e.g. 解释量子计算)">
    <button onclick="testRoute()">Route</button>
  </div>
  <div class="route-result" id="route-result"></div>`;

  el.innerHTML = html;
}

async function testRoute() {
  const query = document.getElementById('route-query').value;
  if (!query) return;
  const res = await fetch('/api/route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query})
  });
  const route = await res.json();
  document.getElementById('route-result').innerHTML =
    `→ Tier: <b>${route.tier}</b> · Model: <b>${route.model}</b> · ` +
    `Free: ${route.is_free ? '✅' : '💰'} · Context: ${route.max_context.toLocaleString()}`;
}

function renderGateway(gw) {
  const el = document.getElementById('gateway-content');
  el.innerHTML = `
    <div style="font-size:20px;">
      <span class="status-dot ${gw.online ? 'status-online' : 'status-offline'}"></span>
      ${gw.online ? 'Online' : 'Offline'}
    </div>
    <div style="margin-top:8px;font-size:13px;color:#888;">${escapeHtml(gw.url)}</div>
  `;
}

async function loadNodes() {
  const res = await fetch('/api/network/nodes?limit=30');
  const data = await res.json();
  const el = document.getElementById('nodes-content');
  if (!data.nodes.length) {
    el.innerHTML = '<div class="empty">No nodes registered yet.</div>';
    return;
  }
  el.innerHTML = data.nodes.map(n =>
    `<div class="node-item">
      <span style="color:#e94560;">⬡</span>
      ${escapeHtml(n.did?.substring(0,36))}...
      <span class="tag tag-blue">${n.node_type}</span>
      <span style="color:#666;">${(n.registered_at||'').substring(0,19)}</span>
    </div>`
  ).join('');
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

load();
</script>
</body>
</html>"""


def launch_dashboard(host: str = "127.0.0.1", port: int = 8420):
    """Start the dashboard server."""
    uvicorn.run(dashboard_app, host=host, port=port, log_level="info")
