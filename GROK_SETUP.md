# Groq AI Integration Setup

AcademiaPro uses Groq for the visible AI support widget and authenticated AI API endpoints.

## Environment

Set your Groq API key:

```bash
GROQ_API_KEY=gsk-your-groq-api-key
```

Optional settings:

```bash
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TIMEOUT=90
GROQ_MAX_TOKENS=6000
```

## Live Website AI

The floating AI widget calls:

```text
POST /ai/chat/send
GET  /ai/chat/history
```

Responses are generated through Groq when `GROQ_API_KEY` is configured.

## Authenticated API Endpoints

These require login:

```text
POST /api/ai/chat
POST /api/ai/order-assistance
GET  /api/ai/conversation-history
```

Admin-only endpoints:

```text
POST /api/ai/admin/system-analysis
POST /api/ai/admin/content-review
POST /api/ai/admin/dispute-resolution
```

## Local Test

Start the app after setting `.env`, then send a message through the site AI widget. If Groq rejects the request, check that the key starts with `gsk_` and that the model is available in your Groq account.
