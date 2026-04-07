# Jarvis
* 一个agent的学习实践仓库
* 参考自[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code/blob/main/README-zh.md)
* 感谢智谱提供的免费模型([glm-4.7-flash](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash))
* 感谢google提供的免费模型([gemini-3.1-flash-lite-preview](https://ai.google.dev/gemini-api/docs/pricing?utm_source=google&utm_medium=cpc&utm_campaign=Cloud-SS-DR-AIS-FY26-global-gsem-1713578&utm_content=text-ad&utm_term=KW_gemini%20api&gad_source=1&gad_campaignid=23417416052&gbraid=0AAAAACn9t66YCSKMGJygypn2PXdP7rM4g&gclid=Cj0KCQjws83OBhD4ARIsACblj1_viDn2TdetSJzuWfdfCkOHkhTzkpJxbvLkZM5eAd6aZExwx7ExQfgaAsMlEALw_wcB&hl=zh-cn#gemini-2.5-flash))

## env
```bash
source .venv/bin/activate
uv sync
```

## zlm
```bash
export LLM_API_KEY=xxxx
export LLM_MODEL=glm-4.7-flash
export LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4/
```

## gemini
```bash
export LLM_API_KEY=xxxx
export LLM_MODEL=gemini-3.1-flash-lite-preview
export LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4/
```

## run
```bash
uv run src/main.py
```