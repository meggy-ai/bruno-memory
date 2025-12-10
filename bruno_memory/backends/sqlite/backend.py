"""
SQLite backend implementation for bruno-memory.

Provides persistent memory storage using SQLite database with full-text search capabilities.
"""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from bruno_core.models import (
    Message,
    MemoryEntry,
    MemoryQuery,
    SessionContext,
    ConversationContext,
    UserContext
)

from ...base.base_backend import BaseMemoryBackend
from ...base.memory_config import SQLiteConfig
from ...exceptions import ConnectionError, OperationError, ValidationError
from .schema import SCHEMA_STATEMENTS, SQLITE_PRAGMA, SCHEMA_VERSION, get_insert_schema_version_query


class SQLiteMemoryBackend(BaseMemoryBackend):
    """SQLite implementation of the MemoryInterface."""
    
    def __init__(self, config: Union[SQLiteConfig, Dict[str, Any]]):
        """Initialize SQLite backend.
        
        Args:
            config: SQLite configuration
        """
        if isinstance(config, dict):
            config = SQLiteConfig(**config)
        
        super().__init__(config)
        self.database_path = Path(config.database_path)
        self.enable_fts = config.enable_fts
        self._db: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Connect to SQLite database."""
        try:
            # Ensure parent directory exists
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self._db = await aiosqlite.connect(
                str(self.database_path),
                timeout=self.config.timeout
            )
            
            # Configure SQLite
            for pragma in SQLITE_PRAGMA:
                await self._db.execute(pragma)
            
            # Initialize schema
            await self._initialize_schema()
            
            await self._db.commit()
            self._connected = True
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from SQLite database."""
        if self._db:
            await self._db.close()
            self._db = None
        self._connected = False
    
    async def health_check(self) -> bool:
        """Check if SQLite database is healthy."""
        if not self._connected or not self._db:
            return False
        
        try:
            await self._db.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def _initialize_schema(self) -> None:
        """Initialize database schema."""
        # Execute schema statements
        for statement in SCHEMA_STATEMENTS:
            # Skip FTS tables if disabled
            if not self.enable_fts and ("_fts " in statement or "TRIGGER" in statement):
                continue
            
            await self._db.execute(statement)
        
        # Record schema version
        try:
            await self._db.execute(
                get_insert_schema_version_query(SCHEMA_VERSION, "Initial schema")
            )
        except aiosqlite.IntegrityError:
            # Version already exists
            pass
    
    async def store_message(self, message: Message, conversation_id: str) -> None:
        """Store a message in the database.
        
        Args:
            message: Message to store
            conversation_id: Conversation ID
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        # Validate message
        self.validate_message(message)
        
        # Ensure conversation_id is set
        if not message.conversation_id:
            message.conversation_id = conversation_id
        
        try:
            serialized = self.serialize_message(message)
            
            await self._db.execute("""
                INSERT OR REPLACE INTO messages (
                    id, conversation_id, role, content, timestamp, message_type,
                    metadata, user_id, parent_id, tokens, model, finish_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                serialized["id"],
                serialized["conversation_id"],
                serialized["role"], 
                serialized["content"],
                serialized["timestamp"],
                serialized["message_type"],
                serialized["metadata"],
                serialized["user_id"],
                serialized["parent_id"],
                serialized["tokens"],
                serialized["model"],
                serialized["finish_reason"]
            ))
            
            await self._db.commit()
            
        except Exception as e:
            raise OperationError(f"Failed to store message: {e}")
    
    async def retrieve_messages(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None
    ) -> List[Message]:
        """Retrieve messages from conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages ordered by timestamp
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            query = """
                SELECT id, conversation_id, role, content, timestamp, message_type,
                       metadata, user_id, parent_id, tokens, model, finish_reason
                FROM messages 
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """
            
            params = [conversation_id]
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            async with self._db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
            
            messages = []
            for row in rows:
                data = {
                    "id": row[0],
                    "conversation_id": row[1],
                    "role": row[2],
                    "content": row[3], 
                    "timestamp": row[4],
                    "message_type": row[5],
                    "metadata": row[6],
                    "user_id": row[7],
                    "parent_id": row[8],
                    "tokens": row[9],
                    "model": row[10],
                    "finish_reason": row[11]
                }
                messages.append(self.deserialize_message(data))
            
            return messages
            
        except Exception as e:
            raise OperationError(f"Failed to retrieve messages: {e}")
    
    async def search_messages(
        self, 
        query: str, 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Message]:
        """Search messages using full-text search.
        
        Args:
            query: Search query
            user_id: Optional user ID filter
            limit: Maximum results to return
            
        Returns:
            List of matching messages
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            if self.enable_fts:
                # Use FTS5 for better search
                sql = """
                    SELECT m.id, m.conversation_id, m.role, m.content, m.timestamp, 
                           m.message_type, m.metadata, m.user_id, m.parent_id, 
                           m.tokens, m.model, m.finish_reason
                    FROM messages m
                    INNER JOIN messages_fts fts ON m.id = fts.message_id
                    WHERE messages_fts MATCH ?
                """
                params = [query]
                
                if user_id:
                    sql += " AND m.user_id = ?"
                    params.append(user_id)
                
                sql += " ORDER BY rank LIMIT ?"
                params.append(limit)
                
            else:
                # Fallback to LIKE search
                sql = """
                    SELECT id, conversation_id, role, content, timestamp, message_type,
                           metadata, user_id, parent_id, tokens, model, finish_reason
                    FROM messages 
                    WHERE content LIKE ?
                """
                params = [f"%{query}%"]
                
                if user_id:
                    sql += " AND user_id = ?"
                    params.append(user_id)
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
            
            async with self._db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
            
            messages = []
            for row in rows:
                data = {
                    "id": row[0],
                    "conversation_id": row[1], 
                    "role": row[2],
                    "content": row[3],
                    "timestamp": row[4],
                    "message_type": row[5],
                    "metadata": row[6],
                    "user_id": row[7],
                    "parent_id": row[8],
                    "tokens": row[9],
                    "model": row[10],
                    "finish_reason": row[11]
                }
                messages.append(self.deserialize_message(data))
            
            return messages
            
        except Exception as e:
            raise OperationError(f"Failed to search messages: {e}")
    
    async def store_memory(self, memory_entry: MemoryEntry) -> None:
        """Store a memory entry.
        
        Args:
            memory_entry: Memory entry to store
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        self.validate_memory_entry(memory_entry)
        
        try:
            serialized = self.serialize_memory_entry(memory_entry)
            
            await self._db.execute("""
                INSERT OR REPLACE INTO memory_entries (
                    id, content, memory_type, importance, timestamp, user_id,
                    conversation_id, tags, metadata, embedding, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                serialized["id"],
                serialized["content"],
                serialized["memory_type"],
                serialized["importance"],
                serialized["timestamp"],
                serialized["user_id"],
                serialized["conversation_id"],
                serialized["tags"],
                serialized["metadata"],
                serialized["embedding"],
                serialized["expires_at"]
            ))
            
            await self._db.commit()
            
        except Exception as e:
            raise OperationError(f"Failed to store memory entry: {e}")
    
    async def retrieve_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memory entries based on query.
        
        Args:
            query: Memory query parameters
            
        Returns:
            List of matching memory entries
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            sql = """
                SELECT id, content, memory_type, importance, timestamp, user_id,
                       conversation_id, tags, metadata, embedding, expires_at
                FROM memory_entries
                WHERE 1=1
            """
            params = []
            
            # Add query filters
            if query.user_id:
                sql += " AND user_id = ?"
                params.append(query.user_id)
            
            if query.conversation_id:
                sql += " AND conversation_id = ?"
                params.append(query.conversation_id)
            
            if query.memory_types:
                placeholders = ",".join("?" * len(query.memory_types))
                sql += f" AND memory_type IN ({placeholders})"
                params.extend([mt.value if hasattr(mt, 'value') else str(mt) for mt in query.memory_types])
            
            if query.min_importance is not None:
                sql += " AND importance >= ?"
                params.append(query.min_importance)
            
            if query.tags:
                # Simple tag search - could be improved with JSON operators
                for tag in query.tags:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            # Text search
            if query.query_text:
                if self.enable_fts:
                    sql += """
                        AND id IN (
                            SELECT memory_id FROM memory_entries_fts 
                            WHERE memory_entries_fts MATCH ?
                        )
                    """
                    params.append(query.query_text)
                else:
                    sql += " AND content LIKE ?"
                    params.append(f"%{query.query_text}%")
            
            # Temporal filters
            if query.start_date:
                sql += " AND timestamp >= ?"
                params.append(query.start_date.isoformat())
            
            if query.end_date:
                sql += " AND timestamp <= ?"
                params.append(query.end_date.isoformat())
            
            # Filter expired entries
            sql += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(datetime.now().isoformat())
            
            # Order and limit
            sql += " ORDER BY importance DESC, timestamp DESC"
            
            if query.limit:
                sql += " LIMIT ?"
                params.append(query.limit)
            
            async with self._db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
            
            memories = []
            for row in rows:
                data = {
                    "id": row[0],
                    "content": row[1],
                    "memory_type": row[2],
                    "importance": row[3],
                    "timestamp": row[4],
                    "user_id": row[5],
                    "conversation_id": row[6],
                    "tags": row[7],
                    "metadata": row[8],
                    "embedding": row[9],
                    "expires_at": row[10]
                }
                memories.append(self.deserialize_memory_entry(data))
            
            return memories
            
        except Exception as e:
            raise OperationError(f"Failed to retrieve memories: {e}")
    
    async def delete_memory(self, memory_id: str) -> None:
        """Delete a memory entry.
        
        Args:
            memory_id: ID of memory entry to delete
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            await self._db.execute(
                "DELETE FROM memory_entries WHERE id = ?", 
                (memory_id,)
            )
            await self._db.commit()
            
        except Exception as e:
            raise OperationError(f"Failed to delete memory: {e}")
    
    async def clear_history(self, conversation_id: str, keep_system: bool = True) -> None:
        """Clear conversation history.
        
        Args:
            conversation_id: Conversation ID to clear
            keep_system: Whether to keep system messages
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            if keep_system:
                await self._db.execute("""
                    DELETE FROM messages 
                    WHERE conversation_id = ? AND role != 'system'
                """, (conversation_id,))
            else:
                await self._db.execute("""
                    DELETE FROM messages 
                    WHERE conversation_id = ?
                """, (conversation_id,))
            
            await self._db.commit()
            
        except Exception as e:
            raise OperationError(f"Failed to clear history: {e}")
    
    async def create_session(
        self, 
        user_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """Create a new session.
        
        Args:
            user_id: User ID
            metadata: Optional session metadata
            
        Returns:
            New session context
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            session_id = str(uuid4())
            conversation_id = str(uuid4())
            now = datetime.now()
            
            session = SessionContext(
                session_id=session_id,
                user_id=user_id,
                conversation_id=conversation_id,
                created_at=now,
                metadata=metadata or {},
                is_active=True
            )
            
            serialized = self.serialize_session_context(session)
            
            await self._db.execute("""
                INSERT INTO sessions (
                    session_id, user_id, conversation_id, created_at, 
                    updated_at, metadata, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                serialized["session_id"],
                serialized["user_id"],
                serialized["conversation_id"],
                serialized["created_at"],
                serialized["updated_at"],
                serialized["metadata"],
                serialized["is_active"]
            ))
            
            await self._db.commit()
            return session
            
        except Exception as e:
            raise OperationError(f"Failed to create session: {e}")
    
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session context or None if not found
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            async with self._db.execute("""
                SELECT session_id, user_id, conversation_id, created_at,
                       updated_at, metadata, is_active
                FROM sessions
                WHERE session_id = ?
            """, (session_id,)) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                return None
            
            data = {
                "session_id": row[0],
                "user_id": row[1],
                "conversation_id": row[2],
                "created_at": row[3],
                "updated_at": row[4],
                "metadata": row[5],
                "is_active": row[6]
            }
            
            return self.deserialize_session_context(data)
            
        except Exception as e:
            raise OperationError(f"Failed to get session: {e}")
    
    async def end_session(self, session_id: str) -> None:
        """End a session.
        
        Args:
            session_id: Session ID to end
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            await self._db.execute("""
                UPDATE sessions 
                SET is_active = 0, updated_at = ?
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            
            await self._db.commit()
            
        except Exception as e:
            raise OperationError(f"Failed to end session: {e}")
    
    async def get_context(
        self, 
        conversation_id: str, 
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """Get conversation context.
        
        Args:
            conversation_id: Conversation ID
            user_id: Optional user ID
            
        Returns:
            Conversation context
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            # Get messages
            messages = await self.retrieve_messages(conversation_id)
            
            # Get user context if user_id provided
            user_context = None
            if user_id:
                user_context = UserContext(user_id=user_id, metadata={})
            
            return ConversationContext(
                conversation_id=conversation_id,
                messages=messages,
                user_context=user_context,
                metadata={}
            )
            
        except Exception as e:
            raise OperationError(f"Failed to get context: {e}")
    
    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            stats = {}
            
            # Message count
            async with self._db.execute(
                "SELECT COUNT(*) FROM messages WHERE user_id = ?", 
                (user_id,)
            ) as cursor:
                stats["message_count"] = (await cursor.fetchone())[0]
            
            # Memory entry count
            async with self._db.execute(
                "SELECT COUNT(*) FROM memory_entries WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                stats["memory_count"] = (await cursor.fetchone())[0]
            
            # Active sessions
            async with self._db.execute(
                "SELECT COUNT(*) FROM sessions WHERE user_id = ? AND is_active = 1",
                (user_id,)
            ) as cursor:
                stats["active_sessions"] = (await cursor.fetchone())[0]
            
            # Conversation count
            async with self._db.execute(
                "SELECT COUNT(DISTINCT conversation_id) FROM messages WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                stats["conversation_count"] = (await cursor.fetchone())[0]
            
            return stats
            
        except Exception as e:
            raise OperationError(f"Failed to get statistics: {e}")