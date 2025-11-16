"""API routes for the chatbot service"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint that processes user messages using AWS Bedrock
    and returns Server-Sent Events (SSE)

    Args:
        request: ChatRequest containing user message and optional parameters

    Returns:
        StreamingResponse with text/event-stream content
    """
    import asyncio

    try:
        logger.info(f"Received streaming chat request: {request.message[:50]}...")

        async def generate():
            try:
                # Run the synchronous generator in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                generator = bedrock_service.generate_response_stream(
                    message=request.message,
                    conversation_history=request.conversation_history,
                    system_prompt=request.system_prompt,
                    model_id=request.model_id,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )

                # Iterate over the generator, yielding control between chunks
                for chunk in generator:
                    # Send as Server-Sent Event
                    yield f"data: {chunk}\n\n"
                    # Yield control to event loop to prevent blocking
                    await asyncio.sleep(0)

                # Send completion signal
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error in streaming generation: {str(e)}")
                yield f"data: [ERROR: {str(e)}]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable buffering in nginx
            }
        )
    except Exception as e:
        logger.error(f"Error processing streaming chat request: {str(e)}")
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
