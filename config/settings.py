"""Application settings and configuration"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
# import httpx
from pydantic_settings import BaseSettings
from langfuse import Langfuse
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

# workaround for kate
# client = httpx.Client(verify=False)

class Settings(BaseSettings):
    """Application settings"""

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Bedrock Configuration
    default_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    default_temperature: float = 0.3
    default_max_tokens: int = 2048
    system_prompt_file: str = "prompts/system_prompt.txt"
    knowledge_base_file: str = "prompts/knowledge_base.json"
    few_shots_file: str = "prompts/few_shots.json"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Langfuse Configuration
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_base_url: str = "https://cloud.langfuse.com"
    use_langfuse: bool = True  # Toggle to use Langfuse or local files

    # Langfuse Prompt Names
    langfuse_system_prompt_name: str = "moch-system-prompt"
    langfuse_knowledge_base_name: str = "moch-knowledge-base"
    langfuse_few_shots_name: str = "moch-few-shots"

    local_dev: bool = False  # If true, forces loading from local files

    class Config:
        env_file = ".env"
        case_sensitive = False

    def _get_langfuse_client(self) -> Optional[Langfuse]:
        """Get Langfuse client if credentials are configured"""
        if not self.use_langfuse:
            return None

        if not self.langfuse_secret_key or not self.langfuse_public_key:
            print("Warning: Langfuse credentials not configured")
            return None

        try:
            return Langfuse(
                secret_key=self.langfuse_secret_key,
                public_key=self.langfuse_public_key,
                host=self.langfuse_base_url,
                # httpx_client=client
            )
        except Exception as e:
            print(f"Warning: Could not initialize Langfuse client: {e}")
            return None

    def load_knowledge_base(self, force_local:bool=False) -> Dict[str, Any]:
        """Load knowledge base from Langfuse or fallback to local JSON file"""
        prompt = None
        if not force_local:
            # Try Langfuse first
            if self.use_langfuse:
                try:
                    client = self._get_langfuse_client()
                    if client:
                        # Fetch production version (no caching - always get latest)
                        prompt = client.get_prompt(self.langfuse_knowledge_base_name, cache_ttl_seconds=0)
                        if prompt and prompt.prompt:
                            print(f"✅ Loaded knowledge base from Langfuse (version: {prompt.version})")
                            # Parse JSON from prompt content
                            return json.loads(prompt.prompt)
                except Exception as e:
                    print(f"Warning: Could not load knowledge base from Langfuse: {e}")

        if not prompt:
            # Fallback to local file
            try:
                root_dir = Path(__file__).parent.parent
                kb_path = root_dir / self.knowledge_base_file

                if kb_path.exists():
                    with open(kb_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"📁 Loaded knowledge base from local file")
                        return data
                else:
                    print(f"Warning: Knowledge base file not found at {kb_path}")
                    return {}
            except Exception as e:
                print(f"Warning: Could not load knowledge base from file: {e}")
                return {}

    def load_few_shots(self, force_local:bool=False) -> Dict[str, Any]:
        """Load few-shot examples from Langfuse or fallback to local JSON file"""
        prompt = None
        if not force_local:
            # Try Langfuse first
            if self.use_langfuse:
                try:
                    client = self._get_langfuse_client()
                    if client:
                        # Fetch production version (no caching - always get latest)
                        prompt = client.get_prompt(self.langfuse_few_shots_name, cache_ttl_seconds=0)
                        if prompt and prompt.prompt:
                            print(f"✅ Loaded few-shots from Langfuse (version: {prompt.version})")
                            # Parse JSON from prompt content
                            return json.loads(prompt.prompt)
                except Exception as e:
                    print(f"Warning: Could not load few-shots from Langfuse: {e}")

        if not prompt:
            # Fallback to local file
            try:
                root_dir = Path(__file__).parent.parent
                fs_path = root_dir / self.few_shots_file

                if fs_path.exists():
                    with open(fs_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"📁 Loaded few-shots from local file")
                        return data
                else:
                    print(f"Warning: Few-shots file not found at {fs_path}")
                    return {}
            except Exception as e:
                print(f"Warning: Could not load few-shots from file: {e}")
                return {}

    def load_system_prompt(self, force_local:bool=False) -> str:
        """Load system prompt from Langfuse or file and inject knowledge base and few-shot examples"""
        try:
            prompt = None
            
            if not force_local:
                # Try Langfuse first for base template
                if self.use_langfuse:
                    try:
                        client = self._get_langfuse_client()
                        if client:
                            # Fetch production version (no caching - always get latest)
                            prompt_obj = client.get_prompt(self.langfuse_system_prompt_name, cache_ttl_seconds=0)
                            if prompt_obj and prompt_obj.prompt:
                                prompt = prompt_obj.prompt
                                print(f"✅ Loaded system prompt from Langfuse (version: {prompt_obj.version})")
                    except Exception as e:
                        print(f"Warning: Could not load system prompt from Langfuse: {e}")

            # Fallback to local file if Langfuse failed
            if not prompt:
                root_dir = Path(__file__).parent.parent
                prompt_path = root_dir / self.system_prompt_file

                if prompt_path.exists():
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        prompt = f.read().strip()
                        print(f"📁 Loaded system prompt from local file")
                else:
                    # Ultimate fallback
                    return "You are a helpful AI assistant powered by AWS Bedrock. Provide clear, accurate, and concise responses to user queries."

            # Load knowledge base and inject into prompt
            knowledge_base = self.load_knowledge_base(force_local=force_local)
            if knowledge_base:
                # Convert knowledge base to formatted string
                kb_json = json.dumps(knowledge_base, ensure_ascii=False, indent=2)

                # Replace <knowledge_base> section with actual data
                if '<knowledge_base>' in prompt and '</knowledge_base>' in prompt:
                    start_tag = '<knowledge_base>'
                    end_tag = '</knowledge_base>'
                    start_idx = prompt.find(start_tag) + len(start_tag)
                    end_idx = prompt.find(end_tag)

                    # Replace the content between tags with the JSON data
                    prompt = (
                        prompt[:start_idx] +
                        '\n' + kb_json + '\n' +
                        prompt[end_idx:]
                    )

            # Load few-shot examples and inject into prompt
            few_shots = self.load_few_shots(force_local=force_local)
            if few_shots:
                # Convert few_shots to formatted string
                fs_json = json.dumps(few_shots, ensure_ascii=False, indent=2)

                # Replace <few_shot_examples> section with actual data
                if '<few_shot_examples>' in prompt and '</few_shot_examples>' in prompt:
                    start_tag = '<few_shot_examples>'
                    end_tag = '</few_shot_examples>'
                    start_idx = prompt.find(start_tag) + len(start_tag)
                    end_idx = prompt.find(end_tag)

                    # Replace the content between tags with the JSON data
                    prompt = (
                        prompt[:start_idx] +
                        '\n' + fs_json + '\n' +
                        prompt[end_idx:]
                    )

            if '<current_date>' in prompt and '</current_date>' in prompt:
                current_date = datetime.now().strftime('%Y-%m-%d')
                start_tag = '<current_date>'
                end_tag = '</current_date>'
                start_idx = prompt.find(start_tag) + len(start_tag)
                end_idx = prompt.find(end_tag)

                prompt = (
                    prompt[:start_idx] +
                    '\n' + current_date + '\n' + 
                    prompt[end_idx:]
                )

            return prompt

        except Exception as e:
            # Fallback to default on error
            print(f"Warning: Could not load system prompt: {e}")
            return "You are a helpful AI assistant powered by AWS Bedrock. Provide clear, accurate, and concise responses to user queries."


# Create global settings instance
settings = Settings()
