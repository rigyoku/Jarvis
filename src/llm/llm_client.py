import os
import requests
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator
from logger import info

class LLMResponse:

    response = ""
    thinking = ""
    total_duration = 0.0
    input_token = 0
    cached_token = 0
    output_token = 0
    
    def __init__(self, response: str, thinking: str, total_duration: float, input_token: int, cached_token: int, output_token: int):
        self.response = response
        self.thinking = thinking
        self.total_duration = total_duration
        self.input_token = input_token
        self.cached_token = cached_token
        self.output_token = output_token
        
    def __str__(self):
        return f"Response: {self.response}\nThinking: {self.thinking}\nTotal Duration: {self.total_duration}s\nInput Tokens: {self.input_token}\nCached Tokens: {self.cached_token}\nOutput Tokens: {self.output_token}"

@decorator.singleton
class LLMClient:

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.model = os.getenv("LLM_MODEL", "qwen3.5:4b")
        self.api_key = os.getenv("LLM_API_KEY", "default_api_key")
        info(f"LLMClient initialized with provider: {self.provider}, model: {self.model}")
        

    def generate(self, prompt: str) -> LLMResponse:
        if self.provider == "ollama":
            return self._generate_ollama(prompt)
        return LLMResponse("Unsupported LLM provider", "", 0.0, 0, 0, 0)
    
    def _generate_ollama(self, prompt: str) -> LLMResponse:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt
        }
        response = ""
        thinking = ""
        total_duration = 0.0
        input_token = 0
        cached_token = 0
        output_token = 0
        with requests.post(url, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk and chunk["response"]:
                        response += chunk["response"]
                    if "thinking" in chunk and chunk["thinking"]:
                        thinking += chunk["thinking"]
                    if "total_duration" in chunk and chunk["total_duration"]:
                        total_duration = chunk["total_duration"]
                    if "prompt_eval_count" in chunk and chunk["prompt_eval_count"]:
                        input_token = chunk["prompt_eval_count"]
                    if "eval_count" in chunk and chunk["eval_count"]:
                        output_token = chunk["eval_count"]
                    if chunk.get("done", False):
                        break

        return LLMResponse(response, thinking, total_duration, input_token, cached_token, output_token)
    
if __name__ == "__main__":
    client = LLMClient()
    result = client.generate("你好")
    print(result)