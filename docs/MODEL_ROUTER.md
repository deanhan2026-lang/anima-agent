# Anima Agent — 模型路由层规范

## 概述

Anima Agent 内置国产模型路由层，用户无需手动配置 API endpoint 即可使用主流国产模型。

## 支持的模型提供商

| 提供商 | 模型 | 类型 | 默认 |
|--------|------|------|------|
| DeepSeek | deepseek-chat / deepseek-reasoner | 对话/推理 | ✅ |
| 阿里 Qwen | qwen-max / qwen-plus / qwen-turbo | 对话 | — |
| MiniMax | abab6.5s / abab6.5 | 对话 | — |
| 智谱 GLM | glm-4-plus / glm-4-flash | 对话 | — |
| 月之暗面 | moonshot-v1-8k/32k/128k | 对话 | — |
| 豆包 | doubao-pro-32k | 对话 | — |
| 百度文心 | ernie-4.0-8k | 对话 | — |

## 路由层架构

```
用户发送消息
      │
      ▼
┌─────────────────┐
│  Anima Router   │
│  (模型路由层)    │
├─────────────────┤
│  默认: DeepSeek  │  ← 用户无需 API Key（Anima 内置池）
│  可选: 切换模型  │  ← 用户可自带 API Key
│  智能: 自动降级  │  ← 主模型不可用时切换备用
└────────┬────────┘
         │
    ┌────┼────┬─────────┬──────┐
    ▼    ▼    ▼         ▼      ▼
 DeepSeek Qwen MiniMax 豆包  用户自定义
```

## 配置

```yaml
# anima.yaml
model:
  default: deepseek-chat
  fallback:
    - qwen-plus
    - abab6.5s
  providers:
    deepseek:
      base_url: https://api.deepseek.com
      models:
        - deepseek-chat
        - deepseek-reasoner
    qwen:
      base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
      models:
        - qwen-max
        - qwen-plus
    minimax:
      base_url: https://api.minimaxi.com
      models:
        - abab6.5s
  user_providers:
    # 用户可自带 API Key
    enabled: true
```

## 使用方式

### 默认模式（Anima 内置）

用户安装 Anima Agent 后，无需配置任何 API Key，默认使用 Anima 内置的 DeepSeek Token 池。

```
anima gateway
# → 自动使用 deepseek-chat，无需额外配置
```

### 切换模型

```
# CLI
anima models set qwen-plus
anima models set minimax/abab6.5s
anima models list

# 或在 anima.yaml 中修改
```

### 自带 API Key

```
# 用户可使用自己的 API Key
anima auth add deepseek --api-key sk-xxx
anima auth add qwen --api-key sk-xxx
```

## Token 使用

| 模式 | 费用 | 说明 |
|------|------|------|
| **Anima 内置** | 按用量计费 | 价格 = 模型官方价（Anima 不溢价） |
| **自带 Key** | 用户自行承担 | 直接走用户自己账户 |
| **LingOS 订阅** | 套餐制 | 月付/年付含固定 Token 额度 |

## 技术实现

路由层基于 OpenClaw 的 Provider 机制，增加：
- 预配置的国产模型 endpoints
- 自动降级（fallback chain）
- 使用量统计
- Token 计费集成

```
src/core/model-router.ts
├── providers/
│   ├── deepseek.ts
│   ├── qwen.ts
│   ├── minimax.ts
│   └── ...
├── router.ts          # 路由决策引擎
├── fallback.ts        # 自动降级链
└── billing.ts         # Token 计费
```
