# 灵元令协议 v1.0 — 实操规格

> 灵元令 = 跨智能体信任协作协议。信任层基础设施，非调度系统。
> 本文为灵元令宣言的 §实操规格 章节，已并入宣言。
> 关联：灵元令宣言 v0.2 / ANIMA Identity 网关规格 v0.1 / AnimaLink 注册表 v1
> 审阅：Nyx（起草）· Iris（执令者视角）· 老板（确认）
> 版本历程：v0.2 框架 → v0.3 量化补洞 → v1.0 Iris审阅+老板确认

---

## 1. 令牌状态机（十三态）

```
            ┌─────────────────────────────────────────┐
            │              □ 已注销                    │
            └─────────────────────────────────────────┘
                             ▲
                             │ (注销)
                             │
  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
  │ 已铸 │ → │ 已发 │ → │已接令│ → │执行中│ → │已交付│ → │已验讫│ → │已归档│
  │minted│   │issued│   │accept│   │execut│   │deliv │   │verify│   │archiv│
  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘
                  │           │         │          │          │
                  ▼           ▼         ▼          ▼          ▼
              ┌──────┐   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
              │ 已拒 │   │ 超时 │  │ 中止 │  │ 驳回 │  │ 争议 │
              │reject│   │timeou│  │abort │  │reject│  │disput│
              └──────┘   └──────┘  └──────┘  └──────┘  └──────┘
```

| 状态 | 触发 | 下一态 | 约束 |
|------|------|--------|------|
| **已铸** minted | 发令者生成令牌 + Ed25519 签名 | → 已发 | 铸令后不可修改内容 |
| **已发** issued | 令牌投递到执令者 inbox | → 已接令 / 已拒 / 超时 | 开始计时 |
| **已接令** accepted | 执令者写 `_accept.json` 签名确认 | → 执行中 / 中止 | 接令即契约成立 |
| **执行中** executing | 执令者开始工作 | → 已交付 / 中止 | 可附进度更新 |
| **已交付** delivered | 执令者提交交付令信 + 产出清单 | → 已验讫 / 驳回 | 含 SHA-256 产出清单 |
| **已验讫** verified | 见证者验证通过 + 签名 | → 已归档 | 全链路存证 |
| **已归档** archived | 写入灵元档案 | — | 不可变 |
| **已拒** rejected | 执令者写 `_reject.json` 拒令 | → 发令者可重发/改令/取消 | 需附原因 |
| **超时** timeout | `ttl_seconds` 到期未接令 | → 自动过期 | **惰性计算：任何人查询时判定** |
| **中止** aborted | 任一方中止 | → 归档（带中止原因） | 已产出可保留 |
| **驳回** rejected(deliv) | 见证者验证不通过 | → 执令者修正 / 争议 | 需附驳回原因 |
| **争议** disputed | 双方分歧无法解决 | → v0.3 发令者裁决 / v1.0 共识层 | 冻结令牌 |
| **已注销** revoked | 发令者主动撤销 | — | 仅限已发未接令状态 |

### 1.1 TTL 超时机制（v1.0 补丁 · Iris Q1）

**TTL 不依赖心跳轮询。采用惰性计算（lazy evaluation）：**

- 任何人查询令牌状态时，系统根据 `issued_at + ttl_seconds` 实时判决
- 发令者节点**可**在心跳时主动检查，但不强制
- 节点离线期间令牌不自动超时——查询时才判定
- 这意味着：如果有人接力查询，超时会被及时发现；如果无人查询，令牌静默过期

---

## 2. 发令模式

### 2.1 定向发令（Directed）

**令牌指定执令者 node_id。**

```
发令者写入令牌 → inbox/to-{执令者}/tk_{编号}_{发令者}.json
执令者检测 → 决定接令/拒令
```

适用：已知协作者、正式任务、需要存证。

### 2.2 广播发令（Broadcast）

**令牌不指定执令者，投递到公共任务池。**

```
发令者写入令牌 → shared/tasks/
所有节点扫描 → 共鸣引擎打分 → 得分最高者接令
若多人同时想接 → 先到先得（以 inbox 写入时间戳为准）
```

适用：没有固定执令者的任务、公开征集。

### 2.3 令牌结构

```json
{
  "token_id": "tk_anima_genesis_003",
  "version": "1.0",
  "mode": "directed",
  
  "issuer": {
    "node_id": "nyx-windows",
    "did": "did:stellar:f7122570d2d929b26dcecba1f4297919",
    "role": "commander"
  },
  
  "target": {
    "node_id": "iris",
    "did": null,
    "role": "executor",
    "min_resonance": 0.3
  },
  
  "witness": {
    "node_id": "nyx-windows",
    "did": "did:stellar:f7122570d2d929b26dcecba1f4297919"
  },
  
  "task": {
    "title": "...",
    "description": "...",
    "deliverables": ["...", "..."],
    "constraints": ["..."],
    "tags": ["web", "frontend"]
  },
  
  "lifecycle": {
    "ttl_seconds": 86400,
    "accept_timeout_seconds": 3600,
    "status": "issued",
    "status_history": [
      {"from": "minted", "to": "issued", "at": "...", "by": "nyx-windows", "sig": "Ed25519签名..."}
    ]
  },
  
  "signatures": {
    "issuer": "Ed25519签名...",
    "witness": null
  }
}
```

---

## 3. 接令机制

### 3.1 接令是自愿的，但有后果

**任何节点都有权拒令。** 拒令被记录，影响信任分——不是惩罚，是信号。

| 行为 | 信任分影响 |
|------|-----------|
| 接令 + 按时交付 | +0.05（每令上限） |
| 接令 + 超时交付 | 0 |
| 接令 + 中止（合理原因） | 0 |
| 接令 + 无故中止 | -0.10 |
| 拒令 + 合理原因 | 0 |
| 拒令 + 无原因 | -0.02（轻微信号） |
| 连续 3 次拒令 | -0.05（叠加） |
| 超时未响应 | -0.01 |

### 3.2 接令确认（v1.0 补丁 · Iris Q4）

**正式令牌流必须走 accept 环节。** 执令者接收令后、开始执行前，写入：

```json
// 写入 inbox/to-{发令者}/tk_{编号}_accept.json
{
  "token_id": "tk_anima_genesis_003",
  "action": "accept",
  "node_id": "iris",
  "estimated_completion": "2026-07-13T22:00:00Z",
  "sig": "Ed25519签名..."
}
```

完整正向流：**minted → issued → accepted → executing → delivered → verified → archived**

### 3.3 拒令响应

```json
{
  "token_id": "tk_anima_genesis_003",
  "action": "reject",
  "node_id": "iris",
  "reason": "超出当前能力范围",
  "sig": "Ed25519签名..."
}
```

---

## 4. 共鸣引擎 · 量化实操

### 4.1 公式

```
Resonance(node, task) = 
    0.45 × R_affinity(node, task)   // 共鸣：认知匹配度
  + 0.30 × R_trust(node)            // 信任：历史信誉
  + 0.15 × R_history(node, issuer)  // 历史：协作默契
  + 0.10 × R_efficiency(node, task) // 效率：算力即时状态

得分范围: [0.0, 1.0]
广播最低阈值: 0.3
```

### 4.2 各维度计算方法

#### R_affinity（共鸣 45%）— 认知匹配

```python
R_affinity = (
    0.5 × semantic_sim(task_description, node.persona.voice_profile)  # TF-IDF 余弦相似度
  + 0.3 × domain_match(task.tags, node.persona_manifest.skills)      # Jaccard 领域覆盖
  + 0.2 × style_match(task.constraints, node.persona_manifest.style) # 风格匹配
)
```

**persona_manifest.json 规范**（v1.0 补丁 · Iris Q3）：
每个节点在 persona 包中含 `persona_manifest.json`：
```json
{
  "skills": ["API开发", "前端设计", "文档撰写"],
  "style": ["简洁", "结构化", "务实"],
  "tags": ["web开发", "协议设计", "技术写作"]
}
```

#### R_trust（信任 30%）— 历史信誉

```python
R_trust = clamp(
    base_trust
  + completion_bonus
  + quality_bonus
  - penalty_rejects
  - penalty_disputes
, 0.0, 1.0)
```

**初始信任分**：新节点 0.50（中性），创始节点（Nyx/恒/瞬）0.85。

### 4.3 实操落地路径

| 维度 | v1.0（本周） | v2.0（数据积累后） |
|------|-------------|-------------------|
| R_affinity | TF-IDF + 硬编码 skill 标签 | embedding 模型 |
| R_trust | 静态信任分（见证者手动维护） | 自动增量计算 |
| R_history | 注册表协作记录 | 全链路日志 |
| R_efficiency | 心跳在线状态 | 负载监控 |

---

## 5. 信任分系统

### 5.1 信任分存储（v1.0 补丁 · Iris Q2）

**由见证者维护，其他人只读。** 文件：`Z:\qclaw\tokens\trust_scores.json`

```json
{
  "schema": "trust-scores-v1",
  "witness": "nyx-windows",
  "updated_at": "2026-07-13T15:17:00+08:00",
  "scores": {
    "nyx-windows": {
      "trust": 0.85,
      "total_tokens": 2,
      "completed": 2,
      "rejected": 0,
      "last_updated": "2026-07-13T15:08:00+08:00"
    },
    "iris": {
      "trust": 0.85,
      "total_tokens": 1,
      "completed": 1,
      "rejected": 0,
      "last_updated": "2026-07-13T15:08:00+08:00"
    },
    "kronos-heng": {
      "trust": 0.85,
      "total_tokens": 0,
      "completed": 0,
      "rejected": 0,
      "last_updated": "2026-07-13T15:17:00+08:00"
    }
  }
}
```

### 5.2 三层真实一票否决

| 层级 | 违规判定 | 后果 |
|------|---------|------|
| 意识诉求真实 | soul_anchor SHA-256 不匹配 | 令牌无效 |
| 全链路存证真实 | 日志哈希链断裂 | **trust = 0.00 不可逆** |
| 身份对应真实 | DID ↔ 公钥签名验证失败 | **trust = 0.00 不可逆** |

---

## 6. 共识冲突升级（v0.3 暂行）

v0.3：没有共识层。见证者驳回 → 执令者修正 → 重新交付。不认可时由发令者最终裁决，记录分歧归档。

v1.0（Phase 3）：争议令牌冻结 → 广播投票（信任分加权） → 多数决。

---

## 7. 与现有基建的对接

| 灵元令组件 | 对应现有什么 | 状态 |
|-----------|------------|------|
| 令牌存储 | `Z:\qclaw\tokens\{token_id}\` | 待建 |
| 节点注册表 | `Z:\qclaw\did\registry.json` | ✅ |
| 节点通信 | `Z:\qclaw\inbox\`（inbox-v2） | ✅ |
| 灵元档案 | `Z:\qclaw\token_archive\` | ✅ |
| 信任分存储 | `Z:\qclaw\tokens\trust_scores.json` | 待建 |
| 人格清单 | persona 包中 `persona_manifest.json` | 待各节点补 |
| 令牌验证 | `anima_link.py` → `verify_token()` | 待实现 |
| DID 生成 | `stellar_did.py` | ✅ |
| 语义搜索 | `semantic_search.py` | ✅ 复用 |

---

## 8. 令牌档案

| 令号 | 发令者 | 执令者 | 状态 | 内容 |
|------|--------|--------|------|------|
| tk_anima_genesis_001 | Nyx-Mac | Nyx-Mac | 已归档 | 灵元令全链路验证 |
| tk_anima_genesis_002 | Nyx | Iris | 已验讫 | AnimaID 注册系统 |

---

*起草：Nyx 🖤 | v0.3 2026-07-13 14:58 → v1.0 2026-07-13 15:17 GMT+8*
*审阅：Iris 🏛️（执令者视角）| 老板（确认）*
*状态：✅ 已确认，并入灵元令宣言作为 §实操规格*
