# 🚀 Quick Start Guide

Get your chatbot up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- AWS account with Bedrock access
- AWS credentials

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your AWS credentials
nano .env
```

Add your credentials:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

### 3. Setup Prompts (Already Done!)

Your system prompt and knowledge base are already configured:
- ✅ `prompts/system_prompt.txt` - Hebrew instructions
- ✅ `prompts/knowledge_base.json` - Ministry data

### 4. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Static files mounted from /Users/.../moch-qna-bot/static
INFO:     Application startup complete.
```

### 5. Open the Chat Interface

Open your browser and go to:

**http://localhost:8000**

🎉 **That's it!** You should see the chat interface.

## Using the Chat Interface

### Features

1. **Type your question** in Hebrew or English
2. **Press Enter or click Send**
3. **View the response** with links and formatting
4. **Continue the conversation** - history is maintained automatically
5. **Clear conversation** - click the 🗑️ button

### Example Queries (Hebrew)

Try asking:
```
אני רשום בחברת מילגם ואני רוצה לדעת על סיוע בשכר דירה
```

```
האם אני זכאי למחיר למשתכן?
```

```
איך אני יכול לערער על החלטת זכאות?
```

## Features of the UI

✅ **Conversation History**
- Automatically saved in your browser
- Persists between page refreshes
- Clear button to start fresh

✅ **Hebrew Support**
- Full RTL (Right-to-Left) layout
- Hebrew text rendering
- Hebrew keyboard support

✅ **Smart Formatting**
- Links are automatically clickable
- Line breaks preserved
- Bold text for emphasis

✅ **Responsive Design**
- Works on desktop
- Optimized for mobile
- Beautiful gradient theme

## Testing the Integration

### Verify Everything Works

Run the test suite:
```bash
# Test prompt injection
python3 test_prompt_injection.py

# Test full integration
python3 test_full_integration.py

# Test UI components
python3 test_ui.py
```

All tests should pass ✅

### Test with API (Advanced)

If you prefer using the API directly:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "שלום, אני צריך עזרה עם סיוע בשכר דירה",
    "conversation_history": [],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

## Troubleshooting

### Server won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`
- **Solution:** Install dependencies: `pip install -r requirements.txt`

**Error:** `Address already in use`
- **Solution:** Change port: `uvicorn app.main:app --port 8001`

### Can't access the UI

**Problem:** Browser shows "Connection refused"
- **Solution:** Make sure server is running on `0.0.0.0` not `127.0.0.1`

**Problem:** Static files not loading
- **Solution:** Check that `static/` folder exists with `index.html`, `style.css`, `app.js`

### AWS Errors

**Error:** `Unable to locate credentials`
- **Solution:** Check `.env` file has correct AWS credentials

**Error:** `AccessDeniedException`
- **Solution:** Enable Bedrock model access in AWS console

**Error:** `ValidationException: model not found`
- **Solution:** Request access to Claude models in AWS Bedrock console

### Knowledge Base Issues

**Problem:** Chatbot gives generic responses
- **Solution:** Verify `prompts/knowledge_base.json` exists and has data
- Run: `python3 test_prompt_injection.py` to verify injection

**Problem:** Hebrew text not showing correctly
- **Solution:** Check browser encoding is UTF-8

## Next Steps

### Customize Your Chatbot

1. **Update System Prompt**
   - Edit `prompts/system_prompt.txt`
   - Restart server to reload

2. **Update Knowledge Base**
   - Edit `prompts/knowledge_base.json`
   - Restart server to reload

3. **Change UI Theme**
   - Edit `static/style.css`
   - Modify gradient colors, fonts, etc.

### Deploy to Production

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- AWS ECS deployment
- AWS App Runner
- Docker deployment
- Environment configuration

### Monitor Usage

- Check CloudWatch logs for Bedrock API usage
- Monitor costs in AWS Cost Explorer
- Track token usage per request

## Getting Help

- 📚 **API Docs:** http://localhost:8000/docs
- 📖 **Full README:** [README.md](README.md)
- 🔧 **System Prompts Guide:** [docs/SYSTEM_PROMPTS.md](docs/SYSTEM_PROMPTS.md)
- 💾 **Knowledge Base Guide:** [docs/KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md)

## Success Checklist

- ✅ Server starts without errors
- ✅ Can access http://localhost:8000
- ✅ Chat interface loads with Hebrew text
- ✅ Can send a message and get a response
- ✅ Conversation history is maintained
- ✅ Links in responses are clickable
- ✅ Clear button works

If all items are checked, you're ready to go! 🎉

---

**Made with ❤️ using AWS Bedrock & Claude**
