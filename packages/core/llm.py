import os
import json
import requests
from .config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)

class LLM:
    @staticmethod
    def complete(prompt: str, temperature: float = 0.2) -> str:
        # Prefer OpenAI-compatible if key is present
        if OPENAI_API_KEY:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            try:
                r = requests.post(
                    f"{OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall through to Ollama

        # Ollama fallback
        if OLLAMA_BASE_URL:
            data = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "options": {"temperature": temperature}
            }
            try:
                r = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json=data,
                    timeout=60
                )
                r.raise_for_status()
                # Streamed; take last chunk
                text = ""
                for line in r.text.splitlines():
                    try:
                        obj = json.loads(line)
                        text += obj.get("response", "")
                    except Exception:
                        pass
                return text.strip()
            except Exception as e:
                print(f"Ollama error: {e}")

        # Last resort - echo mode for testing
        return f"[Echo Mode] You asked: {prompt[:100]}... (Configure OPENAI_API_KEY or OLLAMA_BASE_URL)"

