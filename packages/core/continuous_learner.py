"""
Continuous Learning Loop: Memory quality improves with use
Architecture Principle #7
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict
from .advanced_config import (
    GUARD_RULE_THRESHOLD,
    FACT_PROMOTION_THRESHOLD,
    CONFIDENCE_REDUCTION_MULTIPLIER,
)

class ContinuousLearner:
    """
    Learns from user feedback and improves memory quality
    Tracks corrections, successful retrievals, and error patterns
    """
    
    def __init__(self, episodic_store, semantic_kg):
        self.episodic_store = episodic_store
        self.semantic_kg = semantic_kg
        self.error_patterns = defaultdict(int)
        self.successful_retrievals = defaultdict(int)
    
    def analyze_error(self, model_output: str, user_correction: str) -> Dict[str, Any]:
        """Extract error pattern from correction"""
        # Simple analysis: compare outputs
        model_lower = model_output.lower()
        correction_lower = user_correction.lower()
        
        # Find what changed
        model_words = set(model_lower.split())
        correction_words = set(correction_lower.split())
        
        removed = model_words - correction_words
        added = correction_words - model_words
        
        error_type = "unknown"
        if len(removed) > len(added):
            error_type = "overstatement"
        elif len(added) > len(removed):
            error_type = "understatement"
        else:
            error_type = "incorrect_fact"
        
        return {
            "type": error_type,
            "removed_words": list(removed),
            "added_words": list(added),
            "pattern": f"{error_type}:{list(removed)[:3] if removed else []}"
        }
    
    def find_similar_facts(self, error_pattern: Dict[str, Any]) -> List[Dict]:
        """Find facts similar to the error pattern using embeddings"""
        similar = []
        
        try:
            from .stores import EMB
            import numpy as np
            
            facts = self.semantic_kg.active_facts()
            pattern_text = error_pattern.get("pattern", "")
            
            if not pattern_text:
                return similar
            
            # Create embedding for error pattern
            pattern_embedding = EMB.encode(pattern_text)
            
            for fact in facts:
                if isinstance(fact, dict):
                    # Build fact text
                    fact_text = f"{fact.get('subj', '')} {fact.get('pred', '')} {fact.get('obj', '')}"
                    fact_embedding = EMB.encode(fact_text)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(pattern_embedding, fact_embedding) / (
                        np.linalg.norm(pattern_embedding) * np.linalg.norm(fact_embedding)
                    )
                    similarity = (similarity + 1) / 2  # Normalize to 0-1
                    
                    # If similarity > 0.6, consider it similar
                    if similarity > 0.6:
                        similar.append(fact)
        except Exception as e:
            print(f"Find similar facts error: {e}")
            # Fallback to simple keyword matching
            try:
                facts = self.semantic_kg.active_facts()
                pattern_key = error_pattern.get("pattern", "")
                for fact in facts:
                    if isinstance(fact, dict):
                        pred = str(fact.get("pred", "")).lower()
                        if any(word in pred for word in error_pattern.get("removed_words", [])[:2]):
                            similar.append(fact)
            except:
                pass
        
        return similar
    
    def on_user_correction(
        self, 
        model_output: str, 
        user_correction: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn from user corrections
        Returns learning report
        """
        # Extract error pattern
        error_pattern = self.analyze_error(model_output, user_correction)
        
        # Track error frequency
        pattern_key = error_pattern.get("pattern", "unknown")
        self.error_patterns[pattern_key] += 1
        
        # Update confidence scores for similar facts
        similar_facts = self.find_similar_facts(error_pattern)
        confidence_reductions = 0
        
        # In production, would update fact confidence scores
        # For now, just track
        for fact in similar_facts:
            # Would reduce confidence: fact.confidence *= CONFIDENCE_REDUCTION_MULTIPLIER
            confidence_reductions += 1
        
        # Store correction in episodic memory
        try:
            correction_memory = {
                "type": "correction",
                "original": model_output,
                "correction": user_correction,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_type": error_pattern["type"],
                "query": query or "unknown"
            }
            
            # Would store in episodic store
            # self.episodic_store.write(correction_id, correction_memory, user_correction)
            
        except Exception as e:
            print(f"Store correction error: {e}")
        
        # Check if pattern is frequent enough to create guard rule
        pattern_frequency = self.error_patterns[pattern_key]
        guard_rule_created = False
        
        if pattern_frequency >= GUARD_RULE_THRESHOLD:
            try:
                # Create guard rule in semantic memory
                self.semantic_kg.add_fact(
                    "System",
                    "GUARD_RULE",
                    pattern_key,
                    int(datetime.now(timezone.utc).timestamp())
                )
                guard_rule_created = True
            except Exception as e:
                print(f"Create guard rule error: {e}")
        
        return {
            "error_pattern": error_pattern,
            "similar_facts_found": len(similar_facts),
            "confidence_reductions": confidence_reductions,
            "pattern_frequency": pattern_frequency,
            "guard_rule_created": guard_rule_created
        }
    
    def on_successful_retrieval(
        self, 
        query: str, 
        retrieved_facts: List[Dict], 
        used_facts: List[Dict]
    ) -> Dict[str, Any]:
        """
        Strengthen memories that help
        Returns strengthening report
        """
        # Track successful retrievals
        for fact in used_facts:
            fact_id = str(fact.get("id", ""))
            if fact_id:
                self.successful_retrievals[fact_id] += 1
        
        # In production, would:
        # 1. Increment usage_count for each fact
        # 2. Update last_used timestamp
        # 3. Promote to hot cache if usage_count > threshold
        
        promotions = 0
        for fact in used_facts:
            fact_id = str(fact.get("id", ""))
            usage_count = self.successful_retrievals.get(fact_id, 0)
            
            if usage_count >= FACT_PROMOTION_THRESHOLD:
                # Would promote to hot cache
                promotions += 1
        
        return {
            "facts_used": len(used_facts),
            "usage_tracked": len(used_facts),
            "promotions": promotions
        }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning progress"""
        return {
            "error_patterns": dict(self.error_patterns),
            "total_errors": sum(self.error_patterns.values()),
            "successful_retrievals": dict(self.successful_retrievals),
            "total_successes": sum(self.successful_retrievals.values()),
            "unique_error_types": len(self.error_patterns),
            "high_usage_facts": len([
                k for k, v in self.successful_retrievals.items() 
                if v >= FACT_PROMOTION_THRESHOLD
            ])
        }

