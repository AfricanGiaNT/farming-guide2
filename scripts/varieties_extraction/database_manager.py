#!/usr/bin/env python3
"""
Varieties Database Schema Manager
Milestone 1: Database Design

This module manages the database schema for the comprehensive varieties system.
It creates, updates, and validates the database structure for crops, varieties,
and farming processes.
"""

import os
import sys
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VarietiesDatabaseManager:
    """
    Manages the database schema for the varieties system.
    Handles creation, updates, and validation of database tables.
    """
    
    def __init__(self, db_path: str = "data/agricultural_documents.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = os.path.join(project_root, db_path)
        self.schema_version = "1.0.0"
        
        logger.info(f"VarietiesDatabaseManager initialized for: {self.db_path}")
    
    def create_complete_schema(self) -> bool:
        """
        Create the complete database schema for varieties system.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Creating complete varieties database schema")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create crops table
            self._create_crops_table(cursor)
            
            # Create varieties table
            self._create_varieties_table(cursor)
            
            # Create farming processes table
            self._create_farming_processes_table(cursor)
            
            # Create extraction sessions table
            self._create_extraction_sessions_table(cursor)
            
            # Create indexes
            self._create_indexes(cursor)
            
            # Create views for easier querying
            self._create_views(cursor)
            
            # Set schema version
            self._set_schema_version(cursor)
            
            conn.commit()
            logger.info("Complete database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _create_crops_table(self, cursor: sqlite3.Cursor):
        """Create the crops table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL UNIQUE,
                scientific_name TEXT,
                local_name TEXT,
                category TEXT CHECK(category IN ('cereal', 'legume', 'tuber', 'oilseed', 'vegetable', 'cash_crop', 'fruit', 'tree_nut', 'spice', 'other')),
                general_description TEXT,
                overview_image_url TEXT,
                water_requirements_min INTEGER,
                water_requirements_max INTEGER,
                temperature_min REAL,
                temperature_max REAL,
                soil_type_preference TEXT,
                planting_season TEXT,
                harvest_season TEXT,
                common_pests TEXT,
                common_diseases TEXT,
                nutritional_value TEXT,
                market_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Crops table created")
    
    def _create_varieties_table(self, cursor: sqlite3.Cursor):
        """Create the varieties table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS varieties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL,
                variety_name TEXT NOT NULL,
                type TEXT CHECK(type IN ('hybrid', 'open_pollinated', 'landrace', 'improved', 'other')),
                maturity_days INTEGER,
                drought_tolerance TEXT CHECK(drought_tolerance IN ('excellent', 'good', 'moderate', 'poor')),
                disease_resistance TEXT,
                yield_potential TEXT CHECK(yield_potential IN ('high', 'medium', 'low')),
                planting_months TEXT,
                harvest_months TEXT,
                min_rainfall_mm INTEGER,
                max_rainfall_mm INTEGER,
                optimal_temperature_min REAL,
                optimal_temperature_max REAL,
                soil_requirements TEXT,
                spacing_requirements TEXT,
                fertilizer_requirements TEXT,
                pest_management TEXT,
                disease_management TEXT,
                harvesting_guidelines TEXT,
                storage_requirements TEXT,
                seed_rate_per_hectare REAL,
                expected_yield_per_hectare REAL,
                market_preference TEXT,
                seed_availability TEXT,
                cost_per_kg REAL,
                source_document TEXT,
                extraction_confidence REAL CHECK(extraction_confidence >= 0 AND extraction_confidence <= 1),
                validation_status TEXT DEFAULT 'pending' CHECK(validation_status IN ('pending', 'validated', 'rejected')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (crop_id) REFERENCES crops (id) ON DELETE CASCADE,
                UNIQUE(crop_id, variety_name)
            )
        """)
        logger.info("Varieties table created")
    
    def _create_farming_processes_table(self, cursor: sqlite3.Cursor):
        """Create the farming processes table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farming_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variety_id INTEGER NOT NULL,
                process_type TEXT CHECK(process_type IN ('land_preparation', 'planting', 'maintenance', 'harvesting', 'post_harvest')),
                step_number INTEGER,
                step_description TEXT NOT NULL,
                timing TEXT,
                tools_required TEXT,
                materials_required TEXT,
                cost_estimate REAL,
                difficulty_level TEXT CHECK(difficulty_level IN ('easy', 'moderate', 'difficult')),
                time_required_hours REAL,
                weather_dependency TEXT,
                notes TEXT,
                source_document TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (variety_id) REFERENCES varieties (id) ON DELETE CASCADE
            )
        """)
        logger.info("Farming processes table created")
    
    def _create_extraction_sessions_table(self, cursor: sqlite3.Cursor):
        """Create the extraction sessions table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                pdf_files TEXT,
                total_crops_found INTEGER DEFAULT 0,
                total_varieties_extracted INTEGER DEFAULT 0,
                extraction_method TEXT CHECK(extraction_method IN ('ai', 'pattern', 'manual')),
                extraction_status TEXT DEFAULT 'in_progress' CHECK(extraction_status IN ('in_progress', 'completed', 'failed')),
                error_log TEXT,
                processing_time_seconds REAL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        logger.info("Extraction sessions table created")
    
    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Create database indexes for performance."""
        indexes = [
            # Crops table indexes
            "CREATE INDEX IF NOT EXISTS idx_crops_name ON crops(crop_name)",
            "CREATE INDEX IF NOT EXISTS idx_crops_category ON crops(category)",
            "CREATE INDEX IF NOT EXISTS idx_crops_created_at ON crops(created_at)",
            
            # Varieties table indexes
            "CREATE INDEX IF NOT EXISTS idx_varieties_crop_id ON varieties(crop_id)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_name ON varieties(variety_name)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_type ON varieties(type)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_maturity ON varieties(maturity_days)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_yield ON varieties(yield_potential)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_drought ON varieties(drought_tolerance)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_validation ON varieties(validation_status)",
            "CREATE INDEX IF NOT EXISTS idx_varieties_source ON varieties(source_document)",
            
            # Farming processes indexes
            "CREATE INDEX IF NOT EXISTS idx_processes_variety_id ON farming_processes(variety_id)",
            "CREATE INDEX IF NOT EXISTS idx_processes_type ON farming_processes(process_type)",
            "CREATE INDEX IF NOT EXISTS idx_processes_step ON farming_processes(step_number)",
            
            # Extraction sessions indexes
            "CREATE INDEX IF NOT EXISTS idx_sessions_id ON extraction_sessions(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_status ON extraction_sessions(extraction_status)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_started ON extraction_sessions(started_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        logger.info("Database indexes created")
    
    def _create_views(self, cursor: sqlite3.Cursor):
        """Create useful views for easier querying."""
        views = [
            # Complete variety information view
            """
            CREATE VIEW IF NOT EXISTS variety_details AS
            SELECT 
                v.id as variety_id,
                c.crop_name,
                c.scientific_name,
                c.category,
                v.variety_name,
                v.type,
                v.maturity_days,
                v.drought_tolerance,
                v.disease_resistance,
                v.yield_potential,
                v.planting_months,
                v.harvest_months,
                v.min_rainfall_mm,
                v.max_rainfall_mm,
                v.optimal_temperature_min,
                v.optimal_temperature_max,
                v.soil_requirements,
                v.spacing_requirements,
                v.fertilizer_requirements,
                v.pest_management,
                v.disease_management,
                v.harvesting_guidelines,
                v.storage_requirements,
                v.seed_rate_per_hectare,
                v.expected_yield_per_hectare,
                v.market_preference,
                v.seed_availability,
                v.cost_per_kg,
                v.source_document,
                v.extraction_confidence,
                v.validation_status,
                v.created_at,
                v.updated_at
            FROM varieties v
            JOIN crops c ON v.crop_id = c.id
            """,
            
            # Crop summary view
            """
            CREATE VIEW IF NOT EXISTS crop_summary AS
            SELECT 
                c.id as crop_id,
                c.crop_name,
                c.scientific_name,
                c.category,
                COUNT(v.id) as variety_count,
                AVG(v.maturity_days) as avg_maturity_days,
                COUNT(CASE WHEN v.yield_potential = 'high' THEN 1 END) as high_yield_varieties,
                COUNT(CASE WHEN v.drought_tolerance = 'excellent' THEN 1 END) as drought_tolerant_varieties,
                GROUP_CONCAT(DISTINCT v.source_document) as source_documents
            FROM crops c
            LEFT JOIN varieties v ON c.id = v.crop_id
            GROUP BY c.id, c.crop_name, c.scientific_name, c.category
            """,
            
            # Farming process summary view
            """
            CREATE VIEW IF NOT EXISTS farming_process_summary AS
            SELECT 
                v.variety_name,
                c.crop_name,
                fp.process_type,
                COUNT(fp.id) as step_count,
                GROUP_CONCAT(fp.step_description, ' | ') as process_steps
            FROM farming_processes fp
            JOIN varieties v ON fp.variety_id = v.id
            JOIN crops c ON v.crop_id = c.id
            GROUP BY v.variety_name, c.crop_name, fp.process_type
            """
        ]
        
        for view_sql in views:
            cursor.execute(view_sql)
        
        logger.info("Database views created")
    
    def _set_schema_version(self, cursor: sqlite3.Cursor):
        """Set the schema version."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO schema_version (version) VALUES (?)
        """, (self.schema_version,))
        
        logger.info(f"Schema version set to: {self.schema_version}")
    
    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate the database schema.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating database schema")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tables": {},
            "indexes": {},
            "views": {}
        }
        
        try:
            # Check required tables
            required_tables = ['crops', 'varieties', 'farming_processes', 'extraction_sessions']
            
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    validation_results["tables"][table] = "exists"
                else:
                    validation_results["tables"][table] = "missing"
                    validation_results["errors"].append(f"Required table '{table}' is missing")
                    validation_results["valid"] = False
            
            # Check table schemas
            for table in required_tables:
                if validation_results["tables"][table] == "exists":
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    validation_results["tables"][f"{table}_columns"] = columns
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            validation_results["indexes"] = indexes
            
            # Check views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]
            validation_results["views"] = views
            
            # Check schema version
            try:
                cursor.execute("SELECT version FROM schema_version ORDER BY created_at DESC LIMIT 1")
                version_result = cursor.fetchone()
                if version_result:
                    validation_results["schema_version"] = version_result[0]
                else:
                    validation_results["warnings"].append("Schema version not found")
            except Exception:
                validation_results["warnings"].append("Schema version table not accessible")
            
            logger.info(f"Schema validation completed: {'PASS' if validation_results['valid'] else 'FAIL'}")
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            validation_results["valid"] = False
            validation_results["errors"].append(str(e))
        finally:
            conn.close()
        
        return validation_results
    
    def save_crop(self, crop_data: Dict[str, Any]) -> Optional[int]:
        """Save crop data and return crop ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO crops (crop_name, scientific_name, local_name, category, 
                                 general_description, overview_image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                crop_data.get('crop_name'),
                crop_data.get('scientific_name'),
                crop_data.get('local_name'),
                crop_data.get('category'),
                crop_data.get('general_description'),
                crop_data.get('overview_image_url')
            ))
            
            crop_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Crop saved: {crop_data.get('crop_name')} (ID: {crop_id})")
            return crop_id
            
        except Exception as e:
            logger.error(f"Error saving crop: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def save_variety(self, variety_data: Dict[str, Any]) -> Optional[int]:
        """Save variety data and return variety ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO varieties (crop_id, variety_name, type, maturity_days,
                                     drought_tolerance, disease_resistance, yield_potential,
                                     planting_months, harvest_months, min_rainfall_mm,
                                     max_rainfall_mm, optimal_temperature_min, optimal_temperature_max,
                                     soil_requirements, spacing_requirements, fertilizer_requirements,
                                     pest_management, disease_management, harvesting_guidelines,
                                     storage_requirements, source_document, extraction_confidence,
                                     validation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                variety_data.get('crop_id'),
                variety_data.get('variety_name'),
                variety_data.get('variety_type'),
                variety_data.get('maturity_days'),
                variety_data.get('drought_tolerance'),
                variety_data.get('disease_resistance'),
                variety_data.get('yield_potential'),
                variety_data.get('planting_months'),
                variety_data.get('harvest_months'),
                variety_data.get('min_rainfall_mm'),
                variety_data.get('max_rainfall_mm'),
                variety_data.get('optimal_temperature_min'),
                variety_data.get('optimal_temperature_max'),
                variety_data.get('soil_requirements'),
                variety_data.get('spacing_requirements'),
                variety_data.get('fertilizer_requirements'),
                variety_data.get('pest_management'),
                variety_data.get('disease_management'),
                variety_data.get('harvesting_guidelines'),
                variety_data.get('storage_requirements'),
                variety_data.get('source_document'),
                variety_data.get('extraction_confidence', 0.0),
                variety_data.get('validation_status', 'pending')
            ))
            
            variety_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Variety saved: {variety_data.get('variety_name')} (ID: {variety_id})")
            return variety_id
            
        except Exception as e:
            logger.error(f"Error saving variety: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def save_farming_process(self, process_data: Dict[str, Any]) -> Optional[int]:
        """Save farming process data and return process ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO farming_processes (variety_id, process_type, step_number,
                                            step_description, timing, tools_required, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                process_data.get('variety_id'),
                process_data.get('process_type'),
                process_data.get('step_number'),
                process_data.get('step_description'),
                process_data.get('timing'),
                process_data.get('tools_required'),
                process_data.get('notes')
            ))
            
            process_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Farming process saved: {process_data.get('process_type')} (ID: {process_id})")
            return process_id
            
        except Exception as e:
            logger.error(f"Error saving farming process: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def create_extraction_session(self, session_id: str, extraction_method: str) -> bool:
        """Create a new extraction session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO extraction_sessions (session_id, extraction_method, extraction_status)
                VALUES (?, ?, 'in_progress')
            """, (session_id, extraction_method))
            
            conn.commit()
            logger.info(f"Extraction session created: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating extraction session: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_extraction_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update extraction session with results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(session_id)
            
            cursor.execute(f"""
                UPDATE extraction_sessions 
                SET {', '.join(set_clauses)}
                WHERE session_id = ?
            """, values)
            
            conn.commit()
            logger.info(f"Extraction session updated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating extraction session: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_crop_id(self, crop_name: str) -> Optional[int]:
        """Get crop ID by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM crops WHERE crop_name = ?", (crop_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting crop ID: {e}")
            return None
        finally:
            conn.close()
    
    def get_variety_count(self, crop_id: int) -> int:
        """Get variety count for a crop."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM varieties WHERE crop_id = ?", (crop_id,))
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting variety count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_all_crops(self) -> List[Dict[str, Any]]:
        """Get all crops."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM crops ORDER BY crop_name")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all crops: {e}")
            return []
        finally:
            conn.close()
    
    def get_varieties_by_crop_id(self, crop_id: int) -> List[Dict[str, Any]]:
        """Get varieties for a crop."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM varieties WHERE crop_id = ? ORDER BY variety_name", (crop_id,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting varieties by crop ID: {e}")
            return []
        finally:
            conn.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Count records in each table
            tables = ['crops', 'varieties', 'farming_processes', 'extraction_sessions']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Get variety distribution by crop
            cursor.execute("""
                SELECT c.crop_name, COUNT(v.id) as variety_count
                FROM crops c
                LEFT JOIN varieties v ON c.id = v.crop_id
                GROUP BY c.crop_name
                ORDER BY variety_count DESC
            """)
            stats["varieties_by_crop"] = dict(cursor.fetchall())
            
            # Get extraction session stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(total_varieties_extracted) as total_varieties_extracted,
                    AVG(processing_time_seconds) as avg_processing_time
                FROM extraction_sessions
                WHERE extraction_status = 'completed'
            """)
            session_stats = cursor.fetchone()
            if session_stats:
                stats["extraction_stats"] = {
                    "total_sessions": session_stats[0],
                    "total_varieties_extracted": session_stats[1],
                    "avg_processing_time": session_stats[2]
                }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
        finally:
            conn.close()
        
        return stats
    
    def reset_database(self) -> bool:
        """
        Reset the database (drop all tables and recreate).
        
        Returns:
            True if successful, False otherwise
        """
        logger.warning("Resetting database - all data will be lost!")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Drop all tables (excluding sqlite system tables)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if not table.startswith('sqlite_'):
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            # Drop all views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]
            
            for view in views:
                cursor.execute(f"DROP VIEW IF EXISTS {view}")
            
            conn.commit()
            logger.info("Database reset completed")
            
            # Recreate schema
            return self.create_complete_schema()
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


def main():
    """Main function to manage database schema."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage varieties database schema')
    parser.add_argument('--db-path', default='data/agricultural_documents.db', help='Database path')
    parser.add_argument('--action', choices=['create', 'validate', 'stats', 'reset'], 
                       default='create', help='Action to perform')
    
    args = parser.parse_args()
    
    # Initialize database manager
    db_manager = VarietiesDatabaseManager(db_path=args.db_path)
    
    if args.action == 'create':
        print("🏗️  Creating varieties database schema...")
        success = db_manager.create_complete_schema()
        if success:
            print("✅ Database schema created successfully")
        else:
            print("❌ Failed to create database schema")
    
    elif args.action == 'validate':
        print("🔍 Validating database schema...")
        results = db_manager.validate_schema()
        if results['valid']:
            print("✅ Schema validation passed")
        else:
            print("❌ Schema validation failed")
            for error in results['errors']:
                print(f"   Error: {error}")
        
        for warning in results['warnings']:
            print(f"   Warning: {warning}")
    
    elif args.action == 'stats':
        print("📊 Getting database statistics...")
        stats = db_manager.get_database_stats()
        print(f"   Crops: {stats.get('crops_count', 0)}")
        print(f"   Varieties: {stats.get('varieties_count', 0)}")
        print(f"   Farming processes: {stats.get('farming_processes_count', 0)}")
        print(f"   Extraction sessions: {stats.get('extraction_sessions_count', 0)}")
        
        if stats.get('varieties_by_crop'):
            print("\n   Varieties by crop:")
            for crop, count in list(stats['varieties_by_crop'].items())[:10]:
                print(f"     {crop}: {count}")
    
    elif args.action == 'reset':
        print("⚠️  Resetting database...")
        success = db_manager.reset_database()
        if success:
            print("✅ Database reset successfully")
        else:
            print("❌ Failed to reset database")


if __name__ == "__main__":
    main()
