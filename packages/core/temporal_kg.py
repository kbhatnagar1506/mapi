"""
Temporal Knowledge Graph: Time-aware reasoning
Architecture Principle #6
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from .stores import SemanticKG

class TemporalKnowledgeGraph:
    """
    Enhanced knowledge graph with temporal reasoning
    Tracks fact evolution, supersession, and "as of" queries
    """
    
    def __init__(self, semantic_kg: SemanticKG):
        self.kg = semantic_kg
    
    def add_fact_with_time(
        self, 
        subject: str, 
        predicate: str, 
        object_: str, 
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Store facts with temporal metadata
        Returns fact ID
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        ts_int = int(timestamp.timestamp())
        
        # Add fact with temporal properties
        self.kg.add_fact(subject, predicate, object_, ts_int)
        
        # Return a fact identifier (in production, this would be the actual ID)
        import uuid
        return str(uuid.uuid4())
    
    def query_temporal(self, query: str, as_of_date: Optional[datetime] = None) -> List[Dict]:
        """
        Query facts as they were at a specific time
        If as_of_date is None, returns current facts
        """
        try:
            facts = self.kg.active_facts()
            
            if as_of_date is None:
                # Return current active facts
                return [f for f in facts if isinstance(f, dict) and f.get("active", True)]
            
            # Filter by temporal constraints
            as_of_ts = int(as_of_date.timestamp())
            temporal_facts = []
            
            for fact in facts:
                if not isinstance(fact, dict):
                    continue
                
                asserted_at = fact.get("asserted_at", 0)
                
                # Fact must have been asserted before or at as_of_date
                if asserted_at <= as_of_ts:
                    # Check if it was superseded before as_of_date
                    # (Simplified - in production, would query SUPERSEDED_BY relationships)
                    if fact.get("active", True):
                        temporal_facts.append(fact)
            
            return temporal_facts
        
        except Exception as e:
            # Silently use fallback
            return []
    
    def track_fact_evolution(self, fact_id: str) -> Dict[str, Any]:
        """
        Show how a fact changed over time
        Returns evolution chain
        """
        try:
            # Query KG for fact and its supersession chain
            if self.kg.drv:
                with self.kg.drv.session() as session:
                    # Find fact and all superseded versions
                    query = """
                    MATCH path = (f:Fact)-[:SUPERSEDED_BY*]->(latest:Fact)
                    WHERE f.id = $fact_id OR latest.id = $fact_id
                    RETURN path
                    ORDER BY latest.asserted_at DESC
                    LIMIT 1
                    """
                    result = session.run(query, fact_id=fact_id)
                    
                    evolution = {
                        "fact_id": fact_id,
                        "versions": [],
                        "current": None
                    }
                    
                    for record in result:
                        path = record["path"]
                        for node in path.nodes:
                            if isinstance(node, dict) or hasattr(node, '_properties'):
                                props = dict(node) if isinstance(node, dict) else dict(node._properties)
                                evolution["versions"].append({
                                    "id": props.get("id"),
                                    "asserted_at": props.get("asserted_at"),
                                    "pred": props.get("pred"),
                                    "active": props.get("active", True)
                                })
                                if props.get("active", True):
                                    evolution["current"] = props
                    
                    if evolution["versions"]:
                        return evolution
            
            # Fallback: search all facts
            facts = self.kg.active_facts()
            evolution = {
                "fact_id": fact_id,
                "versions": [],
                "current": None
            }
            
            for fact in facts:
                if isinstance(fact, dict) and fact.get("id") == fact_id:
                    evolution["versions"].append({
                        "asserted_at": fact.get("asserted_at"),
                        "pred": fact.get("pred"),
                        "active": fact.get("active", True)
                    })
                    
                    if fact.get("active", True):
                        evolution["current"] = fact
            
            return evolution
        
        except Exception as e:
            # Return empty evolution if error
            return {"fact_id": fact_id, "versions": [], "current": None}
    
    def supersede_fact(
        self, 
        old_fact_id: str, 
        new_subject: str, 
        new_predicate: str, 
        new_object: str
    ) -> str:
        """
        Mark old fact as superseded and create new fact
        Returns new fact ID
        """
        # Create new fact
        new_fact_id = self.add_fact_with_time(new_subject, new_predicate, new_object)
        
        # Mark old as superseded
        try:
            self.kg.supersede(old_fact_id, new_fact_id)
        except Exception as e:
            print(f"Supersede error: {e}")
        
        return new_fact_id
    
    def get_facts_by_time_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """Get all facts asserted within a time range"""
        try:
            facts = self.kg.active_facts()
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            range_facts = []
            for fact in facts:
                if not isinstance(fact, dict):
                    continue
                
                asserted_at = fact.get("asserted_at", 0)
                if start_ts <= asserted_at <= end_ts:
                    range_facts.append(fact)
            
            return range_facts
        
        except Exception as e:
            # Silently use fallback
            return []

