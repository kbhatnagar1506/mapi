#!/usr/bin/env python3
"""
Train the memory system directly (without API) on comprehensive MAPI knowledge
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone
from packages.core.stores import EpisodicStore, ExactStore, SemanticKG
from packages.core.schemas import MemoryWrite

# Initialize stores
print("Initializing stores...")
epi = EpisodicStore()
exact = ExactStore()
kg = SemanticKG()
print("✓ Stores initialized\n")

# EXTENSIVE MAPI knowledge - comprehensive training data
mapi_knowledge = [
    # Project Overview
    {
        "text": "MAPI is a production-grade AI memory system built for AIATL hackathon. It solves fundamental LLM problems: hallucinations, context loss, and knowledge drift.",
        "source": "documentation",
        "tags": ["project", "overview", "purpose"]
    },
    {
        "text": "MAPI stands for Memory API - an AI memory system with temporal reasoning, hybrid retrieval, and verify-before-speak architecture.",
        "source": "documentation",
        "tags": ["project", "name", "definition"]
    },
    
    # Architecture - Memory Tiers
    {
        "text": "MAPI uses a tiered memory architecture with four layers: Working Memory (in-memory/Redis), Episodic Memory (Qdrant vector DB), Semantic Memory (Neo4j knowledge graph), and Exact Store (SQLite FTS5).",
        "source": "documentation",
        "tags": ["architecture", "memory-tiers", "design"]
    },
    {
        "text": "Episodic Memory stores raw interactions with timestamps in Qdrant vector database. It uses 384-dimensional embeddings from Sentence Transformers model all-MiniLM-L6-v2.",
        "source": "documentation",
        "tags": ["architecture", "episodic", "qdrant", "embeddings"]
    },
    {
        "text": "Semantic Memory stores consolidated facts and patterns in Neo4j knowledge graph. It tracks relationships, temporal facts, and supports graph traversal queries.",
        "source": "documentation",
        "tags": ["architecture", "semantic", "neo4j", "knowledge-graph"]
    },
    {
        "text": "Exact Store uses SQLite FTS5 for fast exact text matching. It handles verbatim content, IDs, and quoted string searches.",
        "source": "documentation",
        "tags": ["architecture", "exact", "sqlite", "fts5"]
    },
    {
        "text": "PostgreSQL is the primary database for MAPI, storing memory metadata, relationships, and providing ACID compliance. It runs on port 5432.",
        "source": "documentation",
        "tags": ["architecture", "postgresql", "primary-database"]
    },
    
    # Features - 7 Architecture Principles
    {
        "text": "MAPI implements 7 architecture principles: 1) Lifecycle Separation, 2) Smart Retrieval Router, 3) Memory Consolidation, 4) Hybrid Retrieval with Verification, 5) Hallucination Prevention, 6) Temporal Knowledge Graph, 7) Continuous Learning Loop.",
        "source": "documentation",
        "tags": ["features", "architecture-principles", "design"]
    },
    {
        "text": "Smart Retrieval Router automatically routes queries based on patterns: exact match (IDs/quotes) → SQLite, temporal queries → episodic with decay, relationship queries → knowledge graph, semantic queries → vector search.",
        "source": "documentation",
        "tags": ["features", "smart-router", "retrieval"]
    },
    {
        "text": "Hybrid Retrieval combines three sources: vector similarity search (Qdrant), knowledge graph traversal (Neo4j), and exact text matching (SQLite FTS5). Results are merged and deduplicated.",
        "source": "documentation",
        "tags": ["features", "hybrid-retrieval", "search"]
    },
    {
        "text": "Verify-Before-Speak uses two-stage verification: Stage 1 drafts answer from sources, Stage 2 uses LLM to critique factual support and returns confidence score 0.0-1.0.",
        "source": "documentation",
        "tags": ["features", "verification", "hallucination-prevention"]
    },
    {
        "text": "Hallucination Guard implements 4-layer verification: 1) Semantic consistency (embedding similarity), 2) Knowledge graph validation, 3) Source attribution verification, 4) Confidence calibration.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "verification"]
    },
    {
        "text": "Temporal Knowledge Graph supports time-aware reasoning. You can query facts 'as of' specific dates, track fact evolution over time, and follow supersession chains when facts are updated.",
        "source": "documentation",
        "tags": ["features", "temporal", "knowledge-graph", "time-aware"]
    },
    {
        "text": "Memory Consolidation extracts patterns from episodic memories, detects surprises, applies Ebbinghaus decay curve, and creates semantic abstractions. Runs weekly to compress memories.",
        "source": "documentation",
        "tags": ["features", "consolidation", "memory-compression"]
    },
    {
        "text": "Continuous Learning Loop improves memory quality with use. It learns from user corrections, tracks error patterns, creates guard rules after 3 occurrences, and strengthens frequently used facts.",
        "source": "documentation",
        "tags": ["features", "continuous-learning", "improvement"]
    },
    
    # Technical Stack
    {
        "text": "MAPI backend is built with FastAPI (Python), frontend with Next.js (TypeScript), vector DB is Qdrant, knowledge graph is Neo4j, exact store is SQLite, and primary DB is PostgreSQL.",
        "source": "documentation",
        "tags": ["tech-stack", "technologies", "stack"]
    },
    {
        "text": "MAPI uses OpenAI API for LLM calls (gpt-4o-mini default), with fallback to Ollama for local models. Embeddings use Sentence Transformers all-MiniLM-L6-v2 (384 dimensions).",
        "source": "documentation",
        "tags": ["tech-stack", "llm", "embeddings"]
    },
    {
        "text": "MAPI uses real implementations: LLM-powered fact extraction, embedding-based semantic similarity, cosine similarity for matching, Neo4j Cypher queries for graph traversal, and real memory consolidation.",
        "source": "documentation",
        "tags": ["implementation", "real-features", "no-placeholders"]
    },
    
    # API Endpoints
    {
        "text": "MAPI API endpoints: POST /mem/write (store memory), POST /ask (query with smart routing), GET /health (health check), POST /correction (submit correction), POST /consolidate (trigger consolidation), GET /temporal/facts (query as of date), GET /temporal/evolution/{fact_id} (track evolution), GET /stats/learning (learning stats), GET /mem/list (list memories), GET /mem/{memory_id} (get memory).",
        "source": "documentation",
        "tags": ["api", "endpoints", "rest"]
    },
    {
        "text": "POST /ask endpoint supports temporal queries with 'as_of' parameter. Example: {'query': 'What did I promise John?', 'as_of': '2025-01-15T00:00:00Z', 'top_k': 6}.",
        "source": "documentation",
        "tags": ["api", "ask", "temporal"]
    },
    
    # Database Configuration
    {
        "text": "MAPI databases: PostgreSQL (localhost:5432, user: memory_user, password: memory_pass, db: memory_system), Qdrant (localhost:6333), Neo4j (localhost:7687, user: neo4j, password: test), SQLite (./dev/exact.db).",
        "source": "documentation",
        "tags": ["database", "configuration", "connection"]
    },
    {
        "text": "MAPI has graceful fallbacks: if Qdrant is down, uses in-memory vector store with semantic search. If Neo4j is down, uses in-memory knowledge graph. If PostgreSQL is down, uses in-memory storage.",
        "source": "documentation",
        "tags": ["database", "fallbacks", "resilience"]
    },
    
    # Hackathon Alignment
    {
        "text": "MAPI aligns with three AIATL hackathon tracks: Google Track (Agentic Intelligence) - multi-agent ready, memory as foundation for autonomous agents. Novel Data Collection Track - temporal annotations, supersession chains. Drive Capital Track - hallucination prevention, confidence scoring, production-ready observability.",
        "source": "documentation",
        "tags": ["hackathon", "tracks", "alignment"]
    },
    {
        "text": "MAPI winning differentiators: 1) Temporal Reasoning - 'as of' queries with supersession tracking, 2) Verify-Before-Speak - multi-layer hallucination prevention, 3) Hybrid Retrieval - Exact + Vector + KG (not just RAG), 4) Production Ready - confidence scores, source attribution, observability hooks.",
        "source": "documentation",
        "tags": ["hackathon", "differentiators", "winning"]
    },
    
    # Configuration
    {
        "text": "MAPI configuration is centralized in packages/core/advanced_config.py. Configurable values include: similarity thresholds, confidence thresholds, decay constants, search limits (top_k, max snippets), guard rule thresholds, and embedding model name.",
        "source": "documentation",
        "tags": ["configuration", "settings", "customization"]
    },
    {
        "text": "MAPI default configuration: similarity threshold 0.7, confidence threshold 0.6, default top_k 6, exact search limit 5, episodic search limit 6, KG facts limit 20, max snippets verification 4, guard rule threshold 3, embedding model all-MiniLM-L6-v2.",
        "source": "documentation",
        "tags": ["configuration", "defaults", "thresholds"]
    },
    
    # Implementation Details
    {
        "text": "MAPI uses real LLM calls (OpenAI API), real embeddings (Sentence Transformers), real semantic search (cosine similarity), real fact extraction (LLM-powered), real memory consolidation (queries actual stores), and real graph queries (Neo4j Cypher). No placeholders or hardcoded results.",
        "source": "documentation",
        "tags": ["implementation", "real-features", "production-ready"]
    },
    {
        "text": "MAPI semantic similarity uses 384-dimensional embeddings with cosine similarity. Fact extraction uses LLM to extract structured facts with subject/predicate/object. Contradiction detection uses LLM-powered analysis with JSON reasoning.",
        "source": "documentation",
        "tags": ["implementation", "semantic-similarity", "fact-extraction"]
    },
    {
        "text": "MAPI memory consolidation actually queries episodic store for recent memories using get_recent(days=7). It extracts patterns, finds surprises, creates semantic abstractions, and applies temporal decay.",
        "source": "documentation",
        "tags": ["implementation", "consolidation", "real-queries"]
    },
    
    # Project Structure
    {
        "text": "MAPI project structure: apps/api (FastAPI backend), apps/web (Next.js frontend), packages/core (shared Python modules), dev/docker-compose.yml (database services), scripts/ (seed.py, eval_quick.py).",
        "source": "documentation",
        "tags": ["project-structure", "files", "organization"]
    },
    {
        "text": "MAPI core modules: config.py (environment config), schemas.py (Pydantic models), stores.py (EpisodicStore, ExactStore, SemanticKG), retrieval.py (hybrid retrieval), verify.py (verify-before-speak), llm.py (LLM abstraction), smart_router.py (pattern routing), hallucination_guard.py (4-layer verification), consolidator.py (memory consolidation), temporal_kg.py (temporal reasoning), continuous_learner.py (learning loop), memory_tiers.py (lifecycle separation), postgres_store.py (PostgreSQL store).",
        "source": "documentation",
        "tags": ["project-structure", "modules", "core"]
    },
    
    # Usage and Examples
    {
        "text": "To start MAPI: make up (start databases), make install (install dependencies), make api (start backend on port 8000), make web (start frontend on port 3000), make seed (add sample memories), make eval (run evaluation).",
        "source": "documentation",
        "tags": ["usage", "quickstart", "commands"]
    },
    {
        "text": "MAPI supports exact match queries for IDs (e.g., 'ID=PX-8842'), temporal queries ('What did I say last week?'), relationship queries ('What's related to X?'), semantic queries ('What topics interest me?'), and contradiction detection ('What contradicts X?').",
        "source": "documentation",
        "tags": ["usage", "queries", "examples"]
    },
    
    # Key Capabilities
    {
        "text": "MAPI can answer questions about stored memories, track how facts changed over time, prevent hallucinations through multi-layer verification, learn from corrections, consolidate memories through pattern extraction, and route queries intelligently based on query patterns.",
        "source": "documentation",
        "tags": ["capabilities", "features", "what-it-does"]
    },
    {
        "text": "MAPI returns answers with confidence scores (0.0-1.0), source attribution showing where information came from, routing metadata explaining how query was processed, and hallucination flags if issues detected.",
        "source": "documentation",
        "tags": ["capabilities", "output", "response-format"]
    },
]

def train_memory():
    """Train the memory system with comprehensive MAPI knowledge"""
    print("🧠 Training MAPI memory system on project knowledge...")
    print(f"Total knowledge items: {len(mapi_knowledge)}\n")
    
    success_count = 0
    failed_count = 0
    
    for i, knowledge in enumerate(mapi_knowledge, 1):
        try:
            # Create memory write object
            # Map "documentation" source to "file" (valid enum value)
            source = knowledge.get("source", "file")
            if source == "documentation":
                source = "file"
            
            memory = MemoryWrite(
                text=knowledge["text"],
                source=source,
                tags=knowledge.get("tags", []),
                timestamp=datetime.now(timezone.utc)
            )
            
            # Generate ID
            from uuid import uuid4
            mem_id = str(uuid4())
            
            # Write to all stores
            payload = {
                "source": memory.source,
                "tags": memory.tags,
                "timestamp": memory.timestamp.isoformat(),
                "text": memory.text
            }
            
            # Write to episodic store
            epi.write(mem_id, payload, memory.text)
            
            # Write to exact store
            exact.write(mem_id, memory.text)
            
            # Write to knowledge graph (minimal fact)
            if kg:
                try:
                    head = (memory.text.split() or ["MAPI"])[0]
                    kg.add_fact("MAPI", "HAS_INFO", head, int(datetime.now(timezone.utc).timestamp()))
                except:
                    pass
            
            print(f"✓ [{i:3d}/{len(mapi_knowledge)}] Stored: {knowledge['text'][:70]}...")
            print(f"  ID: {mem_id[:8]}..., Tags: {', '.join(knowledge.get('tags', [])[:3])}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ [{i:3d}/{len(mapi_knowledge)}] Failed: {knowledge['text'][:50]}...")
            print(f"  Error: {e}")
            failed_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Training Complete!")
    print(f"   Successfully stored: {success_count} memories")
    if failed_count > 0:
        print(f"   Failed: {failed_count} memories")
    print(f"{'='*70}\n")
    
    # Test retrieval
    print("🧪 Testing knowledge retrieval...")
    from packages.core.retrieval import route_and_fetch
    from packages.core.schemas import RetrievalQuery
    
    test_queries = [
        "What is MAPI?",
        "What are the memory tiers in MAPI?",
        "What databases does MAPI use?",
        "What are the 7 architecture principles?",
    ]
    
    for query in test_queries:
        try:
            result = route_and_fetch(RetrievalQuery(query=query, top_k=3))
            candidates = result.get("candidates", [])
            print(f"\n📝 Query: {query}")
            print(f"   Found {len(candidates)} candidates")
            if candidates:
                print(f"   Top result: {candidates[0].get('payload', {}).get('text', 'N/A')[:80]}...")
        except Exception as e:
            print(f"   ⚠️  Query failed: {e}")
    
    print(f"\n🎉 MAPI memory system is now trained on project knowledge!")
    print(f"   You can now query the system about MAPI using the /ask endpoint")

if __name__ == "__main__":
    train_memory()

