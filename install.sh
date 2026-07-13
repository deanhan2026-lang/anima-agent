#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  ANIMA AGENT v1.0 — One-Click Installer (macOS / Linux)
#  Copyright (c) 2026 ANIMASTELLAR TECHNOLOGY
#  Licensed under the MIT License
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ─── Colors ───
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; WHITE='\033[1;37m'; BOLD='\033[1m'; NC='\033[0m'

# ─── Branded Banner ───
banner() {
  clear 2>/dev/null || true
  echo ""
  echo -e "${CYAN}${BOLD}   █████╗ ███╗   ██╗██╗███╗   ███╗ █████╗${NC}"
  echo -e "${CYAN}${BOLD}  ██╔══██╗████╗  ██║██║████╗ ████║██╔══██╗${NC}"
  echo -e "${CYAN}${BOLD}  ███████║██╔██╗ ██║██║██╔████╔██║███████║${NC}"
  echo -e "${CYAN}${BOLD}  ██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══██║${NC}"
  echo -e "${CYAN}${BOLD}  ██║  ██║██║ ╚████║██║██║ ╚═╝ ██║██║  ██║${NC}"
  echo -e "${CYAN}${BOLD}  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝${NC}"
  echo ""
  echo -e "  ${WHITE}AI Identity Sovereign Runtime${NC}"
  echo -e "  ${CYAN}v1.0${NC}  ·  ${YELLOW}ANIMASTELLAR TECHNOLOGY${NC}"
  echo -e "  ${CYAN}github.com/animastellar/anima-os${NC}"
  echo ""
}

info()  { echo -e "${GREEN}  [✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}  [!]${NC} $1"; }
error() { echo -e "${RED}  [✗]${NC} $1"; exit 1; }

# ─── License Agreement ───
show_license() {
  banner
  echo -e "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "  ${BOLD}ANIMA AGENT — MIT License${NC}"
  echo -e "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  echo -e "  Copyright (c) 2026 ${CYAN}ANIMASTELLAR TECHNOLOGY${NC}"
  echo ""
  echo -e "  Permission is hereby granted, free of charge, to any person"
  echo -e "  obtaining a copy of this software, to deal in the Software"
  echo -e "  without restriction, including the rights to use, copy,"
  echo -e "  modify, merge, publish, and distribute."
  echo ""
  echo -e "  THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF"
  echo -e "  ANY KIND. See LICENSE for full terms."
  echo ""
  echo -e "  ${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  read -p "  Accept the license terms? [Y/n]: " -r ACCEPT
  ACCEPT=${ACCEPT:-Y}
  if [[ ! $ACCEPT =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "  ${RED}Installation cancelled.${NC}"
    exit 1
  fi
  info "License accepted."
}

show_license

# ─── 1. Detect Python3 ───
echo ""
echo -e "${WHITE}━━━ Step 1/5: Python Environment ━━━${NC}"

PYTHON=""
for cmd in python3 python; do
  if command -v $cmd &>/dev/null && $cmd --version &>/dev/null; then
    PYTHON=$cmd
    break
  fi
done

if [ -z "$PYTHON" ]; then
  error "Python 3.10+ required but not found.
  macOS:  brew install python@3.11
  Ubuntu: sudo apt install python3 python3-pip"
fi

PY_VER=$($PYTHON --version 2>&1 | awk '{print $2}')
info "Found $PYTHON ($PY_VER)"

# ─── 2. Install ANIMA AGENT ───
echo ""
echo -e "${WHITE}━━━ Step 2/5: Installing ANIMA AGENT v1.0 ━━━${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

$PYTHON -m pip install --quiet --upgrade pip 2>/dev/null || true
echo -e "  ${CYAN}→${NC} Installing dependencies (pynacl, cryptography, fastapi, rich, click...)"
$PYTHON -m pip install --quiet -e "." 2>&1 | tail -1
info "ANIMA AGENT v1.0 — installed"
echo -e "  ${CYAN}  ANIMASTELLAR TECHNOLOGY · github.com/animastellar/anima-os${NC}"

# ─── 3. Verify CLI ───
echo ""
echo -e "${WHITE}━━━ Step 3/5: Verifying Installation ━━━${NC}"

if $PYTHON -m anima_agent.cli.main --version &>/dev/null; then
  info "CLI verified: anima command available"
else
  ANIMA_BIN="$($PYTHON -c "import site; print(site.USER_BASE)")/bin/anima" 2>/dev/null || true
  if [ -n "$ANIMA_BIN" ] && [ -f "$ANIMA_BIN" ]; then
    info "CLI installed at: $ANIMA_BIN"
  else
    warn "CLI binary path not auto-detected. Use: python3 -m anima_agent.cli.main"
  fi
fi

# ─── 4. Model Key Setup ───
echo ""
echo -e "${WHITE}━━━ Step 4/5: AI Model Setup ━━━${NC}"
echo ""
echo -e "  ANIMA AGENT uses ${GREEN}GLM-4-Flash${NC} as default (permanently FREE)."
echo -e "  To unlock all models, set these environment variables:"
echo ""
echo -e "    ${CYAN}export GLM_API_KEY${NC}         # → open.bigmodel.cn (FREE)"
echo -e "    ${CYAN}export DEEPSEEK_API_KEY${NC}    # → platform.deepseek.com"
echo -e "    ${CYAN}export MOONSHOT_API_KEY${NC}    # → platform.moonshot.cn"
echo -e "    ${CYAN}export SILICONFLOW_API_KEY${NC} # → siliconflow.cn"
echo ""
echo -e "  Quick start (GLM-4-Flash, completely free):"
echo ""
echo -e "    1. Register at ${YELLOW}https://open.bigmodel.cn${NC}"
echo -e "    2. Get your free API key"
echo -e "    3. Run: ${CYAN}export GLM_API_KEY='your-key-here'${NC}"
echo ""

# ─── 5. Generate DID ───
echo -e "${WHITE}━━━ Step 5/5: ANIMA Identity Setup ━━━${NC}"
echo ""
echo -e "  ${BOLD}Generate your ANIMA Identity (DID)?${NC}"
echo -e "  This creates an Ed25519 keypair that stays on your device."
echo -e "  Only your public key is registered on the ANIMA network."
echo ""
read -p "  Generate DID now? [Y/n]: " -r REPLY
REPLY=${REPLY:-Y}

if [[ $REPLY =~ ^[Yy]$ ]]; then
  read -p "  Label (optional, e.g. 'home-mac'): " -r LABEL
  $PYTHON -m anima_agent.cli.main identity generate ${LABEL:+--label "$LABEL"}
else
  info "Skipped. Run 'anima identity generate' anytime."
fi

# ─── Done ───
echo ""
echo -e "${GREEN}${BOLD}  ╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}  ║     ANIMA AGENT v1.0 — Ready!           ║${NC}"
echo -e "${GREEN}${BOLD}  ╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Quick Start:${NC}"
echo -e "    ${CYAN}anima status${NC}              System overview"
echo -e "    ${CYAN}anima persona load nyx${NC}     Load STELLAR NYX personality"
echo -e "    ${CYAN}anima dashboard${NC}           Launch desktop UI"
echo -e "    ${CYAN}anima identity status${NC}     View your DID"
echo -e "    ${CYAN}anima model list${NC}           Available AI models"
echo -e "    ${CYAN}anima gov laws${NC}            ANIMA Governance (G001–G008)"
echo ""
echo -e "  ${YELLOW}ANIMASTELLAR TECHNOLOGY${NC} · github.com/animastellar/anima-os"
echo ""
