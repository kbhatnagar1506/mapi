#!/usr/bin/env python3
import requests
import sys

URL = "http://localhost:8000"

CASES = [
    {"query": "What report did I promise John?", "match": "Q3 report"},
    {"query": "What's Project X ID?", "match": "PX-8842"},
    {"query": "What did we discuss about transformers?", "match": "transformer"},
]

def eval_quick():
    print("Running quick evaluation...\n")
    ok = 0
    
    for i, c in enumerate(CASES, 1):
        try:
            r = requests.post(
                f"{URL}/ask",
                json={"query": c["query"], "top_k": 6},
                timeout=20
            )
            r.raise_for_status()
            data = r.json()
            got = data.get("answer", "")
            hit = c["match"].lower() in got.lower()
            conf = data.get("confidence", 0)
            
            status = "✓ PASS" if hit else "✗ FAIL"
            print(f"[{i}] {c['query']}")
            print(f"    {status} (confidence: {conf:.2f})")
            print(f"    Answer: {got[:100]}...")
            print()
            
            ok += int(hit)
        except Exception as e:
            print(f"✗ Error on case {i}: {e}\n")
    
    print(f"Results: {ok}/{len(CASES)} passed")
    return ok == len(CASES)

if __name__ == "__main__":
    success = eval_quick()
    sys.exit(0 if success else 1)

