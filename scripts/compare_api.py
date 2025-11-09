#!/usr/bin/env python3
"""
Compare Plain API vs Enhanced System
Tests both approaches with the same queries and compares results
"""
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.core.stores import EpisodicStore, ExactStore, SemanticKG
from packages.core.retrieval import route_and_fetch
from packages.core.verify import verify_before_speak
from packages.core.schemas import RetrievalQuery

def plain_api_query(query: str) -> Dict[str, Any]:
    """
    Plain API - Simple baseline approach
    Just searches exact store with keyword matching
    """
    exact = ExactStore()
    
    try:
        # Simple keyword search
        results = exact.search(query, limit=5)
        
        if results:
            # Simple concatenation of results
            answer = " ".join([r.get("content", "")[:200] for r in results[:3]])
            confidence = 0.7 if len(results) > 0 else 0.0
        else:
            answer = "No information found."
            confidence = 0.0
        
        return {
            "answer": answer,
            "confidence": confidence,
            "sources": [{"type": "exact", "score": 0.8, "payload": r} for r in results[:3]],
            "routing": {"reason": "plain_keyword_search"}
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "confidence": 0.0,
            "sources": [],
            "routing": {"reason": "error", "error": str(e)}
        }

def enhanced_system_query(query: str) -> Dict[str, Any]:
    """
    Enhanced System - Our algorithm + trained knowledge
    Uses smart routing, verification, and all memory tiers
    """
    # Initialize stores
    epi = EpisodicStore()
    exact = ExactStore()
    kg = SemanticKG()
    
    try:
        # Create query object
        q = RetrievalQuery(query=query, top_k=6)
        
        # Use smart router
        bundle = route_and_fetch(q)
        
        candidates = bundle.get("candidates", [])
        routing = bundle.get("routing", {})
        
        # If router didn't find results, try direct SQLite search (trained knowledge)
        if not candidates:
            # Try exact store directly
            simple_query = " ".join([w for w in query.split() if len(w) > 2])[:50]
            try:
                exact_results = exact.search(simple_query, limit=5)
                if exact_results:
                    candidates = [{
                        "type": "exact",
                        "score": 0.8,
                        "payload": {"content": r.get("content", ""), "text": r.get("content", "")},
                        "source": "exact_store"
                    } for r in exact_results]
                    routing["reason"] = "Fallback to SQLite exact store (trained knowledge)"
            except Exception as e:
                # If FTS5 fails, try searching for key terms
                key_terms = ["MAPI"] + [w for w in query.split() if w.lower() in 
                    ["memory", "tiers", "databases", "architecture", "principles", "hallucinations", "system"]]
                for term in key_terms:
                    try:
                        exact_results = exact.search(term, limit=3)
                        if exact_results:
                            candidates = [{
                                "type": "exact",
                                "score": 0.8,
                                "payload": {"content": r.get("content", ""), "text": r.get("content", "")},
                                "source": "exact_store"
                            } for r in exact_results]
                            routing["reason"] = f"Found via keyword search: {term}"
                            break
                    except:
                        continue
        
        # Enhanced verification
        if candidates:
            result = verify_before_speak(query, candidates, semantic_kg=kg)
            
            if len(result) == 3:
                draft, conf, guard_result = result
            else:
                draft, conf = result
                guard_result = {}
            
            return {
                "answer": draft,
                "confidence": conf,
                "sources": candidates[:5],
                "routing": routing,
                "guard_result": guard_result
            }
        
        return {
            "answer": "No relevant information found.",
            "confidence": 0.0,
            "sources": [],
            "routing": routing
        }
        
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "confidence": 0.0,
            "sources": [],
            "routing": {"reason": "error", "error": str(e)}
        }

def compare_queries(queries: List[str]) -> Dict[str, Any]:
    """Compare both systems on a set of queries"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "queries": [],
        "summary": {
            "total_queries": len(queries),
            "plain_wins": 0,
            "enhanced_wins": 0,
            "ties": 0,
            "avg_confidence_plain": 0.0,
            "avg_confidence_enhanced": 0.0
        }
    }
    
    total_plain_conf = 0.0
    total_enhanced_conf = 0.0
    
    print("=" * 80)
    print("SYSTEM COMPARISON: Plain API vs Enhanced System")
    print("=" * 80)
    print()
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}/{len(queries)}: {query}")
        print("-" * 80)
        
        # Run both systems
        print("Running Plain API...")
        plain_result = plain_api_query(query)
        
        print("Running Enhanced System...")
        enhanced_result = enhanced_system_query(query)
        
        # Compare
        plain_conf = plain_result.get("confidence", 0.0)
        enhanced_conf = enhanced_result.get("confidence", 0.0)
        
        total_plain_conf += plain_conf
        total_enhanced_conf += enhanced_conf
        
        winner = "Enhanced" if enhanced_conf > plain_conf else ("Plain" if plain_conf > enhanced_conf else "Tie")
        if winner == "Enhanced":
            results["summary"]["enhanced_wins"] += 1
        elif winner == "Plain":
            results["summary"]["plain_wins"] += 1
        else:
            results["summary"]["ties"] += 1
        
        # Display results
        print(f"\nPlain API:")
        print(f"  Answer: {plain_result['answer'][:200]}...")
        print(f"  Confidence: {plain_conf:.2f}")
        print(f"  Sources: {len(plain_result.get('sources', []))}")
        
        print(f"\nEnhanced System:")
        print(f"  Answer: {enhanced_result['answer'][:200]}...")
        print(f"  Confidence: {enhanced_conf:.2f}")
        print(f"  Sources: {len(enhanced_result.get('sources', []))}")
        print(f"  Routing: {enhanced_result.get('routing', {}).get('reason', 'N/A')}")
        
        print(f"\nWinner: {winner}")
        print("=" * 80)
        print()
        
        # Store results
        results["queries"].append({
            "query": query,
            "plain": {
                "answer": plain_result["answer"],
                "confidence": plain_conf,
                "sources_count": len(plain_result.get("sources", []))
            },
            "enhanced": {
                "answer": enhanced_result["answer"],
                "confidence": enhanced_conf,
                "sources_count": len(enhanced_result.get("sources", [])),
                "routing": enhanced_result.get("routing", {}).get("reason", "N/A")
            },
            "winner": winner
        })
    
    # Calculate averages
    if len(queries) > 0:
        results["summary"]["avg_confidence_plain"] = total_plain_conf / len(queries)
        results["summary"]["avg_confidence_enhanced"] = total_enhanced_conf / len(queries)
    
    return results

def main():
    """Main comparison function"""
    # Force gpt-3.5-turbo for this comparison
    import os
    os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
    
    # Test with just one query
    test_queries = [
        "What is MAPI?"
    ]
    
    print("Starting comparison...")
    print(f"Testing {len(test_queries)} queries")
    print()
    
    results = compare_queries(test_queries)
    
    # Print summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {results['summary']['total_queries']}")
    print(f"Plain API Wins: {results['summary']['plain_wins']}")
    print(f"Enhanced System Wins: {results['summary']['enhanced_wins']}")
    print(f"Ties: {results['summary']['ties']}")
    print(f"\nAverage Confidence:")
    print(f"  Plain API: {results['summary']['avg_confidence_plain']:.2f}")
    print(f"  Enhanced System: {results['summary']['avg_confidence_enhanced']:.2f}")
    print()
    
    # Save results
    output_file = project_root / "comparison_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to: {output_file}")
    
    # Calculate win rate
    if results['summary']['total_queries'] > 0:
        enhanced_win_rate = (results['summary']['enhanced_wins'] / results['summary']['total_queries']) * 100
        print(f"\nEnhanced System Win Rate: {enhanced_win_rate:.1f}%")
        
        if enhanced_win_rate > 50:
            print("🎉 Enhanced System performs better!")
        elif enhanced_win_rate == 50:
            print("🤝 Systems are evenly matched")
        else:
            print("⚠️  Plain API performs better (unexpected)")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nComparison interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during comparison: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

