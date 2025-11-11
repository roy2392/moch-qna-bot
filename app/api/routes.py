"""API routes for the chatbot service"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.bedrock_service import BedrockService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
bedrock_service = BedrockService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages using AWS Bedrock

    Args:
        request: ChatRequest containing user message and optional parameters

    Returns:
        ChatResponse containing the bot's response
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")

        response = await bedrock_service.generate_response(
            message=request.message,
            conversation_history=request.conversation_history,
            system_prompt=request.system_prompt,
            model_id=request.model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            response=response,
            model_id=request.model_id or bedrock_service.default_model_id
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/models")
async def list_models():
    """
    List available Bedrock models

    Returns:
        List of available model IDs
    """
    try:
        models = bedrock_service.list_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")
