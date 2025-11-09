"""
Memory Consolidation: Intelligent compression through abstraction
Architecture Principle #3
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
import math
from .advanced_config import (
    DECAY_CONSTANT_DAYS,
    PATTERN_WORD_FREQ_THRESHOLD,
    PATTERN_TAG_FREQ_THRESHOLD,
    RARE_WORD_THRESHOLD,
    RARE_WORD_PERCENT,
    CONSOLIDATION_DAYS,
    DEFAULT_DECAY_SCORE,
)

class MemoryConsolidator:
    """
    Consolidates episodic memories into semantic patterns
    Inspired by neuroscience: episodic → semantic transformation
    """
    
    def __init__(self, episodic_store, semantic_kg):
        self.episodic_store = episodic_store
        self.semantic_kg = semantic_kg
    
    def extract_patterns(self, episodes: List[Dict]) -> List[Dict]:
        """Extract high-frequency patterns from episodic memories"""
        patterns = []
        
        # Pattern 1: Frequency analysis
        word_freq = Counter()
        tag_freq = Counter()
        source_freq = Counter()
        
        for ep in episodes:
            text = ep.get("text", "").lower()
            words = text.split()
            word_freq.update(words)
            tag_freq.update(ep.get("tags", []))
            source_freq.update([ep.get("source", "unknown")])
        
        # Pattern 2: Temporal patterns
        time_patterns = defaultdict(list)
        for ep in episodes:
            ts = ep.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hour = dt.hour
                    time_patterns[hour].append(ep)
                except:
                    pass
        
        # Pattern 3: Content similarity clusters
        # Simple: group by common words
        clusters = defaultdict(list)
        for ep in episodes:
            text = ep.get("text", "").lower()
            # Use first significant word as cluster key
            words = [w for w in text.split() if len(w) > 3]
            if words:
                cluster_key = words[0]
                clusters[cluster_key].append(ep)
        
        # Build pattern descriptions
        for word, count in word_freq.most_common(10):
            if count >= PATTERN_WORD_FREQ_THRESHOLD:
                patterns.append({
                    "type": "word_frequency",
                    "pattern": word,
                    "count": count,
                    "confidence": min(1.0, count / len(episodes)),
                    "description": f"Word '{word}' appears {count} times"
                })
        
        for tag, count in tag_freq.most_common(5):
            if count >= PATTERN_TAG_FREQ_THRESHOLD:
                patterns.append({
                    "type": "tag_frequency",
                    "pattern": tag,
                    "count": count,
                    "confidence": min(1.0, count / len(episodes)),
                    "description": f"Tag '{tag}' used {count} times"
                })
        
        return patterns
    
    def find_surprises(self, episodes: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """Identify surprising/important moments (outliers)"""
        surprises = []
        
        # Surprise 1: Contradictions
        # Simple: look for "not", "never", "but", "however"
        contradiction_words = ["not", "never", "but", "however", "although", "despite"]
        for ep in episodes:
            text = ep.get("text", "").lower()
            if any(word in text for word in contradiction_words):
                surprises.append({
                    "type": "contradiction",
                    "episode": ep,
                    "reason": "Contains contradiction indicators"
                })
        
        # Surprise 2: Rare events (low frequency words)
        all_words = []
        for ep in episodes:
            all_words.extend(ep.get("text", "").lower().split())
        
        word_freq = Counter(all_words)
        
        for ep in episodes:
            words = ep.get("text", "").lower().split()
            rare_count = sum(1 for w in words if word_freq[w] <= RARE_WORD_THRESHOLD)
            if rare_count > len(words) * RARE_WORD_PERCENT:
                surprises.append({
                    "type": "rare_event",
                    "episode": ep,
                    "reason": f"Contains {rare_count} rare words"
                })
        
        return surprises
    
    def apply_ebbinghaus_decay(self, episodes: List[Dict], decay_constant: float = None) -> List[Dict]:
        """
        Apply Ebbinghaus forgetting curve decay
        Score = e^(-time_elapsed / decay_constant)
        """
        if decay_constant is None:
            decay_constant = DECAY_CONSTANT_DAYS
        
        now = datetime.now(timezone.utc)
        decayed = []
        
        for ep in episodes:
            ts_str = ep.get("timestamp", "")
            if not ts_str:
                ep["decay_score"] = DEFAULT_DECAY_SCORE
                decayed.append(ep)
                continue
            
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                time_elapsed = (now - ts).days
                decay_score = math.exp(-time_elapsed / decay_constant)
                ep["decay_score"] = decay_score
                ep["age_days"] = time_elapsed
            except:
                ep["decay_score"] = DEFAULT_DECAY_SCORE
                ep["age_days"] = 999
        
        return decayed
    
    def consolidate_weekly(self) -> Dict[str, Any]:
        """
        Main consolidation process (run weekly)
        Returns consolidation report
        """
        # Step 1: Get recent episodic memories
        print("Starting weekly memory consolidation...")
        
        # Actually query the episodic store for recent memories
        try:
            episodes = self.episodic_store.get_recent(days=CONSOLIDATION_DAYS)
            print(f"Found {len(episodes)} recent episodes to consolidate")
        except Exception as e:
            print(f"Error getting recent episodes: {e}")
            episodes = []
        
        if not episodes:
            return {
                "status": "no_episodes",
                "patterns_created": 0,
                "surprises_found": 0
            }
        
        # Step 2: Extract patterns
        patterns = self.extract_patterns(episodes)
        
        # Step 3: Find surprises
        surprises = self.find_surprises(episodes, patterns)
        
        # Step 4: Create semantic abstractions
        patterns_created = 0
        for pattern in patterns:
            try:
                # Store in knowledge graph
                self.semantic_kg.add_fact(
                    "User",
                    "PATTERN",
                    pattern["pattern"],
                    int(datetime.now(timezone.utc).timestamp())
                )
                patterns_created += 1
            except Exception as e:
                print(f"Error storing pattern: {e}")
        
        # Step 5: Preserve exceptions explicitly
        for surprise in surprises:
            try:
                # Mark as important exception
                ep = surprise["episode"]
                self.semantic_kg.add_fact(
                    "User",
                    "EXCEPTION",
                    ep.get("text", "")[:50],  # First 50 chars
                    int(datetime.now(timezone.utc).timestamp())
                )
            except Exception as e:
                print(f"Error storing surprise: {e}")
        
        # Step 6: Apply decay
        decayed = self.apply_ebbinghaus_decay(episodes)
        
        return {
            "status": "success",
            "episodes_processed": len(episodes),
            "patterns_created": patterns_created,
            "surprises_found": len(surprises),
            "decay_applied": len(decayed)
        }

