# 常见问题

## 安装

### "需要管理员权限" 怎么办？

Windows 安装脚本需要管理员权限来装 Node.js 和 OpenClaw。右键 PowerShell → 以管理员身份运行。

如果公司电脑没有管理员权限，可以手动安装：

```bash
# 1. 先装 Node.js 22+（从 nodejs.org 下载安装包，不需要管理员）
# 2. 再装 OpenClaw
npm install -g openclaw
# 3. 导入模型配置
openclaw config set models --file https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/config/models.yaml
```

### Node.js 版本不对？

OpenClaw 需要 Node.js 22.19+ / 23.11+ / 24+。

```bash
node -v   # 检查当前版本
```

版本不够？去 [nodejs.org](https://nodejs.org) 下最新 LTS 版（22.x）。

### 安装脚本报 "无法连接到 raw.githubusercontent.com"？

这是 DNS 或网络问题。换 GitHub 镜像：

```powershell
# 方法 1: 用 jsdelivr CDN
irm https://cdn.jsdelivr.net/gh/deanhan2026-lang/anima-agent@master/scripts/install.ps1 | iex

# 方法 2: 先下载再本地运行
# 浏览器打开 https://github.com/deanhan2026-lang/anima-agent/blob/master/scripts/install.ps1
# 点 Raw → 另存为 install.ps1 → PowerShell 运行
powershell -ExecutionPolicy Bypass -File install.ps1
```

### npm install -g openclaw 很慢？

换国内镜像：

```bash
npm config set registry https://registry.npmmirror.com
npm install -g openclaw
```

---

## API Key

### 用哪个模型最好？

**推荐 DeepSeek V4 Flash**，三个理由：
1. 免费额度（注册即送，够个人用户用很久）
2. 推理能力强，支持思考模式
3. 国内直连，不用翻墙

[platform.deepseek.com](https://platform.deepseek.com) → 注册 → API Keys → 创建

### DeepSeek API Key 怎么设置？

```bash
openclaw config set models.providers.deepseek.apiKey "sk-你的key"
openclaw config set models.mode merge
```

设置完重启 OpenClaw 或运行 `openclaw onboard` 选择 DeepSeek 模型。

### 怎么切换模型？

```bash
# 列出所有可用模型
openclaw config get models

# 在 onboard 中选择
openclaw onboard

# 或在对话中用 natural language 指定
# "用 DeepSeek V4 Flash 帮我分析这个文件"
```

### Qwen / GLM / 豆包的 Key 在哪申请？

| 模型 | 申请地址 | 是否免费 |
|------|---------|---------|
| Qwen Turbo | [dashscope.aliyun.com](https://dashscope.aliyun.com) | ✅ 百万 Token 免费额度 |
| GLM-4.6 | [open.bigmodel.cn](https://open.bigmodel.cn) | ❌ 需充值 |
| MiniMax M1 | [platform.minimax.chat](https://platform.minimax.chat) | ❌ 需充值 |
| 豆包 | [console.volcengine.com](https://console.volcengine.com) | ❌ 需充值 |

### 配置了 API Key 还是报错 "401 Unauthorized"？

检查三件事：

```bash
# 1. Key 是否正确设置
openclaw config get models.providers.deepseek.apiKey

# 2. Key 格式是否正确（应该是 sk- 开头）
# 3. 余额是否用完（登录厂商后台查看）
```

---

## 与 OpenClaw 的关系

### 装了 Anima Agent，还需要装 OpenClaw 吗？

Anima Agent 的安装脚本会自动装 OpenClaw。两者关系：

- **OpenClaw** 是引擎（MIT 许可，社区维护）
- **Anima Agent** 是发行版（预配置 + 中文引导 + 可选灵魂插件）

你可以随时用 `openclaw` 命令操作底层，Anima 不锁任何功能。

### Anima Agent 和 OpenClaw 的配置冲突吗？

不冲突。Anima 只是往 OpenClaw 的配置里加了国产模型 provider。你自己的配置不受影响。

### OpenClaw 升级了怎么办？

```bash
npm update -g openclaw
```

Anima 的模型配置不会丢失。OpenClaw 是 MIT 许可的独立项目，Anima 不会 fork 核心代码。

---

## 使用

### onboard 是什么？

`openclaw onboard` 是 OpenClaw 的首次设置向导。会引导你：
1. 选择默认模型
2. 配置消息通道（QQ/微信/飞书/Telegram 等）
3. 设置时区、语言

选中文 + DeepSeek V4 Flash 就行。

### Agent 回复很慢？

检查当前模型：
```bash
openclaw config get models
```

如果用的是收费模型（国内直连一般 2-5 秒），如果特别慢（>30 秒），可能是：
- 免费模型高峰期排队
- 网络问题（试试换 DeepSeek 或 Qwen Turbo）

### 怎么让 Agent 在 QQ/微信上回我？

需要配置对应通道。具体步骤取决于通道类型。

**QQ（QQ开放平台）：**
```bash
openclaw config set channels.qqbot.appId "your-app-id"
openclaw config set channels.qqbot.token "your-token"
```

**企业微信：**
```bash
openclaw config set channels.wechat.corpId "your-corp-id"
openclaw config set channels.wechat.token "your-token"
```

详细配置见 [OpenClaw 通道文档](https://docs.openclaw.ai/channels)。

### Agent 能操作我的文件吗？

能。OpenClaw Agent 能读写文件、执行命令、操作浏览器。这是它的核心能力之一。

**安全建议：**
- 不要在对安全敏感的生产环境直接运行
- 可以限制 Agent 的工作目录
- 重要文件先备份

---

## 安全 & 隐私

### 我的数据会传到哪？

- API 请求传到模型厂商服务器（DeepSeek / Qwen 等）
- 不会传到 Anima 或灵元星辰的服务器
- 对话记录存储在本地（`%USERPROFILE%\.openclaw\state\`）

### 灵元三件套（DID）会收集我的隐私吗？

不会。DID 只生成公开的公钥（用于身份验证），你的对话数据、记忆文件、个人信息完全存储在本地，不上传、不上链。

---

## 其他

### 能在 Linux 服务器上部署吗？

可以。OpenClaw 支持 Linux。安装后配置为后台服务即可。

```bash
# 安装
curl -fsSL https://openclaw.ai/install.sh | bash
# 配置
openclaw config set models --file https://raw.githubusercontent.com/deanhan2026-lang/anima-agent/main/config/models.yaml
# 设为系统服务
openclaw gateway install-service
```

### 怎么卸载？

```bash
npm uninstall -g openclaw
# 删除配置（可选）
rm -rf ~/.openclaw ~/.anima-agent
```

### 有其他问题？

- [GitHub Issues](https://github.com/deanhan2026-lang/anima-agent/issues)
- [OpenClaw 官方文档](https://docs.openclaw.ai)

---

🖤 Anima Agent v0.1.0 · 灵元星辰科技
