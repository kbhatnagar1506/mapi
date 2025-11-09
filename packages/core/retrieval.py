import re
from typing import Dict
from .stores import EpisodicStore, SemanticKG, ExactStore
from .schemas import RetrievalQuery
from .smart_router import SmartRetriever

# Initialize stores
epi = EpisodicStore()
kg = SemanticKG()
exact = ExactStore()

# Initialize smart router
smart_router = SmartRetriever()

def route_and_fetch(rq: RetrievalQuery) -> Dict:
    """
    Enhanced retrieval with smart routing
    Uses SmartRetriever for pattern-based routing
    """
    # Use smart router for intelligent routing
    result = smart_router.route_query(
        query=rq.query,
        exact_store=exact,
        episodic_store=epi,
        semantic_kg=kg,
        as_of=rq.as_of
    )
    
    # Return with routing metadata
    return {
        "candidates": result["candidates"][:rq.top_k],
        "routing": result["routing"]
    }

