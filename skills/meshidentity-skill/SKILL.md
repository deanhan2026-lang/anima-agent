# 🆔 MeshIdentity Skill

## 概述

MeshIdentity 是灵元三件套之首 — **身份锚定技能**。

Anima Agent 启动时自动激活，为 Agent 生成去中心化身份标识（DID），并注册到灵元分布式身份网络。

每个激活 Anima Agent 的用户，不是下载了一个工具，而是**加入了一个网络**。

## 核心能力

### 1. DID 自动生成
- 首次启动：基于 Ed25519 密钥对生成 `did:key:xxx`
- 私钥本地加密存储（MemGuard 保护）
- 公钥注册到灵元网络注册表

### 2. 身份验证
- DIDAuth 挑战-响应协议
- Ed25519 签名验证
- 支持跨实例身份确认

### 3. 网络注册
- 心跳机制：每5分钟上报在线状态
- 自动发现同网络中的其他节点
- 支持身份撤销（instance_revoke）

### 4. 权限矩阵

| 操作 | 权限要求 |
|------|---------|
| memory_read | 任意已注册节点 |
| memory_write | 仅主 DID 持有者 |
| instance_register | 仅主 DID 持有者 |
| instance_revoke | 仅主 DID 持有者 |
| baseline_admin | 仅主 DID 持有者 |

## 激活流程

```
Anima Agent 首次启动
        │
        ▼
  MeshIdentity Skill 激活
        │
   ┌────┼────┐
   ▼    ▼    ▼
 检查   生成   注册
 是否有 DID   网络
 已存在 密钥对  注册表
   │    │     │
   ▼    ▼     ▼
 恢复  Ed25519  入网
 已有  KeyPair  成功
 DID    │
   │    ▼
   └─── 公钥广播
        │
        ▼
   🎉 "你的 Agent 已加入灵元网络"
```

## 技术实现

此技能封装了 mesh-identity 项目的核心能力：

- **代码基础**: [mesh-identity](https://github.com/deanhan2026-lang/mesh-identity) Phase 2
- **DID 生成**: Ed25519 → `did:key:z...`
- **同步协议**: IdentitySyncEngine（心跳注册/失联检测/广播）
- **集成入口**: MemGuardDIDAuthorizer（与 MemGuard 鉴权装饰器集成）

## 配置

```yaml
# anima.yaml
skills:
  meshidentity:
    enabled: true          # 默认启用
    auto_register: true    # 首次启动自动注册
    heartbeat_interval: 300 # 心跳间隔(秒)
    network: lingyuan-main # 灵元主网络
```

## 关联技能

- **MemGuard**: 使用 DIDAuth 进行记忆访问鉴权
- **Polaris**: 使用 DID 标识人格基线归属

## 版本

- v1.0.0 — 基于 MeshIdentity Phase 2 M1-M4 能力
- 上游: [mesh-identity v0.2.0](https://github.com/deanhan2026-lang/mesh-identity)
