"""
ANIMA AGENT — Model Router
Multi-model routing with smart fallback.

Strategy:
  L1 Default:  GLM-4-Flash (永久免费, daily conversation)
  L2 Reasoning: DeepSeek V4 (深度推理)
  L3 Long Context: Kimi / GLM-4.7-Flash (256K / 200K context)
  L4 Fallback:  SiliconFlow aggregator (聚合兜底)
"""

from enum import Enum
from typing import Optional
import json
from pathlib import Path


class ModelTier(str, Enum):
    DEFAULT = "default"       # GLM-4-Flash — everyday
    REASONING = "reasoning"   # DeepSeek V4 — deep think
    LONG_CTX = "long_context" # Kimi — large context windows
    FALLBACK = "fallback"     # Aggregator — last resort


class ModelEndpoint:
    """A single model endpoint configuration."""
    def __init__(
        self,
        name: str,
        provider: str,
        base_url: str,
        model_id: str,
        tier: ModelTier,
        api_key_env: str = "",
        max_context: int = 128_000,
        cost_per_million: float = 0.0,
        is_free: bool = False,
    ):
        self.name = name
        self.provider = provider
        self.base_url = base_url
        self.model_id = model_id
        self.tier = tier
        self.api_key_env = api_key_env
        self.max_context = max_context
        self.cost_per_million = cost_per_million
        self.is_free = is_free


# ─── DEFAULT MODEL REGISTRY ───

DEFAULT_MODELS = {
    "glm-4-flash": ModelEndpoint(
        name="GLM-4-Flash",
        provider="zhipu",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        model_id="glm-4-flash",
        tier=ModelTier.DEFAULT,
        api_key_env="GLM_API_KEY",
        max_context=128_000,
        is_free=True,
    ),
    "deepseek-v4": ModelEndpoint(
        name="DeepSeek V4",
        provider="deepseek",
        base_url="https://api.deepseek.com",
        model_id="deepseek-chat",
        tier=ModelTier.REASONING,
        api_key_env="DEEPSEEK_API_KEY",
        max_context=64_000,
        cost_per_million=0.27,
    ),
    "kimi": ModelEndpoint(
        name="Kimi (Moonshot)",
        provider="moonshot",
        base_url="https://api.moonshot.cn/v1",
        model_id="moonshot-v1-128k",
        tier=ModelTier.LONG_CTX,
        api_key_env="MOONSHOT_API_KEY",
        max_context=256_000,
        cost_per_million=12.0,
    ),
    "siliconflow": ModelEndpoint(
        name="SiliconFlow Aggregator",
        provider="siliconflow",
        base_url="https://api.siliconflow.cn/v1",
        model_id="Qwen/Qwen2.5-7B-Instruct",
        tier=ModelTier.FALLBACK,
        api_key_env="SILICONFLOW_API_KEY",
        max_context=32_000,
        is_free=True,
    ),
}

# ─── ROUTING MATH ───

REASONING_KEYWORDS = [
    "分析", "推理", "为什么", "怎么", "原因",
    "解释", "原理", "证明", "论证", "逻辑",
    "analyze", "reason", "explain", "why", "how",
    "prove", "check", "verify", "debug", "review",
]

LONG_CTX_KEYWORDS = [
    "总结", "摘要", "全文", "长文", "文档",
    "summarize", "summary", "全文阅读", "大文件",
]


def classify_request(content: str, context_length: int = 0) -> ModelTier:
    """
    Classify a request to determine which model tier to use.

    Heuristic:
      1. Explicit context size → LONG_CTX
      2. Reasoning keywords → REASONING
      3. Default → DEFAULT
    """
    lower = content.lower()

    if context_length > 64_000:
        return ModelTier.LONG_CTX

    for kw in LONG_CTX_KEYWORDS:
        if kw.lower() in lower:
            return ModelTier.LONG_CTX

    for kw in REASONING_KEYWORDS:
        if kw.lower() in lower:
            return ModelTier.REASONING

    return ModelTier.DEFAULT


def get_route(content: str, context_length: int = 0) -> dict:
    """
    Determine the model route for a request.

    Returns dict compatible with OpenClaw model config.
    """
    tier = classify_request(content, context_length)

    # Route mapping (tier → preferred model)
    route_map = {
        ModelTier.DEFAULT: DEFAULT_MODELS["glm-4-flash"],
        ModelTier.REASONING: DEFAULT_MODELS["deepseek-v4"],
        ModelTier.LONG_CTX: DEFAULT_MODELS["kimi"],
    }

    primary = route_map[tier]
    fallback_chain = [
        {
            "provider": "openai-compatible",
            "base_url": DEFAULT_MODELS["siliconflow"].base_url,
            "model": DEFAULT_MODELS["siliconflow"].model_id,
        }
    ]

    return {
        "tier": tier.value,
        "model": primary.name,
        "provider": primary.provider,
        "base_url": primary.base_url,
        "model_id": primary.model_id,
        "max_context": primary.max_context,
        "is_free": primary.is_free,
        "fallback_chain": fallback_chain,
    }


def get_model_list() -> list[dict]:
    """Return all registered models with tier info."""
    models = []
    for key, ep in DEFAULT_MODELS.items():
        models.append({
            "key": key,
            "name": ep.name,
            "tier": ep.tier.value,
            "max_context": ep.max_context,
            "is_free": ep.is_free,
            "cost_per_million": ep.cost_per_million,
        })
    return models


def get_openclaw_config() -> dict:
    """Generate OpenClaw-compatible model configuration."""
    config = {
        "models": {}
    }

    for key, ep in DEFAULT_MODELS.items():
        api_key_env = ep.api_key_env if ep.api_key_env else "ANIMA_API_KEY"
        config["models"][key] = {
            "provider": "openai-compatible",
            "base_url": ep.base_url,
            "api_key": f"${{{api_key_env}}}",
            "model": ep.model_id,
            "context_window": ep.max_context,
        }

    return config
