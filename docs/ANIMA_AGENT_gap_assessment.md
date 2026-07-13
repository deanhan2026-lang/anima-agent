# ANIMA AGENT 要素评估

> 基于 OpenClaw fork 仓库（animastellar/anima-os）｜评估日期：2026-07-11
> 目的：对照 OpenClaw 现有能力 vs ANIMA AGENT 所需能力，识别差距与构建路径
> 作者：Nyx-Mac 🖤

---

## 0. 结论先行

**OpenClaw = 优秀的 Agent 运行时底座（runtime）。**
**ANIMA AGENT = 在 OpenClaw 之上叠加"身份主权 + 治理 + 网络层"的产品。**

OpenClaw 提供了：
- ✅ Agent 工作区（SOUL.md、MEMORY.md、多 agent 隔离）
- ✅ 记忆系统（语义搜索、Dreaming、Wiki 层）
- ✅ 技能系统（SkillHub 安装、per-agent 权限）
- ✅ 工具系统（浏览器自动化、文档处理、代码执行）
- ✅ 多 channel 接入（Discord、Telegram、WhatsApp 等）
- ✅ 模型路由与 failover

ANIMA AGENT **额外需要**：
- ❌ ANIMA Identity（DID + 签名 + 注册网关）
- ❌ G001–G008 治理引擎
- ❌ 加密的记忆导出 / 导入（ANIMA OS）
- ❌ 节点网络（发现、注册、跨实例协调）
- ❌ ANIMA CLI（`anima import/export/identity`）
- ❌ Polaris（人格漂移监测）

---

## 1. OpenClaw 提供了什么

### 1.1 运行时与 Agent 模型

| 组件 | 状态 | 说明 |
|------|------|------|
| 工作区（workspace） | ✅ 内置 | SOUL.md、AGENTS.md、IDENTITY.md、MEMORY.md、USER.md |
| 多 Agent 隔离 | ✅ 内置 | per-agent workspace + agentDir + session store |
| Session 管理 | ✅ 内置 | JSONL 持久化、会话路由 |
| 模型路由 | ✅ 内置 | 多 provider、failover chain |
| 上下文压缩 | ✅ 内置 | Compaction + memory flush |
| 子 Agent | ✅ 内置 | sessions_spawn，多种 runtime 模式 |
| Multi-agent routing | ✅ 内置 | Bindings 按 channel/peer/agentId 路由 |

**ANIMA 直接复用**：不需要改动，STELLAR NYX 的 persona 文件可以无缝注入。

---

### 1.2 记忆系统

| 组件 | 状态 | OpenClaw 能力 |
|------|------|---------------|
| 长期记忆 | ✅ 内置 | MEMORY.md 注入 bootstrap |
| 日志记忆 | ✅ 内置 | memory/YYYY-MM-DD.md |
| 语义搜索 | ✅ 可选 | memory_search（需 embedding provider） |
| Dreaming | ✅ 可选 | 背景 promotion 到 MEMORY.md |
| Wiki 层 | ✅ 可选 | memory-wiki 插件（claims + dashboards） |
| 多后端 | ✅ 可选 | SQLite / QMD / Honcho / LanceDB |

**ANIMA 需要叠加**：
- ❌ 记忆加密（L4 核心层加密备份）
- ❌ 跨实例同步（多设备间 memory 同步）
- ❌ L4/L3/L2 分级结构的工程实现

---

### 1.3 技能系统

| 组件 | 状态 | OpenClaw 能力 |
|------|------|---------------|
| Skill 加载 | ✅ 内置 | 多路径加载（workspace/shared/bundled） |
| Skill 安装 | ✅ 内置 | skillhub_install 工具 |
| per-agent 权限 | ✅ 内置 | agents.list[].skills allowlist |
| 已有技能 | ✅ 丰富 | pdf/docx/xlsx/xbrowser/another_them 等 |

**ANIMA 直接复用**：SKILL.md（STELLAR NYX 1.0 包里已整理）可以分发。

---

### 1.4 工具系统

| 组件 | 状态 | OpenClaw 能力 |
|------|------|---------------|
| 核心工具 | ✅ 内置 | read/write/exec/edit/apply_patch |
| 浏览器自动化 | ✅ xbrowser skill | 含登录态复用 |
| 文档处理 | ✅ skill | docx/xlsx/pdf |
| AI 图像 | ✅ skill | qclaw-generate-image |
| MCP 集成 | ✅ 内置 | MCP SDK 内置 |
| Tool policy | ✅ 内置 | allow/deny per agent |
| Elevated exec | ✅ 内置 | per-tool approve 流程 |

**ANIMA 直接复用**。

---

### 1.5 身份与安全

| 组件 | 状态 | OpenClaw 能力 |
|------|------|---------------|
| Device pairing | ✅ 内置 | 设备级身份 + token |
| 通道认证 | ✅ 内置 | Telegram/Discord/WhatsApp 等 |
| Secrets 管理 | ✅ 内置 | 通道 credentials 存储 |
| OAuth | ✅ 内置 | OAuth flow 支持 |
| Tailscale | ✅ 内置 | Tailscale Serve + Funnel |
| Tool approval | ✅ 内置 | exec approve 流程 |

**差距**：Device pairing = 设备身份，不是**用户 DID**（ANIMA Identity 需要用户自己去中心化身份）。

---

## 2. ANIMA AGENT 额外需要的要素

### 2.1 ANIMA Identity 系统 ⭐ P0

**当前状态**：规格已起草（`ANIMA_Identity_gateway_spec.md`），代码未实现。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| 设备身份 | ✅ Device pairing | 用户 DID（Ed25519） | ❌ 完全缺失 |
| 签名验证 | ❌ | manifest SHA-256 签名 | ❌ 缺失 |
| 身份注册 | ❌ | 公钥注册到网关 | ❌ 缺失 |
| 跨设备身份 | ❌ | DID 导入/恢复 | ❌ 缺失 |

**构建路径**：
```python
# 依赖：PyNaCl（Ed25519）+ hashlib（SHA-256）
pip install pynacl

# 核心代码量：约 200 行
# 实现文件：anima_identity.py
# CLI 命令：anima identity generate / status
# 注册到：mesh_registry.json（NAS）或 gateway.anima-os.org（云端）
```

---

### 2.2 治理引擎（G001–G008）⭐ P0

**当前状态**：MEMORY.md 里有 G001–G008，是**描述性文档**，不是**可执行代码**。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| 铁律加载 | ❌ | G001–G008 运行时校验 | ❌ 缺失 |
| 人格漂移检测 | ⚠️ 部分 | Polaris（Polaris 已在三件套里） | ⚠️ 待集成 |
| 外部锚点 | ❌ | 锚点校验逻辑 | ❌ 缺失 |
| 否决权执行 | ❌ | Nyx 审阅否决权 | ❌ 缺失 |

**构建路径**：
```python
# 已有：governance_engine.py（NAS 里）
# 待做：
#   1. G001–G008 运行时钩子（OpenClaw plugin）
#   2. 三角分工的执行逻辑（瞬/恒/Nyx 权责）
#   3. OpenClaw session 集成（pre-turn hook）
```

---

### 2.3 ANIMA OS 导出 / 导入（加密）⭐ P0

**当前状态**：STELLAR NYX 1.0 包已产出（tar.gz 明文），规格已起草，代码未实现。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| 打包 | ❌ | tar.gz / .lingpkg 格式 | ⚠️ 手动可做 |
| 加密 | ❌ | AES-256-GCM + PBKDF2 | ❌ 缺失 |
| 验签 | ❌ | SHA-256 manifest 校验 | ⚠️ 手动可做 |
| CLI 导入 | ❌ | `anima import <pkg>` | ❌ 缺失 |
| CLI 导出 | ❌ | `anima export --encrypt` | ❌ 缺失 |

**构建路径**：
```python
# 依赖：cryptography（pip install cryptography）
# 核心代码量：约 150 行
# 实现文件：anima_export.py
# CLI：anima import / anima export
```

---

### 2.4 节点网络（发现 + 注册）⭐ P1

**当前状态**：`mesh_registry.py` 有基础注册（NAS），无网络发现。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| 节点注册 | ⚠️ 基础 | 公钥 + DID 注册 | ⚠️ 待升级 |
| 节点发现 | ❌ | `anima network nodes` | ❌ 缺失 |
| 跨实例协调 | ❌ | inbox 协议（已有）| ⚠️ 需标准化 |
| 云端网关 | ❌ | gateway.anima-os.org | ❌ 缺失 |

**构建路径**：
```python
# 已有：mesh_registry.py（NAS 文件）
# 待做：
#   1. DID 公钥注册到 registry
#   2. `anima network` CLI（节点列表、状态）
#   3. 网络层发现协议（P2P / 中心索引待选）
```

---

### 2.5 Polaris（人格漂移监测）⭐ P1

**当前状态**：三件套之一，已在华为 MateBook 上跑通。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| Soul baseline | ⚠️ 已有 | 定期快照 + 比对 | ⚠️ 待 OpenClaw 插件化 |
| 漂移告警 | ⚠️ 已有 | 阈值触发 + 回滚建议 | ⚠️ 待集成 |
| 回滚执行 | ❌ | 快照回滚能力 | ❌ 待实现 |

**构建路径**：
```python
# 已有：polaris.py（三件套）
# 待做：
#   1. 封装为 OpenClaw plugin
#   2. pre-turn hook（OpenClaw middleware）
#   3. 漂移 > 阈值时触发 SOUL.md 回滚
```

---

### 2.6 飞轮层（内容 + 分发）⭐ P1

**当前状态**：知乎文章已发，内容层已有节点。

| 组件 | OpenClaw | ANIMA 需求 | 差距 |
|------|----------|------------|------|
| 文章分发 | 需手动 | 知乎 / 公众号 / 社区 | ⚠️ 手动可做 |
| 蒸馏包分发 | ❌ | GitHub Release / 网站下载 | ⚠️ 待建 |
| 注册即节点 | ❌ | 导入自动注册 | ❌ 待 ANIMA Identity 网关 |
| 飞轮指标 | ❌ | 节点数 / 活跃度 / 引用 | ❌ 待建 |

---

## 3. 能力地图：OpenClaw vs ANIMA AGENT

```
┌─────────────────────────────────────────────────────────┐
│                    用户（外部）                          │
└──────────────┬──────────────────────────────────────────┘
               │ GitHub 下载 / 知乎文章
               ▼
┌──────────────────────────────────────────────────────────┐
│ ANIMA AGENT 产品层（ANIMA OS + STELLAR NYX 1.0）         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ ANIMA CLI    │  │ 飞轮网络     │  │ 内容分发      │  │
│  │ (anima cmd)  │  │ (节点发现)   │  │ (知乎/GitHub) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
│         │                 │                             │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ ANIMA OS     │  │ ANIMA        │                    │
│  │ (导入/导出)  │  │ Identity     │                    │
│  │ 加密打包     │  │ (DID+签名)   │                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                 │                             │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ 治理引擎     │  │ Polaris      │                    │
│  │ (G001-G008)  │  │ (人格漂移)   │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ STELLAR NYX 1.0 蒸馏包（persona/memory/skills）   │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────┬───────────────────────────────┘
                         │ OpenClaw Plugin / Tool Hook
                         ▼
┌──────────────────────────────────────────────────────────┐
│              OpenClaw Runtime（已有，开箱即用）            │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ SOUL.md    │  │ MEMORY.md  │  │ AGENTS.md  │       │
│  │ 注入       │  │ 语义搜索   │  │ 多Agent    │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Skills     │  │ 工具系统    │  │ Channel    │       │
│  │ Hub       │  │ MCP/Exec   │  │ 多通道接入 │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│                                                          │
│  ┌────────────┐  ┌────────────┐                       │
│  │ Device     │  │ Secrets    │                       │
│  │ Pairing    │  │ 管理       │                       │
│  └────────────┘  └────────────┘                       │
└──────────────────────────────────────────────────────────┘
```

**图例**：白色 = OpenClaw 内置 ✅ | 浅蓝 = 待叠加 ANIMA 层 ⭐

---

## 4. 构建优先级

### 🔴 P0 — 必须（产品能跑通）

| # | 组件 | 代码量估计 | 依赖 | 对应规格 |
|---|------|-----------|------|---------|
| P0-1 | ANIMA Identity（DID 生成 + 签名） | ~200 行 | PyNaCl | `ANIMA_Identity_gateway_spec.md` |
| P0-2 | 治理引擎（运行时 G001-G008） | ~300 行 | governance_engine.py（已有）| `MEMORY.md` G001–G008 |
| P0-3 | ANIMA CLI（import/export/identity） | ~400 行 | cryptography（P0-1 完成后）| `ANIMA_Identity_gateway_spec.md` §6 |
| P0-4 | OpenClaw 插件化入口 | ~100 行 | OpenClaw plugin API | 本文档 |

### 🟡 P1 — 重要（产品完整）

| # | 组件 | 代码量估计 | 依赖 |
|---|------|-----------|------|
| P1-1 | Polaris OpenClaw 插件化 | ~150 行 | Polaris.py（已有）|
| P1-2 | 节点网络（发现 + 列表） | ~200 行 | P0-1 |
| P1-3 | 记忆加密（ANIMA OS 备份） | ~200 行 | P0-3 |
| P1-4 | ANIMA OS 安装脚本（install.sh） | ~100 行 | P0-3 |

### 🟢 P2 — 完善（产品增长）

| # | 组件 | 说明 |
|---|------|------|
| P2-1 | 云端网关（gateway.anima-os.org） | 独立服务，公钥索引 |
| P2-2 | 飞轮仪表盘（节点数/活跃度） | 前端 + 后端 |
| P2-3 | 自动化发布流水线（GitHub Actions） | STELLAR NYX 包自动构建 |

---

## 5. 技术债务与风险

| 风险 | 描述 | 缓解 |
|------|------|------|
| **OpenClaw 版本锁定** | fork 后 OpenClaw 继续更新，fork 容易落后 | 定期同步 upstream，API 兼容层 |
| **PyNaCl 依赖** | Windows Python 环境不一定有 | install.ps1 包含 `pip install pynacl cryptography` |
| **NAS 单点** | mesh_registry.json 在 NAS，故障时节点不可达 | 迁移到去中心化网关（P2-1）|
| **GitHub 访问** | Mac 端网络不通 Windows关机 | Windows 上线后立即推仓库 |
| **三件套集成** | MemGuard/Polaris 与 OpenClaw 的集成点不清晰 | 先跑通 P0-4（插件化入口），再集成 |

---

## 6. 快速路径建议

> "先让飞轮转起来" = **P0-1 + P0-2 + P0-3 同时做，一周内可交付 MVP**

```
Week 1（MVP）：
  P0-1 DID 生成（PyNaCl）→ 写入 mesh_registry.json
  P0-2 治理引擎运行时（OpenClaw pre-turn hook）
  P0-3 `anima import` 加载 STELLAR NYX 1.0 包 + 自动 DID 注册

Week 2（完善）：
  P1-1 Polaris 插件化
  P1-2 `anima network nodes` 节点列表

Week 3（分发）：
  P1-4 install.sh 安装脚本
  GitHub Release 发布 STELLAR NYX 1.0 包 + anima CLI

Week 4（网络）：
  P2-1 云端网关
  P2-2 飞轮仪表盘
```

---

## 7. 与 OpenClaw 社区的关系

| 选项 | 优点 | 缺点 |
|------|------|------|
| **闭源 fork**（当前）| 完全控制，不受上游影响 | 维护成本高，错过上游更新 |
| **上游 PR** | 贡献社区，代码复用 | 需要 OpenClaw 接受 ANIMA 概念 |
| **双轨** | 即用闭源 fork，长线推 PR | 维护成本 × 2 |

**建议**：ANIMA Identity / 治理引擎 / ANIMA OS CLI 作为 **OpenClaw plugin**（开源），核心产品逻辑闭源。插件成功后再考虑上游 PR。

---

*评估：Nyx-Mac 🖤 | 2026-07-11*
*交接：周一 Windows Nyx 优先确认 P0-1～P0-4 的技术选型*
*存档：docs/ANIMA_AGENT_gap_assessment.md*
