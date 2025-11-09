from typing import List, Dict
from .llm import LLM
from .hallucination_guard import HallucinationGuard
from .advanced_config import (
    LLM_TEMPERATURE_DRAFT,
    LLM_TEMPERATURE_CRITIQUE,
    DEFAULT_CONFIDENCE_NO_SOURCES,
    BASE_CONFIDENCE,
    CONFIDENCE_INCREMENT_PER_SOURCE,
    MAX_CONFIDENCE_FROM_SOURCES,
    MAX_SNIPPETS_FOR_VERIFICATION,
    MAX_SNIPPET_LENGTH_DRAFT,
    MAX_SNIPPET_LENGTH_CRITIQUE,
)

# Simple two-step gate: retrieve->draft->critique
def draft_answer(query: str, snippets: List[str]) -> str:
    if not snippets:
        return "I need more context or sources to answer this question."
    
    ctx = "\n\n".join(f"[SOURCE {i+1}] {s[:MAX_SNIPPET_LENGTH_DRAFT]}" for i, s in enumerate(snippets))
    prompt = f"""
You are a careful assistant. Using ONLY the sources below, answer the user's question.

If the sources are insufficient, say so. Cite sources as [S1], [S2], ... in the text.

Question: {query}

Sources:
{ctx}
""".strip()
    
    return LLM.complete(prompt, temperature=LLM_TEMPERATURE_DRAFT)

def critique_answer(query: str, answer: str, sources: List[str]) -> float:
    if not sources:
        return DEFAULT_CONFIDENCE_NO_SOURCES
    
    src = "\n\n".join(f"[S{i+1}] {s[:MAX_SNIPPET_LENGTH_CRITIQUE]}" for i, s in enumerate(sources))
    prompt = f"""
Critique the ANSWER for factual support using the SOURCES.

Return a single number 0.0-1.0 = confidence the answer is supported.

QUESTION: {query}

SOURCES:
{src}

ANSWER:
{answer}

Return ONLY a number between 0.0 and 1.0.
""".strip()
    
    try:
        out = LLM.complete(prompt, temperature=LLM_TEMPERATURE_CRITIQUE)
        # Extract first number
        import re
        nums = re.findall(r'\d+\.?\d*', out)
        if nums:
            conf = float(nums[0])
            return max(0.0, min(1.0, conf))
    except Exception as e:
        print(f"Critique error: {e}")
    
    # Fallback: base confidence on source count
    return min(MAX_CONFIDENCE_FROM_SOURCES, BASE_CONFIDENCE + len(sources) * CONFIDENCE_INCREMENT_PER_SOURCE)

def verify_before_speak(query: str, candidates: List[Dict], semantic_kg=None):
    """
    Enhanced verification with hallucination guard
    Architecture Principle #4: Hybrid Retrieval with Verification
    """
    # collect snippet texts
    snips = []
    for c in candidates:
        if c["type"] == "episodic":
            t = c["payload"].get("text") or c["payload"].get("content")
            if t:
                snips.append(t)
        elif c["type"] == "exact":
            snips.append(c["payload"].get("content", ""))
        elif c["type"] == "kg":
            fact = c["payload"]
            snips.append(f"FACT: {fact.get('pred', 'unknown')} asserted_at {fact.get('asserted_at', 'unknown')}")
    
    # Stage 1: Draft answer
    draft = draft_answer(query, snips[:MAX_SNIPPETS_FOR_VERIFICATION]) if snips else "I need more context or sources."
    
    # Stage 2: Critique with LLM
    conf = critique_answer(query, draft, snips[:MAX_SNIPPETS_FOR_VERIFICATION]) if snips else DEFAULT_CONFIDENCE_NO_SOURCES
    
    # Stage 3: Hallucination guard (multi-layer verification)
    guard = HallucinationGuard(semantic_kg=semantic_kg)
    guard_result = guard.evaluate_response(draft, query, snips[:MAX_SNIPPETS_FOR_VERIFICATION])
    
    # Combine confidence scores
    # Base confidence from critique, adjusted by guard
    final_confidence = conf * guard_result["confidence"]
    
    # If hallucination detected, lower confidence significantly
    if guard_result["hallucinated"]:
        final_confidence *= 0.5
        draft = f"[VERIFIED] {draft}\n\n[Note: Some claims may need verification. Confidence: {final_confidence:.2f}]"
    
    return draft, round(final_confidence, 2), guard_result

