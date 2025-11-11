# AWS Bedrock Chatbot Service

A simple, production-ready chatbot service built with FastAPI and AWS Bedrock, featuring Claude AI models.

## Features

- RESTful API built with FastAPI
- AWS Bedrock integration with Claude models
- Conversation history support
- Docker containerization
- Comprehensive logging
- Environment-based configuration
- Health check endpoints

## Project Structure

```
moch-qna-bot/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── bedrock_service.py # Bedrock integration
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py          # Logging configuration
│   ├── __init__.py
│   └── main.py                # FastAPI application
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration settings
├── docs/
│   ├── API.md                 # API documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── SYSTEM_PROMPTS.md      # System prompts guide
│   └── KNOWLEDGE_BASE.md      # Knowledge base integration guide
├── prompts/
│   ├── system_prompt.txt      # Your custom system prompt
│   ├── system_prompt.example.txt  # Example template
│   ├── knowledge_base.json    # Your data (auto-injected into prompt)
│   └── knowledge_base.example.json  # Example structure
├── static/
│   ├── index.html             # Chat UI
│   ├── style.css              # Styles
│   └── app.js                 # Frontend logic
├── tests/
│   ├── __init__.py
│   └── test_api.py            # API tests
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3.11+
- AWS account with Bedrock access
- AWS credentials configured
- Docker (optional, for containerized deployment)

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your AWS credentials
```

### 3. Setup System Prompt and Knowledge Base

```bash
# Copy example system prompt
cp prompts/system_prompt.example.txt prompts/system_prompt.txt

# Copy example knowledge base
cp prompts/knowledge_base.example.json prompts/knowledge_base.json

# Edit with your custom prompt and data
nano prompts/system_prompt.txt
nano prompts/knowledge_base.json
```

The knowledge base JSON will be automatically injected into the `<knowledge_base>` section of your system prompt. See [Knowledge Base Guide](docs/KNOWLEDGE_BASE.md) for details.

### 4. Run the Service

**Option A: Direct Python**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Docker Compose**
```bash
docker-compose up --build
```

### 5. Access the Application

**Web UI (Recommended):**
- 🌐 Chat Interface: http://localhost:8000

**API & Documentation:**
- 📚 API Documentation: http://localhost:8000/docs
- 💚 Health Check: http://localhost:8000/health
- 🔌 Chat Endpoint: http://localhost:8000/api/v1/chat

## Usage

### Web Interface

Open your browser and go to **http://localhost:8000** to access the chat interface.

**Features:**
- ✅ Hebrew (RTL) support
- ✅ Conversation history (persists in browser)
- ✅ Beautiful, responsive design
- ✅ Real-time typing indicators
- ✅ Clickable links in responses
- ✅ Clear conversation button
- ✅ Mobile-friendly

### API Usage

### Basic Chat Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### With Conversation History

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did we discuss earlier?",
    "conversation_history": [
      {"role": "user", "content": "Tell me about AWS Bedrock"},
      {"role": "assistant", "content": "AWS Bedrock is..."}
    ]
  }'
```

### List Available Models

```bash
curl "http://localhost:8000/api/v1/models"
```

## Configuration

Configure the service through environment variables or `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `DEFAULT_MODEL_ID` | Default Bedrock model | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `DEFAULT_TEMPERATURE` | Default temperature | `0.7` |
| `DEFAULT_MAX_TOKENS` | Default max tokens | `2048` |
| `SYSTEM_PROMPT_FILE` | Path to system prompt file | `prompts/system_prompt.txt` |
| `KNOWLEDGE_BASE_FILE` | Path to knowledge base JSON | `prompts/knowledge_base.json` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Available Models

- `anthropic.claude-3-sonnet-20240229-v1:0` (Default)
- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`
- `anthropic.claude-v2:1`
- `anthropic.claude-v2`

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to AWS and other platforms
- [System Prompts Guide](docs/SYSTEM_PROMPTS.md) - Customize the AI assistant's behavior
- [Knowledge Base Guide](docs/KNOWLEDGE_BASE.md) - Integrate JSON data into your prompts

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
