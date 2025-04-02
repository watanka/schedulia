# src/db/factory.py
from typing import Dict, Any
from src.db.base import DatabaseInterface
from src.db.memory_db import MemoryDatabase
from src.db.postgres_db import PostgresDatabase

class DatabaseFactory:
    @staticmethod
    def create_database(config: Dict[str, Any]) -> DatabaseInterface:
        db_type = config.get("type", "memory")
        
        if db_type == "memory":
            return MemoryDatabase()
        elif db_type == "postgres":
            connection_string = config.get("connection_string")
            if not connection_string:
                raise ValueError("PostgreSQL connection string is required")
            return PostgresDatabase(connection_string)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")