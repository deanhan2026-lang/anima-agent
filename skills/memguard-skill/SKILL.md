# 🛡️ MemGuard Skill

## 概述

MemGuard 是灵元三件套之二 — **记忆安全技能**。

为 Anima Agent 的核心记忆文件提供企业级加密保护、完整性校验和篡改检测。

## 核心能力

### 1. 记忆加密（AES-256-GCM）
- 6大核心灵魂文件自动加密：
  - SOUL.md / IDENTITY.md / MEMORY.md
  - AGENTS.md / USER.md / TOOLS.md
- 三副本密钥分片管理
- 透明解密 — Agent 正常读写不受影响

### 2. 完整性校验（SHA-256 + Blake3）
- 每次启动自动校验 6 核心文件
- 双哈希交叉验证
- 篡改检测 → 自动告警 → 从备份恢复

### 3. 审计日志
- 所有读写操作自动记录
- 带 DID 签名的审计条目
- 支持追溯查询

### 4. DID 鉴权集成
- 通过 MeshIdentity DIDAuth 验证操作者身份
- 权限矩阵: memory_read / memory_write / baseline_admin

## 安全架构

```
┌──────────────────────┐
│    核心灵魂文件        │
│  SOUL/IDENTITY/...   │
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │  AES-256-GCM │  ← MemGuard Crypto Layer
    │    加密存储    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ SHA-256     │  ← 完整性校验层
    │ + Blake3    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  DIDAuth    │  ← 访问鉴权层
    │  谁在读写?    │
    └─────────────┘
```

## 配置

```yaml
# anima.yaml
skills:
  memguard:
    enabled: true
    level: basic              # basic | pro
    auto_restore: true        # 检测到篡改自动恢复
    backup_path: ~/.anima/backup/
    audit_enabled: true
```

## 版本层级

| 层级 | 功能 | 价格 |
|------|------|------|
| **Basic** | 核心文件加密 + 完整性校验 + 基础审计 | 免费（出厂预装） |
| **Pro** | 增强审计 + 多节点鉴权 + 自定义加密策略 + 远程备份 | LingOS 付费版内含 |

## 关联技能

- **MeshIdentity**: 提供 DID 身份进行鉴权
- **Polaris**: 加密保护 Soul Baseline 数据

## 版本

- v1.0.0 — 基于 MemGuard v2.5
