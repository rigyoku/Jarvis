# Jarvis
一个agent的学习实践仓库, 参考自[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code/blob/main/README-zh.md)

## env
```bash
source .venv/bin/activate
uv sync
```

## ollama
```bash
ollama run qwen3.5:4b
# ollama run qwen3.5:9b
# ollama run gemma4:e2b
```

## run
```bash
LLM_MODEL=gemma4:e2b
uv run src/main.py
```