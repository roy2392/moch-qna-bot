# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

#### GET /

Health check endpoint for the service.

**Response:**
```json
{
  "status": "healthy",
  "service": "AWS Bedrock Chatbot"
}
```

#### GET /health

Alternative health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### Chat

#### POST /api/v1/chat

Send a message to the chatbot and receive a response.

**Request Body:**
```json
{
  "message": "string (required)",
  "conversation_history": [
    {
      "role": "string (user|assistant)",
      "content": "string"
    }
  ],
  "model_id": "string (optional)",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Parameters:**
- `message` (required): User's message
- `conversation_history` (optional): Array of previous messages
- `model_id` (optional): Bedrock model ID to use
- `temperature` (optional): Temperature for generation (0.0-1.0), default: 0.7
- `max_tokens` (optional): Maximum tokens to generate (1-4096), default: 2048

**Response:**
```json
{
  "response": "string",
  "model_id": "string"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

**Response Example:**
```json
{
  "response": "Quantum computing is a type of computing that...",
  "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
}
```

### Models

#### GET /api/v1/models

List all available Bedrock models.

**Response:**
```json
{
  "models": [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-v2:1",
    "anthropic.claude-v2"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/models"
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request
- `422`: Validation Error
- `500`: Internal Server Error

## Interactive Documentation

The service provides interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
