# Grok API Integration Setup

This document explains how to set up and use the Grok AI integration in AcademiaPro.

## Configuration

### 1. Add Grok API Key

Set the `GROK_API_KEY` environment variable with your Grok API key:

```bash
# Local development (.env file)
GROK_API_KEY=gsk_your_actual_api_key_here

# Production (Render/Railway/etc)
# Add as environment variable in your deployment platform
```

### 2. Install Dependencies

The required `requests` library is already in `requirements.txt`. Just ensure you've installed it:

```bash
pip install -r requirements.txt
```

## API Endpoints

All AI endpoints require authentication (user must be logged in).

### Content Generation Endpoints

#### 1. Writer Help - Generate Content for Writers
```
POST /api/ai/writer-help
Content-Type: application/json

{
    "prompt": "Help me write an essay about climate change"
}

Response:
{
    "success": true,
    "content": "Generated content here..."
}
```

#### 2. Chat Support - Multi-turn Chat
```
POST /api/ai/chat
Content-Type: application/json

{
    "message": "How do I place an order?",
    "conversation_id": null  // optional, for continuing conversation
}

Response:
{
    "success": true,
    "response": "Here's how to place an order...",
    "conversation_id": 123
}
```

#### 3. Order Assistance
```
POST /api/ai/order-assistance
Content-Type: application/json

{
    "order_details": {
        "order_id": "12345",
        "subject": "Psychology Essay",
        "pages": 5,
        "deadline": "2024-06-25"
    },
    "question": "What should I include in the introduction?"
}

Response:
{
    "success": true,
    "assistance": "Based on your order, here's what to include..."
}
```

### Admin Endpoints

All admin endpoints require user.is_admin = True

#### 1. System Performance Analysis
```
POST /api/ai/admin/system-analysis
Content-Type: application/json

{
    "metrics": {
        "active_users": 150,
        "total_orders": 1240,
        "completed_orders": 1100,
        "pending_orders": 140,
        "response_time_ms": 250,
        "error_rate": 0.02,
        "db_queries_per_minute": 450
    }
}

Response:
{
    "success": true,
    "analysis": "Performance assessment and recommendations..."
}
```

#### 2. Content Review for Compliance
```
POST /api/ai/admin/content-review
Content-Type: application/json

{
    "content": "Essay content here...",
    "type": "essay"  // or "assignment", "paper", etc.
}

Response:
{
    "success": true,
    "review": "Quality assessment, compliance check, recommendations..."
}
```

#### 3. Dispute Resolution Assistance
```
POST /api/ai/admin/dispute-resolution
Content-Type: application/json

{
    "dispute_details": {
        "order_id": "12345",
        "buyer": "student@example.com",
        "writer": "writer@example.com",
        "issue": "Content quality concerns",
        "buyer_claims": "Content doesn't meet requirements",
        "writer_response": "All requirements were met"
    }
}

Response:
{
    "success": true,
    "resolution": "Analysis and recommended resolution..."
}
```

#### 4. Conversation History
```
GET /api/ai/conversation-history

Response:
{
    "success": true,
    "history": [
        {
            "id": 1,
            "context": "chat",
            "user_message": "How does the platform work?",
            "ai_response": "Here's how it works...",
            "created_at": "2024-06-24T10:30:00"
        },
        ...
    ]
}
```

## System Prompts

The AI follows different system prompts for different contexts to ensure appropriate behavior:

1. **writer_content_help** - Academic writing assistant
2. **chat_support** - Customer support assistant
3. **order_assistance** - Order management assistant
4. **admin_system_monitoring** - System performance analysis
5. **admin_content_review** - Content quality and compliance
6. **dispute_resolution** - Dispute mediation

Each prompt ensures the AI follows the mission and values of AcademiaPro.

## Frontend Integration Example

### JavaScript/HTML for Chat Widget

```html
<!-- Chat Widget HTML -->
<div id="ai-chat" class="chat-widget">
    <div class="chat-messages" id="chat-messages"></div>
    <div class="chat-input-area">
        <input type="text" id="chat-input" placeholder="Ask me anything...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
async function sendMessage() {
    const message = document.getElementById('chat-input').value;
    
    const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
    });
    
    const data = await response.json();
    
    if (data.success) {
        displayMessage('ai', data.response);
        document.getElementById('chat-input').value = '';
    }
}
</script>
```

## Conversation Storage

All AI conversations are stored in the `AIConversationMessage` table for:
- User reference and history
- Quality monitoring
- Training and improvement
- Compliance tracking

Access user's conversation history via: `GET /api/ai/conversation-history`

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad request (missing/invalid parameters)
- 403: Forbidden (admin endpoints, user not admin)
- 500: Server error

## Security Considerations

1. **API Key**: Never commit the actual API key to git. Use environment variables.
2. **Rate Limiting**: Consider adding rate limiting for AI endpoints
3. **Content Filtering**: Review user prompts for abuse
4. **Data Privacy**: Conversations are stored - ensure GDPR/privacy compliance
5. **Access Control**: Admin endpoints require authentication

## Monitoring

Monitor these metrics:
- API response times
- Error rates
- API usage per user
- Conversation length and frequency
- Admin feature usage

## Troubleshooting

### "GROK_API_KEY not configured"
- Ensure GROK_API_KEY environment variable is set
- On Render: Add to environment variables in service settings
- Local: Add to .env file

### API Timeouts
- Default timeout is 30 seconds
- Increase timeout in grok_service.py if needed

### Invalid API Key
- Verify the API key from Grok dashboard
- Check for extra spaces or formatting issues
- Regenerate key if suspected compromise

## Support

For issues or questions about the Grok integration:
1. Check the error message in API response
2. Review application logs
3. Contact Grok support for API-specific issues
