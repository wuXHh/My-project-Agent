from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@dataclass(frozen=True)
class LLMResult:
    text: str
    usage: LLMUsage
    raw: dict[str, Any] | None = None


class LLMClient(Protocol):
    def generate(self, *, task: str, prompt: str, temperature: float = 0.2, max_tokens: int = 1200) -> LLMResult: ...


class StubLLMClient:
    def generate(self, *, task: str, prompt: str, temperature: float = 0.2, max_tokens: int = 1200) -> LLMResult:
        # MVP: deterministic placeholder; real provider will return model outputs + usage.
        text = f"[stub:{task}]\n" + prompt[: min(len(prompt), 800)]
        usage = LLMUsage(input_tokens=len(prompt) // 4, output_tokens=min(max_tokens, len(text) // 4), cost_usd=0.0)
        return LLMResult(text=text, usage=usage, raw=None)


class ModelRouter:
    def __init__(self, provider: str = "stub"):
        self.provider = provider
        self._client: LLMClient = StubLLMClient()

    def client_for(self, task: str) -> LLMClient:
        # 预留：按 task 路由不同模型/温度/上下文窗口/供应商
        return self._client

