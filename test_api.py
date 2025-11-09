#!/usr/bin/env python3
"""
Quick API test script
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_api_imports():
    """Test that API imports successfully"""
    try:
        from apps.api.main import app
        print("✓ API imports successfully")
        
        # Count routes
        routes = [r for r in app.routes if hasattr(r, 'path')]
        print(f"✓ Total endpoints: {len(routes)}")
        
        # Show key endpoints
        print("\nKey endpoints:")
        for r in routes:
            methods = list(r.methods) if hasattr(r, 'methods') else ['GET']
            path = r.path
            print(f"  {methods[0]:6} {path}")
        
        return True
    except Exception as e:
        print(f"✗ API import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schemas():
    """Test schema validation"""
    try:
        from packages.core.schemas import MemoryWrite, RetrievalQuery, SourceType
        
        # Test MemoryWrite validation
        mem = MemoryWrite(
            text="Test memory",
            source=SourceType.CHAT,
            tags=["test"]
        )
        print(f"✓ MemoryWrite validation works: {mem.text}")
        
        # Test RetrievalQuery validation
        query = RetrievalQuery(query="What is MAPI?")
        print(f"✓ RetrievalQuery validation works: {query.query}")
        
        return True
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        return False

def test_responses():
    """Test response models"""
    try:
        from apps.api.responses import APIResponse, PaginatedResponse
        
        # Test APIResponse
        resp = APIResponse(ok=True, data={"test": "data"}, message="Success")
        print(f"✓ APIResponse works: {resp.ok}")
        
        # Test PaginatedResponse
        pag = PaginatedResponse(
            ok=True,
            data=[{"id": "1"}],
            pagination={"offset": 0, "limit": 10},
            total=1,
            page=1,
            limit=10,
            has_more=False
        )
        print(f"✓ PaginatedResponse works: {pag.total} items")
        
        return True
    except Exception as e:
        print(f"✗ Response models failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API Test Suite")
    print("=" * 50)
    
    results = []
    
    print("\n1. Testing API imports...")
    results.append(test_api_imports())
    
    print("\n2. Testing schema validation...")
    results.append(test_schemas())
    
    print("\n3. Testing response models...")
    results.append(test_responses())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

