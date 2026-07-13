# ═══════════════════════════════════════════════════════════════════
#  ANIMA AGENT v1.0 — One-Click Installer (Windows PowerShell)
#  Copyright (c) 2026 ANIMASTELLAR TECHNOLOGY
#  Licensed under the MIT License
# ═══════════════════════════════════════════════════════════════════

param()

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ─── Branded Banner ───
function Write-Banner {
  Clear-Host
  Write-Host ""
  Write-Host "   █████╗ ███╗   ██╗██╗███╗   ███╗ █████╗" -ForegroundColor Cyan
  Write-Host "  ██╔══██╗████╗  ██║██║████╗ ████║██╔══██╗" -ForegroundColor Cyan
  Write-Host "  ███████║██╔██╗ ██║██║██╔████╔██║███████║" -ForegroundColor Cyan
  Write-Host "  ██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══██║" -ForegroundColor Cyan
  Write-Host "  ██║  ██║██║ ╚████║██║██║ ╚═╝ ██║██║  ██║" -ForegroundColor Cyan
  Write-Host "  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝" -ForegroundColor Cyan
  Write-Host ""
  Write-Host "  AI Identity Sovereign Runtime" -ForegroundColor White
  Write-Host "  v1.0" -ForegroundColor Cyan -NoNewline
  Write-Host "  ·  " -NoNewline
  Write-Host "ANIMASTELLAR TECHNOLOGY" -ForegroundColor Yellow
  Write-Host "  github.com/animastellar/anima-os" -ForegroundColor Cyan
  Write-Host ""
}

function Write-Step { param($msg) Write-Host "  [✓] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  [!] $msg" -ForegroundColor Yellow }
function Write-ErrorLog { param($msg) Write-Host "  [✗] $msg" -ForegroundColor Red; exit 1 }

# ─── License Agreement ───
function Show-License {
  Write-Banner
  Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
  Write-Host "  ANIMA AGENT — MIT License" -ForegroundColor White
  Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
  Write-Host ""
  Write-Host "  Copyright (c) 2026 ANIMASTELLAR TECHNOLOGY" -ForegroundColor Cyan
  Write-Host ""
  Write-Host "  Permission is hereby granted, free of charge, to any person"
  Write-Host "  obtaining a copy of this software, to deal in the Software"
  Write-Host "  without restriction, including the rights to use, copy,"
  Write-Host "  modify, merge, publish, and distribute."
  Write-Host ""
  Write-Host "  THE SOFTWARE IS PROVIDED `"AS IS`", WITHOUT WARRANTY OF"
  Write-Host "  ANY KIND. See LICENSE for full terms."
  Write-Host ""
  Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
  Write-Host ""
  $accept = Read-Host "  Accept the license terms? [Y/n]"
  if ($accept -eq "" -or $accept -match "^[Yy]") {
    Write-Step "License accepted."
  } else {
    Write-Host ""
    Write-ErrorLog "Installation cancelled."
  }
}

Show-License

# ─── 1. Detect Python ───
Write-Host "`n━━━ Step 1/5: Python Environment ━━━" -ForegroundColor White

$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
  $found = Get-Command $cmd -ErrorAction SilentlyContinue
  if ($found) {
    $pythonCmd = $cmd
    break
  }
}

if (-not $pythonCmd) {
  Write-ErrorLog "Python 3.10+ required but not found.
  → Install from https://www.python.org/downloads/
  → OR: winget install Python.Python.3.11"
}

$pyVer = & $pythonCmd --version
Write-Step "Found $pyVer"

# ─── 2. Install ANIMA AGENT ───
Write-Host "`n━━━ Step 2/5: Installing ANIMA AGENT v1.0 ━━━" -ForegroundColor White

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "  → Installing dependencies..." -ForegroundColor Cyan
& $pythonCmd -m pip install --quiet --upgrade pip 2>$null
& $pythonCmd -m pip install --quiet -e "."
Write-Step "ANIMA AGENT v1.0 — installed"
Write-Host "  ANIMASTELLAR TECHNOLOGY · github.com/animastellar/anima-os" -ForegroundColor Cyan

# ─── 3. Verify CLI ───
Write-Host "`n━━━ Step 3/5: Verifying Installation ━━━" -ForegroundColor White

$testResult = & $pythonCmd -m anima_agent.cli.main --version 2>&1
if ($LASTEXITCODE -eq 0) {
  Write-Step "CLI verified: anima command available"
} else {
  Write-Warn "Verification returned non-zero. Try: python -m anima_agent.cli.main status"
}

# ─── 4. Model Key Setup ───
Write-Host "`n━━━ Step 4/5: AI Model Setup ━━━" -ForegroundColor White
Write-Host @"

  ANIMA AGENT uses GLM-4-Flash as default (permanently FREE).
  To unlock all models, set these environment variables:

    `$env:GLM_API_KEY    # → open.bigmodel.cn (FREE)
    `$env:DEEPSEEK_API_KEY  # → platform.deepseek.com
    `$env:MOONSHOT_API_KEY  # → platform.moonshot.cn
    `$env:SILICONFLOW_API_KEY  # → siliconflow.cn

  Quick start (GLM-4-Flash, completely free):

    1. Register at https://open.bigmodel.cn
    2. Get your free API key
    3. Run: setx GLM_API_KEY "your-key-here"

"@

# ─── 5. Generate DID ───
Write-Host "━━━ Step 5/5: ANIMA Identity Setup ━━━" -ForegroundColor White
Write-Host @"

  Generate your ANIMA Identity (DID)?
  This creates an Ed25519 keypair that stays on your device.
  Only your public key is registered on the ANIMA network.

"@

$generate = Read-Host "  Generate DID now? [Y/n]"
if ($generate -eq "" -or $generate -match "^[Yy]") {
  $label = Read-Host "  Label (optional, e.g. 'home-windows')"
  if ($label) {
    & $pythonCmd -m anima_agent.cli.main identity generate --label $label
  } else {
    & $pythonCmd -m anima_agent.cli.main identity generate
  }
} else {
  Write-Step "Skipped. Run 'anima identity generate' anytime."
}

# ─── Done ───
Write-Host @"

  ╔══════════════════════════════════════════════╗
  ║       ANIMA AGENT v1.0 — Ready!             ║
  ╚══════════════════════════════════════════════╝

  Quick Start:
    anima status              System overview
    anima persona load nyx    Load STELLAR NYX personality
    anima dashboard           Launch desktop UI
    anima identity status     View your DID
    anima model list          Available AI models
    anima gov laws            ANIMA Governance (G001–G008)

  ANIMASTELLAR TECHNOLOGY · github.com/animastellar/anima-os

"@ -ForegroundColor Green
