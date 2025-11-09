import os
import time
import sqlite3
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from .config import (
    VECTOR_HOST,
    VECTOR_PORT,
    VECTOR_COLLECTION,
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASS,
    SQLITE_PATH
)

# Embeddings
from .advanced_config import EMBEDDING_MODEL
EMB = SentenceTransformer(EMBEDDING_MODEL)

# Episodic (vector)
class EpisodicStore:
    def __init__(self, host=VECTOR_HOST, port=VECTOR_PORT, collection=VECTOR_COLLECTION):
        self.host = host
        self.port = port
        self.col = collection
        self.c = None
        self._connected = False
        self._connect()

    def _connect(self):
        try:
            self.c = QdrantClient(host=self.host, port=self.port, timeout=2)
            cols = [x.name for x in self.c.get_collections().collections]
            if self.col not in cols:
                self.c.recreate_collection(
                    self.col,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            self._connected = True
        except Exception as e:
            print(f"Qdrant connection warning: {e}")
            print("Episodic store will use in-memory fallback")
            self._connected = False
            self._memory_store = {}  # Fallback in-memory store

    def embed(self, text: str) -> List[float]:
        return EMB.encode(text).tolist()

    def write(self, id_: str, payload: Dict[str, Any], text: str):
        if self._connected and self.c:
            try:
                self.c.upsert(
                    collection_name=self.col,
                    points=[PointStruct(id=id_, vector=self.embed(text), payload=payload)]
                )
            except Exception as e:
                print(f"Qdrant write error: {e}, using fallback")
                self._connected = False
                self._memory_store = {}
        
        # Fallback to in-memory
        if not self._connected:
            if not hasattr(self, '_memory_store'):
                self._memory_store = {}
            self._memory_store[id_] = {
                'vector': self.embed(text),
                'payload': payload,
                'text': text
            }

    def search(self, query: str, limit: int = None):
        from .advanced_config import EPISODIC_SEARCH_LIMIT
        if limit is None:
            limit = EPISODIC_SEARCH_LIMIT
        if self._connected and self.c:
            try:
                return self.c.search(
                    collection_name=self.col,
                    query_vector=self.embed(query),
                    limit=limit
                )
            except Exception as e:
                print(f"Qdrant search error: {e}, using fallback")
                self._connected = False
        
        # Fallback: semantic search using embeddings (not just keyword matching)
        if not self._connected:
            if not hasattr(self, '_memory_store'):
                return []
            
            # Use embeddings for semantic similarity in fallback
            query_embedding = self.embed(query)
            results = []
            
            for id_, item in self._memory_store.items():
                try:
                    # Calculate cosine similarity
                    item_embedding = item.get('vector', [])
                    if item_embedding:
                        import numpy as np
                        similarity = np.dot(query_embedding, item_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding)
                        )
                        # Normalize to 0-1
                        score = (similarity + 1) / 2
                    else:
                        # Fallback to keyword matching if no vector
                        query_lower = query.lower()
                        text_lower = item.get('text', '').lower()
                        if query_lower in text_lower:
                            score = 0.8
                        else:
                            continue
                    
                    # Create a mock result object
                    class MockResult:
                        def __init__(self, score, payload):
                            self.score = score
                            self.payload = payload
                    results.append(MockResult(score, item['payload']))
                except Exception as e:
                    print(f"Fallback search error for item {id_}: {e}")
                    continue
            
            # Sort by score and return top results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]
        return []
    
    def get_recent(self, days: int = 7):
        """Get recent memories from the store"""
        if self._connected and self.c:
            try:
                # Query all points and filter by timestamp
                # Note: Qdrant doesn't have native time filtering, so we get all and filter
                from datetime import datetime, timedelta, timezone
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                
                # Get all points (with limit for safety)
                all_points = self.c.scroll(collection_name=self.col, limit=10000)[0]
                
                recent = []
                for point in all_points:
                    payload = point.payload
                    timestamp_str = payload.get("timestamp", "")
                    if timestamp_str:
                        try:
                            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if ts >= cutoff:
                                recent.append({
                                    "id": str(point.id),
                                    "text": payload.get("text", ""),
                                    "source": payload.get("source", ""),
                                    "tags": payload.get("tags", []),
                                    "timestamp": timestamp_str
                                })
                        except:
                            pass
                
                return recent
            except Exception as e:
                print(f"Get recent error: {e}")
                return []
        
        # Fallback: filter in-memory store
        if hasattr(self, '_memory_store'):
            from datetime import datetime, timedelta, timezone
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            recent = []
            for id_, item in self._memory_store.items():
                timestamp_str = item.get('payload', {}).get('timestamp', '')
                if timestamp_str:
                    try:
                        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if ts >= cutoff:
                            recent.append({
                                "id": id_,
                                "text": item.get('text', ''),
                                "source": item.get('payload', {}).get('source', ''),
                                "tags": item.get('payload', {}).get('tags', []),
                                "timestamp": timestamp_str
                            })
                    except:
                        pass
            return recent
        
        return []

# Exact (SQLite FTS5)
class ExactStore:
    def __init__(self, path=SQLITE_PATH):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY, content TEXT, ts INTEGER)")
        cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(content)")
        self.conn.commit()

    def write(self, id_: str, content: str):
        ts = int(time.time())
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO docs(id, content, ts) VALUES(?,?,?)", (id_, content, ts))
        cur.execute(
            "INSERT INTO docs_fts(rowid, content) VALUES((SELECT rowid FROM docs WHERE id=?), ?)",
            (id_, content)
        )
        self.conn.commit()

    def search(self, query: str, limit: int = None):
        from .advanced_config import EXACT_SEARCH_LIMIT
        if limit is None:
            limit = EXACT_SEARCH_LIMIT
        cur = self.conn.cursor()
        cur.execute(
            "SELECT d.id, d.content, d.ts FROM docs d JOIN docs_fts f ON d.rowid=f.rowid WHERE docs_fts MATCH ? LIMIT ?",
            (query, limit)
        )
        rows = cur.fetchall()
        return [{"id": r[0], "content": r[1], "ts": r[2], "score": 0.7} for r in rows]

# Semantic KG (Neo4j)
class SemanticKG:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS):
        self.uri = uri
        self.user = user
        self.password = password
        self.drv = None
        self._connected = False
        self._memory_facts = []  # Fallback in-memory store
        self._connect()

    def _connect(self):
        try:
            self.drv = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection with timeout
            with self.drv.session() as s:
                s.run("RETURN 1")
            self._connected = True
        except Exception as e:
            print(f"Neo4j connection warning: {e}")
            print("Knowledge graph will use in-memory fallback")
            self._connected = False

    def _ensure_connected(self):
        # Don't keep trying if we've already determined it's not available
        if not self._connected:
            return False
        if self.drv is None:
            return False
        return True

    def add_fact(self, subj: str, pred: str, obj: str, ts: int):
        if self._ensure_connected() and self.drv:
            try:
                import uuid
                fact_id = str(uuid.uuid4())
                q = (
                    "MERGE (s:Entity {name:$subj})\n"
                    "MERGE (o:Entity {name:$obj})\n"
                    "CREATE (f:Fact {id:$fact_id, pred:$pred, asserted_at:$ts, active:true})\n"
                    "MERGE (s)-[:SUBJECT_OF]->(f)-[:OBJECT_OF]->(o)"
                )
                with self.drv.session() as s:
                    s.run(q, subj=subj, obj=obj, pred=pred, ts=ts, fact_id=fact_id)
                return
            except Exception as e:
                # Only print error once, then mark as disconnected
                if self._connected:
                    self._connected = False
                # Silently use fallback after first error
        
        # Fallback: in-memory storage
        import uuid
        self._memory_facts.append({
            'id': str(uuid.uuid4()),
            'pred': pred,
            'asserted_at': ts,
            'active': True,
            'subj': subj,
            'obj': obj
        })

    def supersede(self, fact_id_prev: str, fact_id_new: str):
        if self._ensure_connected() and self.drv:
            try:
                q = (
                    "MATCH (a:Fact {id:$prev}),(b:Fact {id:$new})\n"
                    "MERGE (a)-[:SUPERSEDED_BY]->(b) SET a.active=false"
                )
                with self.drv.session() as s:
                    s.run(q, prev=fact_id_prev, new=fact_id_new)
                return
            except Exception as e:
                # Only print error once, then mark as disconnected
                if self._connected:
                    self._connected = False
                # Silently use fallback after first error
        
        # Fallback: mark as inactive in memory
        for fact in self._memory_facts:
            if fact['id'] == fact_id_prev:
                fact['active'] = False

    def active_facts(self):
        from .advanced_config import KG_FACTS_LIMIT
        if self._ensure_connected() and self.drv:
            try:
                q = f"MATCH (f:Fact {{active:true}}) RETURN f LIMIT {KG_FACTS_LIMIT}"
                with self.drv.session() as s:
                    return [dict(r["f"]) for r in s.run(q)]
            except Exception as e:
                print(f"Neo4j query error: {e}")
                self._connected = False
        
        # Fallback: return active facts from memory
        from .advanced_config import KG_FACTS_LIMIT
        return [f for f in self._memory_facts if f.get('active', True)][:KG_FACTS_LIMIT]

