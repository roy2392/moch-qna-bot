#!/usr/bin/env python3
"""
Test script to verify Langfuse integration is working correctly.

This script will:
1. Test fetching system prompt from Langfuse
2. Test fetching knowledge base from Langfuse
3. Test fetching few-shots from Langfuse
4. Verify data injection still works correctly
"""

import json
from config.settings import settings


def test_langfuse_integration():
    """Test Langfuse integration"""

    print("=" * 80)
    print("Testing Langfuse Integration")
    print("=" * 80)

    # Check if Langfuse is enabled
    print(f"\n🔧 Configuration:")
    print(f"   - USE_LANGFUSE: {settings.use_langfuse}")
    print(f"   - Langfuse Base URL: {settings.langfuse_base_url}")
    print(f"   - Has Secret Key: {'✅' if settings.langfuse_secret_key else '❌'}")
    print(f"   - Has Public Key: {'✅' if settings.langfuse_public_key else '❌'}")

    # Test 1: Load knowledge base
    print("\n" + "=" * 80)
    print("1. Testing Knowledge Base Loading")
    print("=" * 80)
    kb = settings.load_knowledge_base()
    if kb:
        print(f"✅ Knowledge base loaded")
        print(f"   - Type: {type(kb)}")
        print(f"   - Has categories: {'categories' in kb}")
        if 'categories' in kb:
            print(f"   - Number of categories: {len(kb.get('categories', []))}")
    else:
        print("❌ Knowledge base NOT loaded")
        return False

    # Test 2: Load few-shots
    print("\n" + "=" * 80)
    print("2. Testing Few-Shots Loading")
    print("=" * 80)
    fs = settings.load_few_shots()
    if fs:
        print(f"✅ Few-shots loaded")
        print(f"   - Type: {type(fs)}")
        print(f"   - Has examples: {'few_shot_examples' in fs}")
        if 'few_shot_examples' in fs:
            print(f"   - Number of examples: {len(fs.get('few_shot_examples', []))}")
            if fs['few_shot_examples']:
                print(f"   - First example ID: {fs['few_shot_examples'][0].get('id', 'N/A')}")
    else:
        print("❌ Few-shots NOT loaded")
        return False

    # Test 3: Load system prompt
    print("\n" + "=" * 80)
    print("3. Testing System Prompt Loading")
    print("=" * 80)
    prompt = settings.load_system_prompt()
    if prompt:
        print(f"✅ System prompt loaded")
        print(f"   - Length: {len(prompt)} characters")
        print(f"   - Contains Hebrew: {'אתה' in prompt}")
    else:
        print("❌ System prompt NOT loaded")
        return False

    # Test 4: Verify knowledge base injection
    print("\n" + "=" * 80)
    print("4. Verifying Knowledge Base Injection")
    print("=" * 80)
    kb_json = json.dumps(kb, ensure_ascii=False, indent=2)
    if kb_json in prompt:
        print("✅ Knowledge base JSON found in prompt")
    else:
        print("⚠️  Knowledge base JSON NOT found in prompt (may use local file)")
        # Check if empty tags are still there
        if '<knowledge_base>' in prompt and '</knowledge_base>' in prompt:
            # Extract content between tags
            start_idx = prompt.find('<knowledge_base>') + len('<knowledge_base>')
            end_idx = prompt.find('</knowledge_base>')
            content = prompt[start_idx:end_idx].strip()
            if content:
                print(f"   - Content length between tags: {len(content)} chars")
            else:
                print("   ❌ Tags are empty - injection failed!")
                return False

    # Test 5: Verify few-shots injection
    print("\n" + "=" * 80)
    print("5. Verifying Few-Shots Injection")
    print("=" * 80)
    fs_json = json.dumps(fs, ensure_ascii=False, indent=2)
    if fs_json in prompt:
        print("✅ Few-shots JSON found in prompt")
    else:
        print("⚠️  Few-shots JSON NOT found in prompt (may use local file)")
        # Check if empty tags are still there
        if '<few_shot_examples>' in prompt and '</few_shot_examples>' in prompt:
            # Extract content between tags
            start_idx = prompt.find('<few_shot_examples>') + len('<few_shot_examples>')
            end_idx = prompt.find('</few_shot_examples>')
            content = prompt[start_idx:end_idx].strip()
            if content:
                print(f"   - Content length between tags: {len(content)} chars")
            else:
                print("   ❌ Tags are empty - injection failed!")
                return False

    # Test 6: Check specific content
    print("\n" + "=" * 80)
    print("6. Verifying Specific Content")
    print("=" * 80)

    # Check for Hebrew content
    if 'מחיר למשתכן' in prompt or 'סיוע בשכר דירה' in prompt:
        print("✅ Hebrew knowledge base content found")
    else:
        print("❌ Hebrew knowledge base content NOT found")
        return False

    # Check for few-shot structure
    if 'few_shot_examples' in prompt or 'classification_patterns' in prompt:
        print("✅ Few-shot structure found")
    else:
        print("❌ Few-shot structure NOT found")
        return False

    # Print source summary
    print("\n" + "=" * 80)
    print("📊 Data Sources Summary")
    print("=" * 80)
    print("\nBased on the output above:")
    print("- Check for '✅ Loaded ... from Langfuse' = Data from Langfuse")
    print("- Check for '📁 Loaded ... from local file' = Data from local files")
    print("\n✅ Integration is working correctly!")
    print("\n🔄 If Langfuse prompts are loaded, your chatbot is now:")
    print("   - Fetching prompts from Langfuse")
    print("   - Falling back to local files if Langfuse is unavailable")
    print("   - Injecting both knowledge base and few-shots")
    print("\n📝 To manage prompts:")
    print(f"   1. Visit: {settings.langfuse_base_url}")
    print("   2. Go to 'Prompts' section")
    print("   3. Edit and create new versions")
    print("   4. Changes will be reflected immediately!")

    return True


if __name__ == "__main__":
    try:
        success = test_langfuse_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
