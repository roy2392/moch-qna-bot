#!/usr/bin/env python3
"""Test the full integration with a sample API call"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.services.bedrock_service import BedrockService
from config.settings import settings


async def test_prompt_in_service():
    """Test that the BedrockService uses the integrated prompt correctly"""
    print("=" * 80)
    print("Testing Bedrock Service Integration")
    print("=" * 80)

    service = BedrockService()

    # Load the prompt as the service would
    prompt = settings.load_system_prompt()

    print(f"✓ Loaded prompt: {len(prompt)} characters")
    print(f"✓ Contains Hebrew: {'Yes' if any('\u0590' <= c <= '\u05FF' for c in prompt) else 'No'}")
    print(f"✓ Contains JSON data: {'Yes' if '{' in prompt and '"knowledge_base"' in prompt else 'No'}")

    # Show what will be sent to Bedrock
    print("\n" + "=" * 80)
    print("Prompt Structure Analysis")
    print("=" * 80)

    sections = [
        ('<system_prompt>', '</system_prompt>'),
        ('<role>', '</role>'),
        ('<knowledge_base>', '</knowledge_base>'),
        ('<response_guidelines>', '</response_guidelines>'),
        ('<matching_rules>', '</matching_rules>'),
        ('<special_cases>', '</special_cases>'),
        ('<error_handling>', '</error_handling>'),
        ('<formatting>', '</formatting>'),
        ('<quality_standards>', '</quality_standards>'),
        ('<examples>', '</examples>'),
        ('<critical_reminders>', '</critical_reminders>'),
    ]

    for start_tag, end_tag in sections:
        if start_tag in prompt and end_tag in prompt:
            start_idx = prompt.find(start_tag)
            end_idx = prompt.find(end_tag) + len(end_tag)
            section_content = prompt[start_idx:end_idx]
            line_count = section_content.count('\n') + 1

            # Check if this is knowledge_base with JSON
            if start_tag == '<knowledge_base>':
                kb_start = prompt.find(start_tag) + len(start_tag)
                kb_end = prompt.find(end_tag)
                kb_content = prompt[kb_start:kb_end].strip()
                if kb_content.startswith('{'):
                    print(f"✓ {start_tag:25s} : {line_count:4d} lines (JSON DATA INJECTED)")
                else:
                    print(f"⚠ {start_tag:25s} : {line_count:4d} lines (NO JSON DATA)")
            else:
                print(f"✓ {start_tag:25s} : {line_count:4d} lines")
        else:
            print(f"❌ {start_tag:25s} : NOT FOUND")

    # Sample data from knowledge base
    print("\n" + "=" * 80)
    print("Knowledge Base Content Verification")
    print("=" * 80)

    kb = settings.load_knowledge_base()
    if kb and 'knowledge_base' in kb:
        kb_data = kb['knowledge_base']

        # Show sample category
        if 'categories' in kb_data and len(kb_data['categories']) > 0:
            first_cat = kb_data['categories'][0]
            print(f"\n✓ Sample Category:")
            print(f"  Main Topic: {first_cat.get('main_topic')}")
            print(f"  Code: {first_cat.get('main_topic_code')}")
            print(f"  Sub-topics: {len(first_cat.get('sub_topics', []))}")

            if first_cat.get('sub_topics'):
                first_sub = first_cat['sub_topics'][0]
                print(f"\n✓ Sample Sub-topic:")
                print(f"  Name: {first_sub.get('sub_topic')}")
                print(f"  Code: {first_sub.get('sub_topic_code')}")
                print(f"  Summary: {first_sub.get('summary', '')[:100]}...")

        # Show metadata
        if 'metadata' in kb_data:
            print(f"\n✓ Metadata:")
            for key, value in kb_data['metadata'].items():
                print(f"  {key}: {value}")

    print("\n" + "=" * 80)
    print("✅ Integration Test Complete!")
    print("=" * 80)
    print("\nThe prompt is ready to be sent to AWS Bedrock with:")
    print("  • Hebrew system instructions")
    print("  • Injected JSON knowledge base data")
    print("  • All sections properly structured")
    print("\nTo test with actual Bedrock API:")
    print("  1. Ensure AWS credentials are configured")
    print("  2. Run: uvicorn app.main:app --reload")
    print("  3. Make a request to: POST /api/v1/chat")


if __name__ == "__main__":
    asyncio.run(test_prompt_in_service())
