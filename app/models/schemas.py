"""Pydantic schemas for request/response models"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message")
    conversation_history: Optional[List[Message]] = Field(
        default=None,
        description="Previous conversation history"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt to guide the assistant's behavior"
    )
    model_id: Optional[str] = Field(
        default=None,
        description="AWS Bedrock model ID to use"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for response generation"
    )
    max_tokens: Optional[int] = Field(
        default=2048,
        ge=1,
        le=4096,
        description="Maximum number of tokens to generate"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Bot's response")
    model_id: str = Field(..., description="Model ID used for generation")
