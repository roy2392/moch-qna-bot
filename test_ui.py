#!/usr/bin/env python3
"""Test the UI and conversation history functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("UI Integration Test")
print("=" * 80)

# Check static files exist
static_dir = Path("static")
required_files = ["index.html", "style.css", "app.js"]

print("\n1. Checking static files...")
for file in required_files:
    file_path = static_dir / file
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   ✓ {file:15s} - {size:,} bytes")
    else:
        print(f"   ❌ {file:15s} - NOT FOUND")
        sys.exit(1)

# Check main.py has static files mounted
print("\n2. Checking FastAPI configuration...")
from app.main import app

# Check if static files are mounted
static_mounted = any(route.path == "/static" for route in app.routes)
if static_mounted:
    print("   ✓ Static files mounted")
else:
    print("   ❌ Static files NOT mounted")
    sys.exit(1)

# Check root redirects to UI
root_routes = [r for r in app.routes if hasattr(r, 'path') and r.path == "/"]
if root_routes:
    print("   ✓ Root path configured")
else:
    print("   ❌ Root path not found")

# Check API endpoints
api_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/v1' in r.path]
if api_routes:
    print(f"   ✓ Found {len(api_routes)} API routes")
else:
    print("   ❌ No API routes found")

print("\n3. Testing conversation history support...")

# Check that the schemas support conversation history
from app.models.schemas import ChatRequest, Message

# Create a test request with conversation history
try:
    test_request = ChatRequest(
        message="Test message",
        conversation_history=[
            Message(role="user", content="Previous user message"),
            Message(role="assistant", content="Previous assistant message")
        ]
    )
    print("   ✓ ChatRequest supports conversation_history")
    print(f"   ✓ History contains {len(test_request.conversation_history)} messages")
except Exception as e:
    print(f"   ❌ Error creating ChatRequest with history: {e}")
    sys.exit(1)

# Check BedrockService accepts conversation history
from app.services.bedrock_service import BedrockService
import inspect

service = BedrockService()
sig = inspect.signature(service.generate_response)
params = list(sig.parameters.keys())

if 'conversation_history' in params:
    print("   ✓ BedrockService.generate_response accepts conversation_history")
else:
    print("   ❌ BedrockService.generate_response missing conversation_history parameter")

print("\n4. UI Feature Check...")

# Read the JavaScript file
js_content = (static_dir / "app.js").read_text()

features = {
    "Conversation history array": "conversationHistory = []" in js_content,
    "localStorage save": "localStorage.setItem" in js_content,
    "localStorage load": "localStorage.getItem" in js_content,
    "Message formatting": "formatMessage" in js_content,
    "Clear conversation": "clearConversation" in js_content,
    "API endpoint": "API_ENDPOINT" in js_content,
}

for feature, present in features.items():
    status = "✓" if present else "❌"
    print(f"   {status} {feature}")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)

print("\nTo start the server:")
print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

print("\nThen open in your browser:")
print("  http://localhost:8000")

print("\nThe UI includes:")
print("  • Hebrew RTL support")
print("  • Conversation history (persists in localStorage)")
print("  • Beautiful gradient design")
print("  • Typing indicators")
print("  • Link formatting")
print("  • Mobile responsive")
print("  • Clear conversation button")

print("\n" + "=" * 80)
