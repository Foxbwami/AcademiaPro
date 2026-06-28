# Deploying Groq AI on Render

In your Render service, open **Environment** and add:

```text
GROQ_API_KEY=gsk-your-real-groq-api-key
```

Optional:

```text
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TIMEOUT=90
GROQ_MAX_TOKENS=6000
```

Redeploy after saving environment variables.

## Troubleshooting

- If the widget says the AI provider is unavailable, confirm `GROQ_API_KEY` is set and redeploy.
- If Groq returns a model error, set `GROQ_MODEL` to a model enabled for your Groq account.
- If responses are short, increase `GROQ_MAX_TOKENS`.
- If requests time out, increase `GROQ_TIMEOUT`.
