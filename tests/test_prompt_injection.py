#!/usr/bin/env python3
"""Test script to verify knowledge base injection into system prompt"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings


def test_knowledge_base_loading():
    """Test that knowledge base loads correctly"""
    print("=" * 80)
    print("Testing Knowledge Base Loading")
    print("=" * 80)

    # Load knowledge base
    kb = settings.load_knowledge_base()

    if not kb:
        print("❌ ERROR: Knowledge base is empty or failed to load")
        return False

    print(f"✓ Knowledge base loaded successfully")
    print(f"✓ Contains {len(kb)} top-level keys: {list(kb.keys())}")

    # Check structure
    if 'knowledge_base' in kb:
        kb_data = kb['knowledge_base']
        if 'categories' in kb_data:
            print(f"✓ Found {len(kb_data['categories'])} categories")
            for i, cat in enumerate(kb_data['categories'][:3], 1):
                main_topic = cat.get('main_topic', 'Unknown')
                code = cat.get('main_topic_code', 'N/A')
                sub_count = len(cat.get('sub_topics', []))
                print(f"  {i}. {main_topic} (Code: {code}) - {sub_count} sub-topics")

        if 'metadata' in kb_data:
            metadata = kb_data['metadata']
            print(f"✓ Metadata: version={metadata.get('version')}, updated={metadata.get('last_updated')}")

    return True


def test_system_prompt_injection():
    """Test that system prompt loads and injects knowledge base"""
    print("\n" + "=" * 80)
    print("Testing System Prompt Injection")
    print("=" * 80)

    # Load complete prompt
    prompt = settings.load_system_prompt()

    if not prompt:
        print("❌ ERROR: System prompt is empty or failed to load")
        return False

    print(f"✓ System prompt loaded successfully")
    print(f"✓ Total length: {len(prompt)} characters")
    print(f"✓ Total lines: {prompt.count(chr(10)) + 1}")

    # Check if knowledge_base tags exist
    if '<knowledge_base>' in prompt and '</knowledge_base>' in prompt:
        # Extract content between tags
        start_idx = prompt.find('<knowledge_base>') + len('<knowledge_base>')
        end_idx = prompt.find('</knowledge_base>')
        kb_content = prompt[start_idx:end_idx].strip()

        # Check if it's JSON (should start with { or [)
        if kb_content.startswith('{') or kb_content.startswith('['):
            print(f"✓ Knowledge base data injected successfully")
            print(f"✓ Injected content length: {len(kb_content)} characters")

            # Try to parse it to verify it's valid JSON
            import json
            try:
                json.loads(kb_content)
                print(f"✓ Injected content is valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Injected content is not valid JSON: {e}")
                return False
        else:
            print(f"⚠ WARNING: Knowledge base tags found but content doesn't look like JSON")
            print(f"  Content preview: {kb_content[:200]}...")
            return False
    else:
        print(f"❌ ERROR: <knowledge_base> tags not found in prompt")
        return False

    return True


def test_hebrew_support():
    """Test that Hebrew text is preserved correctly"""
    print("\n" + "=" * 80)
    print("Testing Hebrew Support")
    print("=" * 80)

    prompt = settings.load_system_prompt()

    # Check for Hebrew characters
    hebrew_chars = [c for c in prompt if '\u0590' <= c <= '\u05FF']

    if hebrew_chars:
        print(f"✓ Hebrew characters detected: {len(hebrew_chars)} characters")
        print(f"✓ Sample Hebrew text from prompt:")

        # Find first Hebrew line
        for line in prompt.split('\n')[:50]:
            if any('\u0590' <= c <= '\u05FF' for c in line):
                print(f"  {line.strip()[:80]}")
                break
    else:
        print(f"⚠ WARNING: No Hebrew characters found in prompt")

    return True


def show_prompt_preview():
    """Show a preview of the final integrated prompt"""
    print("\n" + "=" * 80)
    print("Final Integrated Prompt Preview")
    print("=" * 80)

    prompt = settings.load_system_prompt()

    lines = prompt.split('\n')
    print(f"\nFirst 20 lines:")
    print("-" * 80)
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:3d} | {line[:75]}")

    # Find knowledge_base section
    if '<knowledge_base>' in prompt:
        kb_start_line = prompt[:prompt.find('<knowledge_base>')].count('\n')
        print(f"\n<knowledge_base> section starts at line {kb_start_line + 1}")

        start_idx = prompt.find('<knowledge_base>')
        end_idx = prompt.find('</knowledge_base>') + len('</knowledge_base>')
        kb_section = prompt[start_idx:end_idx]
        kb_lines = kb_section.split('\n')

        print(f"Knowledge base section: {len(kb_lines)} lines")
        print(f"\nFirst 10 lines of knowledge base:")
        print("-" * 80)
        for i, line in enumerate(kb_lines[:10], 1):
            print(f"{i:3d} | {line[:75]}")

        print(f"\n... [{len(kb_lines) - 20} more lines] ...")

        print(f"\nLast 10 lines of knowledge base:")
        print("-" * 80)
        for i, line in enumerate(kb_lines[-10:], len(kb_lines) - 9):
            print(f"{i:3d} | {line[:75]}")


def main():
    """Run all tests"""
    print("\n" + "🔍 " * 20)
    print("KNOWLEDGE BASE INJECTION TEST")
    print("🔍 " * 20 + "\n")

    results = []

    # Run tests
    results.append(("Knowledge Base Loading", test_knowledge_base_loading()))
    results.append(("System Prompt Injection", test_system_prompt_injection()))
    results.append(("Hebrew Support", test_hebrew_support()))

    # Show preview
    show_prompt_preview()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} - {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your knowledge base is properly integrated.")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME TESTS FAILED. Please check the errors above.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
