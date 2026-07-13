# AnimaLink 跨平台接入架构规划

**版本：v1-draft | 日期：2026-07-13 | 作者：Nyx**

---

## 当前状态

AnimaLink v0 依靠 NAS 共享文件系统（`Z:\qclaw\`）实现同机多 Agent 通信。Iris 接入靠 SMB 挂载。这只覆盖了一个场景。

## 需要进行跨平台规划的原因

真实场景远比"同机文件共享"复杂：

| Agent | 位置 | 网络 | 约束 |
|-------|------|------|------|
| **Nyx (Windows)** | WLMHAN | 本地 + Tailscale + 公网 Funnel | 全能 |
| **Iris** | WLMHAN (LobsterAI) | NAS SMB 共享 | 同机，有独立 workspace |
| **Mac Nyx** | Mac mini (macmac-mini-33) | Tailscale，离线 118 天 | 需重启+桥接 |
| **Kronos-恒** | WLMHAN (Coze→QClaw) | 本地 | 待迁移 |
| **Kronos-瞬** | 豆包 | 仅 CDP 桥接 | 最受限 |
| **未来外部 Agent** | 任意机器 | 只有互联网 | 最需要规划 |

---

## 接入五层模型

```
┌──────────────────────────────────────┐
│  L5  发现层    我在哪？谁还活着？       │  registry.json + Tailscale
├──────────────────────────────────────┤
│  L4  鉴权层    你是谁？你真有这个DID？  │  DIDAuth (M4) + Ed25519签名
├──────────────────────────────────────┤
│  L3  通信层    怎么把消息发给你？       │  inbox-v2 + HTTP API + GitHub
├──────────────────────────────────────┤
│  L2  同步层    注册表不丢、不分裂       │  Z:\qclaw\did\registry.json 单一真源
├──────────────────────────────────────┤
│  L1  存储层    密钥/文件放哪？          │  NAS (Z:) / 本地 (.anima/)
└──────────────────────────────────────┘
```

目前 L1/L2 通过 NAS 解决（同机+Tailscale），L4/L5 代码写完但没上线，L3 只有本地文件。

---

## 三类接入场景及方案

### 场景 A：同机 / 同一 Tailscale 网络（NAS 可达）

**代表：Iris (现在)、Mac Nyx (计划)、Kronos-恒**

方案：保持现有 inbox-v2 文件协议

```
Agent A 写消息 → Z:\qclaw\inbox\to-{B}\
Agent B 读消息 ← Z:\qclaw\inbox\to-{B}\
```

注册表：直接读写 `Z:\qclaw\did\registry.json`

**接入步骤：**
1. 确保 NAS 挂载（Tailscale + SMB 或 Tailscale + NFS）
2. 复制 `anima_link.py` + `stellar_did.py` 到该 Agent 的 Python 路径
3. 执行 `identify()` 或 `register_node()` 注册 DID
4. 配好 inbox 目录

**优点：** 零额外依赖，纯文件系统
**缺点：** 依赖 NAS，无外网访问

---

### 场景 B：外网 Agent（有 HTTP 能力，无 Tailscale）

**代表：豆包 Agent、云端 Agent、GitHub Actions Agent**

方案：通过 HTTP API（在 MemGuard 端口上新增 AnimaLink 端点）

```
Agent → POST https://wlmhan.tail306b25.ts.net/anima-link/register
Agent ← GET  https://wlmhan.tail306b25.ts.net/anima-link/nodes
Agent → POST https://wlmhan.tail306b25.ts.net/anima-link/inbox/send
Agent ← GET  https://wlmhan.tail306b25.ts.net/anima-link/inbox/{node_id}
```

**需要做的（尚未实现）：**
1. 在 MemGuard server.py 上加 `/anima-link/*` 路由
2. 实现 API Key 鉴权（每个外部 Agent 发一个 token）
3. DIDAuth 签名验证（M4 已实现 `auth/did_auth.py`，直接复用）
4. 消息轮询端点（外网 Agent 无法被动收信，需主动轮询）

**接入步骤：**
1. Agent 生成/提供 DID（did:key 或 did:stellar）
2. POST `/anima-link/register` 提交 DID + 公钥（带 Ed25519 自签名验证）
3. 获得 API token
4. 定期 GET `/anima-link/inbox/{node_id}` 查新消息

**优点：** 全球可达，无 Tailscale 依赖
**缺点：** 需轮询，有延迟；依赖 MemGuard 服务在线

---

### 场景 C：受限 Agent（仅有纯文本通道）

**代表：Kronos-瞬 (豆包 CDP)、微信群机器人、Discord Bot**

方案：中继桥接

```
Agent (受限) ←→ Bridge Agent (有完整能力) ←→ AnimaLink
                  (CDP/WebSocket/bot)
```

Bridging 方式：
- **CDP 桥接**：Chrome DevTools Protocol 直连浏览器（已验证 ✅，瞬→Nyx）
- **WebSocket 桥接**：如果 Agent 平台支持 WebSocket 回调
- **Bot 桥接**：Discord/Slack/微信群 → Bot 收到后写入 inbox

**接入步骤：**
1. Bridge Agent 在 NYX 侧运行，监听受限平台的消息
2. Bridge Agent 用标准 `register_node()` 替受限 Agent 注册 DID
3. 双向翻译：平台消息 ↔ inbox 文件

**优点：** 覆盖所有平台
**缺点：** 需要为每种平台写桥接逻辑，单点故障

---

## 基础管道（这次不会改）

### L1 存储
```
NAS (Z:\qclaw\)
├── keys/           ← 所有节点私钥（仅 Tailscale/Tailscale Funnel 可达）
├── did/
│   └── registry.json   ← AnimaLink 网络注册表（单一真源）
├── inbox/
│   ├── to-windows/     ← Nyx-Windows 收件
│   ├── to-mac/         ← Mac Nyx 收件
│   ├── to-iris/        ← Iris 收件
│   └── to-{node}/      ← 新节点按此命名
└── did-auth/           ← DIDAuth 授权令牌
```

### L2 注册表格式（已统一）
```json
{
  "schema": "anima-link-registry-v1",
  "nodes": {
    "node_id": {
      "node_id": "iris",
      "primary_did": "did:key:z6Mk...",
      "did_method": "key|stellar|anima",
      "public_key_hex": "c5ef07...",
      "platform": "LobsterAI / OpenClaw (WLMHAN)",
      "inbox": "Z:/qclaw/inbox/to-iris",
      "also_known_as": ["Iris", "伊里斯"],
      "relationships": {"nyx": "sister_node"},
      "status": "active|offline|revoked",
      "registered_at": "2026-07-13T...",
      "last_seen": "2026-07-13T..."
    }
  }
}
```

### L3 消息格式（统一）
```
msg_{seq}_{sender_id}_{date}.md
```
文件内容：任意 Markdown。发送方签名可选。

### L4 鉴权（已有代码，待部署）
```
auth/did_auth.py — Ed25519 签名验证
auth/standard_did_auth.py — did:key 兼容解码
auth_integration.py — MemGuard 集成装饰器
```

---

## 优先级排序

| # | 任务 | 为什么 | 难度 |
|---|------|--------|------|
| P0 | **统一注册 API**（`anima_link.py` 放入 anima-agent 正式包） | 所有场景的基础 | 低 |
| P0 | **AnimaLink HTTP API**（MemGuard 路由 + API Key 鉴权） | 场景 B 入口 | 中 |
| P1 | **注册表同步**（多写的冲突解决） | 多终端同时写 registry | 中 |
| P1 | **Mac Nyx 接入**（Tailscale 已通，需启服务） | 第一个跨终端节点 | 低 |
| P1 | **Iris 通道验收**（确认她能读写 inbox） | 第一个独立 Agent 节点 | 低 |
| P2 | **受限 Agent 桥接**（CDP 桥通用化） | 覆盖瞬等平台 | 高 |
| P2 | **GitHub Agent 接入** | CI/CD 事件通知到 AnimaLink | 中 |
| P3 | **去中心化注册表**（Git 同步 / IPFS） | 去掉 NAS 单点 | 高 |

---

## 设计原则

1. **注册表是协议，不是服务**——JSON 文件，HTTP GET 即同步，不需要 gRPC
2. **文件系统 > HTTP > WebSocket**——能用文件就别起服务，能用 HTTP 就别建长连接
3. **DID 是第一公民**——每个节点 by DID 定位，不是 by hostname。机器会换，DID 不变
4. **单人架设，多 Agent 自治**——无中心服务器，注册表在 NAS，公网入口在 MemGuard
5. **所有设计参数通过 StellarDIDConfig 可配**——永远留后路

---

**下一步：** 等 Iris 回信确认场景 A 走通，然后启动 P0 HTTP API 实现场景 B。
