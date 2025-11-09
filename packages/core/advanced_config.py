"""
Advanced Configuration: All thresholds, limits, and model settings
Loads from environment variables with sensible defaults
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# HALLUCINATION GUARD THRESHOLDS
# ============================================================================
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
OVERCONFIDENCE_RATIO = float(os.getenv("OVERCONFIDENCE_RATIO", "1.5"))

# Confidence multipliers for different error types
CONFIDENCE_MULT_SEMANTIC_DRIFT = float(os.getenv("CONF_MULT_SEMANTIC_DRIFT", "0.5"))
CONFIDENCE_MULT_CONTRADICTION = float(os.getenv("CONF_MULT_CONTRADICTION", "0.3"))
CONFIDENCE_MULT_FALSE_ATTRIBUTION = float(os.getenv("CONF_MULT_FALSE_ATTRIBUTION", "0.6"))
CONFIDENCE_MULT_OVERCONFIDENCE = float(os.getenv("CONF_MULT_OVERCONFIDENCE", "0.7"))

# Default confidence scores
DEFAULT_MODEL_CONFIDENCE = float(os.getenv("DEFAULT_MODEL_CONFIDENCE", "0.7"))
MIN_EVIDENCE_STRENGTH = float(os.getenv("MIN_EVIDENCE_STRENGTH", "0.2"))
EVIDENCE_STRENGTH_RANGE_START = float(os.getenv("EVIDENCE_STRENGTH_RANGE_START", "0.3"))
EVIDENCE_STRENGTH_RANGE_END = float(os.getenv("EVIDENCE_STRENGTH_RANGE_END", "0.8"))

# Keyword confidence scores
CONFIDENCE_HIGHLY = float(os.getenv("CONFIDENCE_HIGHLY", "0.9"))
CONFIDENCE_SOMEWHAT = float(os.getenv("CONFIDENCE_SOMEWHAT", "0.6"))
CONFIDENCE_NOT = float(os.getenv("CONFIDENCE_NOT", "0.3"))

# ============================================================================
# VERIFICATION THRESHOLDS
# ============================================================================
LLM_TEMPERATURE_DRAFT = float(os.getenv("LLM_TEMP_DRAFT", "0.2"))
LLM_TEMPERATURE_CRITIQUE = float(os.getenv("LLM_TEMP_CRITIQUE", "0.0"))
DEFAULT_CONFIDENCE_NO_SOURCES = float(os.getenv("DEFAULT_CONF_NO_SOURCES", "0.3"))
BASE_CONFIDENCE = float(os.getenv("BASE_CONFIDENCE", "0.5"))
CONFIDENCE_INCREMENT_PER_SOURCE = float(os.getenv("CONF_INCREMENT_PER_SOURCE", "0.1"))
MAX_CONFIDENCE_FROM_SOURCES = float(os.getenv("MAX_CONF_FROM_SOURCES", "0.9"))

# ============================================================================
# SEARCH LIMITS
# ============================================================================
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "6"))
EXACT_SEARCH_LIMIT = int(os.getenv("EXACT_SEARCH_LIMIT", "5"))
EPISODIC_SEARCH_LIMIT = int(os.getenv("EPISODIC_SEARCH_LIMIT", "6"))
KG_FACTS_LIMIT = int(os.getenv("KG_FACTS_LIMIT", "20"))
KG_RELATIONSHIP_LIMIT = int(os.getenv("KG_RELATIONSHIP_LIMIT", "10"))
MAX_SNIPPETS_FOR_VERIFICATION = int(os.getenv("MAX_SNIPPETS_VERIFICATION", "4"))

# ============================================================================
# MEMORY CONSOLIDATION THRESHOLDS
# ============================================================================
DECAY_CONSTANT_DAYS = float(os.getenv("DECAY_CONSTANT_DAYS", "7.0"))
PATTERN_WORD_FREQ_THRESHOLD = int(os.getenv("PATTERN_WORD_FREQ", "3"))
PATTERN_TAG_FREQ_THRESHOLD = int(os.getenv("PATTERN_TAG_FREQ", "2"))
RARE_WORD_THRESHOLD = int(os.getenv("RARE_WORD_THRESHOLD", "1"))
RARE_WORD_PERCENT = float(os.getenv("RARE_WORD_PERCENT", "0.3"))
CONSOLIDATION_DAYS = int(os.getenv("CONSOLIDATION_DAYS", "7"))
DEFAULT_DECAY_SCORE = float(os.getenv("DEFAULT_DECAY_SCORE", "0.5"))

# ============================================================================
# CONTINUOUS LEARNING THRESHOLDS
# ============================================================================
GUARD_RULE_THRESHOLD = int(os.getenv("GUARD_RULE_THRESHOLD", "3"))
FACT_PROMOTION_THRESHOLD = int(os.getenv("FACT_PROMOTION_THRESHOLD", "10"))
CONFIDENCE_REDUCTION_MULTIPLIER = float(os.getenv("CONF_REDUCTION_MULT", "0.9"))

# ============================================================================
# TEMPORAL REASONING THRESHOLDS
# ============================================================================
TEMPORAL_DECAY_DAYS = float(os.getenv("TEMPORAL_DECAY_DAYS", "30.0"))
MIN_DECAY_FACTOR = float(os.getenv("MIN_DECAY_FACTOR", "0.3"))

# ============================================================================
# SMART ROUTER SCORES
# ============================================================================
SCORE_EXACT_MATCH = float(os.getenv("SCORE_EXACT_MATCH", "0.9"))
SCORE_CONTRADICTION = float(os.getenv("SCORE_CONTRADICTION", "0.8"))
SCORE_KG_DEFAULT = float(os.getenv("SCORE_KG_DEFAULT", "0.65"))
SCORE_RELATIONSHIP = float(os.getenv("SCORE_RELATIONSHIP", "0.75"))
SCORE_EPISODIC_DEFAULT = float(os.getenv("SCORE_EPISODIC_DEFAULT", "0.7"))

# ============================================================================
# EMBEDDING MODEL
# ============================================================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ============================================================================
# PROCESSING LIMITS
# ============================================================================
MAX_SNIPPET_LENGTH_DRAFT = int(os.getenv("MAX_SNIPPET_DRAFT", "400"))
MAX_SNIPPET_LENGTH_CRITIQUE = int(os.getenv("MAX_SNIPPET_CRITIQUE", "300"))
MAX_SNIPPET_PREVIEW_UI = int(os.getenv("MAX_SNIPPET_PREVIEW", "100"))
FACT_TEXT_TRUNCATION = int(os.getenv("FACT_TEXT_TRUNCATION", "50"))

# ============================================================================
# SESSION/TTL
# ============================================================================
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))

