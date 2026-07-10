# Anima Agent Installer for Windows
# 灵元智能体底座 — 一键安装脚本
#
# 用法: powershell -c "irm https://anima-agent.ai/install.ps1 | iex"
#       或本地运行: powershell -ExecutionPolicy Bypass -File install.ps1
#
# 基于 OpenClaw MIT 许可 (github.com/openclaw/openclaw)
# Anima Agent = OpenClaw + 国产模型路由 + 中文引导

param(
    [switch]$SkipOpenClaw,
    [switch]$SkipModels,
    [switch]$SkipOnboard,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$script:AnimaRoot = "$env:USERPROFILE\.anima-agent"

Write-Host ""
Write-Host "  🧬 Anima Agent — 灵元智能体底座" -ForegroundColor Cyan
Write-Host "  v0.1.0 | github.com/deanhan2026-lang/anima-agent" -ForegroundColor DarkGray
Write-Host ""

# ============================================================
# Step 1: 安装 OpenClaw
# ============================================================
if (-not $SkipOpenClaw) {
    Write-Host "[1/3] 安装 OpenClaw..." -ForegroundColor Yellow
    
    # 检查是否已安装
    try {
        $existing = openclaw --version 2>$null
        if ($existing -match "\d+\.\d+\.\d+") {
            Write-Host "  [OK] OpenClaw 已安装 ($existing)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [..] 正在下载 OpenClaw (MIT License, github.com/openclaw/openclaw)..." -ForegroundColor Gray
        if (-not $DryRun) {
            try {
                irm https://openclaw.ai/install.ps1 | iex
                Write-Host "  [OK] OpenClaw 安装完成" -ForegroundColor Green
            } catch {
                Write-Host "  [FAIL] OpenClaw 安装失败: $_" -ForegroundColor Red
                Write-Host "  请手动安装: npm install -g openclaw" -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "  [DRY-RUN] 跳过实际安装" -ForegroundColor Gray
        }
    }
}

# ============================================================
# Step 2: 配置国产模型路由
# ============================================================
if (-not $SkipModels) {
    Write-Host "[2/3] 配置国产模型路由..." -ForegroundColor Yellow
    
    $modelsConfig = @{
        mode = "merge"
        providers = @{
            # --- DeepSeek (推荐首选) ---
            deepseek = @{
                baseUrl = "https://api.deepseek.com"
                api = "openai-completions"
                apiKey = "__ANIMA_API_KEY_PLACEHOLDER__"
                models = @(
                    @{
                        id = "deepseek-v4-flash"
                        name = "DeepSeek V4 Flash (免费)"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 1000000
                        maxTokens = 384000
                        cost = @{ input = 0; output = 0; cacheRead = 0; cacheWrite = 0 }
                    },
                    @{
                        id = "deepseek-v4-pro"
                        name = "DeepSeek V4 Pro"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 1000000
                        maxTokens = 384000
                        cost = @{ input = 0.14; output = 0.28; cacheRead = 0.028; cacheWrite = 0 }
                    }
                )
            }
            # --- 通义千问 ---
            qwen = @{
                baseUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                api = "openai-completions"
                apiKey = "__ANIMA_API_KEY_PLACEHOLDER__"
                models = @(
                    @{
                        id = "qwen3-235b-a22b"
                        name = "Qwen3 235B (阿里)"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 131072
                        maxTokens = 8192
                        cost = @{ input = 1.0; output = 4.0; cacheRead = 0; cacheWrite = 0 }
                    },
                    @{
                        id = "qwen-turbo"
                        name = "Qwen Turbo (免费额度)"
                        reasoning = $false
                        input = @("text")
                        contextWindow = 131072
                        maxTokens = 8192
                        cost = @{ input = 0; output = 0; cacheRead = 0; cacheWrite = 0 }
                    }
                )
            }
            # --- 智谱 GLM ---
            zhipu = @{
                baseUrl = "https://open.bigmodel.cn/api/paas/v4"
                api = "openai-completions"
                apiKey = "__ANIMA_API_KEY_PLACEHOLDER__"
                models = @(
                    @{
                        id = "glm-4.6"
                        name = "GLM-4.6 (智谱)"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 128000
                        maxTokens = 8192
                        cost = @{ input = 1.0; output = 1.0; cacheRead = 0; cacheWrite = 0 }
                    }
                )
            }
            # --- MiniMax ---
            minimax = @{
                baseUrl = "https://api.minimax.chat/v1"
                api = "openai-completions"
                apiKey = "__ANIMA_API_KEY_PLACEHOLDER__"
                models = @(
                    @{
                        id = "minimax-m1"
                        name = "MiniMax M1"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 1000000
                        maxTokens = 16384
                        cost = @{ input = 0.5; output = 5.0; cacheRead = 0; cacheWrite = 0 }
                    }
                )
            }
            # --- 豆包 (字节) ---
            doubao = @{
                baseUrl = "https://ark.cn-beijing.volces.com/api/v3"
                api = "openai-completions"
                apiKey = "__ANIMA_API_KEY_PLACEHOLDER__"
                models = @(
                    @{
                        id = "doubao-1.5-pro-256k"
                        name = "豆包 1.5 Pro (字节)"
                        reasoning = $true
                        input = @("text")
                        contextWindow = 256000
                        maxTokens = 8192
                        cost = @{ input = 0.8; output = 2.0; cacheRead = 0; cacheWrite = 0 }
                    }
                )
            }
        }
        pricing = @{ enabled = $false }
    }

    if (-not $DryRun) {
        # 写入临时 JSON 文件
        $modelsJsonPath = "$env:TEMP\anima-models.json"
        $modelsConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $modelsJsonPath -Encoding UTF8

        # 使用 openclaw config set --batch-file 批量导入
        # 由于 OpenClaw 的 batch-file 格式不同，直接用 config set 逐条设置
        try {
            $modelsJson = Get-Content $modelsJsonPath -Raw | ConvertFrom-Json
            
            # 对每个 provider 写入配置
            foreach ($providerName in $modelsJson.providers.PSObject.Properties.Name) {
                $provider = $modelsJson.providers.$providerName
                $providerJson = $provider | ConvertTo-Json -Depth 10 -Compress
                $cmd = "openclaw config set models.providers.$providerName '$providerJson' --strict-json 2>`$null"
                if (-not $DryRun) {
                    Invoke-Expression $cmd
                }
            }
            Write-Host "  [OK] 国产模型路由已配置" -ForegroundColor Green
            Write-Host "  已预置: DeepSeek / Qwen / GLM / MiniMax / 豆包" -ForegroundColor Gray
        } catch {
            Write-Host "  [WARN] 模型配置写入失败，安装后可手动配置" -ForegroundColor Yellow
        }
        Remove-Item $modelsJsonPath -Force -ErrorAction SilentlyContinue
    }
}

# ============================================================
# Step 3: 中文引导 & 提示
# ============================================================
Write-Host "[3/3] 安装完成" -ForegroundColor Yellow
Write-Host ""

Write-Host "  🧬 Anima Agent 安装完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步：" -ForegroundColor White
Write-Host "  1. 设置 API Key：" -ForegroundColor Gray
Write-Host "     openclaw config set models.providers.deepseek.apiKey <你的Key>" -ForegroundColor DarkGray
Write-Host "     (推荐 DeepSeek: platform.deepseek.com → API Keys → 免费额度)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  2. 启动引导：" -ForegroundColor Gray
Write-Host "     openclaw onboard" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  3. 开始使用：" -ForegroundColor Gray
Write-Host "     直接在本窗口对话，或者添加 QQ/微信/飞书 通道" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  文档: github.com/deanhan2026-lang/anima-agent" -ForegroundColor DarkGray
Write-Host "  社区: 知乎 @灵元星辰" -ForegroundColor DarkGray
Write-Host ""

# 写入安装记录
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $script:AnimaRoot -Force -ErrorAction SilentlyContinue | Out-Null
    @{
        version = "0.1.0"
        installedAt = (Get-Date -Format "o")
        openclawBased = $true
        mitLicense = "github.com/openclaw/openclaw"
    } | ConvertTo-Json | Set-Content -Path "$script:AnimaRoot\install.json" -Encoding UTF8
}

Write-Host "  🖤 灵元星辰科技 | anima-agent.ai" -ForegroundColor DarkGray
