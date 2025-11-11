#!/usr/bin/env python3
"""Test script to verify both knowledge_base and few_shots are injected into system prompt"""

import json
from config.settings import settings

def test_full_injection():
    """Test that both knowledge base and few-shot examples are injected"""

    print("=" * 80)
    print("Testing Full System Prompt Injection")
    print("=" * 80)

    # Test 1: Load knowledge base
    print("\n1. Testing knowledge_base loading...")
    kb = settings.load_knowledge_base()
    if kb:
        print(f"✅ Knowledge base loaded successfully")
        print(f"   - Categories: {len(kb.get('categories', []))}")
        if kb.get('categories'):
            print(f"   - First category: {kb['categories'][0].get('category_name', 'N/A')}")
    else:
        print("❌ Knowledge base NOT loaded")
        return False

    # Test 2: Load few-shot examples
    print("\n2. Testing few_shots loading...")
    fs = settings.load_few_shots()
    if fs:
        print(f"✅ Few-shots loaded successfully")
        print(f"   - Examples: {len(fs.get('few_shot_examples', []))}")
        if fs.get('few_shot_examples'):
            print(f"   - First example ID: {fs['few_shot_examples'][0].get('id', 'N/A')}")
    else:
        print("❌ Few-shots NOT loaded")
        return False

    # Test 3: Load system prompt
    print("\n3. Testing system prompt loading...")
    prompt = settings.load_system_prompt()
    if prompt:
        print(f"✅ System prompt loaded successfully")
        print(f"   - Length: {len(prompt)} characters")
    else:
        print("❌ System prompt NOT loaded")
        return False

    # Test 4: Verify knowledge base injection
    print("\n4. Verifying knowledge_base injection...")
    kb_json = json.dumps(kb, ensure_ascii=False, indent=2)
    if kb_json in prompt:
        print("✅ Knowledge base JSON found in prompt")
    else:
        print("❌ Knowledge base JSON NOT found in prompt")
        # Check if tags are still there (meaning injection didn't happen)
        if '<knowledge_base>' in prompt and '</knowledge_base>' in prompt:
            print("   ⚠️  Tags still present - injection may have failed")
        return False

    # Test 5: Verify few-shots injection
    print("\n5. Verifying few_shots injection...")
    fs_json = json.dumps(fs, ensure_ascii=False, indent=2)
    if fs_json in prompt:
        print("✅ Few-shots JSON found in prompt")
    else:
        print("❌ Few-shots JSON NOT found in prompt")
        # Check if tags are still there
        if '<few_shot_examples>' in prompt and '</few_shot_examples>' in prompt:
            print("   ⚠️  Tags still present - injection may have failed")
        return False

    # Test 6: Check for specific content
    print("\n6. Verifying specific content...")

    # Check for Hebrew content from knowledge base
    if 'מחיר למשתכן' in prompt or 'סיוע בשכר דירה' in prompt:
        print("✅ Hebrew knowledge base content found")
    else:
        print("❌ Hebrew knowledge base content NOT found")
        return False

    # Check for few-shot example content
    if 'few_shot_examples' in prompt or 'classification_patterns' in prompt:
        print("✅ Few-shot structure found")
    else:
        print("❌ Few-shot structure NOT found")
        return False

    # Test 7: Print sample of prompt
    print("\n7. Sample of injected prompt:")
    print("-" * 80)
    # Find and print the few_shot_examples section
    if '<few_shot_examples>' in prompt:
        idx = prompt.find('<few_shot_examples>')
        end_idx = prompt.find('</few_shot_examples>')
        if end_idx > idx:
            sample = prompt[idx:min(idx+500, end_idx)]
            print(sample + "...")
    print("-" * 80)

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✨ Summary:")
    print(f"   - Knowledge base: ✅ Loaded and injected")
    print(f"   - Few-shot examples: ✅ Loaded and injected")
    print(f"   - System prompt: ✅ Ready for use")
    print(f"   - Total prompt size: {len(prompt)} characters")
    print("\n🎉 The LLM will now receive both knowledge_base.json and few_shots.json!")

    return True


if __name__ == "__main__":
    try:
        success = test_full_injection()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
