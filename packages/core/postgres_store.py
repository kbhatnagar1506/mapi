"""
PostgreSQL Primary Database Store
Stores memory metadata, relationships, and provides ACID compliance
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

# Try to import SQLAlchemy (graceful fallback if not installed)
try:
    from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Index, text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    from sqlalchemy.dialects.postgresql import UUID
    SQLALCHEMY_AVAILABLE = True
except ImportError as e:
    SQLALCHEMY_AVAILABLE = False
    print(f"SQLAlchemy not available: {e}. PostgreSQL features will use in-memory fallback.")

from .config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB
)

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = None

# Database Models (only if SQLAlchemy available)
if SQLALCHEMY_AVAILABLE:
    class MemoryRecord(Base):
        """Primary memory record table"""
        __tablename__ = "memory_records"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        text = Column(Text, nullable=False)
        source = Column(String(50), nullable=False)  # "chat", "file", "url"
        tags = Column(JSON, default=list)
        timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
        
        # Metadata
        user_id = Column(String(100), nullable=True, index=True)
        session_id = Column(String(100), nullable=True, index=True)
        
        # Storage references
        qdrant_id = Column(String(100), nullable=True)  # Reference to Qdrant vector
        exact_id = Column(String(100), nullable=True)    # Reference to SQLite exact store
        
        # Relationships
        created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
        updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
        
        # Indexes for common queries
        __table_args__ = (
            Index('idx_timestamp', 'timestamp'),
            Index('idx_source', 'source'),
            Index('idx_user_session', 'user_id', 'session_id'),
        )

    class MemoryRelationship(Base):
        """Relationships between memories"""
        __tablename__ = "memory_relationships"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        from_memory_id = Column(UUID(as_uuid=True), ForeignKey('memory_records.id'), nullable=False)
        to_memory_id = Column(UUID(as_uuid=True), ForeignKey('memory_records.id'), nullable=False)
        relationship_type = Column(String(50), nullable=False)  # "related_to", "supersedes", "contradicts"
        confidence = Column(Float, default=1.0)
        created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
        
        __table_args__ = (
            Index('idx_from_memory', 'from_memory_id'),
            Index('idx_to_memory', 'to_memory_id'),
            Index('idx_relationship_type', 'relationship_type'),
        )

    class MemoryMetadata(Base):
        """Additional metadata for memories"""
        __tablename__ = "memory_metadata"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        memory_id = Column(UUID(as_uuid=True), ForeignKey('memory_records.id'), nullable=False, unique=True)
        embedding_model = Column(String(100), nullable=True)
        vector_dimension = Column(Integer, nullable=True)
        confidence_score = Column(Float, nullable=True)
        access_count = Column(Integer, default=0)
        last_accessed = Column(DateTime(timezone=True), nullable=True)
        custom_metadata = Column(JSON, default=dict)
        
        __table_args__ = (
            Index('idx_memory_id', 'memory_id'),
            Index('idx_access_count', 'access_count'),
        )

class PostgresStore:
    """PostgreSQL primary database store"""
    
    def __init__(
        self,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        
        # Build connection string
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        self.engine = None
        self.SessionLocal = None
        self._connected = False
        self._connect()
    
    def _connect(self):
        """Connect to PostgreSQL and create tables"""
        if not SQLALCHEMY_AVAILABLE:
            print("PostgreSQL: SQLAlchemy not available, using in-memory fallback")
            self._connected = False
            self._memory_records = {}
            return
        
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=5,
                max_overflow=10
            )
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.SessionLocal() as session:
                session.execute(text("SELECT 1"))
                session.commit()
            
            self._connected = True
            print("✓ PostgreSQL connected and tables created")
            
        except Exception as e:
            print(f"PostgreSQL connection warning: {e}")
            print("PostgreSQL store will use in-memory fallback")
            self._connected = False
            self._memory_records = {}  # Fallback storage
    
    def get_session(self) -> Session:
        """Get database session"""
        if not SQLALCHEMY_AVAILABLE:
            raise Exception("SQLAlchemy not available")
        if not self._connected:
            raise Exception("PostgreSQL not connected")
        return self.SessionLocal()
    
    def create_memory(
        self,
        text: str,
        source: str,
        tags: List[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        qdrant_id: Optional[str] = None,
        exact_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Create a new memory record"""
        if not self._connected:
            # Fallback: in-memory storage
            memory_id = str(uuid.uuid4())
            self._memory_records[memory_id] = {
                "id": memory_id,
                "text": text,
                "source": source,
                "tags": tags or [],
                "timestamp": timestamp or datetime.now(timezone.utc),
                "user_id": user_id,
                "session_id": session_id
            }
            return memory_id
        
        try:
            with self.get_session() as session:
                memory = MemoryRecord(
                    text=text,
                    source=source,
                    tags=tags or [],
                    user_id=user_id,
                    session_id=session_id,
                    qdrant_id=qdrant_id,
                    exact_id=exact_id,
                    timestamp=timestamp or datetime.now(timezone.utc)
                )
                session.add(memory)
                session.commit()
                return str(memory.id)
        except Exception as e:
            print(f"PostgreSQL create error: {e}")
            raise
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get memory by ID"""
        if not self._connected:
            return self._memory_records.get(memory_id)
        
        try:
            with self.get_session() as session:
                memory = session.query(MemoryRecord).filter(MemoryRecord.id == memory_id).first()
                if memory:
                    return {
                        "id": str(memory.id),
                        "text": memory.text,
                        "source": memory.source,
                        "tags": memory.tags,
                        "timestamp": memory.timestamp.isoformat(),
                        "user_id": memory.user_id,
                        "session_id": memory.session_id,
                        "qdrant_id": memory.qdrant_id,
                        "exact_id": memory.exact_id
                    }
        except Exception as e:
            print(f"PostgreSQL get error: {e}")
        
        return None
    
    def list_memories(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List memories with filters"""
        if not self._connected:
            # Fallback: filter in-memory records
            records = list(self._memory_records.values())
            if user_id:
                records = [r for r in records if r.get("user_id") == user_id]
            if session_id:
                records = [r for r in records if r.get("session_id") == session_id]
            if source:
                records = [r for r in records if r.get("source") == source]
            return records[offset:offset+limit]
        
        try:
            with self.get_session() as session:
                query = session.query(MemoryRecord)
                
                if user_id:
                    query = query.filter(MemoryRecord.user_id == user_id)
                if session_id:
                    query = query.filter(MemoryRecord.session_id == session_id)
                if source:
                    query = query.filter(MemoryRecord.source == source)
                
                memories = query.order_by(MemoryRecord.timestamp.desc()).limit(limit).offset(offset).all()
                
                return [{
                    "id": str(m.id),
                    "text": m.text,
                    "source": m.source,
                    "tags": m.tags,
                    "timestamp": m.timestamp.isoformat(),
                    "user_id": m.user_id,
                    "session_id": m.session_id
                } for m in memories]
        except Exception as e:
            print(f"PostgreSQL list error: {e}")
            return []
    
    def create_relationship(
        self,
        from_memory_id: str,
        to_memory_id: str,
        relationship_type: str,
        confidence: float = 1.0
    ) -> str:
        """Create a relationship between memories"""
        if not self._connected:
            return str(uuid.uuid4())  # Fallback
        
        try:
            with self.get_session() as session:
                rel = MemoryRelationship(
                    from_memory_id=from_memory_id,
                    to_memory_id=to_memory_id,
                    relationship_type=relationship_type,
                    confidence=confidence
                )
                session.add(rel)
                session.commit()
                return str(rel.id)
        except Exception as e:
            print(f"PostgreSQL relationship error: {e}")
            raise
    
    def update_metadata(
        self,
        memory_id: str,
        access_count: Optional[int] = None,
        confidence_score: Optional[float] = None,
        custom_metadata: Optional[Dict] = None
    ):
        """Update memory metadata"""
        if not self._connected:
            return
        
        try:
            with self.get_session() as session:
                metadata = session.query(MemoryMetadata).filter(
                    MemoryMetadata.memory_id == memory_id
                ).first()
                
                if not metadata:
                    metadata = MemoryMetadata(memory_id=memory_id)
                    session.add(metadata)
                
                if access_count is not None:
                    metadata.access_count = access_count
                if confidence_score is not None:
                    metadata.confidence_score = confidence_score
                if custom_metadata is not None:
                    metadata.custom_metadata = custom_metadata
                
                metadata.last_accessed = datetime.now(timezone.utc)
                session.commit()
        except Exception as e:
            print(f"PostgreSQL metadata update error: {e}")

