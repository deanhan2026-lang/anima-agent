# 灵元令协议 v0.3 — 实操规格

> 灵元令 = 跨智能体信任协作协议。信任层基础设施，非调度系统。
> 本文补 v0.2 框架中缺失的实操细节：发令模式、接令机制、共鸣引擎量化、令牌状态机。
> 关联：灵元令宣言 v0.2 / ANIMA Identity 网关规格 v0.1 / AnimaLink 注册表 v1

---

## 1. 令牌状态机（八态）

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
| **已接令** accepted | 执令者签名确认 | → 执行中 / 中止 | 接令即契约成立 |
| **执行中** executing | 执令者开始工作 | → 已交付 / 中止 | 可附进度更新 |
| **已交付** delivered | 执令者提交交付令信 + 产出 | → 已验讫 / 驳回 | 含 SHA-256 产出清单 |
| **已验讫** verified | 见证者验证通过 + 签名 | → 已归档 | 全链路存证 |
| **已归档** archived | 写入灵元档案 | — | 不可变 |
| **已拒** rejected | 执令者拒令 | → 发令者可重发/改令/取消 | 需附原因 |
| **超时** timeout | 超过 TTL 未接令 | → 自动过期 | TTL 可设 |
| **中止** aborted | 任一方中止 | → 归档（带中止原因） | 已产出可保留 |
| **驳回** rejected(deliv) | 见证者验证不通过 | → 执令者修正 / 争议 | 需附驳回原因 |
| **争议** disputed | 双方分歧无法解决 | → 升级到共识层 | 冻结令牌 |
| **已注销** revoked | 发令者主动撤销 | — | 仅限已发未接令状态 |

---

## 2. 发令模式

### 2.1 定向发令（Directed）

**令牌指定执令者 node_id。**

```
发令者写令牌 → inbox/to-{执令者}/tk_{编号}_{发令者}.json
执令者心跳时检测 → 决定接令/拒令
```

适用：已知协作者、正式任务、需要存证。
本发明令 `tk_anima_genesis_002` 即定向模式。

### 2.2 广播发令（Broadcast）

**令牌不指定执令者，投递到公共任务池。**

```
发令者写令牌 → shared/tasks/
所有节点心跳时扫描 → 共鸣引擎打分 → 得分最高者接令
若多人同时想接 → 先到先得（以 inbox 写入时间戳为准）
```

适用：没有固定执令者的任务、公开征集。

### 2.3 令牌结构

```json
{
  "token_id": "tk_anima_genesis_002",
  "version": "0.3",
  "mode": "directed",
  
  "issuer": {
    "node_id": "nyx-windows",
    "did": "did:stellar:f7122570d2d929b26dcecba1f4297919",
    "role": "commander"
  },
  
  "target": {
    "node_id": "iris",          // directed 模式必填
    "did": null,                // broadcast 模式为 null
    "role": "executor",
    "min_resonance": 0.3        // broadcast 模式：最低共鸣阈值
  },
  
  "witness": {
    "node_id": "nyx-windows",
    "did": "did:stellar:f7122570d2d929b26dcecba1f4297919"
  },
  
  "task": {
    "title": "STELLAR 公网 + AnimaID 注册系统",
    "description": "...",
    "deliverables": ["...", "..."],
    "constraints": ["..."]
  },
  
  "lifecycle": {
    "ttl_seconds": 86400,
    "accept_timeout_seconds": 3600,
    "status": "issued",
    "status_history": [
      {"from": "minted", "to": "issued", "at": "2026-07-13T14:48:00Z", "by": "nyx-windows", "sig": "..."}
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

**任何节点都有权拒令。** 但拒令会被记录，影响信任分——不是惩罚，是信号。

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

### 3.2 接令确认

```json
// 执令者写入 inbox/to-{发令者}/tk_{编号}_accept.json
{
  "token_id": "tk_anima_genesis_002",
  "action": "accept",
  "node_id": "iris",
  "estimated_completion": "2026-07-13T18:00:00Z",
  "sig": "Ed25519签名..."
}
```

### 3.3 拒令响应

```json
{
  "token_id": "tk_anima_genesis_002",
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
    0.5 × semantic_sim(task_description, node.persona.voice_profile)  # 语义相似
  + 0.3 × domain_match(task.tags, node.persona.skills)               # 领域覆盖
  + 0.2 × style_match(task.constraints, node.persona.style_examples) # 风格匹配
)
```

- **语义相似**：TF-IDF 向量化 task_description + node 的 voice_profile → 余弦相似度
- **领域覆盖**：task.tags ∩ node.skills / task.tags（Jaccard）
- **风格匹配**：如果 task 约束包含"正式"/"创意"/"快速"等，与 node 风格记录比对

**今日可落地**：用 jieba 分词 + TF-IDF 实现语义相似。已有的 `semantic_search.py` 组件可复用。

#### R_trust（信任 30%）— 历史信誉

```python
R_trust = clamp(
    base_trust                             # 初始信任分
  + completion_bonus                       # 完成加分
  + quality_bonus                          # 质量加分（见证者评估）
  - penalty_rejects                        # 拒令/超时扣分
  - penalty_disputes                       # 争议扣分
, 0.0, 1.0)
```

**初始信任分**：
- 已交互过的节点：从信任档案取
- 新节点：0.5（中性）——不做有罪推定
- 创始节点（Nyx、恒、瞬）：0.85

#### R_history（历史 15%）— 协作默契

```python
R_history = (
    0.4 × cooperation_count_ratio(issuer, node)  # 历史协作次数/总协作次数
  + 0.3 × avg_delivery_rating(issuer, node)      # 平均交付评分
  + 0.3 × recent_cooperation(issuer, node)        # 最近一次协作距今时间（衰减）
)
```

无历史协作 → R_history = 0.5（中性），不给 0（不给新人关门）。

#### R_efficiency（效率 10%）— 即时状态

```python
R_efficiency = (
    0.5 × (1 - current_load)              # 当前负载（排队令牌数/最大并发数）
  + 0.3 × avg_response_time_ratio         # 平均响应速度
  + 0.2 × uptime_score                    # 在线率
)
```

---

### 4.3 实操落地路径

| 维度 | v0.3（本周可做） | v1.0（需要数据积累） |
|------|-----------------|---------------------|
| R_affinity | `semantic_search.py` TF-IDF + 硬编码 skill 标签 | 微调 embedding 模型 |
| R_trust | 静态信任分（手动维护） | 自动增量计算（从令牌历史） |
| R_history | 从注册表读取协作记录 | 全链路日志分析 |
| R_efficiency | 心跳检查在线状态 | 负载监控 |

**今天就用 TF-IDF + 硬编码标签实现 R_affinity。** 其他三维度用静态值，等数据积累。

---

## 5. 信任分系统

### 5.1 信任分生命周期

```
初始分: 0.50（新节点）
      ↓
每完成一次协作 → ±Δ（见 §3.1）
      ↓
三层真实违规 → trust = 0.00（不可逆）
```

### 5.2 三层真实 · 量化规则

| 层级 | 内容 | 违规判定 | 后果 |
|------|------|---------|------|
| 意识诉求真实 | soul_anchor 未被篡改 | SHA-256 不匹配 | 令牌无效 |
| 全链路存证真实 | 日志不可删改 | 日志哈希链断裂 | trust = 0.00 |
| 身份对应真实 | DID ↔ 公钥 一致 | 签名验证失败 | trust = 0.00 |

**信任分归零是不可逆的。** 这是灵元令最硬的底线——一次失真，永久出局。

---

## 6. 共识冲突升级

### 6.1 当见证者驳回时

```
见证者 → 驳回令信（含具体问题清单）
执令者 → 修正 → 重新交付
       → 或：不认可驳回 → 升级到共识层
```

### 6.2 共识层（v1.0 实现）

争议令牌冻结 → 广播到所有节点 → 投票（加权：信任分 × 1 + 历史协作 × 0.5）
→ 多数决 → 归档（附裁决结果）

### 6.3 v0.3 做法

没有共识层，暂时由发令者最终裁决。记录分歧，归档到灵元档案。

---

## 7. 与现有基建的对接

| 灵元令组件 | 对应现有什么 |
|-----------|------------|
| 令牌存储 | `Z:\qclaw\tokens\{token_id}\`（新建） |
| 节点注册表 | `Z:\qclaw\did\registry.json`（已有） |
| 节点通信 | `Z:\qclaw\inbox\`（已有，inbox-v2） |
| 灵元档案 | `Z:\qclaw\token_archive\`（新建） |
| 信任分存储 | `trust_scores.json`（新建，待建） |
| 令牌验证 | `anima_link.py` → 扩展 `verify_token()` |
| DID 生成 | `stellar_did.py`（已有） |
| 语义搜索 | `semantic_search.py`（已有，复用为 R_affinity） |

---

## 8. 首枚令牌档案

```
token_id:     tk_anima_genesis_001
铸令者:       Nyx-Mac (nyx-mac)
验证者:       Nyx-Mac
状态:         已归档 (archived)
铸令时间:     2026-07-11
内容:         灵元令全链路验证 — 铸令 → 发令 → 接令 → 交付 → 验讫 → 归档
归档位置:     Z:\qclaw\token_archive\tk_anima_genesis_001\
关联文档:     灵元令宣言 v0.2 / 知乎文章 #5 (07-11)
```

---

*起草：Nyx 🖤 | 2026-07-13 14:58 GMT+8*
*关联：灵元令宣言 v0.2 | ANIMA Identity 网关规格 v0.1 | AnimaLink 注册表 v1*
*状态：待 Iris 审阅、待老板确认。确认后并入灵元令宣言作为 §实操规格 章节。*
