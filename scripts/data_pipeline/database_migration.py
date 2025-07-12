"""
Database Migration Tool for Agricultural Advisor Bot.
Migrates data from FAISS to PostgreSQL vector database.
"""

import os
import json
import pickle
from typing import Dict, Any, List, Optional
from pathlib import Path
from scripts.data_pipeline.vector_database import VectorDatabase
from scripts.data_pipeline.postgresql_vector_database import PostgreSQLVectorDatabase
from scripts.data_pipeline.semantic_search import SemanticSearch
from scripts.utils.logger import logger


class DatabaseMigrator:
    """
    Tool for migrating vector databases between different backends.
    """
    
    def __init__(self, backup_path: str = "backups/migration"):
        """
        Initialize database migrator.
        
        Args:
            backup_path: Path to store migration backups
        """
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Database migrator initialized")
    
    def migrate_faiss_to_postgresql(self, 
                                   faiss_storage_path: str = "data/vector_db",
                                   postgresql_params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Migrate data from FAISS to PostgreSQL vector database.
        
        Args:
            faiss_storage_path: Path to FAISS storage directory
            postgresql_params: PostgreSQL connection parameters
            
        Returns:
            True if migration successful, False otherwise
        """
        logger.info("Starting FAISS to PostgreSQL migration...")
        
        try:
            # Step 1: Create backup
            backup_created = self._create_migration_backup(faiss_storage_path)
            if not backup_created:
                logger.error("Failed to create migration backup")
                return False
            
            # Step 2: Load FAISS data
            faiss_data = self._load_faiss_data(faiss_storage_path)
            if not faiss_data:
                logger.error("Failed to load FAISS data")
                return False
            
            # Step 3: Initialize PostgreSQL database
            postgresql_db = PostgreSQLVectorDatabase(**(postgresql_params or {}))
            
            # Step 4: Clear existing PostgreSQL data (if any)
            postgresql_db.clear_database()
            
            # Step 5: Migrate embeddings and chunks
            embeddings = faiss_data['embeddings']
            chunks = faiss_data['chunks']
            
            if not embeddings or not chunks:
                logger.error("No embeddings or chunks found in FAISS data")
                return False
            
            # Add data to PostgreSQL
            success = postgresql_db.add_vectors(embeddings, chunks)
            if not success:
                logger.error("Failed to add vectors to PostgreSQL")
                return False
            
            # Step 6: Verify migration
            verification_passed = self._verify_migration(faiss_data, postgresql_db)
            if not verification_passed:
                logger.error("Migration verification failed")
                return False
            
            logger.info("FAISS to PostgreSQL migration completed successfully")
            logger.info(f"Migrated {len(embeddings)} vectors from FAISS to PostgreSQL")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _create_migration_backup(self, storage_path: str) -> bool:
        """Create a backup of the current data before migration."""
        try:
            import shutil
            from datetime import datetime
            
            # Create timestamped backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_path / f"faiss_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy FAISS storage directory
            storage_path_obj = Path(storage_path)
            if storage_path_obj.exists():
                shutil.copytree(storage_path_obj, backup_dir / "vector_db")
                logger.info(f"Created migration backup at: {backup_dir}")
                return True
            else:
                logger.warning(f"FAISS storage path not found: {storage_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating migration backup: {e}")
            return False
    
    def _load_faiss_data(self, storage_path: str) -> Optional[Dict[str, Any]]:
        """Load data from FAISS storage."""
        try:
            # Initialize FAISS vector database
            faiss_db = VectorDatabase(storage_path=storage_path)
            
            # Load the index
            if not faiss_db.load_index():
                logger.error("Failed to load FAISS index")
                return None
            
            # Extract embeddings and chunks
            embeddings = []
            chunks = []
            
            # Get all vectors (this is a limitation of FAISS - we can't directly extract embeddings)
            # We'll use the metadata to reconstruct
            metadata = faiss_db.metadata
            id_to_chunk = faiss_db.id_to_chunk
            
            if not metadata:
                logger.error("No metadata found in FAISS database")
                return None
            
            # For each chunk, we need to regenerate embeddings
            # This is a limitation - we'll need to re-embed the text
            logger.info("Re-generating embeddings for FAISS data...")
            
            from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
            embedding_generator = EmbeddingGenerator()
            
            # Extract texts from chunks
            texts = [chunk.get('text', '') for chunk in metadata]
            
            # Generate embeddings
            embeddings = embedding_generator.generate_embeddings(texts)
            
            if not embeddings:
                logger.error("Failed to regenerate embeddings")
                return None
            
            return {
                'embeddings': embeddings,
                'chunks': metadata,
                'total_vectors': len(embeddings)
            }
            
        except Exception as e:
            logger.error(f"Error loading FAISS data: {e}")
            return None
    
    def _verify_migration(self, faiss_data: Dict[str, Any], postgresql_db: PostgreSQLVectorDatabase) -> bool:
        """Verify that migration was successful."""
        try:
            # Check vector count
            pg_stats = postgresql_db.get_database_stats()
            faiss_vector_count = faiss_data['total_vectors']
            pg_vector_count = pg_stats.get('total_vectors', 0)
            
            if faiss_vector_count != pg_vector_count:
                logger.error(f"Vector count mismatch: FAISS={faiss_vector_count}, PostgreSQL={pg_vector_count}")
                return False
            
            # Test a sample search
            if faiss_data['embeddings']:
                sample_embedding = faiss_data['embeddings'][0]
                search_results = postgresql_db.search(sample_embedding, top_k=3)
                
                if not search_results:
                    logger.error("Sample search returned no results")
                    return False
                
                logger.info(f"Sample search returned {len(search_results)} results")
            
            logger.info("Migration verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return False
    
    def create_postgresql_config(self, 
                                host: str = "localhost",
                                port: int = 5432,
                                database: str = "farming_guide",
                                user: str = "postgres",
                                password: str = "") -> bool:
        """
        Create PostgreSQL configuration file.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            
        Returns:
            True if config created successfully
        """
        try:
            config_content = f"""# PostgreSQL Configuration for Agricultural Advisor Bot
# Update with your actual database credentials

# Method 1: DATABASE_URL (recommended)
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}

# Method 2: Individual parameters (alternative)
DB_HOST={host}
DB_PORT={port}
DB_NAME={database}
DB_USER={user}
DB_PASSWORD={password}

# Vector database settings
VECTOR_DB_TYPE=postgresql
VECTOR_DB_TABLE=document_embeddings
VECTOR_DB_DIMENSION=1536
"""
            
            # Write to config file
            config_path = Path("config/postgresql.env")
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            logger.info(f"PostgreSQL configuration created at: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating PostgreSQL config: {e}")
            return False
    
    def rollback_migration(self, backup_timestamp: str) -> bool:
        """
        Rollback migration by restoring from backup.
        
        Args:
            backup_timestamp: Timestamp of backup to restore
            
        Returns:
            True if rollback successful
        """
        try:
            backup_dir = self.backup_path / f"faiss_backup_{backup_timestamp}"
            
            if not backup_dir.exists():
                logger.error(f"Backup directory not found: {backup_dir}")
                return False
            
            # Restore FAISS data
            import shutil
            backup_vector_db = backup_dir / "vector_db"
            current_vector_db = Path("data/vector_db")
            
            if current_vector_db.exists():
                shutil.rmtree(current_vector_db)
            
            shutil.copytree(backup_vector_db, current_vector_db)
            
            logger.info(f"Rollback completed from backup: {backup_timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status and options.
        
        Returns:
            Dictionary with migration status
        """
        try:
            status = {
                'faiss_available': False,
                'postgresql_available': False,
                'faiss_vector_count': 0,
                'postgresql_vector_count': 0,
                'migration_recommended': False
            }
            
            # Check FAISS availability
            try:
                faiss_db = VectorDatabase()
                if faiss_db.load_index():
                    status['faiss_available'] = True
                    stats = faiss_db.get_database_stats()
                    status['faiss_vector_count'] = stats.get('total_vectors', 0)
            except Exception:
                pass
            
            # Check PostgreSQL availability
            try:
                pg_db = PostgreSQLVectorDatabase()
                stats = pg_db.get_database_stats()
                status['postgresql_available'] = True
                status['postgresql_vector_count'] = stats.get('total_vectors', 0)
                pg_db.close()
            except Exception:
                pass
            
            # Migration recommendation
            if status['faiss_available'] and status['postgresql_available']:
                if status['faiss_vector_count'] > 0 and status['postgresql_vector_count'] == 0:
                    status['migration_recommended'] = True
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {}


# Convenience functions for easy migration
def quick_migrate_to_postgresql() -> bool:
    """Quick migration from FAISS to PostgreSQL with default settings."""
    migrator = DatabaseMigrator()
    return migrator.migrate_faiss_to_postgresql()


def setup_postgresql_config(host: str = "localhost", 
                          port: int = 5432,
                          database: str = "farming_guide",
                          user: str = "postgres",
                          password: str = "") -> bool:
    """Quick setup of PostgreSQL configuration."""
    migrator = DatabaseMigrator()
    return migrator.create_postgresql_config(host, port, database, user, password)


if __name__ == "__main__":
    # Example usage
    migrator = DatabaseMigrator()
    
    # Get migration status
    status = migrator.get_migration_status()
    print("Migration Status:")
    print(json.dumps(status, indent=2))
    
    # Perform migration if recommended
    if status.get('migration_recommended', False):
        print("\nStarting migration...")
        success = migrator.migrate_faiss_to_postgresql()
        if success:
            print("Migration completed successfully!")
        else:
            print("Migration failed!") 