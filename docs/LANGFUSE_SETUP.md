# 🚀 Langfuse Integration Setup

## Overview

Your chatbot is now integrated with Langfuse for centralized prompt management. This allows you to:
- Edit prompts in the Langfuse UI
- Version control your prompts
- A/B test different versions
- Track prompt performance
- Collaborate with your team

## Current Status

✅ **Integration Complete:**
- Langfuse SDK installed and configured
- Settings updated to fetch from Langfuse with local file fallback
- Upload script created
- Prompts uploaded to Langfuse

⚠️ **Action Required:**
You need to manually set the prompts as "production" in the Langfuse UI (one-time setup)

---

## Setup Instructions

### Step 1: Upload Prompts (Already Done!)

The following prompts have been uploaded to Langfuse:
- `moch-system-prompt` - System prompt template
- `moch-knowledge-base` - Housing program data (JSON)
- `moch-few-shots` - Example query-response pairs (JSON)

### Step 2: Set Production Labels in Langfuse UI

**⚠️ IMPORTANT: You must complete this step for Langfuse integration to work!**

1. **Visit Langfuse:**
   ```
   https://cloud.langfuse.com
   ```

2. **Navigate to Prompts:**
   - Click on "Prompts" in the left sidebar

3. **For Each Prompt** (`moch-system-prompt`, `moch-knowledge-base`, `moch-few-shots`):

   a. **Click on the prompt name**

   b. **Find the latest version** (should be version 1 or 2)

   c. **Click the three dots (⋮) menu** next to the version

   d. **Select "Set as production"** or "Promote to production"

   e. **Confirm the action**

4. **Verify:**
   - Each prompt should now show a "production" label/badge
   - The version should be marked as the production version

### Step 3: Test the Integration

Run the test script to verify Langfuse is working:

```bash
python3 test_langfuse_integration.py
```

**Expected output:**
```
✅ Loaded knowledge base from Langfuse (version: 1)
✅ Loaded few-shots from Langfuse (version: 1)
✅ Loaded system prompt from Langfuse (version: 1)
```

If you still see `📁 Loaded from local file`, the production labels are not set correctly.

---

## How It Works

### Architecture

```
┌──────────────────────────────────────┐
│  Langfuse Cloud                      │
│  ├─ moch-system-prompt (production)  │
│  ├─ moch-knowledge-base (production) │
│  └─ moch-few-shots (production)      │
└────────────┬─────────────────────────┘
             │
             ↓ (Fetch on each request with 60s cache)
             │
┌────────────┴─────────────────────────┐
│  Your Chatbot (config/settings.py)  │
│  - Tries Langfuse first              │
│  - Falls back to local files         │
│  - Injects data into system prompt   │
└────────────┬─────────────────────────┘
             │
             ↓
┌────────────┴─────────────────────────┐
│  AWS Bedrock (Claude)                │
└──────────────────────────────────────┘
```

### Data Flow

**On each chatbot request:**

1. **Load System Prompt Template:**
   - Try: Fetch from Langfuse (`moch-system-prompt` with "production" label)
   - Fallback: Load from `prompts/system_prompt.txt`
   - Cache: 60 seconds

2. **Load Knowledge Base:**
   - Try: Fetch from Langfuse (`moch-knowledge-base`)
   - Fallback: Load from `prompts/knowledge_base.json`
   - Parse JSON and inject into `<knowledge_base>` tags

3. **Load Few-Shots:**
   - Try: Fetch from Langfuse (`moch-few-shots`)
   - Fallback: Load from `prompts/few_shots.json`
   - Parse JSON and inject into `<few_shot_examples>` tags

4. **Send to Claude:**
   - Complete prompt with injected data
   - User query + conversation history
   - Generate response

---

## Managing Prompts in Langfuse

### Editing a Prompt

1. Go to Langfuse → Prompts
2. Click on the prompt you want to edit
3. Click "New version" or "Edit"
4. Make your changes
5. Save
6. Set the new version as "production"
7. **Changes are reflected immediately** (after 60s cache expires)

### Example: Updating Knowledge Base

1. **In Langfuse UI:**
   - Navigate to "Prompts" → "moch-knowledge-base"
   - Click "New version"
   - Edit the JSON content
   - Save
   - Set as "production"

2. **Your chatbot will:**
   - Continue using cached version for up to 60 seconds
   - Then automatically fetch the new version
   - Start using updated data immediately
   - No server restart needed!

### Example: A/B Testing Prompts

1. **Create two versions:**
   - Version 1: Current system prompt
   - Version 2: New system prompt with different tone

2. **In Langfuse:**
   - Set Version 1 as "production" initially
   - Monitor performance/responses
   - When ready, promote Version 2 to "production"
   - Compare results

3. **Roll back if needed:**
   - Simply set Version 1 back as "production"

---

## Configuration

### Environment Variables

Your `.env` file already has:

```bash
# Langfuse Configuration
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

# Optional: Toggle Langfuse usage
USE_LANGFUSE=True  # Set to False to use only local files
```

### Prompt Names

Configured in `config/settings.py`:

```python
langfuse_system_prompt_name = "moch-system-prompt"
langfuse_knowledge_base_name = "moch-knowledge-base"
langfuse_few_shots_name = "moch-few-shots"
```

### Caching

- **Cache TTL:** 60 seconds
- **Purpose:** Reduce API calls to Langfuse
- **Behavior:** After fetching from Langfuse, the prompt is cached for 60 seconds
- **Update time:** Changes in Langfuse will take effect within 60 seconds

To modify cache duration, edit `config/settings.py`:
```python
prompt = client.get_prompt(name, cache_ttl_seconds=60)  # Change this value
```

---

## Fallback Mechanism

### When Langfuse is Unavailable

The chatbot automatically falls back to local files if:
- Langfuse API is down
- Network issues
- Invalid credentials
- Prompt not found in Langfuse
- Prompt doesn't have "production" label set

**Files used as fallback:**
- `prompts/system_prompt.txt`
- `prompts/knowledge_base.json`
- `prompts/few_shots.json`

**Advantage:** Your chatbot never goes down due to Langfuse issues!

### Logs

Check server logs to see which source is being used:

```bash
# Langfuse successful:
✅ Loaded knowledge base from Langfuse (version: 1)
✅ Loaded few-shots from Langfuse (version: 1)
✅ Loaded system prompt from Langfuse (version: 1)

# Fallback to local files:
📁 Loaded knowledge base from local file
📁 Loaded few-shots from local file
📁 Loaded system prompt from local file
```

---

## Updating Prompts

### Method 1: Via Langfuse UI (Recommended)

**Pros:**
- No code changes needed
- Version control built-in
- Instant rollback
- Team collaboration
- Change tracking

**Steps:**
1. Edit prompt in Langfuse UI
2. Create new version
3. Set as "production"
4. Done! (takes effect in <60 seconds)

### Method 2: Via Upload Script

**Use when:** You want to update from local files

**Steps:**
1. Edit local files:
   - `prompts/system_prompt.txt`
   - `prompts/knowledge_base.json`
   - `prompts/few_shots.json`

2. Run upload script:
   ```bash
   python3 upload_prompts_to_langfuse.py
   ```

3. In Langfuse UI, set the new versions as "production"

### Method 3: Local Files Only

**Use when:** You don't want to use Langfuse

**Steps:**
1. Set in `.env`:
   ```bash
   USE_LANGFUSE=False
   ```

2. Edit local files directly

3. Server will auto-reload (if `--reload` flag is set)

---

## Troubleshooting

### Issue: Prompts Not Loading from Langfuse

**Symptoms:**
```
Warning: Could not load ... from Langfuse
📁 Loaded ... from local file
```

**Solutions:**

1. **Check Production Label:**
   - Go to Langfuse → Prompts
   - Verify each prompt has a version marked as "production"
   - If not, set it manually (see Step 2 above)

2. **Check Credentials:**
   - Verify `.env` has correct Langfuse keys
   - Test connection:
     ```bash
     python3 -c "from langfuse import Langfuse; from config.settings import settings; print(Langfuse(secret_key=settings.langfuse_secret_key, public_key=settings.langfuse_public_key).get_client_id())"
     ```

3. **Check Prompt Names:**
   - In Langfuse, verify prompts are named exactly:
     - `moch-system-prompt`
     - `moch-knowledge-base`
     - `moch-few-shots`
   - Names are case-sensitive

4. **Check Network:**
   - Ensure server can reach `https://cloud.langfuse.com`
   - Check firewall/proxy settings

### Issue: Changes Not Reflecting

**Cause:** Cache (60 seconds)

**Solutions:**
1. Wait 60 seconds after setting new version as production
2. Restart server to clear cache immediately:
   ```bash
   # Find and kill server
   pkill -f uvicorn

   # Start fresh
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Issue: Upload Script Fails

**Common errors:**

**Error: "Invalid credentials"**
- Check `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` in `.env`

**Error: "Prompt already exists"**
- This is OK! It creates a new version
- Set the new version as "production" in Langfuse UI

---

## Best Practices

### 1. Always Test After Changes

```bash
# Test integration
python3 test_langfuse_integration.py

# Test actual chatbot response
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "שלום, מה זה מחיר למשתכן?"}'
```

### 2. Use Versioning Strategically

- **Patch changes:** Minor text tweaks, typo fixes
- **Minor changes:** Adding examples, updating links
- **Major changes:** Complete prompt rewrites

Label versions clearly in Langfuse (use tags/labels).

### 3. Monitor Performance

Langfuse provides analytics:
- View prompt versions used
- Track response quality
- Compare different versions
- Monitor costs

### 4. Keep Local Files in Sync

Even though you're using Langfuse, keep local files updated:
1. They serve as backup
2. Useful for development/testing
3. Required for fallback mechanism

### 5. Document Changes

In Langfuse, add notes when creating new versions:
- What changed
- Why it changed
- Expected impact

---

## Advanced Usage

### Custom Labels

Instead of "production", you can use custom labels:

**In code (`config/settings.py`):**
```python
prompt = client.get_prompt(name, label="staging")  # or "testing", "v2", etc.
```

**In Langfuse:**
- Set different versions with different labels
- Switch between them by changing code

### Multiple Environments

**Development:**
```bash
# .env.development
USE_LANGFUSE=False  # Use local files for dev
```

**Production:**
```bash
# .env.production
USE_LANGFUSE=True  # Use Langfuse in prod
```

### Observability

Langfuse tracks:
- Which prompt versions are used
- When they're fetched
- Cache hit rates
- Performance metrics

Check the Langfuse dashboard for insights!

---

## Summary

✅ **What's Done:**
1. Langfuse SDK installed
2. Code updated to fetch from Langfuse
3. Fallback mechanism implemented
4. Prompts uploaded to Langfuse
5. 60-second caching configured

⚠️ **What You Need to Do:**
1. Visit https://cloud.langfuse.com
2. Go to "Prompts" section
3. Set each prompt version as "production"
4. Run `python3 test_langfuse_integration.py` to verify

🎉 **Once Complete:**
- Edit prompts in Langfuse UI
- Changes reflect in <60 seconds
- No code changes or restarts needed
- Full version control and team collaboration
- Built-in fallback for reliability

---

**Need Help?**
- Langfuse Docs: https://langfuse.com/docs
- Langfuse Discord: https://discord.gg/7NXusRtqYU

**Created:** 2025-11-11
**Status:** Ready (pending production label setup)
