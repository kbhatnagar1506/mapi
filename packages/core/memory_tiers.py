"""
Lifecycle Separation: Four distinct memory tiers
Architecture Principle #1
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import json
from .advanced_config import SESSION_TTL_HOURS

class SystemPreferences:
    """Semi-permanent: User settings, behavioral patterns, role definitions"""
    def __init__(self, storage_path: str = "./dev/system_prefs.json"):
        self.storage_path = storage_path
        self._load()
    
    def _load(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {}
    
    def _save(self):
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f)
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value
        self._save()
    
    def get_user_model(self) -> Dict[str, Any]:
        """Get consolidated user preferences and patterns"""
        return self.data.get("user_model", {})

class SessionContext:
    """Temporary: Current conversation frame, ongoing task state"""
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        self.created_at = datetime.now(timezone.utc)
        self.ttl_hours = SESSION_TTL_HOURS
    
    def is_expired(self) -> bool:
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > (self.ttl_hours * 3600)
    
    def update(self, key: str, value: Any):
        self.context[key] = value
    
    def get(self, key: str, default=None):
        return self.context.get(key, default)
    
    def clear(self):
        self.context = {}
        self.created_at = datetime.now(timezone.utc)

# Episodic and Semantic are already in stores.py, but we'll enhance them
# This file provides the lifecycle separation structure

