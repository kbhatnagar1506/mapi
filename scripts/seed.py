#!/usr/bin/env python3
import requests
import time
import sys

URL = "http://localhost:8000"

mems = [
    {
        "text": "On 2025-11-01 we decided Bonn was the capital pre-1990; Berlin after 1990.",
        "source": "chat",
        "tags": ["history"]
    },
    {
        "text": "Send Q3 report to John tomorrow morning.",
        "source": "chat",
        "tags": ["todo"]
    },
    {
        "text": "Project X ID=PX-8842 requires budget approval.",
        "source": "chat",
        "tags": ["id"]
    },
    {
        "text": "Meeting notes: Discussed transformer architecture improvements. Key point: attention mechanisms need optimization.",
        "source": "chat",
        "tags": ["research", "ai"]
    },
    {
        "text": "User prefers dark mode and compact UI layouts.",
        "source": "chat",
        "tags": ["preferences"]
    },
]

def seed():
    print("Seeding memories...")
    for i, m in enumerate(mems, 1):
        try:
            r = requests.post(f"{URL}/mem/write", json=m, timeout=10)
            r.raise_for_status()
            print(f"✓ [{i}/{len(mems)}] Saved: {m['text'][:50]}...")
            time.sleep(0.2)
        except Exception as e:
            print(f"✗ Failed to save memory {i}: {e}")
            sys.exit(1)
    print("\n✓ Seeding complete!")

if __name__ == "__main__":
    seed()

