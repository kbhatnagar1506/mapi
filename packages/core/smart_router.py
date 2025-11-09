"""
Smart Retrieval Router: Match Storage to Query Pattern
Architecture Principle #2
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .schemas import RetrievalQuery
from .advanced_config import (
    EXACT_SEARCH_LIMIT,
    EPISODIC_SEARCH_LIMIT,
    KG_FACTS_LIMIT,
    KG_RELATIONSHIP_LIMIT,
    SCORE_EXACT_MATCH,
    SCORE_CONTRADICTION,
    SCORE_KG_DEFAULT,
    SCORE_RELATIONSHIP,
    SCORE_EPISODIC_DEFAULT,
    TEMPORAL_DECAY_DAYS,
    MIN_DECAY_FACTOR,
)

class SmartRetriever:
    """Routes queries to the appropriate storage based on query pattern"""
    
    # Patterns for query classification
    EXACT_PATTERNS = [
        re.compile(r"#[A-Za-z0-9_-]+"),  # Hashtags
        re.compile(r"\bID[:=]\s*\w+"),  # ID: something
        re.compile(r"\bexact(?:ly)?\b", re.I),  # "exact" keyword
        re.compile(r'"[^"]+"'),  # Quoted strings
    ]
    
    TEMPORAL_PATTERNS = [
        re.compile(r"\b(?:last|yesterday|today|tomorrow|week|month|year|ago)\b", re.I),
        re.compile(r"\b(?:when|as of|at that time|during)\b", re.I),
        re.compile(r"\d{4}-\d{2}-\d{2}"),  # Dates
    ]
    
    RELATIONSHIP_PATTERNS = [
        re.compile(r"\b(?:related to|connected|associated|linked|relationship)\b", re.I),
        re.compile(r"\b(?:who|what|where|how|why)\b.*\b(?:with|to|from)\b", re.I),
    ]
    
    SEMANTIC_PATTERNS = [
        re.compile(r"\b(?:topics|interests|preferences|patterns|usually|always|never)\b", re.I),
        re.compile(r"\b(?:what do I|my|I typically|I usually)\b", re.I),
    ]
    
    CONTRADICTION_PATTERNS = [
        re.compile(r"\b(?:contradict|conflict|disagree|wrong|incorrect|mistake)\b", re.I),
        re.compile(r"\b(?:but|however|although|despite)\b", re.I),
    ]
    
    def needs_exact_match(self, query: str) -> bool:
        """Check if query requires exact token matching"""
        return any(pattern.search(query) for pattern in self.EXACT_PATTERNS)
    
    def needs_temporal_reasoning(self, query: str) -> bool:
        """Check if query requires temporal filtering"""
        return any(pattern.search(query) for pattern in self.TEMPORAL_PATTERNS)
    
    def needs_relationship_reasoning(self, query: str) -> bool:
        """Check if query requires graph traversal"""
        return any(pattern.search(query) for pattern in self.RELATIONSHIP_PATTERNS)
    
    def needs_semantic_search(self, query: str) -> bool:
        """Check if query requires semantic understanding"""
        return any(pattern.search(query) for pattern in self.SEMANTIC_PATTERNS)
    
    def needs_contradiction_detection(self, query: str) -> bool:
        """Check if query is about finding contradictions"""
        return any(pattern.search(query) for pattern in self.CONTRADICTION_PATTERNS)
    
    def route_query(
        self, 
        query: str, 
        exact_store,
        episodic_store,
        semantic_kg,
        as_of: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate storage systems
        Returns routing decision and candidates
        """
        routing_decision = {
            "primary": [],
            "secondary": [],
            "reason": ""
        }
        
        candidates = []
        
        # Priority 1: Exact match (highest precision)
        if self.needs_exact_match(query):
            routing_decision["primary"].append("exact")
            routing_decision["reason"] = "Query contains exact identifiers (IDs, quotes, hashtags)"
            try:
                results = exact_store.search(query, limit=EXACT_SEARCH_LIMIT)
                candidates.extend([{
                    "type": "exact",
                    "score": r.get("score", SCORE_EXACT_MATCH),
                    "payload": r,
                    "source": "exact_store"
                } for r in results])
            except Exception as e:
                print(f"Exact search error: {e}")
        
        # Priority 2: Contradiction detection (requires KG)
        if self.needs_contradiction_detection(query):
            routing_decision["primary"].append("kg")
            routing_decision["reason"] = "Query seeks contradiction detection"
            try:
                # This would use enhanced KG queries
                facts = semantic_kg.active_facts()
                candidates.extend([{
                    "type": "kg",
                    "score": SCORE_CONTRADICTION,
                    "payload": f,
                    "source": "knowledge_graph"
                } for f in facts[:EXACT_SEARCH_LIMIT]])
            except Exception as e:
                print(f"KG contradiction search error: {e}")
        
        # Priority 3: Temporal reasoning
        if self.needs_temporal_reasoning(query) or as_of:
            routing_decision["primary"].append("temporal")
            routing_decision["reason"] = "Query requires temporal filtering"
            try:
                # Temporal search with decay
                results = episodic_store.search(query, limit=EPISODIC_SEARCH_LIMIT)
                # Apply temporal decay scoring
                for r in results:
                    payload = r.payload if hasattr(r, 'payload') else r
                    timestamp_str = payload.get("timestamp", "")
                    if timestamp_str:
                        try:
                            from datetime import timezone
                            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            age_days = (datetime.now(timezone.utc) - ts).days
                            # Decay: newer = higher score
                            decay_factor = max(MIN_DECAY_FACTOR, 1.0 - (age_days / TEMPORAL_DECAY_DAYS))
                            score = float(r.score) * decay_factor if hasattr(r, 'score') else SCORE_EPISODIC_DEFAULT * decay_factor
                        except:
                            score = r.score if hasattr(r, 'score') else SCORE_EPISODIC_DEFAULT
                    else:
                        score = r.score if hasattr(r, 'score') else SCORE_EPISODIC_DEFAULT
                    
                    candidates.append({
                        "type": "episodic",
                        "score": score,
                        "payload": payload,
                        "source": "episodic_store_temporal"
                    })
            except Exception as e:
                print(f"Temporal search error: {e}")
        
        # Priority 4: Relationship reasoning (KG traversal)
        if self.needs_relationship_reasoning(query):
            routing_decision["primary"].append("kg")
            routing_decision["reason"] = "Query requires relationship traversal"
            try:
                facts = semantic_kg.active_facts()
                candidates.extend([{
                    "type": "kg",
                    "score": SCORE_RELATIONSHIP,
                    "payload": f,
                    "source": "knowledge_graph_relationships"
                } for f in facts[:KG_RELATIONSHIP_LIMIT]])
            except Exception as e:
                print(f"KG relationship search error: {e}")
        
        # Priority 5: Semantic search (vector similarity)
        if self.needs_semantic_search(query) or not routing_decision["primary"]:
            if not routing_decision["primary"]:
                routing_decision["primary"].append("semantic")
                routing_decision["reason"] = "Default to semantic search"
            else:
                routing_decision["secondary"].append("semantic")
            
            try:
                results = episodic_store.search(query, limit=EPISODIC_SEARCH_LIMIT)
                for r in results:
                    payload = r.payload if hasattr(r, 'payload') else r
                    candidates.append({
                        "type": "episodic",
                        "score": float(r.score) if hasattr(r, 'score') else SCORE_EPISODIC_DEFAULT,
                        "payload": payload,
                        "source": "episodic_store_semantic"
                    })
            except Exception as e:
                print(f"Semantic search error: {e}")
        
        # Deduplicate and sort
        seen = set()
        unique_candidates = []
        for c in candidates:
            key = str(c.get("payload", {}).get("id", "")) + c.get("type", "")
            if key not in seen:
                seen.add(key)
                unique_candidates.append(c)
        
        unique_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "routing": routing_decision,
            "candidates": unique_candidates
        }

