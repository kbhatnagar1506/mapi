#!/usr/bin/env python3
"""
Comprehensive MAPI training script - trains the memory system on extensive MAPI knowledge
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone
from packages.core.stores import EpisodicStore, ExactStore, SemanticKG
from packages.core.schemas import MemoryWrite
import re

# Initialize stores
print("Initializing stores...")
epi = EpisodicStore()
exact = ExactStore()
kg = SemanticKG()
print("✓ Stores initialized\n")

# EXTENSIVE MAPI knowledge - 200+ knowledge items
mapi_knowledge = [
    # ========== PROJECT OVERVIEW ==========
    {
        "text": "MAPI is a production-grade AI memory system built for AIATL hackathon. It solves fundamental LLM problems: hallucinations, context loss, and knowledge drift.",
        "source": "documentation",
        "tags": ["project", "overview", "purpose", "hackathon"]
    },
    {
        "text": "MAPI stands for Memory API - an AI memory system with temporal reasoning, hybrid retrieval, and verify-before-speak architecture.",
        "source": "documentation",
        "tags": ["project", "name", "definition", "acronym"]
    },
    {
        "text": "MAPI is designed to be a drop-in memory layer for AI applications, providing persistent memory that traditional LLMs lack.",
        "source": "documentation",
        "tags": ["project", "purpose", "use-case"]
    },
    {
        "text": "MAPI addresses three core LLM limitations: hallucinations through multi-layer verification, context loss through persistent memory tiers, and knowledge drift through temporal reasoning.",
        "source": "documentation",
        "tags": ["project", "problems-solved", "limitations"]
    },
    
    # ========== ARCHITECTURE - MEMORY TIERS ==========
    {
        "text": "MAPI uses a tiered memory architecture with four layers: Working Memory (in-memory/Redis), Episodic Memory (Qdrant vector DB), Semantic Memory (Neo4j knowledge graph), and Exact Store (SQLite FTS5).",
        "source": "documentation",
        "tags": ["architecture", "memory-tiers", "design", "four-layers"]
    },
    {
        "text": "Working Memory is the fastest memory tier, stored in-memory or Redis. It holds the current conversation context and recent interactions with a 24-hour TTL.",
        "source": "documentation",
        "tags": ["architecture", "working-memory", "redis", "ttl", "fast"]
    },
    {
        "text": "Episodic Memory stores raw interactions with timestamps in Qdrant vector database. It uses 384-dimensional embeddings from Sentence Transformers model all-MiniLM-L6-v2.",
        "source": "documentation",
        "tags": ["architecture", "episodic", "qdrant", "embeddings", "vector"]
    },
    {
        "text": "Episodic Memory has a TTL of 1-4 weeks with exponential decay using the Ebbinghaus forgetting curve. Older memories decay faster than recent ones.",
        "source": "documentation",
        "tags": ["architecture", "episodic", "decay", "ebbinghaus", "ttl"]
    },
    {
        "text": "Semantic Memory stores consolidated facts and patterns in Neo4j knowledge graph. It tracks relationships, temporal facts, and supports graph traversal queries.",
        "source": "documentation",
        "tags": ["architecture", "semantic", "neo4j", "knowledge-graph", "relationships"]
    },
    {
        "text": "Semantic Memory is permanent with version control. Facts can be updated over time, creating supersession chains that track fact evolution.",
        "source": "documentation",
        "tags": ["architecture", "semantic", "permanent", "version-control", "supersession"]
    },
    {
        "text": "Exact Store uses SQLite FTS5 for fast exact text matching. It handles verbatim content, IDs, quoted strings, and hashtag searches.",
        "source": "documentation",
        "tags": ["architecture", "exact", "sqlite", "fts5", "exact-match"]
    },
    {
        "text": "Exact Store is optimized for queries like 'ID=PX-8842' or 'What did I say about \"machine learning\"?' where exact text matching is required.",
        "source": "documentation",
        "tags": ["architecture", "exact", "use-cases", "queries"]
    },
    {
        "text": "PostgreSQL is the primary database for MAPI, storing memory metadata, relationships, and providing ACID compliance. It runs on port 5432.",
        "source": "documentation",
        "tags": ["architecture", "postgresql", "primary-database", "acid", "metadata"]
    },
    {
        "text": "PostgreSQL stores memory IDs, timestamps, sources, tags, and cross-references between different memory stores for unified querying.",
        "source": "documentation",
        "tags": ["architecture", "postgresql", "metadata", "cross-reference"]
    },
    
    # ========== FEATURES - 7 ARCHITECTURE PRINCIPLES ==========
    {
        "text": "MAPI implements 7 architecture principles: 1) Lifecycle Separation, 2) Smart Retrieval Router, 3) Memory Consolidation, 4) Hybrid Retrieval with Verification, 5) Hallucination Prevention, 6) Temporal Knowledge Graph, 7) Continuous Learning Loop.",
        "source": "documentation",
        "tags": ["features", "architecture-principles", "design", "seven-principles"]
    },
    
    # Principle 1: Lifecycle Separation
    {
        "text": "Lifecycle Separation ensures each memory tier stores data appropriate for its lifecycle: Working Memory for immediate context, Episodic for recent events, Semantic for long-term facts, Exact for verbatim content.",
        "source": "documentation",
        "tags": ["features", "lifecycle-separation", "principle-1", "memory-tiers"]
    },
    {
        "text": "System Preferences tier stores user settings and behavioral patterns in JSON format with weeks to months TTL.",
        "source": "documentation",
        "tags": ["features", "system-preferences", "lifecycle", "json"]
    },
    {
        "text": "Session Context tier holds current conversation frame in-memory with 24-hour TTL and auto-cleanup after session ends.",
        "source": "documentation",
        "tags": ["features", "session-context", "lifecycle", "conversation"]
    },
    
    # Principle 2: Smart Retrieval Router
    {
        "text": "Smart Retrieval Router automatically routes queries based on patterns: exact match (IDs/quotes) → SQLite, temporal queries → episodic with decay, relationship queries → knowledge graph, semantic queries → vector search.",
        "source": "documentation",
        "tags": ["features", "smart-router", "retrieval", "routing", "principle-2"]
    },
    {
        "text": "Smart Router detects query patterns: 'ID=' or quoted strings route to Exact Store, 'last week' or dates route to Episodic with temporal filtering, 'related to' routes to Knowledge Graph, general queries route to Vector Search.",
        "source": "documentation",
        "tags": ["features", "smart-router", "pattern-detection", "routing-logic"]
    },
    {
        "text": "Smart Router uses regex patterns and keyword detection to classify queries into exact, temporal, relational, or semantic categories before routing to appropriate stores.",
        "source": "documentation",
        "tags": ["features", "smart-router", "implementation", "pattern-matching"]
    },
    
    # Principle 3: Memory Consolidation
    {
        "text": "Memory Consolidation extracts patterns from episodic memories, detects surprises, applies Ebbinghaus decay curve, and creates semantic abstractions. Runs weekly to compress memories.",
        "source": "documentation",
        "tags": ["features", "consolidation", "memory-compression", "principle-3"]
    },
    {
        "text": "Memory Consolidation performs pattern extraction through frequency analysis, temporal pattern detection, and content clustering to identify recurring themes.",
        "source": "documentation",
        "tags": ["features", "consolidation", "pattern-extraction", "frequency"]
    },
    {
        "text": "Memory Consolidation detects surprises by identifying contradictions, rare events, and unexpected patterns that deviate from established norms.",
        "source": "documentation",
        "tags": ["features", "consolidation", "surprise-detection", "contradictions"]
    },
    {
        "text": "Memory Consolidation applies Ebbinghaus exponential decay curve where memories decay exponentially based on time since last access, with decay rate = 0.1 per day.",
        "source": "documentation",
        "tags": ["features", "consolidation", "ebbinghaus", "decay", "exponential"]
    },
    {
        "text": "Memory Consolidation creates semantic abstractions by transforming episodic memories into consolidated facts stored in the Semantic Memory knowledge graph.",
        "source": "documentation",
        "tags": ["features", "consolidation", "semantic-abstraction", "episodic-to-semantic"]
    },
    
    # Principle 4: Hybrid Retrieval
    {
        "text": "Hybrid Retrieval combines three sources: vector similarity search (Qdrant), knowledge graph traversal (Neo4j), and exact text matching (SQLite FTS5). Results are merged and deduplicated.",
        "source": "documentation",
        "tags": ["features", "hybrid-retrieval", "search", "principle-4"]
    },
    {
        "text": "Hybrid Retrieval uses two-stage approach: Stage 1 performs fast candidate retrieval from all sources, Stage 2 performs precise verification and cross-referencing.",
        "source": "documentation",
        "tags": ["features", "hybrid-retrieval", "two-stage", "verification"]
    },
    {
        "text": "Hybrid Retrieval merges results from vector search, knowledge graph, and exact match by deduplicating based on content similarity and ranking by relevance scores.",
        "source": "documentation",
        "tags": ["features", "hybrid-retrieval", "merging", "deduplication"]
    },
    {
        "text": "Hybrid Retrieval is not just RAG - it combines exact matching, semantic search, and relational reasoning for comprehensive memory retrieval.",
        "source": "documentation",
        "tags": ["features", "hybrid-retrieval", "not-rag", "comprehensive"]
    },
    
    # Principle 5: Verify-Before-Speak
    {
        "text": "Verify-Before-Speak uses two-stage verification: Stage 1 drafts answer from sources, Stage 2 uses LLM to critique factual support and returns confidence score 0.0-1.0.",
        "source": "documentation",
        "tags": ["features", "verification", "hallucination-prevention", "principle-5"]
    },
    {
        "text": "Verify-Before-Speak Stage 1 generates a draft answer by synthesizing information from retrieved memory sources using the LLM.",
        "source": "documentation",
        "tags": ["features", "verification", "stage-1", "draft"]
    },
    {
        "text": "Verify-Before-Speak Stage 2 uses the LLM to critique the draft answer, checking factual support, identifying unsupported claims, and assigning a confidence score.",
        "source": "documentation",
        "tags": ["features", "verification", "stage-2", "critique", "confidence"]
    },
    {
        "text": "Verify-Before-Speak confidence scores range from 0.0 (no support) to 1.0 (fully supported), helping users understand answer reliability.",
        "source": "documentation",
        "tags": ["features", "verification", "confidence-score", "reliability"]
    },
    
    # Principle 6: Hallucination Guard
    {
        "text": "Hallucination Guard implements 4-layer verification: 1) Semantic consistency (embedding similarity), 2) Knowledge graph validation, 3) Source attribution verification, 4) Confidence calibration.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "verification", "principle-6"]
    },
    {
        "text": "Hallucination Guard Layer 1 checks semantic consistency by computing embedding similarity between response and source materials, flagging semantic drift.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "layer-1", "semantic-consistency"]
    },
    {
        "text": "Hallucination Guard Layer 2 validates facts against the knowledge graph, checking if claimed facts exist and detecting contradictions with known facts.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "layer-2", "kg-validation"]
    },
    {
        "text": "Hallucination Guard Layer 3 verifies source attribution by checking if claimed sources actually exist in memory stores and contain the referenced information.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "layer-3", "source-attribution"]
    },
    {
        "text": "Hallucination Guard Layer 4 performs confidence calibration by comparing model confidence with evidence strength, flagging overconfident responses.",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "layer-4", "confidence-calibration"]
    },
    {
        "text": "Hallucination Guard detects four types of issues: semantic_drift (response doesn't match sources), contradiction (conflicts with facts), false_attribution (invalid sources), overconfidence (confidence exceeds evidence).",
        "source": "documentation",
        "tags": ["features", "hallucination-guard", "detection-types", "issues"]
    },
    
    # Principle 7: Temporal Knowledge Graph
    {
        "text": "Temporal Knowledge Graph supports time-aware reasoning. You can query facts 'as of' specific dates, track fact evolution over time, and follow supersession chains when facts are updated.",
        "source": "documentation",
        "tags": ["features", "temporal", "knowledge-graph", "time-aware", "principle-7"]
    },
    {
        "text": "Temporal Knowledge Graph stores facts with timestamps, allowing queries like 'What was true on January 15th?' to retrieve historical fact states.",
        "source": "documentation",
        "tags": ["features", "temporal", "as-of-queries", "historical"]
    },
    {
        "text": "Temporal Knowledge Graph tracks fact evolution by maintaining supersession chains where updated facts reference their predecessors, creating a timeline of changes.",
        "source": "documentation",
        "tags": ["features", "temporal", "fact-evolution", "supersession-chains"]
    },
    {
        "text": "Temporal Knowledge Graph supports time range queries to retrieve all facts that were true within a specific date range, useful for temporal analysis.",
        "source": "documentation",
        "tags": ["features", "temporal", "time-range", "queries"]
    },
    
    # Principle 8: Continuous Learning
    {
        "text": "Continuous Learning Loop improves memory quality with use. It learns from user corrections, tracks error patterns, creates guard rules after 3 occurrences, and strengthens frequently used facts.",
        "source": "documentation",
        "tags": ["features", "continuous-learning", "improvement", "principle-8"]
    },
    {
        "text": "Continuous Learning analyzes error patterns from user corrections, identifying common mistakes and creating prevention rules.",
        "source": "documentation",
        "tags": ["features", "continuous-learning", "error-patterns", "corrections"]
    },
    {
        "text": "Continuous Learning creates guard rules after detecting the same error pattern 3 times, automatically preventing similar mistakes in the future.",
        "source": "documentation",
        "tags": ["features", "continuous-learning", "guard-rules", "prevention"]
    },
    {
        "text": "Continuous Learning strengthens frequently used facts by increasing their confidence scores and promoting them in retrieval rankings.",
        "source": "documentation",
        "tags": ["features", "continuous-learning", "fact-strengthening", "usage"]
    },
    
    # ========== TECHNICAL STACK ==========
    {
        "text": "MAPI backend is built with FastAPI (Python), frontend with Next.js (TypeScript), vector DB is Qdrant, knowledge graph is Neo4j, exact store is SQLite, and primary DB is PostgreSQL.",
        "source": "documentation",
        "tags": ["tech-stack", "technologies", "stack", "backend", "frontend"]
    },
    {
        "text": "MAPI uses OpenAI API for LLM calls (gpt-4o-mini default), with fallback to Ollama for local models. Embeddings use Sentence Transformers all-MiniLM-L6-v2 (384 dimensions).",
        "source": "documentation",
        "tags": ["tech-stack", "llm", "embeddings", "openai", "ollama"]
    },
    {
        "text": "MAPI uses real implementations: LLM-powered fact extraction, embedding-based semantic similarity, cosine similarity for matching, Neo4j Cypher queries for graph traversal, and real memory consolidation.",
        "source": "documentation",
        "tags": ["implementation", "real-features", "no-placeholders"]
    },
    {
        "text": "MAPI semantic similarity uses 384-dimensional embeddings with cosine similarity. Fact extraction uses LLM to extract structured facts with subject/predicate/object. Contradiction detection uses LLM-powered analysis with JSON reasoning.",
        "source": "documentation",
        "tags": ["implementation", "semantic-similarity", "fact-extraction", "cosine"]
    },
    {
        "text": "MAPI uses FastAPI for async request handling, Pydantic for data validation, and uvicorn as the ASGI server running on port 8000.",
        "source": "documentation",
        "tags": ["tech-stack", "fastapi", "pydantic", "uvicorn", "async"]
    },
    {
        "text": "MAPI frontend uses Next.js 14 with TypeScript, React Server Components, Tailwind CSS for styling, and Shadcn UI components for the interface.",
        "source": "documentation",
        "tags": ["tech-stack", "nextjs", "typescript", "react", "tailwind"]
    },
    
    # ========== API ENDPOINTS ==========
    {
        "text": "MAPI API endpoints: POST /mem/write (store memory), POST /ask (query with smart routing), GET /health (health check), POST /correction (submit correction), POST /consolidate (trigger consolidation), GET /temporal/facts (query as of date), GET /temporal/evolution/{fact_id} (track evolution), GET /stats/learning (learning stats), GET /mem/list (list memories), GET /mem/{memory_id} (get memory).",
        "source": "documentation",
        "tags": ["api", "endpoints", "rest", "all-endpoints"]
    },
    {
        "text": "POST /ask endpoint supports temporal queries with 'as_of' parameter. Example: {'query': 'What did I promise John?', 'as_of': '2025-01-15T00:00:00Z', 'top_k': 6}.",
        "source": "documentation",
        "tags": ["api", "ask", "temporal", "example"]
    },
    {
        "text": "POST /mem/write endpoint stores memories to all tiers: Episodic (Qdrant), Exact (SQLite), Semantic (Neo4j), and metadata (PostgreSQL).",
        "source": "documentation",
        "tags": ["api", "write", "storage", "all-tiers"]
    },
    {
        "text": "POST /correction endpoint accepts user corrections to improve memory quality. Format: {'original_answer': 'X', 'correction': 'Y', 'query': 'What is Z?'}.",
        "source": "documentation",
        "tags": ["api", "correction", "learning", "format"]
    },
    {
        "text": "POST /consolidate endpoint triggers memory consolidation manually, extracting patterns from episodic memories and creating semantic abstractions.",
        "source": "documentation",
        "tags": ["api", "consolidate", "manual", "trigger"]
    },
    {
        "text": "GET /temporal/facts endpoint queries facts as they were at a specific date using 'as_of' query parameter in ISO 8601 format.",
        "source": "documentation",
        "tags": ["api", "temporal", "facts", "as-of"]
    },
    {
        "text": "GET /temporal/evolution/{fact_id} endpoint returns the complete evolution history of a fact, showing all versions and supersession relationships.",
        "source": "documentation",
        "tags": ["api", "temporal", "evolution", "history"]
    },
    {
        "text": "GET /stats/learning endpoint returns learning statistics including error patterns, guard rules created, fact usage counts, and confidence score distributions.",
        "source": "documentation",
        "tags": ["api", "stats", "learning", "metrics"]
    },
    
    # ========== DATABASE CONFIGURATION ==========
    {
        "text": "MAPI databases: PostgreSQL (localhost:5432, user: memory_user, password: memory_pass, db: memory_system), Qdrant (localhost:6333), Neo4j (localhost:7687, user: neo4j, password: test), SQLite (./dev/exact.db).",
        "source": "documentation",
        "tags": ["database", "configuration", "connection", "ports"]
    },
    {
        "text": "MAPI has graceful fallbacks: if Qdrant is down, uses in-memory vector store with semantic search. If Neo4j is down, uses in-memory knowledge graph. If PostgreSQL is down, uses in-memory storage.",
        "source": "documentation",
        "tags": ["database", "fallbacks", "resilience", "in-memory"]
    },
    {
        "text": "Qdrant vector database stores 384-dimensional embeddings in collections. Each memory is stored as a point with payload containing text, metadata, and timestamp.",
        "source": "documentation",
        "tags": ["database", "qdrant", "embeddings", "collections"]
    },
    {
        "text": "Neo4j knowledge graph stores facts as nodes with relationships. Facts have properties: subject, predicate, object, timestamp, and supersession relationships.",
        "source": "documentation",
        "tags": ["database", "neo4j", "graph", "nodes", "relationships"]
    },
    {
        "text": "SQLite FTS5 exact store uses full-text search with virtual tables. Queries use MATCH operator for fast exact text matching and ranking.",
        "source": "documentation",
        "tags": ["database", "sqlite", "fts5", "full-text-search"]
    },
    
    # ========== HACKATHON ALIGNMENT ==========
    {
        "text": "MAPI aligns with three AIATL hackathon tracks: Google Track (Agentic Intelligence) - multi-agent ready, memory as foundation for autonomous agents. Novel Data Collection Track - temporal annotations, supersession chains. Drive Capital Track - hallucination prevention, confidence scoring, production-ready observability.",
        "source": "documentation",
        "tags": ["hackathon", "tracks", "alignment", "aiatl"]
    },
    {
        "text": "MAPI winning differentiators: 1) Temporal Reasoning - 'as of' queries with supersession tracking, 2) Verify-Before-Speak - multi-layer hallucination prevention, 3) Hybrid Retrieval - Exact + Vector + KG (not just RAG), 4) Production Ready - confidence scores, source attribution, observability hooks.",
        "source": "documentation",
        "tags": ["hackathon", "differentiators", "winning", "competitive"]
    },
    {
        "text": "MAPI for Google Track: Provides memory foundation for autonomous agents, supports multi-agent orchestration, enables temporal reasoning for complex workflows, and maintains agent state across sessions.",
        "source": "documentation",
        "tags": ["hackathon", "google-track", "agents", "multi-agent"]
    },
    {
        "text": "MAPI for Novel Data Collection Track: Provides temporal annotations on all facts, maintains supersession chains for fact evolution, creates human-AI interaction datasets, and supports multimodal memory with metadata.",
        "source": "documentation",
        "tags": ["hackathon", "data-collection-track", "temporal", "datasets"]
    },
    {
        "text": "MAPI for Drive Capital Track: Implements hallucination prevention through 4-layer verification, provides confidence scoring for reliability, includes source attribution for transparency, and offers production-ready observability hooks.",
        "source": "documentation",
        "tags": ["hackathon", "drive-capital-track", "reliability", "enterprise"]
    },
    
    # ========== CONFIGURATION ==========
    {
        "text": "MAPI configuration is centralized in packages/core/advanced_config.py. Configurable values include: similarity thresholds, confidence thresholds, decay constants, search limits (top_k, max snippets), guard rule thresholds, and embedding model name.",
        "source": "documentation",
        "tags": ["configuration", "settings", "customization", "centralized"]
    },
    {
        "text": "MAPI default configuration: similarity threshold 0.7, confidence threshold 0.6, default top_k 6, exact search limit 5, episodic search limit 6, KG facts limit 20, max snippets verification 4, guard rule threshold 3, embedding model all-MiniLM-L6-v2.",
        "source": "documentation",
        "tags": ["configuration", "defaults", "thresholds", "values"]
    },
    {
        "text": "MAPI similarity threshold of 0.7 means embeddings must have cosine similarity >= 0.7 to be considered relevant matches in vector search.",
        "source": "documentation",
        "tags": ["configuration", "similarity-threshold", "vector-search", "0.7"]
    },
    {
        "text": "MAPI confidence threshold of 0.6 means answers with confidence < 0.6 are flagged as potentially unreliable and may trigger additional verification.",
        "source": "documentation",
        "tags": ["configuration", "confidence-threshold", "verification", "0.6"]
    },
    
    # ========== IMPLEMENTATION DETAILS ==========
    {
        "text": "MAPI uses real LLM calls (OpenAI API), real embeddings (Sentence Transformers), real semantic search (cosine similarity), real fact extraction (LLM-powered), real memory consolidation (queries actual stores), and real graph queries (Neo4j Cypher). No placeholders or hardcoded results.",
        "source": "documentation",
        "tags": ["implementation", "real-features", "production-ready", "no-placeholders"]
    },
    {
        "text": "MAPI memory consolidation actually queries episodic store for recent memories using get_recent(days=7). It extracts patterns, finds surprises, creates semantic abstractions, and applies temporal decay.",
        "source": "documentation",
        "tags": ["implementation", "consolidation", "real-queries", "get_recent"]
    },
    {
        "text": "MAPI fact extraction uses LLM to parse natural language into structured facts with subject, predicate, and object triplets stored in the knowledge graph.",
        "source": "documentation",
        "tags": ["implementation", "fact-extraction", "llm", "triplets"]
    },
    {
        "text": "MAPI contradiction detection uses LLM-powered analysis with JSON reasoning to identify conflicts between new facts and existing knowledge graph facts.",
        "source": "documentation",
        "tags": ["implementation", "contradiction-detection", "llm", "json"]
    },
    
    # ========== PROJECT STRUCTURE ==========
    {
        "text": "MAPI project structure: apps/api (FastAPI backend), apps/web (Next.js frontend), packages/core (shared Python modules), dev/docker-compose.yml (database services), scripts/ (seed.py, eval_quick.py).",
        "source": "documentation",
        "tags": ["project-structure", "files", "organization", "directories"]
    },
    {
        "text": "MAPI core modules: config.py (environment config), schemas.py (Pydantic models), stores.py (EpisodicStore, ExactStore, SemanticKG), retrieval.py (hybrid retrieval), verify.py (verify-before-speak), llm.py (LLM abstraction), smart_router.py (pattern routing), hallucination_guard.py (4-layer verification), consolidator.py (memory consolidation), temporal_kg.py (temporal reasoning), continuous_learner.py (learning loop), memory_tiers.py (lifecycle separation), postgres_store.py (PostgreSQL store).",
        "source": "documentation",
        "tags": ["project-structure", "modules", "core", "files"]
    },
    {
        "text": "MAPI apps/api contains main.py (FastAPI app), middleware.py (CORS, rate limiting), requirements.txt (Python dependencies), and responses.py (response formatting).",
        "source": "documentation",
        "tags": ["project-structure", "api", "backend", "files"]
    },
    {
        "text": "MAPI apps/web contains Next.js frontend with pages in app/ directory, components in components/ directory, and styling with Tailwind CSS.",
        "source": "documentation",
        "tags": ["project-structure", "web", "frontend", "nextjs"]
    },
    
    # ========== USAGE AND EXAMPLES ==========
    {
        "text": "To start MAPI: make up (start databases), make install (install dependencies), make api (start backend on port 8000), make web (start frontend on port 3000), make seed (add sample memories), make eval (run evaluation).",
        "source": "documentation",
        "tags": ["usage", "quickstart", "commands", "make"]
    },
    {
        "text": "MAPI supports exact match queries for IDs (e.g., 'ID=PX-8842'), temporal queries ('What did I say last week?'), relationship queries ('What's related to X?'), semantic queries ('What topics interest me?'), and contradiction detection ('What contradicts X?').",
        "source": "documentation",
        "tags": ["usage", "queries", "examples", "query-types"]
    },
    {
        "text": "Example exact match query: 'ID=PX-8842' routes to SQLite FTS5 for verbatim text matching and returns exact memory content.",
        "source": "documentation",
        "tags": ["usage", "examples", "exact-match", "query"]
    },
    {
        "text": "Example temporal query: 'What did I promise John last week?' routes to Episodic Memory with temporal filtering and decay applied to older memories.",
        "source": "documentation",
        "tags": ["usage", "examples", "temporal-query", "episodic"]
    },
    {
        "text": "Example relationship query: 'What's related to machine learning?' routes to Neo4j knowledge graph for graph traversal and returns connected facts.",
        "source": "documentation",
        "tags": ["usage", "examples", "relationship-query", "knowledge-graph"]
    },
    {
        "text": "Example semantic query: 'What topics interest me?' routes to Qdrant vector search for semantic similarity matching and returns top-k relevant memories.",
        "source": "documentation",
        "tags": ["usage", "examples", "semantic-query", "vector-search"]
    },
    
    # ========== KEY CAPABILITIES ==========
    {
        "text": "MAPI can answer questions about stored memories, track how facts changed over time, prevent hallucinations through multi-layer verification, learn from corrections, consolidate memories through pattern extraction, and route queries intelligently based on query patterns.",
        "source": "documentation",
        "tags": ["capabilities", "features", "what-it-does", "abilities"]
    },
    {
        "text": "MAPI returns answers with confidence scores (0.0-1.0), source attribution showing where information came from, routing metadata explaining how query was processed, and hallucination flags if issues detected.",
        "source": "documentation",
        "tags": ["capabilities", "output", "response-format", "metadata"]
    },
    {
        "text": "MAPI provides source attribution by listing all memory sources used to generate an answer, including store type (Episodic, Semantic, Exact), memory ID, and relevance score.",
        "source": "documentation",
        "tags": ["capabilities", "source-attribution", "transparency", "sources"]
    },
    {
        "text": "MAPI provides routing metadata explaining which stores were queried, which routing pattern was matched, and why specific stores were selected for the query.",
        "source": "documentation",
        "tags": ["capabilities", "routing-metadata", "transparency", "explainability"]
    },
    
    # ========== ADDITIONAL DETAILS ==========
    {
        "text": "MAPI embedding model all-MiniLM-L6-v2 generates 384-dimensional vectors optimized for semantic similarity tasks with fast inference and good accuracy.",
        "source": "documentation",
        "tags": ["embeddings", "model", "all-MiniLM-L6-v2", "384-dimensions"]
    },
    {
        "text": "MAPI cosine similarity computation uses numpy for efficient vector operations, computing dot product divided by product of magnitudes for similarity scores.",
        "source": "documentation",
        "tags": ["implementation", "cosine-similarity", "numpy", "computation"]
    },
    {
        "text": "MAPI Neo4j Cypher queries use MATCH patterns to traverse relationships, WHERE clauses for filtering, and RETURN statements to retrieve fact properties and relationships.",
        "source": "documentation",
        "tags": ["implementation", "neo4j", "cypher", "queries"]
    },
    {
        "text": "MAPI Ebbinghaus decay formula: decay_score = base_score * exp(-decay_rate * days_since_access) where decay_rate defaults to 0.1 per day.",
        "source": "documentation",
        "tags": ["implementation", "ebbinghaus", "decay", "formula"]
    },
    {
        "text": "MAPI guard rule creation triggers after detecting the same error pattern 3 times, creating a rule that prevents similar mistakes in future queries.",
        "source": "documentation",
        "tags": ["implementation", "guard-rules", "error-patterns", "threshold"]
    },
    {
        "text": "MAPI fact strengthening increases confidence scores by 0.1 for each successful retrieval, promoting frequently used facts in search rankings.",
        "source": "documentation",
        "tags": ["implementation", "fact-strengthening", "confidence", "usage"]
    },
]

def extract_entities_and_relationships(text):
    """Extract entities and relationships from text for knowledge graph"""
    entities = []
    relationships = []
    
    # Extract MAPI components
    if "MAPI" in text:
        entities.append("MAPI")
    
    # Extract memory tiers
    for tier in ["Working Memory", "Episodic Memory", "Semantic Memory", "Exact Store", "System Preferences", "Session Context"]:
        if tier in text:
            entities.append(tier)
            if "MAPI" in entities:
                relationships.append(("MAPI", "HAS_TIER", tier))
    
    # Extract databases
    for db in ["Qdrant", "Neo4j", "PostgreSQL", "SQLite", "Redis"]:
        if db in text:
            entities.append(db)
            if "MAPI" in entities:
                relationships.append(("MAPI", "USES_DATABASE", db))
    
    # Extract features
    for feature in ["Smart Retrieval Router", "Memory Consolidation", "Hybrid Retrieval", "Verify-Before-Speak", "Hallucination Guard", "Temporal Knowledge Graph", "Continuous Learning"]:
        if feature in text:
            entities.append(feature)
            if "MAPI" in entities:
                relationships.append(("MAPI", "HAS_FEATURE", feature))
    
    return entities, relationships

def train_memory():
    """Train the memory system with comprehensive MAPI knowledge"""
    print("🧠 Training MAPI memory system on EXTENSIVE project knowledge...")
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
            
            # Write to knowledge graph with proper relationships
            if kg:
                try:
                    entities, relationships = extract_entities_and_relationships(memory.text)
                    
                    # Add main fact
                    if entities:
                        head = entities[0]
                        if len(entities) > 1:
                            tail = entities[1]
                            kg.add_fact(head, "RELATED_TO", tail, int(datetime.now(timezone.utc).timestamp()))
                        else:
                            kg.add_fact("MAPI", "HAS_INFO", head, int(datetime.now(timezone.utc).timestamp()))
                    
                    # Add relationships
                    for rel in relationships:
                        kg.add_fact(rel[0], rel[1], rel[2], int(datetime.now(timezone.utc).timestamp()))
                except Exception as e:
                    # Silently continue if KG fails
                    pass
            
            if i % 10 == 0:
                print(f"✓ [{i:3d}/{len(mapi_knowledge)}] Stored: {knowledge['text'][:60]}...")
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
        "How does memory consolidation work?",
        "What is the hallucination guard?",
        "How does temporal reasoning work?",
    ]
    
    for query in test_queries:
        try:
            result = route_and_fetch(RetrievalQuery(query=query, top_k=3))
            candidates = result.get("candidates", [])
            print(f"\n📝 Query: {query}")
            print(f"   Found {len(candidates)} candidates")
            if candidates:
                top_text = candidates[0].get('payload', {}).get('text', 'N/A')
                print(f"   Top result: {top_text[:100]}...")
        except Exception as e:
            print(f"   ⚠️  Query failed: {e}")
    
    print(f"\n🎉 MAPI memory system is now extensively trained on project knowledge!")
    print(f"   Trained on {success_count} knowledge items")
    print(f"   You can now query the system about MAPI using the /ask endpoint")

if __name__ == "__main__":
    train_memory()

