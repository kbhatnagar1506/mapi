#!/usr/bin/env python3
"""
Compare retrieval results before and after training
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.core.stores import EpisodicStore, ExactStore, SemanticKG
from packages.core.retrieval import route_and_fetch
from packages.core.schemas import RetrievalQuery
from packages.core.verify import verify_before_speak

def compare_retrieval():
    """Compare retrieval results for MAPI knowledge"""
    
    print("🔍 MAPI Knowledge Retrieval Comparison")
    print("="*70)
    print()
    
    # Initialize stores
    epi = EpisodicStore()
    exact = ExactStore()
    kg = SemanticKG()
    
    # Test queries about MAPI
    test_queries = [
        {
            "query": "What is MAPI?",
            "expected": "MAPI is a production-grade AI memory system"
        },
        {
            "query": "What are the memory tiers?",
            "expected": "tiered memory architecture with four layers"
        },
        {
            "query": "What databases does MAPI use?",
            "expected": "PostgreSQL, Qdrant, Neo4j, SQLite"
        },
        {
            "query": "What are the 7 architecture principles?",
            "expected": "Lifecycle Separation, Smart Retrieval Router"
        },
        {
            "query": "How does MAPI prevent hallucinations?",
            "expected": "Hallucination Guard, 4-layer verification"
        }
    ]
    
    print("Testing Retrieval Capabilities:\n")
    
    results_summary = {
        "total_queries": len(test_queries),
        "found_results": 0,
        "high_confidence": 0,
        "no_results": 0
    }
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected = test["expected"]
        
        print(f"{i}. Query: {query}")
        print(f"   Expected: {expected}...")
        print("-" * 70)
        
        # Test retrieval
        try:
            result = route_and_fetch(RetrievalQuery(query=query, top_k=5))
            candidates = result.get("candidates", [])
            routing = result.get("routing", {})
            
            print(f"   Routing: {routing.get('reason', 'default')}")
            print(f"   Found: {len(candidates)} candidates")
            
            if candidates:
                results_summary["found_results"] += 1
                
                # Show top results
                for j, c in enumerate(candidates[:2], 1):
                    text = c.get("payload", {}).get("text", "") or c.get("payload", {}).get("content", "")
                    score = c.get("score", 0)
                    source = c.get("type", "unknown")
                    
                    print(f"   {j}. [{source}] Score: {score:.3f}")
                    print(f"      {text[:90]}...")
                
                # Test verification
                try:
                    draft, conf, guard = verify_before_speak(query, candidates, semantic_kg=kg)
                    print(f"   Confidence: {conf:.2f}")
                    
                    if conf > 0.6:
                        results_summary["high_confidence"] += 1
                    
                    if guard.get("hallucinated"):
                        print(f"   ⚠️  Hallucination flags: {', '.join(guard.get('flags', []))}")
                    
                    print(f"   Answer: {draft[:100]}...")
                except Exception as e:
                    print(f"   ⚠️  Verification error: {e}")
            else:
                results_summary["no_results"] += 1
                print("   ⚠️  No results found")
                print("   💡 This may be because:")
                print("      - In-memory stores are per-instance (not persistent)")
                print("      - SQLite has the data but search may need exact matches")
                print("      - Start databases (make up) for persistent storage")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results_summary["no_results"] += 1
        
        print()
    
    # Summary
    print("="*70)
    print("📊 Retrieval Summary")
    print("="*70)
    print(f"Total queries: {results_summary['total_queries']}")
    print(f"Found results: {results_summary['found_results']}")
    print(f"High confidence (>0.6): {results_summary['high_confidence']}")
    print(f"No results: {results_summary['no_results']}")
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    print("   1. Start databases for persistent storage:")
    print("      make up")
    print()
    print("   2. Use the API for consistent store instances:")
    print("      make api")
    print("      Then query via: curl -X POST http://localhost:8000/ask ...")
    print()
    print("   3. Check SQLite directly:")
    print("      sqlite3 dev/exact.db \"SELECT COUNT(*) FROM exact_store;\"")
    print()

if __name__ == "__main__":
    compare_retrieval()

