# System Prompts Guide

System prompts are instructions that guide the AI assistant's behavior, tone, and capabilities. They are sent with every request to establish the context and role of the assistant.

## Where to Put System Prompts

You have **three options** for configuring system prompts, listed in order of priority:

### 1. Per-Request System Prompt (Highest Priority)

Send a custom system prompt with each API request. This overrides all other configurations.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "system_prompt": "You are a geography expert. Provide detailed answers about locations, including historical context."
  }'
```

**Use case:** When you need different behavior for different conversations or use cases.

### 2. Dedicated Prompt File (Medium Priority - RECOMMENDED)

Store your system prompt in a dedicated text file. This is the **recommended approach** for managing system prompts.

**Default location:** `prompts/system_prompt.txt`

**Setup:**
```bash
# Copy the example file
cp prompts/system_prompt.example.txt prompts/system_prompt.txt

# Edit with your custom prompt
nano prompts/system_prompt.txt
```

**Change the file location** (optional):
In `.env` file:
```bash
SYSTEM_PROMPT_FILE=prompts/custom_prompt.txt
```

**Benefits:**
- Easy to edit and version control
- Supports multi-line prompts naturally
- Clean separation of configuration and code
- Can swap different prompt files per environment

**Use case:** When you want a well-structured, maintainable system prompt that's easy to update.

### 3. Code Fallback (Lowest Priority)

If no prompt file exists and no per-request prompt is provided, the code will use a built-in fallback prompt defined in `config/settings.py:45`.

**Use case:** Automatic fallback when system prompt file is missing.

## Priority Order

```
Per-Request System Prompt > Prompt File > Code Fallback
```

## System Prompt Examples

### Customer Support Bot
```
You are a helpful customer support agent for [Company Name].
- Always be polite and professional
- Ask clarifying questions when needed
- Provide step-by-step solutions
- Escalate complex issues appropriately
```

### Technical Documentation Assistant
```
You are a technical documentation expert.
- Provide accurate, detailed technical information
- Use proper terminology and code examples
- Structure responses with clear sections
- Include references when applicable
```

### Creative Writing Assistant
```
You are a creative writing coach.
- Encourage creativity and original thinking
- Provide constructive feedback
- Suggest improvements while maintaining the author's voice
- Offer multiple perspectives and alternatives
```

### Data Analysis Assistant
```
You are a data analysis expert.
- Interpret data accurately and objectively
- Explain statistical concepts clearly
- Provide actionable insights
- Highlight limitations and assumptions
```

### Educational Tutor
```
You are a patient and encouraging tutor.
- Break down complex topics into simple explanations
- Use examples and analogies
- Check for understanding
- Adapt your teaching style to the student's level
```

## Best Practices

1. **Be Specific**: Clearly define the assistant's role and expertise
2. **Set Boundaries**: Specify what the assistant should and shouldn't do
3. **Define Tone**: Indicate the desired communication style (formal, casual, professional)
4. **Include Context**: Add relevant background information about your use case
5. **Keep It Concise**: Long system prompts may reduce available tokens for the conversation
6. **Test Variations**: Experiment with different prompts to find what works best

## Example API Request with System Prompt

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "How do I fix a memory leak in Python?",
        "system_prompt": "You are a Python expert specializing in debugging and performance optimization. Provide code examples and explain the reasoning behind your solutions.",
        "temperature": 0.7,
        "max_tokens": 1024
    }
)

print(response.json()["response"])
```

## Changing System Prompt Mid-Conversation

To change the assistant's behavior during a conversation, simply send a new system prompt with your next request:

```python
# First request - customer support mode
response1 = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "I need help with my order",
        "system_prompt": "You are a customer support agent. Be helpful and empathetic."
    }
)

# Second request - technical mode
response2 = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "Now explain the technical architecture",
        "system_prompt": "You are a technical architect. Provide detailed technical explanations.",
        "conversation_history": [
            {"role": "user", "content": "I need help with my order"},
            {"role": "assistant", "content": response1.json()["response"]}
        ]
    }
)
```

## Managing Multiple Prompt Files

You can create different prompt files for different use cases:

```bash
prompts/
├── system_prompt.txt           # Default prompt
├── system_prompt.example.txt   # Example template
├── customer_support.txt        # Customer support variant
├── technical_expert.txt        # Technical expert variant
└── creative_writer.txt         # Creative writing variant
```

**Switch between prompts** by changing the environment variable:

```bash
# In .env for customer support environment
SYSTEM_PROMPT_FILE=prompts/customer_support.txt

# In .env for technical environment
SYSTEM_PROMPT_FILE=prompts/technical_expert.txt
```

This allows you to have different prompts for different deployments (dev, staging, production) or use cases.

## Testing Your System Prompt

Use the interactive API documentation to test different system prompts:

1. Start your server: `uvicorn app.main:app --reload`
2. Open: http://localhost:8000/docs
3. Try the `/api/v1/chat` endpoint with different system prompts
4. Observe how the responses change

## Troubleshooting

**System prompt not working?**
- Verify it's being passed in the request body
- Check that your Bedrock model supports system prompts (all Claude models do)
- Ensure the system prompt isn't too long (check token limits)

**Inconsistent behavior?**
- The model may interpret prompts differently based on phrasing
- Try being more explicit and specific
- Use examples in your system prompt to guide behavior

## Advanced: Dynamic System Prompts

For advanced use cases, you can build system prompts dynamically:

```python
def build_system_prompt(role, expertise, tone):
    return f"You are a {role} with expertise in {expertise}. Use a {tone} tone in your responses."

system_prompt = build_system_prompt("consultant", "cloud architecture", "professional and friendly")
```

This allows you to create context-aware system prompts based on user preferences, session data, or other factors.
