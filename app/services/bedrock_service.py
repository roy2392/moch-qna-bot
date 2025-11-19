"""AWS Bedrock service for chatbot functionality"""

import json
import boto3
import time
from typing import Optional, List
from app.models.schemas import Message
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class BedrockService:
    """Service class for interacting with AWS Bedrock"""

    def __init__(self):
        """Initialize Bedrock client and Langfuse"""
        self.client = boto3.client('bedrock-runtime', region_name=settings.aws_region)
        self.default_model_id = settings.default_model_id

        # Initialize Langfuse for observability
        self.langfuse = settings._get_langfuse_client()

    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        model_id: Optional[str] = None,
        temperature: float = 0.3,
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
            system = system_prompt or settings.load_system_prompt(force_local=False)

            # Build messages array
            messages = []
            if conversation_history:
                messages.extend([{"role": msg.role, "content": msg.content} for msg in conversation_history])

            # Only append the current message if it's not already the last message in history
            # This prevents duplicate messages when the frontend already includes it in conversation_history
            if not messages or messages[-1]["content"] != message or messages[-1]["role"] != "user":
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
            
            if settings.local_dev:
                # In local development, log the full response for debugging
                logger.info(f"Full response body: {json.dumps(response_body, indent=2, ensure_ascii=False)}")

            response_start = response_text.find("<response>") + 10
            response_end = response_text.find("</response>")
            if response_start != -1 and response_end != -1:
                return response_text[response_start:response_end].strip()

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

    def generate_response_stream(
        self,
        message: str,
        conversation_history: Optional[List[Message]] = None,
        system_prompt: Optional[str] = None,
        model_id: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048
    ):
        """
        Generate a streaming response using AWS Bedrock (synchronous generator)

        Args:
            message: User's input message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to guide assistant behavior
            model_id: Bedrock model ID to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of generated response text
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

            # Only append the current message if it's not already the last message in history
            if not messages or messages[-1]["content"] != message or messages[-1]["role"] != "user":
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
                        name="bedrock-generation-stream",
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

            # Invoke model with streaming
            logger.info(f"Invoking Bedrock model with streaming: {model_id}")
            response = self.client.invoke_model_with_response_stream(
                modelId=model_id,
                body=body
            )

            # Process the streaming response
            full_response = ""
            input_tokens = 0
            output_tokens = 0

            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])

                # Extract text based on model type
                if "anthropic.claude" in model_id:
                    if chunk.get('type') == 'content_block_delta':
                        delta = chunk.get('delta', {})
                        if delta.get('type') == 'text_delta':
                            text = delta.get('text', '')
                            full_response += text
                            yield text
                    elif chunk.get('type') == 'message_start':
                        # Extract usage from message_start
                        usage = chunk.get('message', {}).get('usage', {})
                        input_tokens = usage.get('input_tokens', 0)
                    elif chunk.get('type') == 'message_delta':
                        # Extract output tokens from message_delta
                        delta_usage = chunk.get('delta', {}).get('usage', {})
                        output_tokens = delta_usage.get('output_tokens', 0)
                else:
                    # Handle other model types
                    text = chunk.get('completion', '')
                    full_response += text
                    yield text

            # Calculate latency
            latency = time.time() - start_time

            # Update Langfuse generation with output
            if generation and generation_context:
                try:
                    generation.update(
                        output=full_response,
                        usage_details={
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens
                        }
                    )
                    generation_context.__exit__(None, None, None)
                    self.langfuse.flush()
                except Exception as e:
                    logger.warning(f"Could not update Langfuse generation: {e}")

            logger.info("Successfully generated streaming response")
            logger.info(f"Tokens: {input_tokens} input, {output_tokens} output | Latency: {latency:.2f}s")

        except Exception as e:
            # Close Langfuse generation on error
            if generation_context:
                try:
                    generation_context.__exit__(type(e), e, e.__traceback__)
                    self.langfuse.flush()
                except:
                    pass

            logger.error(f"Error generating streaming response: {str(e)}")
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
