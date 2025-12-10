"""
Migration system for SQLite backend.

Handles schema versioning and upgrades.
"""

import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from ...exceptions import MigrationError
from .schema import SCHEMA_VERSION, get_schema_version_query, get_insert_schema_version_query


class Migration:
    """Represents a single database migration."""
    
    def __init__(
        self,
        version: str,
        description: str,
        up_statements: List[str],
        down_statements: Optional[List[str]] = None
    ):
        """Initialize migration.
        
        Args:
            version: Migration version
            description: Migration description
            up_statements: SQL statements to apply migration
            down_statements: SQL statements to rollback migration
        """
        self.version = version
        self.description = description
        self.up_statements = up_statements
        self.down_statements = down_statements or []


class SQLiteMigrationManager:
    """Manages SQLite database migrations."""
    
    def __init__(self, database_path: str):
        """Initialize migration manager.
        
        Args:
            database_path: Path to SQLite database
        """
        self.database_path = Path(database_path)
        self.migrations: Dict[str, Migration] = {}
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all available migrations."""
        
        # Migration 1.0.0: Initial schema
        initial_schema = Migration(
            version="1.0.0",
            description="Initial schema with messages, sessions, memory_entries, and users tables",
            up_statements=[
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_active TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    metadata TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message_type TEXT,
                    metadata TEXT,
                    user_id TEXT,
                    parent_id TEXT,
                    tokens INTEGER,
                    model TEXT,
                    finish_reason TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES messages(id) ON DELETE SET NULL
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT,
                    tags TEXT,
                    metadata TEXT,
                    embedding TEXT,
                    expires_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (conversation_id) REFERENCES sessions(conversation_id) ON DELETE SET NULL
                );
                """,
                # Create indexes
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
                "CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_sessions_conversation_id ON sessions(conversation_id);",
                "CREATE INDEX IF NOT EXISTS idx_memory_entries_user_id ON memory_entries(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_memory_entries_conversation_id ON memory_entries(conversation_id);",
                "CREATE INDEX IF NOT EXISTS idx_memory_entries_memory_type ON memory_entries(memory_type);",
                "CREATE INDEX IF NOT EXISTS idx_memory_entries_importance ON memory_entries(importance);",
            ],
            down_statements=[
                "DROP TABLE IF EXISTS memory_entries;",
                "DROP TABLE IF EXISTS messages;", 
                "DROP TABLE IF EXISTS sessions;",
                "DROP TABLE IF EXISTS users;",
            ]
        )
        
        self.migrations["1.0.0"] = initial_schema
        
        # Future migrations would be added here
        # Example:
        # migration_1_1_0 = Migration(
        #     version="1.1.0", 
        #     description="Add full-text search tables",
        #     up_statements=[...],
        #     down_statements=[...]
        # )
        # self.migrations["1.1.0"] = migration_1_1_0
    
    async def get_current_version(self) -> Optional[str]:
        """Get current database schema version.
        
        Returns:
            Current version string or None if not set
        """
        try:
            async with aiosqlite.connect(str(self.database_path)) as db:
                # Check if schema_info table exists
                async with db.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name='schema_info'
                """) as cursor:
                    exists = (await cursor.fetchone())[0] > 0
                
                if not exists:
                    return None
                
                # Get current version
                async with db.execute(get_schema_version_query()) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else None
                    
        except Exception as e:
            raise MigrationError(f"Failed to get current version: {e}")
    
    async def needs_migration(self) -> bool:
        """Check if database needs migration.
        
        Returns:
            True if migration is needed
        """
        current_version = await self.get_current_version()
        return current_version != SCHEMA_VERSION
    
    async def get_migration_plan(self) -> List[Migration]:
        """Get list of migrations needed to reach current version.
        
        Returns:
            Ordered list of migrations to apply
        """
        current_version = await self.get_current_version()
        
        # For now, we only support upgrading to latest version
        # In future, we could implement proper version ordering
        if current_version is None:
            # Fresh database, apply all migrations
            return [self.migrations[SCHEMA_VERSION]]
        elif current_version == SCHEMA_VERSION:
            # Already up to date
            return []
        else:
            # Need upgrade - for now just apply latest
            return [self.migrations[SCHEMA_VERSION]]
    
    async def apply_migrations(self, migrations: List[Migration]) -> None:
        """Apply a list of migrations.
        
        Args:
            migrations: List of migrations to apply
            
        Raises:
            MigrationError: If migration fails
        """
        if not migrations:
            return
        
        try:
            async with aiosqlite.connect(str(self.database_path)) as db:
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys = ON;")
                
                for migration in migrations:
                    # Apply migration statements
                    for statement in migration.up_statements:
                        await db.execute(statement)
                    
                    # Record migration
                    await db.execute(
                        get_insert_schema_version_query(migration.version, migration.description)
                    )
                
                await db.commit()
                
        except Exception as e:
            raise MigrationError(f"Migration failed: {e}")
    
    async def rollback_migration(self, target_version: str) -> None:
        """Rollback to a specific version.
        
        Args:
            target_version: Version to rollback to
            
        Raises:
            MigrationError: If rollback fails
        """
        current_version = await self.get_current_version()
        
        if not current_version:
            raise MigrationError("No current version to rollback from")
        
        if target_version == current_version:
            return  # Already at target version
        
        # For now, only support rollback to empty state
        if target_version != "":
            raise MigrationError("Only rollback to empty database supported currently")
        
        try:
            migration = self.migrations[current_version]
            if not migration.down_statements:
                raise MigrationError(f"No rollback available for version {current_version}")
            
            async with aiosqlite.connect(str(self.database_path)) as db:
                # Apply rollback statements
                for statement in migration.down_statements:
                    await db.execute(statement)
                
                # Remove version record
                await db.execute("DROP TABLE IF EXISTS schema_info;")
                
                await db.commit()
                
        except Exception as e:
            raise MigrationError(f"Rollback failed: {e}")
    
    async def migrate_to_latest(self) -> None:
        """Migrate database to latest version.
        
        Raises:
            MigrationError: If migration fails
        """
        # Ensure parent directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create schema_info table if it doesn't exist
        try:
            async with aiosqlite.connect(str(self.database_path)) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS schema_info (
                        version TEXT PRIMARY KEY,
                        applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    );
                """)
                await db.commit()
        except Exception as e:
            raise MigrationError(f"Failed to create schema_info table: {e}")
        
        # Get and apply migration plan
        migrations = await self.get_migration_plan()
        await self.apply_migrations(migrations)
    
    async def validate_schema(self) -> Dict[str, Any]:
        """Validate current database schema.
        
        Returns:
            Validation results
        """
        try:
            async with aiosqlite.connect(str(self.database_path)) as db:
                results = {
                    "valid": True,
                    "version": await self.get_current_version(),
                    "tables": {},
                    "indexes": {}
                }
                
                # Check required tables
                required_tables = ["users", "sessions", "messages", "memory_entries", "schema_info"]
                
                for table in required_tables:
                    async with db.execute(f"""
                        SELECT COUNT(*) FROM sqlite_master 
                        WHERE type='table' AND name='{table}'
                    """) as cursor:
                        exists = (await cursor.fetchone())[0] > 0
                        results["tables"][table] = exists
                        if not exists:
                            results["valid"] = False
                
                # Check indexes
                required_indexes = [
                    "idx_messages_conversation_id",
                    "idx_messages_user_id", 
                    "idx_sessions_user_id",
                    "idx_memory_entries_user_id"
                ]
                
                for index in required_indexes:
                    async with db.execute(f"""
                        SELECT COUNT(*) FROM sqlite_master 
                        WHERE type='index' AND name='{index}'
                    """) as cursor:
                        exists = (await cursor.fetchone())[0] > 0
                        results["indexes"][index] = exists
                        # Indexes are not critical for validity
                
                return results
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "version": None,
                "tables": {},
                "indexes": {}
            }