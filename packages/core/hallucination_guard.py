"""
Hallucination Prevention Through Grounding
Architecture Principle #5: Multi-layer verification
"""
from typing import Dict, List, Any, Optional
from .llm import LLM
from .stores import EMB  # Use real embeddings
from .advanced_config import (
    SIMILARITY_THRESHOLD,
    CONFIDENCE_THRESHOLD,
    OVERCONFIDENCE_RATIO,
    CONFIDENCE_MULT_SEMANTIC_DRIFT,
    CONFIDENCE_MULT_CONTRADICTION,
    CONFIDENCE_MULT_FALSE_ATTRIBUTION,
    CONFIDENCE_MULT_OVERCONFIDENCE,
    DEFAULT_MODEL_CONFIDENCE,
    MIN_EVIDENCE_STRENGTH,
    EVIDENCE_STRENGTH_RANGE_START,
    EVIDENCE_STRENGTH_RANGE_END,
    CONFIDENCE_HIGHLY,
    CONFIDENCE_SOMEWHAT,
    CONFIDENCE_NOT,
)
import numpy as np

class HallucinationGuard:
    """Four-layer hallucination detection system"""
    
    def __init__(self, semantic_kg=None):
        self.kg = semantic_kg
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.confidence_threshold = CONFIDENCE_THRESHOLD
    
    def semantic_matcher(self, response: str, context: List[str]) -> float:
        """Layer 1: Semantic similarity to sources using embeddings"""
        if not context:
            return MIN_EVIDENCE_STRENGTH
        
        try:
            # Use real embeddings for semantic similarity
            response_embedding = EMB.encode(response)
            context_text = " ".join(context)
            context_embedding = EMB.encode(context_text)
            
            # Cosine similarity
            similarity = np.dot(response_embedding, context_embedding) / (
                np.linalg.norm(response_embedding) * np.linalg.norm(context_embedding)
            )
            
            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            similarity = (similarity + 1) / 2
            
            return float(similarity)
        except Exception as e:
            print(f"Embedding similarity error: {e}, falling back to keyword matching")
            # Fallback to keyword matching
            response_lower = response.lower()
            context_text = " ".join(context).lower()
            response_words = set(response_lower.split())
            context_words = set(context_text.split())
            if not response_words:
                return MIN_EVIDENCE_STRENGTH
            overlap = len(response_words & context_words)
            total = len(response_words)
            return overlap / total if total > 0 else 0.0
    
    def extract_facts(self, text: str) -> List[Dict[str, str]]:
        """Extract factual claims from text using LLM"""
        try:
            # Use LLM for better fact extraction
            prompt = f"""
Extract factual claims from the following text. Return each fact as a JSON object with:
- subject: the entity or subject
- predicate: the relationship or action
- object: what the subject relates to
- text: the original phrase

Text: {text}

Return a JSON array of facts. If no clear facts, return empty array [].
Format: [{{"subject": "...", "predicate": "...", "object": "...", "text": "..."}}]
""".strip()
            
            response = LLM.complete(prompt, temperature=0.1)
            
            # Try to parse JSON from response
            import json
            import re
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                facts = json.loads(json_match.group(0))
                if isinstance(facts, list) and len(facts) > 0:
                    return facts
            
            # Fallback: simple pattern matching
            facts = []
            patterns = [
                r"(\w+)\s+(?:is|was|are|were)\s+(\w+)",
                r"(\w+)\s+(?:has|had)\s+(\w+)",
            ]
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.I)
                for match in matches:
                    facts.append({
                        "subject": match.group(1),
                        "predicate": "is" if "is" in match.group(0) else "has",
                        "object": match.group(2),
                        "text": match.group(0)
                    })
            
            return facts
        except Exception as e:
            print(f"Fact extraction error: {e}, using simple patterns")
            # Fallback to simple patterns
            import re
            facts = []
            patterns = [
                r"(\w+)\s+(?:is|was|are|were)\s+(\w+)",
                r"(\w+)\s+(?:has|had)\s+(\w+)",
            ]
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.I)
                for match in matches:
                    facts.append({
                        "subject": match.group(1),
                        "predicate": "is" if "is" in match.group(0) else "has",
                        "object": match.group(2),
                        "text": match.group(0)
                    })
            return facts
    
    def verify_against_kg(self, fact: Dict[str, str]) -> Optional[Dict]:
        """Check if fact exists in knowledge graph using semantic similarity"""
        if not self.kg:
            return None
        
        try:
            # Get all facts from KG
            facts = self.kg.active_facts()
            
            # Use embeddings for semantic matching
            fact_text = f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"
            fact_embedding = EMB.encode(fact_text)
            
            best_match = None
            best_similarity = 0.0
            
            for kg_fact in facts:
                if isinstance(kg_fact, dict):
                    # Build KG fact text
                    kg_text = f"{kg_fact.get('subj', '')} {kg_fact.get('pred', '')} {kg_fact.get('obj', '')}"
                    kg_embedding = EMB.encode(kg_text)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(fact_embedding, kg_embedding) / (
                        np.linalg.norm(fact_embedding) * np.linalg.norm(kg_embedding)
                    )
                    similarity = (similarity + 1) / 2  # Normalize to 0-1
                    
                    if similarity > best_similarity and similarity > 0.7:  # Threshold
                        best_similarity = similarity
                        best_match = kg_fact
            
            if best_match:
                return {
                    "found": True,
                    "kg_fact": best_match,
                    "similarity": best_similarity
                }
        except Exception as e:
            print(f"KG verification error: {e}")
            # Fallback to simple matching
            try:
                facts = self.kg.active_facts()
                for kg_fact in facts:
                    if isinstance(kg_fact, dict):
                        pred = kg_fact.get("pred", "")
                        if fact["predicate"].lower() in pred.lower():
                            return {
                                "found": True,
                                "kg_fact": kg_fact
                            }
            except:
                pass
        
        return {"found": False}
    
    def find_contradictions(self, fact: Dict[str, str]) -> Optional[Dict]:
        """Check if fact contradicts known facts using LLM"""
        if not self.kg:
            return None
        
        try:
            # Get all facts from KG
            facts = self.kg.active_facts()
            
            # Use LLM to detect contradictions
            fact_text = f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"
            kg_facts_text = "\n".join([
                f"- {f.get('subj', '')} {f.get('pred', '')} {f.get('obj', '')}"
                for f in facts[:10] if isinstance(f, dict)
            ])
            
            prompt = f"""
Check if the following fact contradicts any of the known facts below.

New fact: {fact_text}

Known facts:
{kg_facts_text}

Does the new fact contradict any known fact? Return JSON:
{{"contradicted": true/false, "contradicting_fact": "fact text if contradicted", "reason": "why"}}

Return ONLY valid JSON.
""".strip()
            
            response = LLM.complete(prompt, temperature=0.1)
            
            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                if result.get("contradicted"):
                    return result
            
            # Fallback: simple keyword check
            for kg_fact in facts:
                if isinstance(kg_fact, dict):
                    pred = kg_fact.get("pred", "")
                    if "not" in pred.lower() or "never" in pred.lower():
                        return {
                            "contradicted": True,
                            "contradicting_fact": kg_fact
                        }
        except Exception as e:
            print(f"Contradiction check error: {e}")
        
        return {"contradicted": False}
    
    def extract_source_claims(self, text: str) -> List[str]:
        """Extract source attribution claims"""
        import re
        # Look for "[S1]", "[Source 1]", "according to", etc.
        patterns = [
            r"\[S\d+\]",
            r"\[Source\s+\d+\]",
            r"according to\s+[\w\s]+",
        ]
        
        sources = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.I)
            sources.extend([m.group(0) for m in matches])
        
        return sources
    
    def verify_source_exists(self, source_claim: str, actual_sources: List[str]) -> bool:
        """Verify that claimed source actually exists"""
        # Simple check: if source number is mentioned, verify it exists
        import re
        numbers = re.findall(r'\d+', source_claim)
        if numbers:
            source_num = int(numbers[0])
            return source_num <= len(actual_sources)
        return True  # If no number, assume valid
    
    def get_model_confidence(self, response: str) -> float:
        """Extract model's stated confidence (if any)"""
        import re
        # Look for confidence indicators
        confidence_patterns = [
            r"(\d+)%?\s+(?:confident|certain|sure)",
            r"(?:highly|very|somewhat|not)\s+confident",
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response, re.I)
            if match:
                if match.group(0).lower().startswith(("highly", "very")):
                    return CONFIDENCE_HIGHLY
                elif "somewhat" in match.group(0).lower():
                    return CONFIDENCE_SOMEWHAT
                elif "not" in match.group(0).lower():
                    return CONFIDENCE_NOT
        
        # Default: moderate confidence
        return DEFAULT_MODEL_CONFIDENCE
    
    def measure_evidence_strength(self, response: str, context: List[str]) -> float:
        """Measure actual evidence strength supporting response"""
        # Count how many sources support the response
        if not context:
            return MIN_EVIDENCE_STRENGTH
        
        # Simple: count source citations in response
        source_count = len(self.extract_source_claims(response))
        max_sources = len(context)
        
        if max_sources == 0:
            return MIN_EVIDENCE_STRENGTH
        
        evidence_ratio = min(1.0, source_count / max_sources)
        range_size = EVIDENCE_STRENGTH_RANGE_END - EVIDENCE_STRENGTH_RANGE_START
        return EVIDENCE_STRENGTH_RANGE_START + (evidence_ratio * range_size)
    
    def evaluate_response(
        self, 
        response: str, 
        query: str, 
        retrieved_context: List[str]
    ) -> Dict[str, Any]:
        """
        Four-layer verification
        Returns evaluation result with confidence and flags
        """
        result = {
            "hallucinated": False,
            "confidence": 1.0,
            "flags": [],
            "layer_results": {}
        }
        
        # Layer 1: Semantic consistency
        similarity = self.semantic_matcher(response, retrieved_context)
        result["layer_results"]["semantic_similarity"] = similarity
        
        if similarity < self.similarity_threshold:
            result["hallucinated"] = True
            result["flags"].append("semantic_drift")
            result["confidence"] *= CONFIDENCE_MULT_SEMANTIC_DRIFT
        
        # Layer 2: Knowledge graph validation
        facts = self.extract_facts(response)
        kg_verified = 0
        contradictions_found = 0
        
        for fact in facts:
            kg_check = self.verify_against_kg(fact)
            if kg_check and kg_check.get("found"):
                kg_verified += 1
            else:
                # Check for contradictions
                contradiction = self.find_contradictions(fact)
                if contradiction and contradiction.get("contradicted"):
                    contradictions_found += 1
                    result["hallucinated"] = True
                    result["flags"].append("contradiction")
                    result["confidence"] *= CONFIDENCE_MULT_CONTRADICTION
        
        result["layer_results"]["kg_verification"] = {
            "facts_checked": len(facts),
            "kg_verified": kg_verified,
            "contradictions": contradictions_found
        }
        
        # Layer 3: Source attribution
        source_claims = self.extract_source_claims(response)
        invalid_sources = 0
        
        for claim in source_claims:
            if not self.verify_source_exists(claim, retrieved_context):
                invalid_sources += 1
                result["hallucinated"] = True
                result["flags"].append("false_attribution")
                result["confidence"] *= CONFIDENCE_MULT_FALSE_ATTRIBUTION
        
        result["layer_results"]["source_attribution"] = {
            "claims": len(source_claims),
            "invalid": invalid_sources
        }
        
        # Layer 4: Confidence calibration
        model_confidence = self.get_model_confidence(response)
        evidence_strength = self.measure_evidence_strength(response, retrieved_context)
        
        if model_confidence > evidence_strength * OVERCONFIDENCE_RATIO:
            result["hallucinated"] = True
            result["flags"].append("overconfidence")
            result["confidence"] *= CONFIDENCE_MULT_OVERCONFIDENCE
        
        result["layer_results"]["confidence_calibration"] = {
            "model_confidence": model_confidence,
            "evidence_strength": evidence_strength,
            "ratio": model_confidence / evidence_strength if evidence_strength > 0 else 0
        }
        
        # Final confidence (clamped)
        result["confidence"] = max(0.0, min(1.0, result["confidence"]))
        
        return result

