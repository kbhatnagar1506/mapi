import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, status, Request, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

from packages.core.schemas import (
    MemoryWrite, RetrievalQuery, Answer, Candidate, 
    CorrectionRequest, ConsolidationRequest, SourceType
)
from packages.core.stores import EpisodicStore, SemanticKG, ExactStore
from packages.core.postgres_store import PostgresStore
from packages.core.retrieval import route_and_fetch
from packages.core.verify import verify_before_speak
from packages.core.temporal_kg import TemporalKnowledgeGraph
from packages.core.continuous_learner import ContinuousLearner
from packages.core.consolidator import MemoryConsolidator
from packages.core.memory_tiers import SystemPreferences, SessionContext
from apps.api.responses import APIResponse, PaginatedResponse, ErrorResponse
from apps.api.middleware import LoggingMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mapi")

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=4)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MAPI - Memory API",
    description="""
    Production-grade AI memory system with temporal reasoning, 
    hybrid retrieval, and verify-before-speak architecture.
    
    ## Features
    
    - **Tiered Memory Architecture**: Working/Episodic/Semantic/Exact layers
    - **Smart Retrieval Router**: Pattern-based query routing
    - **Hallucination Prevention**: 4-layer verification guard
    - **Temporal Reasoning**: Query facts "as of" specific dates
    - **Continuous Learning**: Improves with user corrections
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "memories",
            "description": "Memory storage and retrieval operations"
        },
        {
            "name": "queries",
            "description": "Query operations with smart routing and verification"
        },
        {
            "name": "temporal",
            "description": "Temporal reasoning and fact evolution tracking"
        },
        {
            "name": "learning",
            "description": "Continuous learning and corrections"
        },
        {
            "name": "monitoring",
            "description": "Health checks and statistics"
        }
    ]
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An error occurred"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "ok": False,
            "error": "Validation error",
            "detail": exc.errors()
        }
    )

# Initialize stores (with graceful fallbacks if services aren't running)
try:
    epi = EpisodicStore()
    logger.info("✓ EpisodicStore initialized")
except Exception as e:
    logger.warning(f"⚠ EpisodicStore init warning: {e}")
    epi = None

try:
    kg = SemanticKG()
    logger.info("✓ SemanticKG initialized")
except Exception as e:
    logger.warning(f"⚠ SemanticKG init warning: {e}")
    kg = None

try:
    exact = ExactStore()
    logger.info("✓ ExactStore initialized")
except Exception as e:
    logger.warning(f"⚠ ExactStore init warning: {e}")
    exact = None

# Initialize PostgreSQL (Primary Database)
try:
    postgres = PostgresStore()
    logger.info("✓ PostgresStore initialized")
except Exception as e:
    logger.warning(f"⚠ PostgresStore init warning: {e}")
    postgres = None

# Initialize advanced components
temporal_kg = TemporalKnowledgeGraph(kg) if kg else None
continuous_learner = ContinuousLearner(epi, kg) if (epi and kg) else None
consolidator = MemoryConsolidator(epi, kg) if (epi and kg) else None
system_prefs = SystemPreferences()
session_context = SessionContext()

@app.get("/", tags=["monitoring"])
def root():
    """Root endpoint"""
    return {
        "ok": True,
        "service": "memory-api",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.post(
    "/mem/write",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[Dict],
    tags=["memories"],
    summary="Store a memory",
    description="Store a memory in all storage layers (PostgreSQL, Qdrant, SQLite, Neo4j)",
    responses={
        201: {"description": "Memory stored successfully"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("100/minute")
async def mem_write(request: Request, m: MemoryWrite):
    """Store a memory with validation and error handling"""
    try:
        eid = str(uuid4())
        payload = {
            "source": m.source.value,
            "tags": m.tags,
            "timestamp": m.timestamp.isoformat(),
            "text": m.text
        }
        
        # Write to PostgreSQL (primary database)
        postgres_id = None
        if postgres:
            try:
                postgres_id = postgres.create_memory(
                    text=m.text,
                    source=m.source.value,
                    tags=m.tags,
                    timestamp=m.timestamp,
                    qdrant_id=eid,
                    exact_id=eid
                )
            except Exception as e:
                logger.error(f"PostgreSQL write error: {e}")
                # Non-fatal, continue with other stores
        
        # Write to episodic and exact stores (run in parallel)
        loop = asyncio.get_event_loop()
        write_tasks = []
        
        if epi:
            write_tasks.append(loop.run_in_executor(executor, epi.write, eid, payload, m.text))
        if exact:
            write_tasks.append(loop.run_in_executor(executor, exact.write, eid, m.text))
        
        if write_tasks:
            await asyncio.gather(*write_tasks, return_exceptions=True)
        
        # Write to knowledge graph
        if kg:
            try:
                head = (m.text.split() or ["unknown"])[0]
                kg.add_fact("User", "MENTIONED", head, int(datetime.now(timezone.utc).timestamp()))
            except Exception as e:
                logger.warning(f"KG write error (non-fatal): {e}")
        
        return APIResponse(
            ok=True,
            data={"id": eid, "postgres_id": postgres_id},
            message="Memory stored successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Memory write error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store memory"
        )

@app.post(
    "/ask",
    response_model=Answer,
    tags=["queries"],
    summary="Query memory system",
    description="""
    Query the memory system with smart routing and verification.
    
    - Automatically routes to appropriate stores based on query pattern
    - Applies 4-layer hallucination guard
    - Returns confidence scores and source attribution
    - Supports temporal reasoning with 'as_of' parameter
    """,
    responses={
        200: {"description": "Successful query"},
        400: {"description": "Invalid query"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("30/minute")
async def ask(request: Request, q: RetrievalQuery):
    """Enhanced query with smart routing and verification"""
    try:
        # Run blocking operations in thread pool
        loop = asyncio.get_event_loop()
        bundle = await loop.run_in_executor(executor, route_and_fetch, q)
        
        # Enhanced verification with hallucination guard
        result = await loop.run_in_executor(
            executor,
            verify_before_speak,
            q.query,
            bundle["candidates"],
            kg
        )
        
        if len(result) == 3:
            draft, conf, guard_result = result
        else:
            # Fallback for old signature
            draft, conf = result
            guard_result = {}
        
        cands = [Candidate(**c) for c in bundle["candidates"]]
        
        # Track successful retrieval for continuous learning (background)
        if continuous_learner:
            used_facts = [c for c in bundle["candidates"][:3]]
            # Run in background to not block response
            loop.run_in_executor(
                executor,
                continuous_learner.on_successful_retrieval,
                q.query,
                bundle["candidates"],
                used_facts
            )
        
        # Include routing metadata in notes
        routing_info = bundle.get("routing", {})
        notes = f"Routing: {routing_info.get('reason', 'default')}"
        if guard_result.get("hallucinated"):
            notes += f" | Hallucination flags: {', '.join(guard_result.get('flags', []))}"
        
        return Answer(
            answer=draft,
            sources=cands,
            confidence=conf,
            notes=notes
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )

@app.get(
    "/health",
    tags=["monitoring"],
    summary="Health check",
    description="Comprehensive health check for all components"
)
def health():
    """Enhanced health check with all components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "stores": {},
        "components": {},
        "stats": {}
    }
    
    # Check stores
    stores_status = {}
    
    # PostgreSQL
    if postgres:
        try:
            from sqlalchemy import text
            with postgres.get_session() as session:
                session.execute(text("SELECT 1"))
            stores_status["postgres"] = {"status": "ok"}
        except Exception as e:
            stores_status["postgres"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
    else:
        stores_status["postgres"] = {"status": "not_initialized"}
    
    # Episodic
    stores_status["episodic"] = {
        "status": "ok" if epi else "not_initialized"
    }
    
    # Exact
    stores_status["exact"] = {
        "status": "ok" if exact else "not_initialized"
    }
    
    # Knowledge Graph
    if kg:
        stores_status["kg"] = {
            "status": "ok" if (kg.drv and kg._connected) else "not_connected"
        }
    else:
        stores_status["kg"] = {"status": "not_initialized"}
    
    health_status["stores"] = stores_status
    
    # Components
    health_status["components"] = {
        "temporal_kg": "ok" if temporal_kg else "not_initialized",
        "continuous_learner": "ok" if continuous_learner else "not_initialized",
        "consolidator": "ok" if consolidator else "not_initialized"
    }
    
    # Stats
    if continuous_learner:
        health_status["stats"]["learning"] = continuous_learner.get_learning_stats()
    
    # Determine overall status
    all_critical_ok = (
        stores_status.get("exact", {}).get("status") == "ok" or
        stores_status.get("episodic", {}).get("status") == "ok"
    )
    
    status_code = status.HTTP_200_OK if all_critical_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        content=health_status,
        status_code=status_code
    )

@app.get(
    "/mem/list",
    response_model=PaginatedResponse[Dict],
    tags=["memories"],
    summary="List memories",
    description="List memories with filtering and pagination"
)
def list_memories(
    user_id: Optional[str] = Query(None, min_length=1, max_length=100, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, min_length=1, max_length=100, description="Filter by session ID"),
    source: Optional[SourceType] = Query(None, description="Filter by source type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """List memories from PostgreSQL with enhanced filtering"""
    if not postgres:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL not initialized"
        )
    
    try:
        source_str = source.value if source else None
        memories = postgres.list_memories(
            user_id=user_id,
            session_id=session_id,
            source=source_str,
            limit=limit,
            offset=offset
        )
        
        # Get total count (simplified - would need count method in postgres_store)
        total = len(memories) + offset  # Approximation
        page = (offset // limit) + 1
        
        return PaginatedResponse(
            ok=True,
            data=memories,
            pagination={
                "offset": offset,
                "limit": limit,
                "total": total
            },
            total=total,
            page=page,
            limit=limit,
            has_more=len(memories) == limit
        )
    except Exception as e:
        logger.error(f"List memories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list memories"
        )

@app.get(
    "/mem/{memory_id}",
    response_model=APIResponse[Dict],
    tags=["memories"],
    summary="Get memory by ID",
    description="Retrieve a specific memory by its ID"
)
def get_memory(memory_id: str):
    """Get a specific memory by ID"""
    if not postgres:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL not initialized"
        )
    
    try:
        memory = postgres.get_memory(memory_id)
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )
        
        return APIResponse(
            ok=True,
            data=memory,
            message="Memory retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory"
        )

@app.post(
    "/correction",
    response_model=APIResponse[Dict],
    tags=["learning"],
    summary="Submit correction",
    description="Submit user correction for continuous learning"
)
@limiter.limit("50/minute")
async def submit_correction(request: Request, correction: CorrectionRequest):
    """Submit user correction for continuous learning"""
    if not continuous_learner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Continuous learner not initialized"
        )
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            continuous_learner.on_user_correction,
            correction.original_answer,
            correction.correction,
            correction.query
        )
        
        return APIResponse(
            ok=True,
            data=result,
            message="Correction processed successfully"
        )
    except Exception as e:
        logger.error(f"Correction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process correction"
        )

@app.post(
    "/consolidate",
    response_model=APIResponse[Dict],
    tags=["learning"],
    summary="Trigger memory consolidation",
    description="Trigger memory consolidation process"
)
async def consolidate_memories(request: Request, consolidation: ConsolidationRequest = ConsolidationRequest()):
    """Trigger memory consolidation"""
    if not consolidator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Consolidator not initialized"
        )
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            consolidator.consolidate_weekly
        )
        
        return APIResponse(
            ok=True,
            data=result,
            message="Consolidation completed"
        )
    except Exception as e:
        logger.error(f"Consolidation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to consolidate memories"
        )

@app.get(
    "/temporal/facts",
    response_model=APIResponse[Dict],
    tags=["temporal"],
    summary="Query temporal facts",
    description="Query facts as of a specific time"
)
def get_temporal_facts(
    as_of: Optional[str] = Query(None, description="ISO format datetime (e.g., 2025-01-15T00:00:00Z)")
):
    """Query facts as of a specific time"""
    if not temporal_kg:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Temporal KG not initialized"
        )
    
    as_of_date = None
    if as_of:
        try:
            as_of_date = datetime.fromisoformat(as_of.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: 2025-01-15T00:00:00Z"
            )
    
    try:
        facts = temporal_kg.query_temporal("", as_of_date)
        
        return APIResponse(
            ok=True,
            data={
                "as_of": as_of or "current",
                "facts": facts,
                "count": len(facts)
            }
        )
    except Exception as e:
        logger.error(f"Temporal query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query temporal facts"
        )

@app.get(
    "/temporal/evolution/{fact_id}",
    response_model=APIResponse[Dict],
    tags=["temporal"],
    summary="Track fact evolution",
    description="Track how a fact evolved over time"
)
def get_fact_evolution(fact_id: str):
    """Track how a fact evolved over time"""
    if not temporal_kg:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Temporal KG not initialized"
        )
    
    try:
        evolution = temporal_kg.track_fact_evolution(fact_id)
        
        return APIResponse(
            ok=True,
            data=evolution,
            message="Fact evolution retrieved"
        )
    except Exception as e:
        logger.error(f"Fact evolution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track fact evolution"
        )

@app.get(
    "/stats/learning",
    response_model=APIResponse[Dict],
    tags=["monitoring"],
    summary="Get learning statistics",
    description="Get continuous learning statistics"
)
def get_learning_stats():
    """Get continuous learning statistics"""
    if not continuous_learner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Continuous learner not initialized"
        )
    
    try:
        stats = continuous_learner.get_learning_stats()
        
        return APIResponse(
            ok=True,
            data=stats,
            message="Learning statistics retrieved"
        )
    except Exception as e:
        logger.error(f"Learning stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning statistics"
        )
