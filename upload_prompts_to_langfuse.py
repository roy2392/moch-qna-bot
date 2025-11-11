#!/usr/bin/env python3
"""
Script to upload current prompts, knowledge base, and few-shots to Langfuse.

This script will:
1. Read your local prompt files
2. Upload them as prompts to Langfuse
3. Create initial versions that can be managed through the Langfuse UI

Run this once to migrate your prompts to Langfuse.
"""

import json
from pathlib import Path
from langfuse import Langfuse
from config.settings import settings


def upload_to_langfuse():
    """Upload all prompts to Langfuse"""

    print("=" * 80)
    print("Uploading Prompts to Langfuse")
    print("=" * 80)

    # Initialize Langfuse client
    print("\n1. Initializing Langfuse client...")
    try:
        client = Langfuse(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_base_url
        )
        print("✅ Langfuse client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Langfuse client: {e}")
        return False

    root_dir = Path(__file__).parent

    # Upload System Prompt
    print("\n2. Uploading System Prompt...")
    try:
        prompt_path = root_dir / settings.system_prompt_file
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt_content = f.read()

            # Create prompt with production label
            result = client.create_prompt(
                name=settings.langfuse_system_prompt_name,
                prompt=system_prompt_content,
                tags=["production", "moch", "hebrew"],
                type="text"
            )
            # Set as production version
            if result:
                try:
                    client.set_prompt_label(settings.langfuse_system_prompt_name, "production", version=result.version)
                except:
                    pass  # Label might already exist
            print(f"✅ System prompt uploaded as '{settings.langfuse_system_prompt_name}'")
        else:
            print(f"⚠️  System prompt file not found at {prompt_path}")
    except Exception as e:
        print(f"❌ Failed to upload system prompt: {e}")

    # Upload Knowledge Base
    print("\n3. Uploading Knowledge Base...")
    try:
        kb_path = root_dir / settings.knowledge_base_file
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_content = f.read()  # Keep as JSON string

            # Create prompt with production label
            result = client.create_prompt(
                name=settings.langfuse_knowledge_base_name,
                prompt=kb_content,
                tags=["production", "moch", "json", "hebrew"],
                type="text"
            )
            # Set as production version
            if result:
                try:
                    client.set_prompt_label(settings.langfuse_knowledge_base_name, "production", version=result.version)
                except:
                    pass  # Label might already exist
            print(f"✅ Knowledge base uploaded as '{settings.langfuse_knowledge_base_name}'")
        else:
            print(f"⚠️  Knowledge base file not found at {kb_path}")
    except Exception as e:
        print(f"❌ Failed to upload knowledge base: {e}")

    # Upload Few-Shot Examples
    print("\n4. Uploading Few-Shot Examples...")
    try:
        fs_path = root_dir / settings.few_shots_file
        if fs_path.exists():
            with open(fs_path, 'r', encoding='utf-8') as f:
                fs_content = f.read()  # Keep as JSON string

            # Create prompt with production label
            result = client.create_prompt(
                name=settings.langfuse_few_shots_name,
                prompt=fs_content,
                tags=["production", "moch", "json", "hebrew"],
                type="text"
            )
            # Set as production version
            if result:
                try:
                    client.set_prompt_label(settings.langfuse_few_shots_name, "production", version=result.version)
                except:
                    pass  # Label might already exist
            print(f"✅ Few-shot examples uploaded as '{settings.langfuse_few_shots_name}'")
        else:
            print(f"⚠️  Few-shots file not found at {fs_path}")
    except Exception as e:
        print(f"❌ Failed to upload few-shots: {e}")

    print("\n" + "=" * 80)
    print("✅ Upload Complete!")
    print("=" * 80)
    print("\n📝 Next Steps:")
    print(f"1. Visit {settings.langfuse_base_url}")
    print("2. Go to the 'Prompts' section")
    print("3. You should see three prompts:")
    print(f"   - {settings.langfuse_system_prompt_name}")
    print(f"   - {settings.langfuse_knowledge_base_name}")
    print(f"   - {settings.langfuse_few_shots_name}")
    print("\n4. You can now:")
    print("   - Edit prompts directly in Langfuse UI")
    print("   - Create new versions")
    print("   - A/B test different versions")
    print("   - Track prompt performance")
    print("   - Collaborate with your team")
    print("\n5. Your chatbot will automatically fetch the latest version!")
    print("\n🔄 Fallback: If Langfuse is unavailable, local files will be used.")

    return True


if __name__ == "__main__":
    try:
        if not settings.langfuse_secret_key or not settings.langfuse_public_key:
            print("❌ Error: Langfuse credentials not configured in .env")
            print("\nPlease add to your .env file:")
            print("LANGFUSE_SECRET_KEY=your_secret_key")
            print("LANGFUSE_PUBLIC_KEY=your_public_key")
            print("LANGFUSE_BASE_URL=https://cloud.langfuse.com")
            exit(1)

        success = upload_to_langfuse()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Upload failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
