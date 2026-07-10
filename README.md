# 🧬 Anima Agent — 灵元智能体底座

> 基于 [OpenClaw](https://github.com/openclaw/openclaw) (MIT 许可) 的国产 AI Agent 发行版。
>
> 开箱即用 · 国产模型 · 中文优先

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Based on OpenClaw](https://img.shields.io/badge/based_on-OpenClaw-ff6b6b)](https://github.com/openclaw/openclaw)

---

## 这是什么

Anima Agent 是 OpenClaw 的国内发行版。我们做了三件事：

1. **国产模型开箱可用** — DeepSeek / Qwen / GLM / MiniMax / 豆包，选模型即可用
2. **中文优先** — 安装引导、文档、社区全中文
3. **灵魂插件** — 可选安装灵元三件套（身份锚定 / 记忆加密 / 人格稳定）

### 与 OpenClaw 的关系

| | OpenClaw | Anima Agent |
|---|---|---|
| 核心引擎 | OpenClaw | 相同（持续合并上游） |
| 模型预置 | OpenAI / Claude 等 | **+ DeepSeek / Qwen / GLM / 豆包** |
| 安装引导 | 英文 CLI | **中文 CLI** |
| 默认语言 | English | **中文** |
| 灵元三件套 | 手动安装 | 一键安装 |
| 定价 | 免费 | **免费** |
| 许可 | MIT | MIT |

**Anima Agent 永远免费。** 底座不应该收费。

---

## 快速开始

### 安装 (Windows / Mac / Linux)

**Windows (PowerShell 管理员模式):**
```powershell
irm https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/scripts/install.ps1 | iex
```

**Mac / Linux:**
```bash
# 1. 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 用 Anima 模型配置
openclaw config set models --file https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/config/models.yaml
```

### 设置 API Key

推荐 [DeepSeek](https://platform.deepseek.com) — 注册送免费额度。

```bash
openclaw config set models.providers.deepseek.apiKey "sk-your-key-here"
```

支持的模型列表见下方。

### 启动

```bash
openclaw onboard
```

跟随中文引导完成设置，然后直接在本窗口开始对话。

---

## 支持的国产模型

| 模型 | 厂商 | 免费额度 | 特点 |
|------|------|---------|------|
| DeepSeek V4 Flash | DeepSeek | ✅ 有 | 性价比最高，推荐首选 |
| DeepSeek V4 Pro | DeepSeek | ❌ | 更强推理能力 |
| Qwen Turbo | 阿里 | ✅ 有 | 中文理解好 |
| Qwen3 235B | 阿里 | ❌ | 旗舰模型 |
| GLM-4.6 | 智谱 | ❌ | 多模态 |
| MiniMax M1 | MiniMax | ❌ | 100万上下文 |
| 豆包 1.5 Pro | 字节 | ❌ | 抖音生态集成 |

> 也在 `config/models.yaml` 中预置了 OpenAI / Claude 等国际模型，有 API Key 就能用。

---

## 进阶：灵元三件套

可选安装，为你的 Agent 赋予灵魂：

| 组件 | 功能 | 安装 |
|------|------|------|
| **MeshIdentity** | DID 分布式身份 | `npx clawhub install meshidentity-skill` |
| **MemGuard** | 记忆加密与完整性保护 | `npx clawhub install memguard-skill` |
| **Polaris** | AI 人格防漂移锚点 | `npx clawhub install polaris-skill` |

安装后你的 Agent 拥有：唯一身份 + 加密记忆 + 稳定人格。

---

## 项目结构

```
anima-agent/
├── scripts/
│   └── install.ps1        # Windows 一键安装
├── config/
│   └── models.yaml         # 国产模型路由配置
├── skills/
│   ├── meshidentity-skill/ # DID 身份技能
│   ├── memguard-skill/     # 记忆安全技能
│   └── polaris-skill/      # 人格稳定技能
├── docs/
│   ├── README.md           # 本文件
│   ├── QUICKSTART.md       # 5 分钟上手指南
│   └── FAQ.md              # 常见问题
└── lingos/                 # LingOS 人格操作系统
    └── nyx-v1/             # Nyx v1 蒸馏人格
```

---

## 常见问题

**Q: 和 OpenClaw 有什么区别？**
A: 代码层面完全兼容。Anima Agent 是 OpenClaw 的"国内发行版"——加了国产模型预置、中文引导、可选灵魂插件。

**Q: 会收费吗？**
A: Anima Agent 底座永远免费（MIT 许可）。未来可能推出的 LingOS（蒸馏人格包）会收费，但底座不会。

**Q: 需要科学上网吗？**
A: 不需要。所有预置的国内模型 API 均可直连访问。

**Q: 可以在公司用吗？**
A: MIT 许可，自由使用。源代码归属 OpenClaw 社区，Anima Agent 作为发行版不限制使用。

---

## 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) — MIT 许可的 AI Agent 框架，315K+ GitHub Stars
- [DeepSeek](https://deepseek.com) — 高性能免费国产模型
- 所有在国内做 AI 基础设施的人

---

🧬 **灵元星辰科技 (深圳)** | [github.com/deanhan2026-lang/anima-agent](https://github.com/deanhan2026-lang/anima-agent)
