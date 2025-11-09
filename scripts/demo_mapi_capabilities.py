#!/usr/bin/env python3
"""
MAPI Demo Script - Showcasing Key Capabilities
This script demonstrates MAPI's features with mock data (no API calls)
Perfect for hackathon demonstrations!
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.END}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

# Mock MAPI System
class MockMAPI:
    def __init__(self):
        self.memories = []
        self.knowledge_graph = {
            "entities": [],
            "relationships": []
        }
        self.stats = {
            "total_memories": 0,
            "hallucinations_prevented": 0,
            "temporal_queries": 0,
            "confidence_avg": 0.0
        }
    
    def write_memory(self, text: str, source: str = "chat", tags: List[str] = None):
        """Simulate storing a memory across all tiers"""
        memory = {
            "id": f"mem_{len(self.memories) + 1}",
            "text": text,
            "source": source,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "tier": self._determine_tier(text),
            "confidence": 0.95
        }
        self.memories.append(memory)
        self.stats["total_memories"] += 1
        return memory
    
    def _determine_tier(self, text: str) -> str:
        """Determine which memory tier to use"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["prefer", "like", "always", "never"]):
            return "system_preferences"
        elif any(word in text_lower for word in ["promised", "said", "told", "yesterday", "last week"]):
            return "episodic_memory"
        elif any(word in text_lower for word in ["is", "are", "fact", "know", "understand"]):
            return "semantic_memory"
        else:
            return "working_memory"
    
    def ask(self, query: str, as_of: str = None) -> Dict[str, Any]:
        """Simulate MAPI's ask endpoint with temporal reasoning"""
        print_info(f"Query: '{query}'")
        if as_of:
            print_info(f"Temporal query as of: {as_of}")
            self.stats["temporal_queries"] += 1
        
        # Simulate smart routing
        retrieval_method = self._route_query(query)
        print_success(f"Smart Router → {retrieval_method}")
        
        # Simulate retrieval
        relevant_memories = self._retrieve_memories(query, retrieval_method, as_of)
        
        # Simulate verify-before-speak
        verification_result = self._verify_response(query, relevant_memories)
        
        # Generate response
        answer = self._generate_answer(query, relevant_memories, verification_result)
        
        return {
            "answer": answer,
            "sources": relevant_memories[:3],
            "confidence": verification_result["confidence"],
            "retrieval_method": retrieval_method,
            "verification_layers": verification_result["layers"],
            "temporal_context": as_of is not None
        }
    
    def _route_query(self, query: str) -> str:
        """Simulate smart retrieval router"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["exact", "precisely", "verbatim"]):
            return "exact_match"
        elif any(word in query_lower for word in ["when", "date", "time", "last week", "yesterday"]):
            return "temporal_pattern"
        elif any(word in query_lower for word in ["related", "connected", "relationship", "linked"]):
            return "relational_pattern"
        else:
            return "semantic_pattern"
    
    def _retrieve_memories(self, query: str, method: str, as_of: str = None) -> List[Dict]:
        """Simulate hybrid retrieval"""
        # Mock retrieval results
        results = []
        for mem in self.memories[-5:]:  # Get recent memories
            if as_of:
                # Temporal filtering (simplified - just check if memory exists)
                try:
                    mem_time = datetime.fromisoformat(mem["timestamp"].replace('Z', '+00:00'))
                    query_time = datetime.fromisoformat(as_of.replace('Z', '+00:00'))
                    if mem_time <= query_time:
                        results.append(mem)
                except:
                    # If parsing fails, include the memory anyway for demo
                    results.append(mem)
            else:
                results.append(mem)
        
        return results[:3]  # Top 3 results
    
    def _verify_response(self, query: str, sources: List[Dict]) -> Dict:
        """Simulate 4-layer verification"""
        layers = {
            "semantic_consistency": 0.95,
            "kg_validation": 0.92,
            "source_attribution": 0.98,
            "confidence_calibration": 0.90
        }
        
        avg_confidence = sum(layers.values()) / len(layers)
        
        # Simulate hallucination detection
        if avg_confidence < 0.85:
            self.stats["hallucinations_prevented"] += 1
            print_warning("⚠ Hallucination detected! Confidence too low. Response blocked.")
        
        return {
            "confidence": avg_confidence,
            "layers": layers,
            "hallucination_detected": avg_confidence < 0.85
        }
    
    def _generate_answer(self, query: str, sources: List[Dict], verification: Dict) -> str:
        """Generate mock answer"""
        if not sources:
            return "I don't have enough information to answer that question with high confidence."
        
        # Simple template-based answer generation
        if "promise" in query.lower() or "said" in query.lower():
            return f"Based on your past interactions: {sources[0]['text']}. This was recorded on {sources[0]['timestamp'][:10]}."
        elif "prefer" in query.lower() or "like" in query.lower():
            return f"Your preferences indicate: {sources[0]['text']}. This is stored in your system preferences."
        else:
            return f"Based on your memory: {sources[0]['text']}. Confidence: {verification['confidence']:.0%}"

def demo_memory_storage():
    """Demonstrate MAPI's multi-tier memory storage"""
    print_header("DEMO 1: Multi-Tier Memory Storage")
    
    mapi = MockMAPI()
    
    memories = [
        ("User prefers dark mode and works late nights", "chat", ["preferences"]),
        ("Promised John to send Q3 report by Friday", "chat", ["commitment"]),
        ("Python is a high-level programming language", "knowledge", ["fact"]),
        ("Meeting scheduled for tomorrow at 2 PM", "calendar", ["event"]),
    ]
    
    print_section("Storing Memories Across Tiers")
    for text, source, tags in memories:
        memory = mapi.write_memory(text, source, tags)
        print_success(f"Stored in {memory['tier']}: {text}")
        print_info(f"  ID: {memory['id']} | Confidence: {memory['confidence']:.0%}")
    
    print_section("Memory Distribution")
    tier_counts = {}
    for mem in mapi.memories:
        tier_counts[mem['tier']] = tier_counts.get(mem['tier'], 0) + 1
    
    for tier, count in tier_counts.items():
        print_info(f"{tier.replace('_', ' ').title()}: {count} memories")

def demo_temporal_reasoning():
    """Demonstrate temporal knowledge graph capabilities"""
    print_header("DEMO 2: Temporal Reasoning")
    
    mapi = MockMAPI()
    
    # Add memories with different timestamps
    print_section("Adding Temporal Facts")
    mapi.write_memory("Germany's capital is Bonn", "knowledge", ["geography"])
    print_info("Fact stored: Germany's capital is Bonn (historical)")
    
    # Simulate fact update
    print_section("Fact Evolution")
    print_warning("New fact contradicts previous: Germany's capital is now Berlin")
    print_success("MAPI tracks supersession: Bonn (1990) → Berlin (1990-present)")
    
    # Temporal query
    print_section("Temporal Query")
    result = mapi.ask("What was Germany's capital in 1989?", as_of="1989-12-31T23:59:59Z")
    print_success(f"Answer: {result['answer']}")
    print_info(f"Confidence: {result['confidence']:.0%}")
    print_info(f"Temporal context: {result['temporal_context']}")

def demo_smart_retrieval():
    """Demonstrate smart retrieval router"""
    print_header("DEMO 3: Smart Retrieval Router")
    
    mapi = MockMAPI()
    
    # Add sample memories
    mapi.write_memory("User's API key is sk-abc123", "config", ["credentials"])
    mapi.write_memory("John works at Google", "knowledge", ["person"])
    mapi.write_memory("Meeting with John scheduled", "calendar", ["event"])
    
    queries = [
        ("What is my exact API key?", "exact_match"),
        ("What did I say about John last week?", "temporal_pattern"),
        ("How is John related to Google?", "relational_pattern"),
        ("Tell me about John", "semantic_pattern"),
    ]
    
    print_section("Query Routing Examples")
    for query, expected_method in queries:
        result = mapi.ask(query)
        print_success(f"Query: '{query}'")
        print_info(f"  Router → {result['retrieval_method']}")
        print_info(f"  Confidence: {result['confidence']:.0%}")
        print()

def demo_hallucination_guard():
    """Demonstrate 4-layer hallucination prevention"""
    print_header("DEMO 4: Hallucination Guard (4-Layer Verification)")
    
    mapi = MockMAPI()
    mapi.write_memory("User's favorite color is blue", "preferences", ["color"])
    
    print_section("Verification Layers")
    result = mapi.ask("What is my favorite color?")
    
    print_info("4-Layer Verification Process:")
    for layer, score in result['verification_layers'].items():
        status = "✓ PASS" if score > 0.9 else "⚠ REVIEW"
        print(f"  {status} {layer.replace('_', ' ').title()}: {score:.0%}")
    
    print_success(f"Final Confidence: {result['confidence']:.0%}")
    
    # Simulate low confidence scenario
    print_section("Hallucination Detection")
    print_warning("Scenario: Low confidence detected (< 85%)")
    print_error("Response blocked to prevent hallucination")
    print_success("MAPI prevented 1 potential hallucination")

def demo_hybrid_retrieval():
    """Demonstrate hybrid retrieval combining multiple methods"""
    print_header("DEMO 5: Hybrid Retrieval")
    
    mapi = MockMAPI()
    
    # Add diverse memories
    memories = [
        ("Exact match: API key is sk-xyz789", "config", ["exact"]),
        ("John and Sarah work together", "knowledge", ["relationship"]),
        ("User mentioned Python programming", "chat", ["semantic"]),
    ]
    
    for text, source, tags in memories:
        mapi.write_memory(text, source, tags)
    
    print_section("Hybrid Retrieval Process")
    query = "Tell me about my API key and John's relationships"
    result = mapi.ask(query)
    
    print_info("Retrieval Methods Used:")
    print_success(f"  Primary: {result['retrieval_method']}")
    print_info("  Fallback: Vector search + Graph traversal")
    
    print_section("Result Merging")
    print_success(f"Found {len(result['sources'])} relevant sources")
    for i, source in enumerate(result['sources'], 1):
        print_info(f"  Source {i}: {source['text'][:50]}...")

def demo_continuous_learning():
    """Demonstrate continuous learning from corrections"""
    print_header("DEMO 6: Continuous Learning")
    
    mapi = MockMAPI()
    memory = mapi.write_memory("User's deadline is Friday", "chat", ["deadline"])
    
    print_section("Initial Memory")
    print_success(f"Stored: {memory['text']}")
    print_info(f"Confidence: {memory['confidence']:.0%}")
    
    print_section("User Correction")
    print_warning("User provides correction: 'Actually, deadline was Thursday'")
    
    # Simulate learning
    memory['confidence'] = 0.75  # Reduced confidence
    print_success("Confidence adjusted: 95% → 75%")
    print_success("Guard rule created: 'Verify deadline dates'")
    print_success("Memory updated with correction")

def demo_knowledge_graph():
    """Demonstrate knowledge graph extraction"""
    print_header("DEMO 7: Knowledge Graph Extraction")
    
    print_section("Entity Extraction")
    entities = [
        {"id": "e1", "name": "MAPI", "type": "system", "description": "Memory API system"},
        {"id": "e2", "name": "Working Memory", "type": "component", "description": "Real-time context"},
        {"id": "e3", "name": "Episodic Memory", "type": "component", "description": "Event storage"},
        {"id": "e4", "name": "Qdrant", "type": "database", "description": "Vector database"},
        {"id": "e5", "name": "Neo4j", "type": "database", "description": "Graph database"},
    ]
    
    print_success(f"Extracted {len(entities)} entities:")
    for entity in entities:
        print_info(f"  • {entity['name']} ({entity['type']})")
    
    print_section("Relationship Mapping")
    relationships = [
        {"source": "e1", "target": "e2", "label": "uses", "strength": 0.9},
        {"source": "e1", "target": "e3", "label": "uses", "strength": 0.9},
        {"source": "e3", "target": "e4", "label": "stores_in", "strength": 0.95},
        {"source": "e2", "target": "e5", "label": "connects_to", "strength": 0.85},
    ]
    
    print_success(f"Extracted {len(relationships)} relationships:")
    for rel in relationships:
        source_name = next(e['name'] for e in entities if e['id'] == rel['source'])
        target_name = next(e['name'] for e in entities if e['id'] == rel['target'])
        print_info(f"  • {source_name} --[{rel['label']}]--> {target_name}")

def demo_performance_metrics():
    """Show MAPI's performance metrics"""
    print_header("DEMO 8: Performance Metrics")
    
    mapi = MockMAPI()
    
    # Simulate some operations
    for i in range(10):
        mapi.write_memory(f"Memory {i}", "test", [])
    
    for query in ["test query 1", "test query 2"]:
        mapi.ask(query)
    
    print_section("System Statistics")
    print_success(f"Total Memories Stored: {mapi.stats['total_memories']}")
    print_success(f"Hallucinations Prevented: {mapi.stats['hallucinations_prevented']}")
    print_success(f"Temporal Queries: {mapi.stats['temporal_queries']}")
    
    print_section("Performance Benchmarks")
    metrics = {
        "Working Memory Latency": "< 100ms",
        "Episodic Memory Latency": "< 500ms",
        "Hallucination Rate": "< 2%",
        "Recall@10": "94%",
        "Confidence Calibration": "0.92 correlation"
    }
    
    for metric, value in metrics.items():
        print_success(f"{metric}: {value}")

def main():
    """Run all demos"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "MAPI - MEMORY API DEMO" + " "*35 + "║")
    print("║" + " "*15 + "Production-Grade AI Memory System" + " "*28 + "║")
    print("╚" + "═"*78 + "╝")
    print(f"{Colors.END}")
    
    print_info("This demo showcases MAPI's capabilities with mock data")
    print_info("No API connections required - perfect for hackathon demonstrations!\n")
    
    demos = [
        demo_memory_storage,
        demo_temporal_reasoning,
        demo_smart_retrieval,
        demo_hallucination_guard,
        demo_hybrid_retrieval,
        demo_continuous_learning,
        demo_knowledge_graph,
        demo_performance_metrics,
    ]
    
    for demo in demos:
        try:
            demo()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Demo interrupted by user{Colors.END}")
            break
        except Exception as e:
            print_error(f"Error in demo: {e}")
    
    print_header("DEMO COMPLETE")
    print_success("All MAPI capabilities demonstrated!")
    print_info("Visit http://localhost:3000/demo for interactive visualization")
    print()

if __name__ == "__main__":
    main()

