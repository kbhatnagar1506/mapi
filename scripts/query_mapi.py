#!/usr/bin/env python3
"""
MAPI Query Script
Demonstrates querying the MAPI system with various query types.
This script simulates query processing without making actual API calls.
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List

class MAPIQuerier:
    """Querier that simulates MAPI query processing"""
    
    def __init__(self):
        self.query_count = 0
        self.total_latency_ms = 0
        
    def simulate_retrieval(self, query: str) -> Dict:
        """Simulate retrieval from MAPI memory tiers"""
        query_lower = query.lower()
        
        # Simulate routing decision
        if any(word in query_lower for word in ["id", "px-", "project"]):
            retrieval_method = "exact_match"
            tier = "exact_store"
        elif any(word in query_lower for word in ["when", "date", "2024", "1990", "temporal"]):
            retrieval_method = "temporal_kg"
            tier = "semantic_memory"
        elif any(word in query_lower for word in ["relationship", "connected", "related"]):
            retrieval_method = "graph_traversal"
            tier = "semantic_memory"
        else:
            retrieval_method = "vector_search"
            tier = "episodic_memory"
        
        # Generate mock sources based on query
        sources = []
        answer = ""
        confidence = random.uniform(0.88, 0.96)
        
        if "john" in query_lower or "report" in query_lower:
            sources = [
                {
                    "text": "Send Q3 financial report to John tomorrow morning. Deadline is Friday.",
                    "source": "chat",
                    "timestamp": "2025-11-01T10:30:00Z",
                    "confidence": 0.95,
                    "memory_id": "mem_12345",
                    "tier": "episodic_memory"
                }
            ]
            answer = "Based on your past notes, you promised to send the Q3 financial report to John. The deadline mentioned was Friday morning."
        
        elif "project x" in query_lower or "px-8842" in query_lower:
            sources = [
                {
                    "text": "Project X ID=PX-8842 requires budget approval from finance team. Estimated cost: $250K.",
                    "source": "email",
                    "timestamp": "2025-10-18T14:20:00Z",
                    "confidence": 0.98,
                    "memory_id": "mem_23456",
                    "tier": "exact_store"
                }
            ]
            answer = "Project X has ID PX-8842 and requires budget approval from the finance team. The estimated cost is $250K."
        
        elif "germany" in query_lower or "capital" in query_lower or "bonn" in query_lower or "berlin" in query_lower:
            sources = [
                {
                    "text": "On 2025-11-01 we decided Bonn was the capital of Germany pre-1990; Berlin after 1990 reunification.",
                    "source": "chat",
                    "timestamp": "2025-11-01T09:15:00Z",
                    "confidence": 0.92,
                    "memory_id": "mem_34567",
                    "tier": "semantic_memory"
                }
            ]
            if "1990" in query_lower or "1989" in query_lower:
                answer = "Bonn was the capital of Germany until 1990. After reunification in 1990, Berlin became the capital."
            else:
                answer = "Germany's capital is Berlin (since 1990). Prior to reunification, Bonn was the capital."
        
        elif "mapi" in query_lower or "memory" in query_lower:
            sources = [
                {
                    "text": "MAPI uses four-tier memory architecture: Working Memory (Redis), Episodic Memory (Qdrant), Semantic Memory (Neo4j), and System Preferences (PostgreSQL).",
                    "source": "documentation",
                    "timestamp": "2025-11-07T12:00:00Z",
                    "confidence": 0.95,
                    "memory_id": "mem_45678",
                    "tier": "semantic_memory"
                },
                {
                    "text": "The temporal knowledge graph tracks fact evolution over time. Query 'What was X in 2024?' returns historical context.",
                    "source": "documentation",
                    "timestamp": "2025-11-07T12:05:00Z",
                    "confidence": 0.93,
                    "memory_id": "mem_45679",
                    "tier": "semantic_memory"
                }
            ]
            answer = "MAPI implements a four-tier memory architecture: Working Memory (Redis for real-time context), Episodic Memory (Qdrant for event storage), Semantic Memory (Neo4j for knowledge graphs), and System Preferences (PostgreSQL). The system includes temporal reasoning capabilities to track fact evolution over time."
        
        elif "transformer" in query_lower or "attention" in query_lower:
            sources = [
                {
                    "text": "Meeting notes: Discussed transformer architecture improvements. Key point: attention mechanisms need optimization for better memory efficiency.",
                    "source": "meeting",
                    "timestamp": "2025-11-03T15:45:00Z",
                    "confidence": 0.90,
                    "memory_id": "mem_56789",
                    "tier": "episodic_memory"
                }
            ]
            answer = "In your meeting notes, you discussed transformer architecture improvements. The key point mentioned was that attention mechanisms need optimization for better memory efficiency."
        
        else:
            sources = [
                {
                    "text": "User prefers dark mode and compact UI layouts. Also mentioned liking orange color scheme.",
                    "source": "chat",
                    "timestamp": "2025-11-06T11:20:00Z",
                    "confidence": 0.85,
                    "memory_id": "mem_67890",
                    "tier": "episodic_memory"
                }
            ]
            answer = "Based on available information, I found some user preferences related to UI design. However, I don't have specific information about your query. Could you provide more context?"
            confidence = 0.75
        
        # Simulate processing latency
        latency_ms = random.randint(80, 250)
        time.sleep(latency_ms / 1000)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "retrieval_method": retrieval_method,
            "tier_used": tier,
            "latency_ms": latency_ms,
            "entities_found": len(sources),
            "verification_passed": True,
            "hallucination_risk": "low" if confidence > 0.9 else "medium"
        }
    
    def query(self, query: str, as_of: str = None) -> Dict:
        """Simulate querying MAPI"""
        print(f"🔍 Query: {query}")
        if as_of:
            print(f"📅 Temporal query (as of): {as_of}")
        
        result = self.simulate_retrieval(query)
        
        print(f"   ✓ Retrieval method: {result['retrieval_method']}")
        print(f"   ✓ Tier used: {result['tier_used']}")
        print(f"   ✓ Confidence: {result['confidence']:.2f}")
        print(f"   ✓ Latency: {result['latency_ms']}ms")
        print(f"   ✓ Sources found: {result['entities_found']}")
        print(f"   ✓ Verification: {'PASSED' if result['verification_passed'] else 'FAILED'}")
        print(f"   ✓ Hallucination risk: {result['hallucination_risk'].upper()}")
        print()
        print(f"📝 Answer:")
        print(f"   {result['answer']}")
        print()
        
        if result['sources']:
            print(f"📚 Sources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'], 1):
                print(f"   [{i}] {source['text'][:80]}...")
                print(f"       Source: {source['source']} | Tier: {source['tier']} | Confidence: {source['confidence']:.2f}")
            print()
        
        self.query_count += 1
        self.total_latency_ms += result['latency_ms']
        
        return result
    
    def run_queries(self):
        """Run a set of queries"""
        print("=" * 70)
        print("MAPI Query Script")
        print("=" * 70)
        print()
        
        queries = [
            "What report did I promise John?",
            "What's Project X ID?",
            "What was Germany's capital in 1989?",
            "How does MAPI's memory architecture work?",
            "What did we discuss about transformers?"
        ]
        
        results = []
        for query in queries:
            result = self.query(query)
            results.append(result)
            print("-" * 70)
            print()
        
        # Summary
        print("=" * 70)
        print("Query Summary")
        print("=" * 70)
        print(f"✅ Total queries: {self.query_count}")
        print(f"✅ Average latency: {self.total_latency_ms / self.query_count:.0f}ms")
        print(f"✅ Average confidence: {sum(r['confidence'] for r in results) / len(results):.2f}")
        print(f"✅ All verifications passed: {all(r['verification_passed'] for r in results)}")
        print(f"✅ Low hallucination risk: {sum(1 for r in results if r['hallucination_risk'] == 'low')}/{len(results)}")
        print()

if __name__ == "__main__":
    querier = MAPIQuerier()
    querier.run_queries()

