# Changelog

所有 Anima Agent 的重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [v0.1.0] — 2026-07-10

### 状态：Pre-alpha / Developer Preview ⚠️

> 这是 Anima Agent 的第一个公开预览版本。功能不完整，API 可能随时变动。
> **不建议在生产环境使用。**

### 新增

- 🧬 **Anima Agent MVP 启动器** (`anima_mvp.py`) — 零依赖 Python 启动器，在任意 Python 3.10+ 环境即可体验 Anima Agent
- 🆔 **MeshIdentity DID** — 自动生成去中心化身份标识，支持 Ed25519 签名
- 🛡️ **MemGuard 记忆校验** — 核心文件 SHA-256 完整性校验
- 🧭 **Polaris 基线锚定** — Soul Baseline 提取与版本追踪
- 🧬 **LingOS Nyx v1** — 首个蒸馏 AI 人格操作系统（基于 Nyx）
- 🪟 **Windows 安装脚本** (`scripts/install.ps1`) — 一键安装，含 npm 镜像切换、Node.js 检测、OpenClaw 安装
- ⚙️ **国产模型路由配置** (`config/models.yaml`) — DeepSeek / Qwen / GLM / MiniMax / 豆包 开箱即用
- 📚 **中文文档** — README、QUICKSTART、FAQ、贡献指南
- 📄 **MIT 许可证** — 基于 OpenClaw（MIT）的合规分发

### 已知限制

- MVP 启动器不包含完整 OpenClaw 功能（需单独安装 `npm install -g openclaw`）
- 仅测试过 Windows 平台（Mac/Linux 安装脚本待添加）
- MeshIdentity DID 为链下版本（支持 Ed25519 生成但未上链）
- MemGuard 仅校验 SHA-256 签名，未实现真正的加密存储
- Polaris 仅做基线提取，漂移检测算法待实现
- Nyx v1 蒸馏人格为静态 System Prompt，非动态蒸馏模型

### 下一步计划 (v0.2.0)

- [ ] Mac/Linux 安装脚本 (`install.sh`)
- [ ] 灵元三件套一键安装 (`install_lingskills.ps1` 完善)
- [ ] 安装向导 UI（CLI 交互式）
- [ ] Nyx v1 人格 V0 内测（10 人）
- [ ] GitHub Actions CI 流水线

---

## 版本命名规则

| 阶段 | 版本号 | 含义 |
|------|--------|------|
| Pre-alpha | `v0.x` | 功能不完整，API 不稳定 |
| Alpha | `v0.x` | 核心功能可用，开始内测 |
| Beta | `v0.x` | 功能冻结，修 Bug，公测 |
| RC | `v0.x-rc` | 发布候选 |
| Stable | `v1.0.0` | 正式发布 |

---

🧬 Anima Agent · MIT License
