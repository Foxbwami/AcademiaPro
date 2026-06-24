# Deploying Grok AI Integration on Render

## Setting Up the Grok API Key on Render

Your Grok AI integration is now deployed! Follow these steps to configure the API key on your Render service.

### Step 1: Go to Render Dashboard

1. Navigate to [render.com](https://render.com)
2. Log in to your account
3. Find your "academia-pro" web service

### Step 2: Add Environment Variable

1. Click on your **academia-pro** service
2. Go to the **Environment** tab
3. Click **Add Environment Variable**
4. Fill in the following:
   - **Key**: `GROK_API_KEY`
   - **Value**: `gsk_your_actual_api_key_from_grok_dashboard`
5. Click **Save Changes**

### Step 3: Redeploy

1. Go to the **Deployments** tab
2. Click the three dots menu next to your latest deployment
3. Select **Redeploy** (or wait for auto-redeploy if enabled)
4. The service will restart with the new environment variable

## Available AI Features

Once deployed, you can use these AI endpoints:

### For Users/Writers
- **POST /api/ai/writer-help** - Content generation assistance
- **POST /api/ai/chat** - Chat support
- **POST /api/ai/order-assistance** - Order help
- **GET /api/ai/conversation-history** - View conversation history

### For Admins
- **POST /api/ai/admin/system-analysis** - Analyze system performance
- **POST /api/ai/admin/content-review** - Review content for compliance
- **POST /api/ai/admin/dispute-resolution** - Assist with dispute resolution

## Testing the Integration

### Test Writer Help
```bash
curl -X POST https://your-render-url/api/ai/writer-help \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "prompt": "Help me write an introduction to an essay about climate change"
  }'
```

### Test Chat Support
```bash
curl -X POST https://your-render-url/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "message": "How do I place an order?"
  }'
```

## Troubleshooting

### "GROK_API_KEY not configured"
- Ensure the environment variable is set in Render dashboard
- After adding, you must redeploy the service
- Check the deployment logs to verify it was picked up

### API Timeouts or Errors
- Check Render logs: **Logs** tab in service dashboard
- Ensure your Grok API key is valid
- Check if Grok API is experiencing issues

### View Deployment Logs
1. Click your service
2. Go to **Logs** tab
3. Filter by recent entries to see startup messages

## Next Steps

### Frontend Integration (Optional)
Add a chat widget to your website:

```html
<!-- In your base template -->
<div id="ai-chat" class="chat-widget">
    <div class="chat-messages" id="chat-messages"></div>
    <input type="text" id="chat-input" placeholder="Ask a question...">
    <button onclick="sendMessage()">Send</button>
</div>

<script>
async function sendMessage() {
    const message = document.getElementById('chat-input').value;
    const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
    });
    const data = await response.json();
    if (data.success) {
        console.log('Response:', data.response);
    }
}
</script>
```

### Monitor AI Usage
- Check conversation history: **GET /api/ai/conversation-history**
- Review admin logs for feature usage
- Monitor API response times in Render metrics

## Verification Checklist

- [ ] Grok API key added to Render environment variables
- [ ] Service redeployed with new environment variable
- [ ] No errors in deployment logs
- [ ] Can access /api/ai/chat endpoint (requires login)
- [ ] AI responses are working as expected
- [ ] Conversations are being stored in database

## Support

For issues:
1. Check [GROK_SETUP.md](./GROK_SETUP.md) for API documentation
2. Review deployment logs in Render dashboard
3. Verify API key is correct and active
4. Contact Grok support for API-specific issues

## Security Notes

- Never commit actual API keys to git (use .env files)
- The API key is now secure in Render's environment variables
- All conversations are stored in your database
- Implement rate limiting if needed to prevent abuse
- Monitor for unusual API usage patterns
