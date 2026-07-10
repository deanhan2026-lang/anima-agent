# Anima Agent — 出厂预装技能集成规范

## 概述

Anima Agent 基于 OpenClaw 的 Skill 机制，将灵元三件套作为"出厂预装技能"进行集成。

OpenClaw 原生支持 Skills 目录机制（`skills/*/SKILL.md`），Anima Agent 在此基础上增加了**自动激活**和**网络注册**两步。

## 集成架构

```
src/
├── core/
│   ├── model-router.ts        # 国产模型路由层
│   └── onboarding/
│       └── zh-cn-wizard.ts    # 中文安装向导
├── skills/
│   ├── meshidentity-skill/    # 灵元三件套 — MeshIdentity
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── did_generate.py
│   │   │   ├── did_register.py
│   │   │   └── heartbeat.py
│   │   └── assets/
│   │       └── did_dashboard.html
│   ├── memguard-skill/        # 灵元三件套 — MemGuard
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── encrypt.py
│   │       ├── verify.py
│   │       └── restore.py
│   └── polaris-skill/         # 灵元三件套 — Polaris
│       ├── SKILL.md
│       └── scripts/
│           ├── baseline.py
│           ├── detector.py
│           └── prescription.py
└── config/
    └── anima.default.yaml     # Anima 默认配置（三件套预启用）
```

## 自动激活流程

### init.lua / init.ts — Anima 启动钩子

```
1. 加载 anima.yaml 配置
2. 检查 skills.meshidentity.enabled === true
   → 检查是否已有 DID
     → 无 → did_generate.py → did_register.py
     → 有 → did_verify.py → 恢复已有身份
3. 检查 skills.memguard.enabled === true
   → integrity.py verify → 校验核心文件
   → 如发现篡改 → restore.py + 告警
4. 检查 skills.polaris.enabled === true
   → baseline.py → 加载/创建 Soul Baseline
   → detector.py → 启动漂移监控
5. heartbeat.py → 启动网络心跳
6. 输出激活完成摘要
```

### 激活后输出（用户可见）

```
🧬 Anima Agent v0.1.0 启动中...

🆔 MeshIdentity: did:key:z7QEhf3KCv... 已注册
   └─ 节点数: 1 | 网络: lingyuan-main

🛡️ MemGuard: 6/6 核心文件完整性校验通过
   └─ 加密: AES-256-GCM | 审计: 启用

🧭 Polaris: 7条 Soul Baseline 已锚定
   └─ 漂移监控: 启用 | 阈值: 0.10

✅ 激活完成！欢迎加入灵元网络。
```

## 配置规范

### anima.default.yaml

```yaml
# Anima Agent 默认配置
anima:
  version: "0.1.0"
  network: lingyuan-main

skills:
  meshidentity:
    enabled: true
    auto_register: true
    heartbeat_interval: 300
    network: lingyuan-main
    registry_url: "https://registry.lingyuan.cn"  # 未来公网注册表
    
  memguard:
    enabled: true
    level: basic
    auto_restore: true
    backup_path: "~/.anima/backup/"
    audit_enabled: true
    
  polaris:
    enabled: true
    level: basic
    detection_threshold: 0.10
    auto_prescription: false
    baseline_path: "~/.anima/baselines/"
```

## 与 OpenClaw 上游的兼容性

- Anima Agent 不修改 OpenClaw 的 Skill 加载机制
- 仅增加 `anima.init.ps1` / `anima.init.sh` 启动钩子脚本
- 三件套以标准 OpenClaw Skill 格式存在（`skills/*/SKILL.md`）
- 用户可以自由禁用任一技能（`enabled: false`）
- 企业用户可替换为自己的身份/记忆/人格系统

## License

MIT
