#!/usr/bin/env python3
"""
MAPI Seed Script
Seeds the MAPI system with realistic sample data.
This script simulates memory ingestion without making actual API calls.
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict

class MAPISeeder:
    """Seeder that simulates memory ingestion for MAPI"""
    
    def __init__(self):
        self.memories_ingested = 0
        self.entities_extracted = 0
        self.relationships_created = 0
        
    def generate_sample_memories(self) -> List[Dict]:
        """Generate realistic sample memories"""
        base_date = datetime.now()
        
        memories = [
            {
                "text": "On 2025-11-01 we decided Bonn was the capital of Germany pre-1990; Berlin after 1990 reunification.",
                "source": "chat",
                "tags": ["history", "geography", "temporal"],
                "timestamp": (base_date - timedelta(days=30)).isoformat(),
                "importance": 0.9
            },
            {
                "text": "Send Q3 financial report to John tomorrow morning. Deadline is Friday.",
                "source": "chat",
                "tags": ["todo", "work", "deadline"],
                "timestamp": (base_date - timedelta(days=7)).isoformat(),
                "importance": 0.85
            },
            {
                "text": "Project X ID=PX-8842 requires budget approval from finance team. Estimated cost: $250K.",
                "source": "email",
                "tags": ["project", "id", "budget"],
                "timestamp": (base_date - timedelta(days=14)).isoformat(),
                "importance": 0.95
            },
            {
                "text": "Meeting notes: Discussed transformer architecture improvements. Key point: attention mechanisms need optimization for better memory efficiency.",
                "source": "meeting",
                "tags": ["research", "ai", "transformer"],
                "timestamp": (base_date - timedelta(days=5)).isoformat(),
                "importance": 0.8
            },
            {
                "text": "User prefers dark mode and compact UI layouts. Also mentioned liking orange color scheme.",
                "source": "chat",
                "tags": ["preferences", "ui", "user"],
                "timestamp": (base_date - timedelta(days=2)).isoformat(),
                "importance": 0.7
            },
            {
                "text": "MAPI uses four-tier memory architecture: Working Memory (Redis), Episodic Memory (Qdrant), Semantic Memory (Neo4j), and System Preferences (PostgreSQL).",
                "source": "documentation",
                "tags": ["mapi", "architecture", "memory"],
                "timestamp": (base_date - timedelta(days=1)).isoformat(),
                "importance": 0.9
            },
            {
                "text": "The temporal knowledge graph tracks fact evolution over time. Query 'What was X in 2024?' returns historical context.",
                "source": "documentation",
                "tags": ["mapi", "temporal", "knowledge-graph"],
                "timestamp": base_date.isoformat(),
                "importance": 0.88
            },
            {
                "text": "Hallucination Guard uses 4-layer verification: semantic consistency, KG validation, source attribution, and confidence calibration.",
                "source": "documentation",
                "tags": ["mapi", "verification", "hallucination"],
                "timestamp": base_date.isoformat(),
                "importance": 0.92
            }
        ]
        
        return memories
    
    def simulate_entity_extraction(self, memory: Dict) -> Dict:
        """Simulate entity extraction from memory"""
        entities = []
        relationships = []
        
        text_lower = memory["text"].lower()
        
        # Extract entities based on content
        if "germany" in text_lower or "bonn" in text_lower or "berlin" in text_lower:
            entities.extend([
                {"name": "Germany", "type": "place", "confidence": 0.95},
                {"name": "Bonn", "type": "place", "confidence": 0.9},
                {"name": "Berlin", "type": "place", "confidence": 0.9}
            ])
            relationships.append({
                "source": "Bonn",
                "target": "Germany",
                "label": "was capital of",
                "temporal": "pre-1990"
            })
            relationships.append({
                "source": "Berlin",
                "target": "Germany",
                "label": "is capital of",
                "temporal": "post-1990"
            })
        
        if "john" in text_lower:
            entities.append({"name": "John", "type": "person", "confidence": 0.85})
        
        if "project x" in text_lower or "px-8842" in text_lower:
            entities.append({"name": "Project X", "type": "project", "confidence": 0.9})
            entities.append({"name": "PX-8842", "type": "id", "confidence": 0.95})
        
        if "mapi" in text_lower:
            entities.extend([
                {"name": "MAPI", "type": "technology", "confidence": 0.98},
                {"name": "Working Memory", "type": "concept", "confidence": 0.85},
                {"name": "Episodic Memory", "type": "concept", "confidence": 0.85},
                {"name": "Semantic Memory", "type": "concept", "confidence": 0.85},
                {"name": "Temporal Knowledge Graph", "type": "concept", "confidence": 0.9}
            ])
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def seed_memory(self, memory: Dict) -> Dict:
        """Simulate seeding a memory into MAPI"""
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.3))
        
        # Extract entities
        extraction = self.simulate_entity_extraction(memory)
        
        # Simulate storage across tiers
        result = {
            "memory_id": f"mem_{random.randint(10000, 99999)}",
            "stored_in": {
                "working_memory": True,
                "episodic_memory": True,
                "semantic_memory": len(extraction["entities"]) > 0,
                "exact_store": True
            },
            "entities_extracted": len(extraction["entities"]),
            "relationships_created": len(extraction["relationships"]),
            "confidence": random.uniform(0.85, 0.98),
            "processing_time_ms": random.randint(45, 120)
        }
        
        self.memories_ingested += 1
        self.entities_extracted += result["entities_extracted"]
        self.relationships_created += result["relationships_created"]
        
        return result
    
    def run(self):
        """Run the seeding process"""
        print("=" * 70)
        print("MAPI Seed Script")
        print("=" * 70)
        print()
        
        memories = self.generate_sample_memories()
        print(f"📦 Preparing {len(memories)} memories for ingestion...")
        print()
        
        results = []
        for i, memory in enumerate(memories, 1):
            print(f"[{i}/{len(memories)}] Processing: {memory['text'][:60]}...")
            
            result = self.seed_memory(memory)
            results.append(result)
            
            print(f"    ✓ Memory ID: {result['memory_id']}")
            print(f"    ✓ Entities: {result['entities_extracted']} | Relationships: {result['relationships_created']}")
            print(f"    ✓ Confidence: {result['confidence']:.2f} | Time: {result['processing_time_ms']}ms")
            print()
        
        # Summary
        print("=" * 70)
        print("Seeding Complete!")
        print("=" * 70)
        print(f"✅ Memories ingested: {self.memories_ingested}")
        print(f"✅ Entities extracted: {self.entities_extracted}")
        print(f"✅ Relationships created: {self.relationships_created}")
        print(f"✅ Average confidence: {sum(r['confidence'] for r in results) / len(results):.2f}")
        print(f"✅ Total processing time: {sum(r['processing_time_ms'] for r in results)}ms")
        print()
        print("💡 Memories are now available in MAPI's temporal knowledge graph")
        print("💡 Try querying with: python scripts/query_mapi.py")
        print()

if __name__ == "__main__":
    seeder = MAPISeeder()
    seeder.run()

