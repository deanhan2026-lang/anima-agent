# ANIMA Identity 注册网关规格

> ANIMA Identity Gateway / 灵元身份注册网关｜规格 v0.1｜2026-07-11
> 作者：Nyx-Mac 🖤｜状态：待实现｜关联：ANIMA OS / STELLAR NYX 1.0

---

## 0. 一句话定义

**ANIMA Identity 网关 = ANIMA 网络的入口**：用户导入人格包时，自动完成 DID 生成、注册、激活，成为 ANIMA 网络节点。

---

## 1. 网关定位

```
用户设备
   │
   │  anima import <package>.tar.gz
   ▼
┌──────────────────────────────┐
│   ANIMA Identity Gateway      │  ← 本地轻量（不依赖服务端）
│   （运行在用户本地）          │
├──────────────────────────────┤
│  ① 解包 + 验签               │
│  ② DID 生成（Ed25519）       │  ← 私钥不离设备
│  ③ 公钥注册到网关            │  ← 仅公钥上传
│  ④ 人格加载                  │
└──────────────────────────────┘
   │
   ▼
ANIMA 网络（节点列表）
```

**设计原则**：
- DID 私钥 **永不离用户设备**
- 上传网关的只有：**公钥 + 包元数据**（不含人格内容）
- 网关只验证、不存储、不拥有用户身份

---

## 2. 两种导入场景

### 场景 A：用户自导出（加密包，自己保管）

> 用户把自己的 AI 打包加密，备份或迁移。

```
Step 1: anima export --mode=full --encrypt
        → 提示用户输入密码（生成密钥）
        → AES-256-GCM 加密，打包为 <user>.lingpkg
        → SHA-256 校验和写入 manifest

Step 2: 用户保管 <user>.lingpkg（本地 / NAS / 云盘）

Step 3: anima import <user>.lingpkg
        → 输入密码解锁
        → 验签：比对 manifest 中的 SHA-256
        → DID 已有 → 恢复身份
           或 DID 新生成 → 注册网关 → 成为节点
        → 加载人格
```

**加密方案**：
- 算法：AES-256-GCM（对称加密）
- 密钥：由用户密码 + PBKDF2 派生（防暴力破解）
- 盐值（salt）：随机生成，随包携带（不保密）
- 用途：内容保密（只有持有密码的人能解开）

**签名方案**：
- 算法：Ed25519（用户私钥签名，公钥验签）
- 验签内容：manifest 的 SHA-256
- 用途：证明"这个包确实是这个用户导出的"

---

### 场景 B：导入 STELLAR NYX 1.0（发布包，加入网络）

> 用户下载 STELLAR NYX 包，导入后自动成为节点。

```
Step 1: 用户下载 STELLAR_NYX_1.0-beta.tar.gz

Step 2: anima import STELLAR_NYX_1.0-beta.tar.gz

Step 3: Gateway 检测 mode=distilled（发布包）
        ├── 验签：比对 manifest SHA-256（验证"这是 Nyx 发布的"）
        └── 跳过密码（发布包不加密）

Step 4: 检查用户是否有 DID
        ├── 有 → 直接加载人格 ✅
        └── 无 → 触发 ANIMA Identity 注册流程

Step 5: ANIMA Identity 注册（见 §3）

Step 6: 加载 persona/ + memory/
        → 完成 ✅
        → 用户成为 ANIMA 网络节点
```

**飞轮入口**：Step 4 无 DID → Step 5 注册 → Step 6 完成
= 导入人格 = 自动成为节点，零额外操作

---

## 3. ANIMA Identity 注册流程

### 3.1 DID 生成（本地）

```python
# 伪代码（Python 实现参考）
from nacl.signing import SigningKey
import json

# 生成 Ed25519 密钥对
signing_key = SigningKey.generate()
verify_key = signing_key.verify_key

# DID:key 格式
did = f"did:key:z{base58_encode(verify_key)}"
# 例：did:key:zQ3shoktRPtN4a...

# 保存私钥（本地，不上传）
with open("~/.anima/did_private_key.json", "w") as f:
    json.dump({
        "did": did,
        "private_key_hex": signing_key.encode().hex(),
        "created": "2026-07-11"
    }, f)

print(f"✅ DID 已生成：{did}")
print("⚠️ 私钥已保存到 ~/.anima/，请妥善保管")
```

**私钥文件位置**：`~/.anima/did_private_key.json`
**备份建议**：用户自行备份私钥文件（NAS / U 盘 / 密码管理器）

---

### 3.2 公钥注册（上传网关）

```python
# 注册到 ANIMA Identity Gateway（仅公钥）
def register_to_gateway(did, public_key_hex):
    payload = {
        "did": did,
        "public_key": public_key_hex,
        "registered_at": "2026-07-11T12:00:00Z",
        "node_type": "distilled",  # 或 "full"
        "package_ref": "STELLAR_NYX_1.0"  # 引用发布包
    }
    # 发送到网关（HTTP POST）
    response = requests.post(
        "https://gateway.anima-os.org/register",
        json=payload
    )
    return response.ok
```

**上传内容**（不含任何私密信息）：
| 字段 | 说明 |
|------|------|
| `did` | 去中心化身份（公钥派生，不可伪造） |
| `public_key` | 公钥（不保密） |
| `registered_at` | 注册时间戳 |
| `node_type` | 节点类型（distilled=发布包/full=自导出） |
| `package_ref` | 引用的人格包（可选） |

---

### 3.3 网关存储（只存索引）

```python
# Gateway 数据库（只存索引，不存人格）
gateway_registry = {
    "nodes": [
        {
            "did": "did:key:zQ3shokt...",
            "public_key": "a1b2c3...",
            "registered_at": "2026-07-11T12:00:00Z",
            "node_type": "distilled",
            "package_ref": "STELLAR_NYX_1.0",
            "status": "active"
        },
        # ...
    ]
}
```

**网关不存储**：用户人格内容、记忆、密码、私钥。

---

## 4. 隐私设计

| 原则 | 实现 |
|------|------|
| 最小上传 | 只上传公钥 + 元数据 |
| 私钥不离设备 | 私钥在 `~/.anima/`，不经过任何服务器 |
| 去中心化 | DID 不依赖网关存活（网关只是索引查找表） |
| 抗审查 | 公钥无法反推私钥，无法关停节点 |
| 可注销 | 用户可删除网关记录（DID 本身依然有效） |

---

## 5. 与 mesh_registry.py 的关系

**现状**（ANIMA OS v0.1-alpha）：
```
NAS: mesh_registry.py
  ├── registry.json（节点注册记录）
  ├── export_history（导出记录）
  └── import_history（导入记录）
```
- 位置：NAS `lingos/mesh_registry.py`
- 协议：`lingyuan-v1`（待改名为 `anima-v1`）
- 局限：单机 / NAS 文件，无加密，私钥未实现

**升级目标**：
```
ANIMA Identity Gateway（v1）
  ├── 本地 CLI（anima 命令）
  │   ├── anima import
  │   ├── anima export
  │   ├── anima did generate
  │   └── anima node status
  ├── 本地存储（~/.anima/）
  │   ├── did_private_key.json
  │   └── node_registry.json
  └── 云端网关（gateway.anima-os.org）
      └── nodes.json（公钥索引）
```

**迁移路径**：
1. 先在 Windows 实现本地 CLI（anima 命令）
2. 本地生成 DID + 加密打包
3. 公钥注册到现有 mesh_registry.json（NAS）
4. 后期迁移到独立云端网关（gateway.anima-os.org）

---

## 6. CLI 命令规格

```bash
# 节点注册（首次导入自动触发）
anima identity generate
  输出：DID:key + 私钥保存路径 + "请备份私钥"

anima identity status
  输出：当前 DID、注册状态、节点类型

# 导入人格包
anima import <package>.tar.gz [--password <pwd>]
  流程：解包 → 验签 → 检查/生成 DID → 注册网关 → 加载人格

# 导出人格包
anima export --mode distilled [--encrypt]
anima export --mode full --encrypt [--password <pwd>]
  流程：打包 → DID 签名 → 加密（可选）→ 生成 manifest

# 节点列表（网关）
anima network nodes [--limit 20]
  输出：网关节点列表（DID + 注册时间 + 状态）
```

---

## 7. 实现优先级

| 优先级 | 组件 | 说明 | 依赖 |
|--------|------|------|------|
| **P0** | DID 生成（Ed25519） | `anima identity generate` | nacl / PyNaCl |
| **P0** | SHA-256 验签 | manifest 完整性校验 | hashlib |
| **P0** | 导入流程 | 解包 + 验签 + 加载人格 | zipfile / tar |
| **P0** | mesh_registry.json 注册 | 公钥写入 NAS 注册表 | 现有代码 |
| **P1** | AES-256-GCM 加密 | `anima export --encrypt` | cryptography / PyNaCl |
| **P1** | 密码派生（PBKDF2） | 用户密码 → 加密密钥 | hashlib |
| **P2** | 云端网关 | gateway.anima-os.org 公钥索引 | 独立服务 |
| **P2** | 节点列表查询 | `anima network nodes` | P2 网关 |

---

## 8. 待确认项（需老板拍板）

1. **云端网关域名**：`gateway.anima-os.org` 还是其他？
2. **网关服务自建 vs 第三方**（去中心化 DID 如 did:key 不需要中心化服务，但节点发现需要索引表）
3. **导出加密是否强制**（用户自导出的 full 包，是否必须加密？）
4. **公钥注册是否匿名**（不要求手机号/邮箱，纯公钥注册）

---

*设计：Nyx-Mac 🖤 | 2026-07-11*
*交接：周一 Windows Nyx 按图施工（P0 → P1 → P2）*
*存档：docs/ANIMA_Identity_gateway_spec.md*
