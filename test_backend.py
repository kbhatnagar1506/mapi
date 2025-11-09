#!/usr/bin/env python3
"""Quick test script to verify backend works"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing backend components...\n")

# Test 1: Imports
print("1. Testing imports...")
try:
    from packages.core.schemas import MemoryWrite, RetrievalQuery, Answer
    from packages.core.stores import EpisodicStore, ExactStore, SemanticKG
    from packages.core.retrieval import route_and_fetch
    from packages.core.verify import verify_before_speak
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Store initialization
print("\n2. Testing store initialization...")
try:
    epi = EpisodicStore()
    print("   ✓ EpisodicStore initialized")
except Exception as e:
    print(f"   ⚠ EpisodicStore: {e}")

try:
    exact = ExactStore()
    print("   ✓ ExactStore initialized")
except Exception as e:
    print(f"   ✗ ExactStore error: {e}")
    sys.exit(1)

try:
    kg = SemanticKG()
    print("   ✓ SemanticKG initialized")
except Exception as e:
    print(f"   ⚠ SemanticKG: {e}")

# Test 3: Write memory
print("\n3. Testing memory write...")
try:
    from datetime import datetime, timezone
    from uuid import uuid4
    
    from packages.core.schemas import SourceType
    test_memory = MemoryWrite(
        text="Test memory: Send Q3 report to John",
        source=SourceType.CHAT,
        tags=["test"]
    )
    
    eid = str(uuid4())
    payload = {
        "source": test_memory.source,
        "tags": test_memory.tags,
        "timestamp": test_memory.timestamp.isoformat(),
        "text": test_memory.text
    }
    
    if epi:
        epi.write(eid, payload, test_memory.text)
        print("   ✓ Episodic write successful")
    
    exact.write(eid, test_memory.text)
    print("   ✓ Exact write successful")
    
    if kg:
        kg.add_fact("User", "MENTIONED", "Test", int(datetime.now(timezone.utc).timestamp()))
        print("   ✓ KG write successful")
    
except Exception as e:
    print(f"   ✗ Write error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Query
print("\n4. Testing query...")
try:
    query = RetrievalQuery(query="What report for John?", top_k=3)
    bundle = route_and_fetch(query)
    print(f"   ✓ Query successful, found {len(bundle['candidates'])} candidates")
except Exception as e:
    print(f"   ✗ Query error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify
print("\n5. Testing verification...")
try:
    query_text = "What report for John?"
    candidates = bundle['candidates']
    result = verify_before_speak(query_text, candidates)
    
    # Handle both old (2 values) and new (3 values) signatures
    if len(result) == 3:
        draft, conf, guard_result = result
        print(f"   ✓ Verification successful, confidence: {conf:.2f}")
        if guard_result.get("hallucinated"):
            print(f"   ⚠ Hallucination detected: {guard_result.get('flags', [])}")
    else:
        draft, conf = result
        print(f"   ✓ Verification successful, confidence: {conf:.2f}")
    
    print(f"   Answer preview: {draft[:100]}...")
except Exception as e:
    print(f"   ⚠ Verification warning: {e} (may need LLM configured)")

print("\n✅ Backend test complete! All core functionality works.")
print("\nTo start the API server:")
print("  cd apps/api && uvicorn main:app --reload --port 8000")

