"""AWS Bedrock service for chatbot functionality"""

import json
import boto3
import time
from typing import Optional, List, Dict
from app.models.schemas import Message
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class BedrockService:
    """Service class for interacting with AWS Bedrock"""

    def __init__(self):
        """Initialize Bedrock client and Langfuse"""
        self.client = boto3.client('bedrock-runtime')
        self.default_model_id = settings.default_model_id

        # Initialize Langfuse for observability
        self.langfuse = settings._get_langfuse_client()

    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        model_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate a response using AWS Bedrock

        Args:
            message: User's input message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to guide assistant behavior
            model_id: Bedrock model ID to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        try:
            start_time = time.time()
            model_id = model_id or self.default_model_id

            # Use provided system prompt or load from file
            system = system_prompt or settings.load_system_prompt()

            # Build messages array
            messages = []
            if conversation_history:
                messages.extend([{"role": msg.role, "content": msg.content} for msg in conversation_history])
            messages.append({"role": "user", "content": message})

            # Prepare request body for Claude models
            if "anthropic.claude" in model_id:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system,
                    "messages": messages
                })
            else:
                # Add support for other models as needed
                body = json.dumps({
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system
                })

            # Create Langfuse generation span if available
            generation_context = None
            generation = None
            if self.langfuse and settings.use_langfuse:
                try:
                    generation_context = self.langfuse.start_as_current_generation(
                        name="bedrock-generation",
                        model=model_id,
                        input=messages,
                        model_parameters={
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    generation = generation_context.__enter__()
                except Exception as e:
                    logger.warning(f"Could not create Langfuse generation: {e}")
                    generation_context = None
                    generation = None

            # Invoke model
            logger.info(f"Invoking Bedrock model: {model_id}")
            response = self.client.invoke_model(
                modelId=model_id,
                body=body
            )

            # Calculate latency
            latency = time.time() - start_time

            # Parse response
            response_body = json.loads(response['body'].read())

            # Extract text and usage based on model type
            if "anthropic.claude" in model_id:
                response_text = response_body['content'][0]['text']
                usage = response_body.get('usage', {})
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
            else:
                response_text = response_body.get('completion', str(response_body))
                input_tokens = 0
                output_tokens = 0

            # Update Langfuse generation with output
            if generation and generation_context:
                try:
                    generation.update(
                        output=response_text,
                        usage_details={
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens
                        }
                    )
                    generation_context.__exit__(None, None, None)
                    self.langfuse.flush()
                except Exception as e:
                    logger.warning(f"Could not update Langfuse generation: {e}")

            logger.info("Successfully generated response")
            logger.info(f"Tokens: {input_tokens} input, {output_tokens} output | Latency: {latency:.2f}s")

            return response_text

        except Exception as e:
            # Close Langfuse generation on error
            if generation_context:
                try:
                    generation_context.__exit__(type(e), e, e.__traceback__)
                    self.langfuse.flush()
                except:
                    pass

            logger.error(f"Error generating response: {str(e)}")
            raise

    def list_available_models(self) -> List[str]:
        """
        List available Bedrock models

        Returns:
            List of model IDs
        """
        return [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-v2:1",
            "anthropic.claude-v2",
        ]
