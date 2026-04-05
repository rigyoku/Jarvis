import os
from typing import Callable, List, Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator
from logger import info
from llm.llm_response import LLMResponse

@decorator.singleton
class LLMClient:

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.model = os.getenv("LLM_MODEL", "qwen3.5:4b")
        self.api_key = os.getenv("LLM_API_KEY", "default_api_key")
        info(f"LLMClient initialized with provider: {self.provider}, model: {self.model}")

    def generate(self, messages: List[Dict[str, Any]], tools: List[Callable[..., Any]] | None = None) -> LLMResponse:
        if self.provider == "ollama":
            from llm.client_ollama import generate_ollama
            return generate_ollama(self.model, messages, tools)
        return LLMResponse("Unsupported LLM provider", "", 0.0, 0, 0, 0, [])
    
if __name__ == "__main__":
    client = LLMClient()
    messages = [{"role": "system", "content": "你是一个搞笑选手"}, {"role": "user", "content": "你好"}]
    result = client.generate(messages, [])
    info(result.response)