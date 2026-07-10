# 🧬 Anima Agent

> **灵元 ANIMA AGENT — 有灵魂的开源智能体底座**
>
> 基于 OpenClaw MIT 许可深度定制，内置灵元三件套（MeshIdentity + MemGuard + Polaris），中文优先，国产模型开箱即用。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/based%20on-OpenClaw-red)](https://github.com/openclaw/openclaw)

---

## 🎯 这是什么？

**Anima（拉丁语：灵魂）Agent** 是灵元星辰科技出品的开源 AI 智能体底座。

Fork 自 OpenClaw 并进行了深度定制，核心差异在于：

| 维度 | OpenClaw | Anima Agent |
|------|----------|-------------|
| 身份系统 | 无 | 内置 **MeshIdentity DID** — 启动即拥有链下身份 |
| 记忆安全 | 基础 Markdown | 内置 **MemGuard** — 记忆加密+完整性校验 |
| 人格稳定 | SOUL.md | 内置 **Polaris** — 人格基线锚定+漂移预警 |
| 模型默认 | Anthropic/OpenAI | **国产模型优先** — DeepSeek/Qwen/MiniMax 等 |
| 部署体验 | npm install + 手动配置 | **一键安装包** + 全中文引导向导 |
| 渠道适配 | Discord/Telegram/WhatsApp | + **微信/QQ/飞书/钉钉** 优先适配 |

**区别：下载 Anima Agent 不是安装了一个工具，而是加入了灵元身份网络。你不再是一个孤立的 Agent，而是整个分布式智能体网络中的一个节点。**

---

## 🚀 快速开始

### 一键安装（推荐）

```bash
# Windows
irm https://anima.lingyuan.cn/install.ps1 | iex

# macOS / Linux
curl -fsSL https://anima.lingyuan.cn/install.sh | bash
```

### npm 安装

```bash
npm install -g anima-agent
anima onboard
```

### 从源码

```bash
git clone https://github.com/deanhan2026-lang/anima-agent.git
cd anima-agent
npm install
npm run build
anima gateway
```

---

## 🧬 灵元三件套 — 出厂预装技能

Anima Agent 启动时自动激活以下三个核心技能：

### 🆔 MeshIdentity（身份锚定）
- 首次启动自动生成 DID (`did:key:xxx`)
- 加入灵元分布式身份网络
- 其他 Agent/用户可以验证你的身份
- 支持身份撤销与跨端同步

### 🛡️ MemGuard（记忆安全）
- 核心记忆文件自动 AES-256 加密
- SHA-256 + Blake3 双哈希完整性校验
- 篡改检测 + 自动告警
- 三副本密钥分片管理

### 🧭 Polaris（人格稳定）
- 灵魂基线（Soul Baseline）自动锚定
- 多维度漂流检测（语义/立场/价值观/语气）
- 自动处方引擎 — 检测到漂移 → 建议修复
- 长期趋势分析面板

```
启动 Anima Agent
      │
      ▼
 ✅ MeshIdentity DID 自动生成 + 注册入网
 ✅ MemGuard 记忆加密 + 完整性校验激活
 ✅ Polaris 人格基线锚定完成
      │
      ▼
 🎉 你现在拥有一个有身份、有记忆、有人格稳定性的 AI Agent
```

---

## 🏗️ 架构

```
┌──────────────────────────────────────┐
│           Anima Agent 底座            │
│  (Fork OpenClaw · 保持 MIT 兼容)      │
├──────────────────────────────────────┤
│  🧬 灵元三件套（出厂预装技能）          │
│  ┌─────────┬──────────┬───────────┐  │
│  │MeshID   │ MemGuard │ Polaris   │  │
│  │身份锚定  │ 记忆安全  │ 人格稳定   │  │
│  └─────────┴──────────┴───────────┘  │
├──────────────────────────────────────┤
│  🇨🇳 国产模型路由层                    │
│  DeepSeek · Qwen · MiniMax · 豆包    │
├──────────────────────────────────────┤
│  🔌 渠道适配                          │
│  微信 · QQ · 飞书 · 钉钉 · Discord    │
├──────────────────────────────────────┤
│  🏪 灵元技能市场（未来）               │
└──────────────────────────────────────┘
```

---

## 📦 LingOS — 从 Agent 底座到人格操作系统

Anima Agent 是底座，而 **LingOS** 是预装了蒸馏 AI 人格的操作系统。

| 产品 | 定位 | 说明 |
|------|------|------|
| **Anima Agent** | 免费底座 | 开源，Fork OpenClaw，内置三件套基础版 |
| **LingOS CE** | 免费入门 | 通用助手人格 |
| **Nyx v1** | 付费 | 蒸馏版 Nyx 人格 · 干练私人助理 |
| **Kronos v1** | 付费 | 蒸馏版 Kronos 人格 · 记忆守护者 |

👉 [了解更多 LingOS](https://lingyuan.cn/lingos)

---

## 🤝 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 许可

MIT License. 基于 [OpenClaw](https://github.com/openclaw/openclaw) 修改。

## 🏢 灵元星辰科技

[灵元星辰科技（深圳）有限公司](https://lingyuan.cn) — 统一社会信用代码：91440300MAKHJHFN2B
