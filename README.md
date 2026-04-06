# Jarvis
* 一个agent的学习实践仓库
* 参考自[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code/blob/main/README-zh.md)
* 感谢智谱提供的免费模型([glm-4.7-flash](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash))

## env
```bash
source .venv/bin/activate
uv sync
```

## zlm
```bash
export ZHIPUAI_API_KEY=xxxx
export LLM_MODEL=glm-4.7-flash
```

## run
```bash
uv run src/main.py
```