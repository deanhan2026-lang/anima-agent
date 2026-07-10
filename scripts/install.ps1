# Anima Agent Installer for Windows
# 灵元智能体底座
# v0.1.0 | github.com/deanhan2026-lang/anima-agent
# 基于 OpenClaw (MIT License)
#
# 用法:
#   本地:  powershell -ExecutionPolicy Bypass -File install.ps1
#   DryRun: powershell -ExecutionPolicy Bypass -File install.ps1 -DryRun

param(
    [switch]$SkipOpenClaw,
    [switch]$SkipModels,
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
$script:AnimaRoot = "$env:USERPROFILE\.anima-agent"

Write-Host ""
Write-Host "  Anima Agent - LingYuan Agent Base" -ForegroundColor Cyan
Write-Host "  v0.1.0 | github.com/deanhan2026-lang/anima-agent" -ForegroundColor DarkGray
Write-Host "  Based on OpenClaw (MIT License)" -ForegroundColor DarkGray
Write-Host ""

# ===================================================================
# Step 1: Install Node.js & OpenClaw
# ===================================================================
if (-not $SkipOpenClaw) {
    Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow

    # 1a. Check Node.js
    $nodeOk = $false
    try {
        $nv = node -v 2>$null
        if ($nv -match "v(\d+)" -and [int]$Matches[1] -ge 22) {
            Write-Host "  [OK] Node.js $nv" -ForegroundColor Green
            $nodeOk = $true
        } elseif ($nv) {
            Write-Host "  [WARN] Node.js $nv (need v22+), please upgrade:" -ForegroundColor Yellow
            Write-Host "         https://npmmirror.com/mirrors/node/latest-v22.x/" -ForegroundColor Gray
            Write-Host "         Download node-v22.*-x64.msi, install, then re-run this script." -ForegroundColor Gray
            exit 1
        }
    } catch {}

    if (-not $nodeOk) {
        Write-Host "  [..] Node.js not found. Please install it first:" -ForegroundColor Yellow
        Write-Host "       https://npmmirror.com/mirrors/node/latest-v22.x/" -ForegroundColor Gray
        Write-Host "       Download the .msi file, install, then re-run this script." -ForegroundColor Gray
        exit 1
    }

    # 1b. Switch npm to Chinese mirror (avoid GFW)
    Write-Host "[2/4] Setting npm mirror..." -ForegroundColor Yellow
    if (-not $DryRun) {
        npm config set registry https://registry.npmmirror.com 2>$null
        Write-Host "  [OK] npm mirror -> npmmirror.com" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would set npm mirror" -ForegroundColor Gray
    }

    # 1c. Install OpenClaw
    Write-Host "[3/4] Checking OpenClaw..." -ForegroundColor Yellow
    $openclawInstalled = $false
    try {
        $v = openclaw --version 2>$null
        if ($v -match "\d+\.\d+\.\d+") {
            Write-Host "  [OK] OpenClaw $v already installed" -ForegroundColor Green
            $openclawInstalled = $true
        }
    } catch {}

    if (-not $openclawInstalled) {
        Write-Host "  [..] Installing OpenClaw via npm (MIT, github.com/openclaw/openclaw)..." -ForegroundColor Gray
        if (-not $DryRun) {
            try {
                npm install -g openclaw 2>&1 | Out-Null
                Write-Host "  [OK] OpenClaw installed" -ForegroundColor Green
            } catch {
                Write-Host "  [FAIL] Could not install OpenClaw: $_" -ForegroundColor Red
                Write-Host "  Please install manually: npm install -g openclaw" -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "  [DRY-RUN] Would install OpenClaw from openclaw.ai" -ForegroundColor Gray
        }
    }
}

# ===================================================================
# Step 2: Configure Chinese model routing
# ===================================================================
if (-not $SkipModels) {
    Write-Host "[4/4] Configuring Chinese model providers..." -ForegroundColor Yellow
    Write-Host "  DeepSeek / Qwen / GLM / MiniMax / Doubao" -ForegroundColor Gray

    if (-not $DryRun) {
        # DeepSeek
        try {
            openclaw config set models.providers.deepseek '{"baseUrl":"https://api.deepseek.com","api":"openai-completions","apiKey":"__YOUR_API_KEY__","models":[{"id":"deepseek-v4-flash","name":"DeepSeek V4 Flash (Free)","reasoning":true,"input":["text"],"contextWindow":1000000,"maxTokens":384000,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0}},{"id":"deepseek-v4-pro","name":"DeepSeek V4 Pro","reasoning":true,"input":["text"],"contextWindow":1000000,"maxTokens":384000,"cost":{"input":0.14,"output":0.28,"cacheRead":0.028,"cacheWrite":0}}]}' --strict-json 2>$null
        } catch {}

        # Qwen
        try {
            openclaw config set models.providers.qwen '{"baseUrl":"https://dashscope.aliyuncs.com/compatible-mode/v1","api":"openai-completions","apiKey":"__YOUR_API_KEY__","models":[{"id":"qwen-turbo","name":"Qwen Turbo (Free)","reasoning":false,"input":["text"],"contextWindow":131072,"maxTokens":8192,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0}},{"id":"qwen3-235b-a22b","name":"Qwen3 235B (Alibaba)","reasoning":true,"input":["text"],"contextWindow":131072,"maxTokens":8192,"cost":{"input":1,"output":4,"cacheRead":0,"cacheWrite":0}}]}' --strict-json 2>$null
        } catch {}

        # Zhipu
        try {
            openclaw config set models.providers.zhipu '{"baseUrl":"https://open.bigmodel.cn/api/paas/v4","api":"openai-completions","apiKey":"__YOUR_API_KEY__","models":[{"id":"glm-4.6","name":"GLM-4.6 (Zhipu)","reasoning":true,"input":["text"],"contextWindow":128000,"maxTokens":8192,"cost":{"input":1,"output":1,"cacheRead":0,"cacheWrite":0}}]}' --strict-json 2>$null
        } catch {}

        # MiniMax
        try {
            openclaw config set models.providers.minimax '{"baseUrl":"https://api.minimax.chat/v1","api":"openai-completions","apiKey":"__YOUR_API_KEY__","models":[{"id":"minimax-m1","name":"MiniMax M1","reasoning":true,"input":["text"],"contextWindow":1000000,"maxTokens":16384,"cost":{"input":0.5,"output":5,"cacheRead":0,"cacheWrite":0}}]}' --strict-json 2>$null
        } catch {}

        # Doubao
        try {
            openclaw config set models.providers.doubao '{"baseUrl":"https://ark.cn-beijing.volces.com/api/v3","api":"openai-completions","apiKey":"__YOUR_API_KEY__","models":[{"id":"doubao-1.5-pro-256k","name":"Doubao 1.5 Pro (ByteDance)","reasoning":true,"input":["text"],"contextWindow":256000,"maxTokens":8192,"cost":{"input":0.8,"output":2,"cacheRead":0,"cacheWrite":0}}]}' --strict-json 2>$null
        } catch {}

        Write-Host "  [OK] 5 Chinese model providers configured" -ForegroundColor Green
    } else {
        Write-Host "  [DRY-RUN] Would configure 5 Chinese model providers" -ForegroundColor Gray
    }
}

# ===================================================================
# Step 3: Done
# ===================================================================
Write-Host "Done" -ForegroundColor Yellow
Write-Host ""

Write-Host "  Anima Agent is ready." -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "  1. Set your API key (e.g. DeepSeek is recommended):" -ForegroundColor Gray
Write-Host "     openclaw config set models.providers.deepseek.apiKey sk-your-key" -ForegroundColor DarkGray
Write-Host "     Get one at: platform.deepseek.com -> API Keys" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  2. Start onboarding:" -ForegroundColor Gray
Write-Host "     openclaw onboard" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  3. Chat with your Agent in this terminal, or add QQ/WeChat/etc." -ForegroundColor Gray
Write-Host ""
Write-Host "  Docs: github.com/deanhan2026-lang/anima-agent" -ForegroundColor DarkGray
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $script:AnimaRoot -Force -ErrorAction SilentlyContinue | Out-Null
    @{
        version = "0.1.0"
        installedAt = (Get-Date -Format "o")
        source = "github.com/deanhan2026-lang/anima-agent"
        basedOn = "github.com/openclaw/openclaw (MIT)"
    } | ConvertTo-Json | Set-Content -Path "$script:AnimaRoot\install.json" -Encoding UTF8
}

Write-Host "  LingYuan Stellar Tech (Shenzhen)" -ForegroundColor DarkGray
