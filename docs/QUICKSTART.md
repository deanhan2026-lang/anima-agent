# 快速开始 · 5 分钟让 Anima Agent 跑起来

## 1. 安装 (1 分钟)

**Windows (推荐):**
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/scripts/install.ps1 | iex"
```

**Mac / Linux:**
```bash
# 先装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash
# 再导入模型配置
openclaw config set models --file https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/config/models.yaml
```

安装完成后会看到 `Anima Agent is ready.`

## 2. 配置 API Key (1 分钟)

推荐用 DeepSeek — 注册就送免费额度，国内直连。

1. 打开 [platform.deepseek.com](https://platform.deepseek.com)
2. 注册 → API Keys → 创建 Key
3. 复制 Key，运行：

```bash
openclaw config set models.providers.deepseek.apiKey "sk-你的key"
```

> 也可以用通义千问、智谱、MiniMax、豆包 — 所有国产模型已预配置。

## 3. 启动 & 对话 (3 分钟)

```bash
openclaw onboard
```

跟随引导完成首次设置（选模型、配通道），然后直接在终端跟 Agent 对话。

```
你: 帮我把今天的工作排一下优先级
Agent: [分析中...] 好的，根据你的日历和待办...
```

## 完成 🎉

你的 Anima Agent 已经跑起来了。

---

## 接下来可以做什么

**加通道** — 让 Agent 在 QQ/微信/飞书上也能回你：
```bash
openclaw config set channels.wechat.token "your-token"
```

**装技能** — 从社区安装更多能力：
```bash
npx clawhub install <skill-name>
```

**加入灵元网络** — 可选安装灵元三件套，让 Agent 拥有唯一身份：
```bash
npx clawhub install meshidentity-skill
npx clawhub install memguard-skill
npx clawhub install polaris-skill
```

---

## 遇到问题？

- GitHub Issues: [github.com/deanhan2026-lang/anima-agent/issues](https://github.com/deanhan2026-lang/anima-agent/issues)
- OpenClaw 官方文档: [docs.openclaw.ai](https://docs.openclaw.ai)

---

🧬 Anima Agent v0.1.0 · MIT License · 基于 OpenClaw
