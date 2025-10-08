"""Database schema utilities for the varieties extraction workflow."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def _resolve_db_path(db_path: str) -> str:
    """Resolve database path relative to project root when needed."""
    if os.path.isabs(db_path):
        return db_path
    return str(PROJECT_ROOT / db_path)

def _column_names(cursor: sqlite3.Cursor, table: str) -> Iterable[str]:
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def ensure_varieties_schema(db_path: str = "data/agricultural_documents.db") -> None:
    """Ensure varieties-related tables include the fields required for validation flow."""
    resolved_path = _resolve_db_path(db_path)
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Database not found at {resolved_path}")

    conn = sqlite3.connect(resolved_path)
    cursor = conn.cursor()

    try:
        # Ensure varieties table exists before attempting modifications
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='varieties'")
        if cursor.fetchone() is None:
            raise RuntimeError("Varieties table does not exist. Run the table creation script first.")

        existing_columns = set(_column_names(cursor, 'varieties'))
        schema_updates = []

        if 'confidence_score' not in existing_columns:
            schema_updates.append("ALTER TABLE varieties ADD COLUMN confidence_score INTEGER DEFAULT 0")
        if 'validation_status' not in existing_columns:
            schema_updates.append("ALTER TABLE varieties ADD COLUMN validation_status TEXT DEFAULT 'pending'")
        if 'extraction_session_id' not in existing_columns:
            schema_updates.append("ALTER TABLE varieties ADD COLUMN extraction_session_id TEXT")

        for statement in schema_updates:
            cursor.execute(statement)

        # Ensure helpful indexes exist
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_varieties_session ON varieties(extraction_session_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_varieties_validation_status ON varieties(validation_status)"
        )

        # Ensure extraction_sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extraction_sessions'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE extraction_sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    documents_processed INTEGER,
                    varieties_extracted INTEGER,
                    varieties_selected INTEGER,
                    status TEXT DEFAULT 'pending'
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_extraction_sessions_status ON extraction_sessions(status)"
            )

        conn.commit()
    finally:
        conn.close()
