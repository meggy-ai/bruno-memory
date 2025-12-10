"""
SQLite database schema for bruno-memory.

Defines tables for messages, sessions, memory entries, and users.
"""

# Database schema version
SCHEMA_VERSION = "1.0.0"

# Table creation SQL statements
MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    message_type TEXT,
    metadata TEXT,  -- JSON
    user_id TEXT,
    parent_id TEXT,
    tokens INTEGER,
    model TEXT,
    finish_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES messages(id) ON DELETE SET NULL
);
"""

SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    metadata TEXT,  -- JSON
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

MEMORY_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    conversation_id TEXT,
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON
    embedding TEXT,  -- JSON array of floats
    expires_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES sessions(conversation_id) ON DELETE SET NULL
);
"""

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    metadata TEXT,  -- JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT
);
"""

SCHEMA_INFO_TABLE = """
CREATE TABLE IF NOT EXISTS schema_info (
    version TEXT PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
"""

# Index definitions for performance
INDEXES = [
    # Message indexes
    "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
    "CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);",
    "CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);",
    
    # Session indexes  
    "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_conversation_id ON sessions(conversation_id);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);",
    
    # Memory entry indexes
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_user_id ON memory_entries(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_conversation_id ON memory_entries(conversation_id);", 
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_memory_type ON memory_entries(memory_type);",
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_importance ON memory_entries(importance);",
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_timestamp ON memory_entries(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_memory_entries_expires_at ON memory_entries(expires_at);",
    
    # User indexes
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active);",
]

# Full-text search virtual table for messages
FTS_MESSAGES_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    message_id UNINDEXED,
    conversation_id UNINDEXED,
    role UNINDEXED,
    content,
    user_id UNINDEXED,
    content='messages',
    content_rowid='rowid'
);
"""

# FTS triggers to keep search table in sync
FTS_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS messages_fts_insert AFTER INSERT ON messages BEGIN
        INSERT INTO messages_fts(message_id, conversation_id, role, content, user_id)
        VALUES (new.id, new.conversation_id, new.role, new.content, new.user_id);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS messages_fts_delete AFTER DELETE ON messages BEGIN
        DELETE FROM messages_fts WHERE message_id = old.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS messages_fts_update AFTER UPDATE ON messages BEGIN
        UPDATE messages_fts SET
            conversation_id = new.conversation_id,
            role = new.role,
            content = new.content,
            user_id = new.user_id
        WHERE message_id = new.id;
    END;
    """
]

# Full-text search virtual table for memory entries
FTS_MEMORY_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS memory_entries_fts USING fts5(
    memory_id UNINDEXED,
    user_id UNINDEXED,
    conversation_id UNINDEXED,
    memory_type UNINDEXED,
    content,
    tags,
    content='memory_entries',
    content_rowid='rowid'
);
"""

FTS_MEMORY_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS memory_fts_insert AFTER INSERT ON memory_entries BEGIN
        INSERT INTO memory_entries_fts(memory_id, user_id, conversation_id, memory_type, content, tags)
        VALUES (new.id, new.user_id, new.conversation_id, new.memory_type, new.content, new.tags);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS memory_fts_delete AFTER DELETE ON memory_entries BEGIN
        DELETE FROM memory_entries_fts WHERE memory_id = old.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS memory_fts_update AFTER UPDATE ON memory_entries BEGIN
        UPDATE memory_entries_fts SET
            user_id = new.user_id,
            conversation_id = new.conversation_id, 
            memory_type = new.memory_type,
            content = new.content,
            tags = new.tags
        WHERE memory_id = new.id;
    END;
    """
]

# Comprehensive schema creation
SCHEMA_STATEMENTS = [
    # Core tables
    USERS_TABLE,
    SESSIONS_TABLE,
    MESSAGES_TABLE,
    MEMORY_ENTRIES_TABLE,
    SCHEMA_INFO_TABLE,
    
    # Indexes
    *INDEXES,
    
    # Full-text search (conditional on config)
    FTS_MESSAGES_TABLE,
    *FTS_TRIGGERS,
    FTS_MEMORY_TABLE,
    *FTS_MEMORY_TRIGGERS,
]

# SQLite configuration statements
SQLITE_PRAGMA = [
    "PRAGMA foreign_keys = ON;",
    "PRAGMA journal_mode = WAL;",
    "PRAGMA synchronous = NORMAL;",
    "PRAGMA cache_size = -2000;",  # 2MB cache
    "PRAGMA temp_store = MEMORY;",
    "PRAGMA mmap_size = 268435456;",  # 256MB mmap
]


def get_table_exists_query(table_name: str) -> str:
    """Get SQL to check if a table exists.
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        SQL query string
    """
    return f"""
    SELECT COUNT(*) FROM sqlite_master 
    WHERE type='table' AND name='{table_name}';
    """


def get_schema_version_query() -> str:
    """Get current schema version from database."""
    return "SELECT version FROM schema_info ORDER BY applied_at DESC LIMIT 1;"


def get_insert_schema_version_query(version: str, description: str = "") -> str:
    """Get SQL to insert schema version info."""
    return f"""
    INSERT INTO schema_info (version, description) 
    VALUES ('{version}', '{description}');
    """


# Export the main components
__all__ = [
    "SCHEMA_VERSION",
    "SCHEMA_STATEMENTS", 
    "SQLITE_PRAGMA",
    "get_table_exists_query",
    "get_schema_version_query",
    "get_insert_schema_version_query",
]