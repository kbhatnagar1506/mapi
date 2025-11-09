# AIATL Memory System

**Production-grade AI memory system with temporal reasoning, hybrid retrieval, and verify-before-speak architecture.**

Built for AIATL hackathon - solving the fundamental problem of AI memory: hallucinations, context loss, and knowledge drift.

## 🎯 Features

- **Tiered Memory Architecture**: Working/Episodic/Semantic/Exact memory layers
- **Hybrid Retrieval**: Vector search + Knowledge Graph + Exact match
- **Temporal Reasoning**: Query facts "as of" specific dates with supersession tracking
- **Verify-Before-Speak**: Self-RAG style verification to prevent hallucinations
- **Production Ready**: Observability, confidence scoring, source attribution

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+ & pnpm
- (Optional) OpenAI API key or Ollama running locally

### 1. Clone & Setup

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your OPENAI_API_KEY (or use Ollama)
# Or leave blank to use echo mode for testing
```

### 2. Start Services

```bash
# Start Qdrant (vector DB) and Neo4j (knowledge graph)
make up

# Install dependencies
make install
```

### 3. Run Application

**Terminal 1 - Backend:**
```bash
make api
# API runs on http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
make web
# Frontend runs on http://localhost:3000
```

### 4. Seed & Test

```bash
# Add sample memories
make seed

# Run quick evaluation
make eval
```

## 📁 Project Structure

```
memory-sys/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── packages/
│   └── core/         # Shared Python modules
│       ├── config.py
│       ├── schemas.py
│       ├── stores.py  # Episodic, Exact, KG stores
│       ├── retrieval.py
│       ├── verify.py
│       └── llm.py
├── dev/
│   └── docker-compose.yml
├── scripts/
│   ├── seed.py
│   └── eval_quick.py
└── Makefile
```

## 🔌 API Endpoints

### `POST /mem/write`
Store a memory (saved to PostgreSQL + Qdrant + SQLite + Neo4j).

```json
{
  "text": "User prefers dark mode",
  "source": "chat",
  "tags": ["preferences"]
}
```

### `GET /mem/list`
List memories with optional filters.

```bash
GET /mem/list?user_id=user123&source=chat&limit=10
```

### `GET /mem/{memory_id}`
Get a specific memory by ID.

### `POST /ask`
Query the memory system.

```json
{
  "query": "What did I promise John?",
  "as_of": "2025-01-15T00:00:00Z",  // optional
  "top_k": 6
}
```

Returns:
```json
{
  "answer": "Based on your past notes: Send Q3 report to John...",
  "sources": [...],
  "confidence": 0.85
}
```

## 🏗️ Architecture

### Memory Tiers

1. **Working Memory**: Last N turns (in-memory/Redis)
2. **Episodic Memory**: Raw interactions with timestamps (Qdrant vector DB)
3. **Semantic Memory**: Consolidated facts, patterns (Neo4j knowledge graph)
4. **Exact Store**: Verbatim content, IDs (SQLite FTS5)

### Retrieval Flow

```
Query → Router → [Exact | Vector | KG] → Merge → Verify → Answer
```

### Verification Layer

1. **Draft**: Generate answer from retrieved sources
2. **Critique**: LLM evaluates factual support (0.0-1.0 confidence)
3. **Finalize**: Return answer with confidence score

## 🎯 Hackathon Tracks

### Google Track (Agentic Intelligence)
- Multi-agent orchestration ready
- Memory as foundation for autonomous agents
- Temporal reasoning for complex workflows

### Novel Data Collection Track
- Multimodal memory (text + temporal + spatial metadata)
- Novel labeling: temporal annotations, supersession chains
- Human-AI interaction dataset

### Drive Capital (Enterprise Reliability)
- Hallucination prevention through verification
- Confidence scoring and source attribution
- Production-ready observability

## 🛠️ Customization

### Swap LLM Provider

Edit `packages/core/llm.py`:
- OpenAI (default)
- Ollama (local)
- Any OpenAI-compatible API

### Change Vector DB

Edit `packages/core/stores.py`:
- Qdrant (default)
- Pinecone
- Weaviate

### Add Observability

Integrate Langfuse in `packages/core/verify.py` for tracing.

## 📊 Evaluation

Run `make eval` to test:
- Retrieval accuracy
- Confidence calibration
- Source attribution

## 🚨 Troubleshooting

**Qdrant connection error:**
```bash
make down && make up
```

**Neo4j not connecting:**
- Check `docker compose -f dev/docker-compose.yml ps`
- Default credentials: `neo4j/test`

**LLM errors:**
- Set `OPENAI_API_KEY` in `.env`, or
- Run Ollama: `ollama serve` and set `OLLAMA_BASE_URL`

**Port conflicts:**
- Backend: Change `PORT` in `.env`
- Frontend: Edit `apps/web/package.json` scripts

## 📝 Demo Script (5-7 min)

1. **Add Memory**: Paste note + ID → shows in timeline
2. **Recall**: "What did I promise John?" → episodic retrieval
3. **Temporal**: Add conflicting fact → show "as of" difference
4. **Reliability**: Show confidence bar + sources
5. **Eval**: Run `make eval` → show pass rate

## 🏆 Winning Strategy

- **Innovation**: Temporal KG + verify-before-speak (not just RAG)
- **Impact**: Drop-in memory layer for research, compliance, ops
- **Execution**: Live demo + eval metrics + observability
- **Scalability**: Horizontal scaling (vector + KG + exact stores)

## 📄 License

MIT License

## 🙏 Credits

Built for AIATL 2025. Inspired by Supermemory, Memoria, and neuroscience research on memory consolidation.

---

**Ready to win AIATL? Let's build! 🚀**

