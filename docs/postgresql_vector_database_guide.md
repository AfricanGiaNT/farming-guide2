# PostgreSQL Vector Database Guide

## Overview

This guide explains how to use PostgreSQL with the pgvector extension as a modern, production-ready alternative to FAISS for your Agricultural Advisor Bot's knowledge base.

## 🚀 Why PostgreSQL Vector Database?

### Current FAISS Limitations
- **Local file storage only** - No cloud deployment
- **No concurrent access** - Single process limitation
- **Limited filtering** - Basic similarity search only
- **No ACID compliance** - Data integrity concerns
- **Backup challenges** - Manual file management

### PostgreSQL Vector Database Benefits
- ✅ **Production-ready** - ACID compliance, transactions, reliability
- ✅ **Concurrent access** - Multiple users/processes safely
- ✅ **Rich querying** - Combine vector search with SQL filters
- ✅ **Metadata indexing** - Fast filtering by document type, date, etc.
- ✅ **Scalability** - Handles millions of vectors efficiently
- ✅ **Cloud-ready** - Deploy anywhere PostgreSQL runs
- ✅ **Better backups** - Standard PostgreSQL backup tools
- ✅ **Monitoring** - Use existing PostgreSQL monitoring tools

## 🛠️ Setup Options

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
python setup_postgresql_vector_db.py
```

This will:
- Install PostgreSQL and pgvector
- Create database and user
- Configure environment variables
- Test the connection
- Create migration scripts

### Option 2: Manual Setup

#### Step 1: Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Step 2: Install pgvector

**macOS:**
```bash
brew install pgvector
```

**Ubuntu/Debian:**
```bash
sudo apt install postgresql-14-pgvector
# OR build from source:
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### Step 3: Create Database and User

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE farming_guide;
CREATE USER farming_bot WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE farming_guide TO farming_bot;
ALTER USER farming_bot CREATEDB;

-- Switch to the new database
\c farming_guide

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant permissions
GRANT ALL ON SCHEMA public TO farming_bot;
```

#### Step 4: Configure Environment

Create `config/postgresql.env`:
```bash
DATABASE_URL=postgresql://farming_bot:your_secure_password@localhost:5432/farming_guide
VECTOR_DB_TYPE=postgresql
VECTOR_DB_TABLE=document_embeddings
VECTOR_DB_DIMENSION=1536
```

### Option 3: Cloud PostgreSQL

You can also use cloud PostgreSQL services:

**Render.com:**
- Create PostgreSQL database
- Enable pgvector extension
- Update DATABASE_URL in config

**AWS RDS:**
- Use PostgreSQL 14+ with pgvector
- Configure security groups
- Update connection string

**Google Cloud SQL:**
- PostgreSQL instance with pgvector
- Configure authorized networks
- Update credentials

## 📊 Database Schema

The PostgreSQL vector database uses this schema:

```sql
-- Main embeddings table
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    embedding vector(1536),
    text_content TEXT NOT NULL,
    metadata JSONB,
    source_document TEXT,
    document_type TEXT DEFAULT 'agricultural_guide',
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metadata table for document tracking
CREATE TABLE document_metadata (
    id SERIAL PRIMARY KEY,
    document_name TEXT UNIQUE NOT NULL,
    file_path TEXT,
    document_type TEXT,
    total_chunks INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX document_embeddings_embedding_idx ON document_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX document_embeddings_source_doc_idx ON document_embeddings (source_document);
CREATE INDEX document_embeddings_doc_type_idx ON document_embeddings (document_type);
CREATE INDEX document_embeddings_metadata_idx ON document_embeddings USING gin (metadata);
```

## 🔄 Migration from FAISS

### Step 1: Test Your Setup

```bash
# Test PostgreSQL vector database
python test_postgresql_vector_db.py
```

### Step 2: Check Migration Status

```bash
# Check if migration is recommended
python -c "
from scripts.data_pipeline.database_migration import DatabaseMigrator
import json
migrator = DatabaseMigrator()
status = migrator.get_migration_status()
print(json.dumps(status, indent=2))
"
```

### Step 3: Perform Migration

```bash
# Run the migration script
python migrate_to_postgresql.py
```

This will:
- ✅ Create backup of FAISS data
- ✅ Re-generate embeddings from text chunks
- ✅ Transfer all vectors to PostgreSQL
- ✅ Verify migration success
- ✅ Preserve metadata and document structure

### Step 4: Update Bot Configuration

Update your bot to use PostgreSQL:

```python
# In your semantic search initialization
from scripts.data_pipeline.postgresql_vector_database import create_vector_database

# Create PostgreSQL vector database instead of FAISS
vector_db = create_vector_database(db_type="postgresql", dimension=1536)
```

## 🔍 Advanced Usage

### Rich Filtering

PostgreSQL allows complex filtering:

```python
# Filter by document type
results = db.search(
    query_embedding,
    top_k=10,
    filter_by_type="agricultural_guide"
)

# Filter by specific document
results = db.search(
    query_embedding,
    top_k=10,
    filter_by_document="Malawi_Groundnut_Guide.pdf"
)

# Complex SQL-based filtering (future enhancement)
# Filter by date range, metadata properties, etc.
```

### Performance Monitoring

```python
# Get database statistics
stats = db.get_database_stats()
print(f"Total vectors: {stats['total_vectors']}")
print(f"Table size: {stats['table_size']}")
print(f"Unique documents: {stats['unique_documents']}")
```

### Backup and Recovery

```bash
# Backup your vector database
pg_dump -h localhost -U farming_bot -d farming_guide > backup.sql

# Restore from backup
psql -h localhost -U farming_bot -d farming_guide < backup.sql
```

## 🎯 Performance Comparison

| Feature | FAISS | PostgreSQL + pgvector |
|---------|-------|----------------------|
| **Setup Complexity** | Low | Medium |
| **Scalability** | Limited | High |
| **Concurrent Access** | No | Yes |
| **Filtering** | Basic | Advanced |
| **Backup/Recovery** | Manual | Automated |
| **Cloud Deployment** | Difficult | Easy |
| **Monitoring** | Limited | Full SQL tools |
| **Search Performance** | Fast | Very Fast |
| **Data Integrity** | None | ACID compliant |

## 📝 Migration Checklist

- [ ] Install PostgreSQL and pgvector
- [ ] Create database and user
- [ ] Configure environment variables
- [ ] Test connection with `test_postgresql_vector_db.py`
- [ ] Run migration with `migrate_to_postgresql.py`
- [ ] Update bot configuration
- [ ] Test bot functionality
- [ ] Monitor performance
- [ ] Setup backup strategy

## 🚨 Troubleshooting

### Common Issues

**1. pgvector extension not found**
```bash
# Install pgvector extension
brew install pgvector  # macOS
sudo apt install postgresql-14-pgvector  # Ubuntu
```

**2. Permission denied**
```sql
-- Grant proper permissions
GRANT ALL ON SCHEMA public TO farming_bot;
GRANT ALL ON ALL TABLES IN SCHEMA public TO farming_bot;
```

**3. Connection refused**
```bash
# Check PostgreSQL is running
brew services start postgresql@14  # macOS
sudo systemctl start postgresql     # Linux
```

**4. Migration fails**
```bash
# Check FAISS data exists
ls -la data/vector_db/

# Verify OpenAI API key for re-embedding
echo $OPENAI_API_KEY
```

### Performance Tuning

```sql
-- Optimize PostgreSQL for vector operations
ALTER SYSTEM SET shared_preload_libraries = 'vector';
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';
```

## 🔗 Additional Resources

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/runtime-config.html)
- [Vector Database Best Practices](https://www.pinecone.io/learn/vector-database/)

## 🎉 Next Steps

After successfully migrating to PostgreSQL:

1. **Monitor Performance** - Use PostgreSQL monitoring tools
2. **Optimize Queries** - Add indexes for common filter patterns
3. **Scale Horizontally** - Consider read replicas for high load
4. **Advanced Features** - Explore full-text search integration
5. **Cloud Deployment** - Move to managed PostgreSQL service

Your Agricultural Advisor Bot now has a production-ready, scalable knowledge base! 🚀 