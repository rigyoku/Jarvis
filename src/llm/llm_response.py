import json
from typing import List, Dict, Any

class LLMResponse:
    response = ""
    thinking = ""
    total_duration = 0.0
    input_token = 0
    cached_token = 0
    output_token = 0
    tool_calls = []
    
    def __init__(self, response: str, thinking: str, total_duration: float, input_token: int, cached_token: int, output_token: int, tool_calls: List[Dict[str, Any]] = []):
        self.response = response
        self.thinking = thinking
        self.total_duration = total_duration
        self.input_token = input_token
        self.cached_token = cached_token
        self.output_token = output_token
        self.tool_calls = tool_calls
        
    def __str__(self):
        return f"{self.response}\nThinking: {self.thinking}\nTotal Duration: {self.total_duration}s\nInput Tokens: {self.input_token}\nCached Tokens: {self.cached_token}\nOutput Tokens: {self.output_token}\nTool Calls: {json.dumps(self.tool_calls, indent=2, ensure_ascii=False)}"
