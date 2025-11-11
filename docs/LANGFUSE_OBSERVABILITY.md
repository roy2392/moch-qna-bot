# 🔍 Langfuse Observability & Tracing

## Overview

**YES!** All LLM requests are now automatically logged to Langfuse as traces. Every conversation with your chatbot is tracked with full observability.

---

## What Gets Logged

### Every LLM Call Records:

**1. Input Data:**
- User's message
- Full conversation history
- System prompt length
- Number of previous messages

**2. Output Data:**
- Generated response (full text)
- Response quality

**3. Token Usage:**
- Input tokens consumed
- Output tokens generated
- Total tokens used
- **Cost estimation** (Langfuse calculates automatically)

**4. Performance Metrics:**
- Latency (response time in seconds)
- Model used
- Temperature setting
- Max tokens setting

**5. Metadata:**
- Timestamp
- Model ID (e.g., `us.anthropic.claude-3-5-sonnet-20240620-v1:0`)
- Conversation length
- System prompt length (characters)

**6. Errors:**
- If generation fails, error details are logged
- Stack traces for debugging

---

## Trace Structure

Each chatbot request creates a **trace** in Langfuse:

```
Trace: bedrock-chat
├─ Generation: bedrock-generation
│  ├─ Input: [conversation messages]
│  ├─ Output: Generated response
│  ├─ Usage: {input: X tokens, output: Y tokens}
│  ├─ Latency: Z seconds
│  └─ Metadata: {model, temperature, etc.}
```

---

## Viewing Traces in Langfuse

### Step 1: Access Langfuse

```
https://cloud.langfuse.com
```

### Step 2: Navigate to Traces

Click on **"Traces"** in the left sidebar

### Step 3: View Your Traces

You'll see a list of all LLM calls:
- Timestamp
- Model used
- Input/Output tokens
- Latency
- Cost (estimated)

### Step 4: Click on a Trace

You can see:
- **Full conversation** (input messages)
- **Generated response** (output)
- **Token breakdown** (input vs output)
- **Timing** (latency graph)
- **Model parameters** (temperature, max_tokens)
- **Cost** (per trace)

---

## Example Trace

### What You'll See:

**Trace Name:** `bedrock-chat`
**Model:** `us.anthropic.claude-3-5-sonnet-20240620-v1:0`
**Timestamp:** 2025-11-11 13:30:55

**Input:**
```json
[
  {
    "role": "user",
    "content": "שלום, מה זה מחיר למשתכן?"
  }
]
```

**Output:**
```
שלום! מחיר למשתכן היא תכנית של משרד הבינוי והשיכון...
```

**Usage:**
- Input tokens: 12,543
- Output tokens: 387
- Total: 12,930 tokens
- **Cost:** ~$0.05 (estimated)

**Performance:**
- Latency: 4.23 seconds

**Metadata:**
- System prompt length: 40,503 characters
- Conversation length: 0 (new conversation)
- Temperature: 0.3
- Max tokens: 2048

---

## Benefits

### 1. Cost Tracking
- See exactly how much each conversation costs
- Track total spend over time
- Identify expensive queries
- Optimize prompts to reduce tokens

### 2. Performance Monitoring
- Track response latency
- Identify slow queries
- Monitor model performance over time
- Detect anomalies

### 3. Quality Assurance
- Review actual responses given to users
- Identify problematic responses
- Find edge cases
- Improve prompts based on real data

### 4. Debugging
- See full context of each interaction
- Trace errors back to specific inputs
- Understand why certain responses were generated
- Reproduce issues easily

### 5. Analytics
- Most common questions
- Average tokens per request
- Peak usage times
- Model comparison

---

## Dashboard Metrics

Langfuse provides automatic dashboards:

**Token Usage:**
- Total tokens (daily/weekly/monthly)
- Input vs Output ratio
- Tokens per trace (average)

**Costs:**
- Daily spend
- Cost per model
- Cost trends
- Budget alerts

**Latency:**
- Average response time
- P95/P99 latency
- Latency distribution
- Slow query identification

**Volume:**
- Requests per day
- Peak hours
- User engagement
- Error rate

---

## Configuration

### Toggle Observability

In `.env`:
```bash
USE_LANGFUSE=True  # Enable both prompt management and tracing
# Set to False to disable Langfuse completely
```

### Server Logs

You'll see additional logs:
```
INFO: Tokens: 12543 input, 387 output | Latency: 4.23s
```

If Langfuse tracing fails (network issues, etc.), the chatbot still works:
```
WARNING: Could not create Langfuse trace: Connection error
```

---

## Privacy & Data

### What's Logged to Langfuse:
- User messages (queries)
- Bot responses
- Conversation history
- Metadata (tokens, latency, etc.)

### What's NOT Logged:
- User authentication details
- IP addresses (unless you add them)
- Session IDs (unless you add them)

### Data Retention:
- Controlled by your Langfuse plan
- Can be deleted anytime from Langfuse UI
- Export available for backup

---

## Advanced Features

### 1. User Tracking

To track specific users, add to `app/api/routes.py`:

```python
trace = langfuse.trace(
    name="bedrock-chat",
    user_id="user_123",  # Add user ID
    session_id="session_abc"  # Add session ID
)
```

### 2. Tagging

Tag traces for organization:

```python
trace = langfuse.trace(
    name="bedrock-chat",
    tags=["production", "hebrew", "housing-ministry"]
)
```

### 3. Scoring

Add manual scores to traces:

```python
langfuse.score(
    trace_id=trace.id,
    name="quality",
    value=0.95
)
```

### 4. Feedback

Collect user feedback:

```python
langfuse.score(
    trace_id=trace.id,
    name="user-feedback",
    value=1 if user_liked else 0
)
```

---

## Querying Traces

### In Langfuse UI:

**Filter by:**
- Date range
- Model
- Token count
- Latency
- Cost
- Tags
- User ID

**Search by:**
- Input text (e.g., find all queries about "מחיר למשתכן")
- Output text
- Metadata

**Export:**
- CSV export
- API access
- Webhook integration

---

## Alerts & Monitoring

### Set Up Alerts:

1. **High Cost Alert:**
   - Notify if daily spend > $X

2. **High Latency Alert:**
   - Notify if latency > Y seconds

3. **Error Rate Alert:**
   - Notify if errors > Z%

4. **Token Spike Alert:**
   - Notify if tokens spike suddenly

---

## Best Practices

### 1. Regular Review
- Check traces daily/weekly
- Look for patterns
- Identify improvements

### 2. Cost Optimization
- Review high-token queries
- Optimize system prompt length
- Adjust max_tokens if needed

### 3. Quality Monitoring
- Sample random traces
- Check response quality
- Update few-shots based on real queries

### 4. Performance Tuning
- Monitor latency trends
- Identify bottlenecks
- Optimize slow queries

### 5. Privacy Compliance
- Review data retention policy
- Anonymize sensitive data
- Set up data deletion schedules

---

## Disabling Tracing

If you want prompt management but NOT tracing:

**Option 1: Disable Langfuse Completely**
```bash
# .env
USE_LANGFUSE=False
```

**Option 2: Modify Code** (config/settings.py)
```python
# Add a new setting
use_langfuse_tracing: bool = False
```

Then in bedrock_service.py:
```python
if self.langfuse and settings.use_langfuse and settings.use_langfuse_tracing:
    # Create traces
```

---

## Integration Status

✅ **What's Enabled:**
- Automatic trace creation for every LLM call
- Token usage tracking
- Latency monitoring
- Cost estimation
- Error logging
- Full input/output logging

✅ **Automatic Fallback:**
- If Langfuse is unavailable, tracing is skipped
- Chatbot continues to work normally
- No errors thrown to users

---

## Testing

Try your chatbot now at http://localhost:8000

**Then check Langfuse:**
1. Go to https://cloud.langfuse.com
2. Click "Traces"
3. You should see your test query!

**Look for:**
- Your input message
- The bot's response
- Token counts
- Response time
- Estimated cost

---

## Summary

🎉 **You now have full observability!**

**Every chat request logs:**
- ✅ Input (user query + history)
- ✅ Output (generated response)
- ✅ Tokens (input/output/total)
- ✅ Cost (estimated)
- ✅ Latency (response time)
- ✅ Metadata (model, settings, etc.)
- ✅ Errors (if any)

**View everything in Langfuse:**
- Real-time traces
- Cost dashboard
- Performance metrics
- Quality monitoring
- Export & analytics

**No impact on your chatbot:**
- Traces are async
- Falls back gracefully
- No user-facing changes
- Works with or without Langfuse

---

**Next Steps:**
1. Test your chatbot (http://localhost:8000)
2. Check Langfuse Traces (https://cloud.langfuse.com → Traces)
3. Explore the dashboards
4. Set up alerts (optional)

**Questions?**
- Langfuse Docs: https://langfuse.com/docs/tracing
- Your traces: https://cloud.langfuse.com/traces

---

**Created:** 2025-11-11
**Status:** ✅ Active & Logging
