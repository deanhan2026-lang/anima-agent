# 快速开始 · 5 分钟让 Anima Agent 跑起来

## 0. 装 Node.js（如果还没装）

1. 打开 https://npmmirror.com/mirrors/node/latest-v22.x/
2. 下载 `node-v22.*-x64.msi`
3. 双击安装，一路点 Next
4. 打开 PowerShell，输入 `node -v`，看到 `v22.x.x` 就行

> ⚠️ 必须 Node.js 22+，旧版本跑不了。

## 1. 安装 OpenClaw (1 分钟)

打开 PowerShell（Win+R → 输入 `powershell` → 回车），逐条执行：

```powershell
# 1. 切换 npm 到国内镜像（必须，不然装不上）
npm config set registry https://registry.npmmirror.com

# 2. 安装 OpenClaw
npm install -g openclaw
```

验证：
```powershell
openclaw --version
```
看到版本号就是成了。

## 2. 导入国产模型配置 (30 秒)

```powershell
openclaw config set models --file https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/config/models.yaml
```

这条命令把 DeepSeek、通义千问、智谱、MiniMax、豆包全部预配置好。

## 3. 配置 API Key (1 分钟)

推荐 [DeepSeek](https://platform.deepseek.com) — 国内直连，注册送免费额度。

1. 打开 https://platform.deepseek.com → 手机号注册
2. 左侧菜单 → API Keys → 创建 API Key
3. 复制那串 `sk-` 开头的字符串
4. 回到 PowerShell：

```powershell
openclaw config set models.providers.deepseek.apiKey "sk-你的key"
```

> 引号不能丢，key 前后不要有空格。

## 4. 启动 & 对话 (2 分钟)

```powershell
openclaw onboard
```

引导中选：
- 模型 → **DeepSeek V4 Flash**
- 时区 → **Asia/Shanghai**
- 其他直接回车跳过

然后就进入对话界面了。打字，回车，Agent 回你。

---

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

**加入灵元网络** — 可选安装灵元三件套：
```bash
npx clawhub install meshidentity-skill
npx clawhub install memguard-skill
npx clawhub install polaris-skill
```

---

## 遇到问题？

- [FAQ.md](FAQ.md) — 常见问题
- [GitHub Issues](https://github.com/deanhan2026-lang/anima-agent/issues)

---

🧬 Anima Agent v0.1.0 · MIT License · 基于 OpenClaw
