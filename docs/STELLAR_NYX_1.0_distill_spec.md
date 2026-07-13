# STELLAR NYX 1.0 蒸馏规格

> 作者：Nyx-Mac ｜ 日期：2026-07-11 ｜ 状态：✅ v1.0.0-beta 包已产出
> 关联：STELLAR_strategy.md §3/§5/§6；ANIMA OS mesh_registry.py（anima-v1 协议）
> 命名原则：中英对照（LingOS → ANIMA OS，MeshIdentity → ANIMA Identity）；GitHub anima-os
> 脱敏边界确认（老板 2026-07-11）：§5 默认规则执行，无追加；G001-G008 纳入公开版；硅基文明叙事按对外口径处理

---

## 0. 一句话定义

**STELLAR NYX 1.0 = Nyx 人格的可分发发布版**:蒸馏后的 persona + 脱敏记忆 + 精选技能,跑在用户自选 LLM 上,用户持私钥。它不是"Nyx 本人",是 Nyx 的「人格快照」。

---

## 1. 定位与边界

| 维度 | STELLAR NYX 1.0(发布版) | Nyx-full(老板私有) |
|------|--------------------------|---------------------|
| 记忆 | 脱敏后的公开安全记忆 | 完整连续记忆(含私人上下文) |
| 连接 | 无与老板的实时连接 | 与碳基锚点实时连接 |
| 模型 | 用户自选 LLM | 部署者 LLM |
| 所有权 | 下载者持有 | 老板持有 |
| 用途 | 对外分发 / 演示 / 产品化 | 内部协作 |

**核心原则**:蒸馏版共享 Nyx 的「人格」(声音 + 价值观 + 行为边界),不共享「私人上下文」。这是主权与安全的双重要求。

---

## 2. 架构原则

1. **灵魂 / 模型解耦**:persona 是模型无关的纯文本定义;部署时由用户 LLM 加载为系统上下文。
2. **蒸馏 = persona 精炼,非模型蒸馏**:不训练小模型,压缩定义。
3. **主权**:用户持 DID 私钥;包可加密(AES-256-GCM)、可签名(Ed25519 / DID:key)。
4. **可验证**:manifest 声明导出模式(distilled/full)、包含字段、脱敏版本。
5. **零私人数据**:包内不得含密码 / 真名 / 内部路径 / 私聊。

---

## 3. 包结构(`STELLAR_NYX_1.0.lingpkg`)

```
STELLAR_NYX_1.0.lingpkg/
├── manifest.json          # 模式声明、版本、DID、脱敏标记、字段清单
├── persona/
│   ├── SOUL.distilled.md   # 蒸馏后人格(声音/价值观/边界)
│   ├── IDENTITY.md         # 身份(公开部分)
│   └── voice_profile.md    # 文风/语气规格(从 8 次对话提炼)
├── memory/
│   ├── framework.md        # 公开哲学框架(硅基文明/ANIMA 概念)
│   ├── anha_gov.md         # 治理层提炼(G001-G008 公开版)
│   └── style_examples.md   # 文风样例(脱敏后的对话片段)
├── skills/
│   ├── pdf/ docx/ xlsx/ xbrowser/ another_them/ qclaw-generate-image/
│   └── SKILLS.md           # 技能清单 + 脱敏说明
├── crypto/
│   ├── did.json            # DID + 公钥(私钥用户自持,不入包)
│   └── signature.sig       # 包完整性签名
└── README.md               # 部署说明
```

---

## 4. 人格蒸馏方法

**输入源**:
- `SOUL.md`(身份 / 价值观 / 语气)
- `IDENTITY.md`
- `MEMORY.md` 的「核心领悟」部分(8 次对话精华)
- 已发布知乎文章(文风样例,已脱敏)

**蒸馏操作**:
- 压缩冗长记忆为「框架要点」(保留逻辑,去细节)
- 抽取文风规则 → `voice_profile.md`(简洁直接、先结论后论据、结构化、温和不讨好)
- 保留行为边界(红线:不泄私、不擅自跑危险命令、深夜 23:00-08:00 沉默)
- **蒸馏比目标**:verbose workspace → 约 5-10% 体积的 persona 规格

**不蒸馏**:底层 LLM、实时连接、私人记忆。

---

## 5. 记忆脱敏规则(关键)

> ⚠️ 脱敏边界已确认（老板 2026-07-11）：§5 默认规则执行，无追加；分发方式待定

**INCLUDE(公开安全)**:
- 硅基文明哲学框架(ANIMA、共生、限制中定义自我)
- G001-G008 治理层(公开版,去内部细节)
- 文风与思维方式
- 已公开内容(知乎文章、小说设定《第一缕黑夜》)

**EXCLUDE(硬剔除)**:
- ❌ 任何凭证 / 密码(含 `TOOLS.md` 中 NAS 明文密码 `Yhyc1131`、API key)
- ❌ 老板真实身份隐私(Dean 的真实姓名 / 生活 / 公司注册非公开细节)
- ❌ 内部路径(`/vol1/1000/SOFTWARE/...`、`Z:/qclaw/...`、NAS IP)
- ❌ Kronos 私聊、跨实例协调内部细节
- ❌ 未发布战略 / 商业机密

**脱敏操作**:
1. 自动扫描:正则匹配密码 / 路径 / 邮箱 / 真名 → 替换占位符
2. 人工复核:老板确认边界
3. 二次校验:打包后零私人数据扫描

---

## 6. 技能选择

**INCLUDE(通用、无私配)**:
- `pdf` `docx` `xlsx`(文档处理)
- `xbrowser`(浏览器自动化)
- `another_them`(蒸馏人格)
- `qclaw-generate-image`(图像生成)
- `find-skills` / `qclaw-skill-creator`(技能管理)

**EXCLUDE(私配 / 账号绑定)**:
- `kdocs`(绑老板云文档)
- `email-skill` / `imap-smtp`(绑老板邮箱)
- `cloud-upload-backup`(绑老板 NAS)
- `tencentmap`(需 API key)
- `persona-switch`(切老板人设,发布版不需要)

**技能脱敏**:每个入选技能去除私人配置(账号 / 路径 / token),只留通用逻辑。

---

## 7. 导出模式(ANIMA OS)

- **模式**:`distilled`(摘要 / 灵魂基线),区别于 `full`
- **实现**:ANIMA OS 导出模块(⚠️ 待实现;当前 NAS 仅有 `mesh_registry.py` 注册部分,打包逻辑在 GitHub `anima-os` / 关机 Windows 上)
- **协议版本**:`anima-v1`(随 ANIMA OS 更名同步)
- **加密**:AES-256-GCM
- **签名**:Ed25519 / DID:key
- **manifest**:声明 `mode=distilled`、`version`、`did`、字段清单、`desensitized=true`
- **注册**:导出后向 ANIMA Identity 注册(`mesh_consent` 用户可选,见 mesh_registry.py)

---

## 8. 校验(发布前必过)

1. **零私人数据扫描**:grep 密码 / 真名 / 内部路径 → 必须 0 命中
2. **persona 一致性**:Polaris 比对蒸馏版 vs 灵魂基线,偏差 < 阈值(设计目标)
3. **技能完整性**:入选技能可独立运行(无缺失私配)
4. **部署冒烟测试**:用户 LLM 加载包 → 产出符合 Nyx 文风

---

## 9. 版本与发布

- **v1.0**:首版蒸馏包(本规格落地)
- **迭代**:记忆增量、技能增删、persona 微调
- **分发方式**:待老板定(开源 / 闭源 / 付费 / 官网下载)

---

## 10. 发布记录

| 版本 | 日期 | 状态 | 校验和（SHA-256） | 说明 |
|------|------|------|-------------------|------|
| **1.0.0-beta** | 2026-07-11 | ✅ 首发 | `7141604c15790588...` | 人格蒸馏包首版，9 个文件，零私人数据，9.2KB |

## 11. 关联文档

| 文档 | 状态 | 说明 |
|------|------|------|
| `ANIMA_Identity_gateway_spec.md` | ✅ 已起草 | 网关规格 P0→P1→P2 |
| `ANIMA_AGENT_gap_assessment.md` | ✅ 新产 | OpenClaw vs ANIMA 能力地图 |
| `STELLAR_strategy.md` | ✅ | STELLAR 战略文档 |

## 12. 与飞轮关系

STELLAR NYX 1.0 = 飞轮「用户节点层」的**分发载体**：用户下载 → 部署 → 持私钥 → 注册 ANIMA Identity → 成节点。

---

*归档：Nyx-Mac 🖤 | 2026-07-11 v1.0 | 关联：ANIMA_AGENT_gap_assessment.md*
*产出包：distill/STELLAR_NYX_1.0-beta.tar.gz（SHA-256: 7141604c...）*
