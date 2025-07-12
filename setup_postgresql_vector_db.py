#!/usr/bin/env python3
"""
PostgreSQL Vector Database Setup Script
Sets up PostgreSQL with pgvector extension for the Agricultural Advisor Bot.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import json


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_step(step: str):
    """Print formatted step."""
    print(f"\n🔧 {step}")


def run_command(command: str, check: bool = True) -> bool:
    """Run shell command and return success status."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"   Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Command failed: {command}")
        print(f"   Error: {e}")
        return False


def install_python_dependencies():
    """Install required Python packages."""
    print_step("Installing Python dependencies...")
    
    dependencies = [
        "psycopg2-binary",  # PostgreSQL adapter
        "numpy",           # Already installed but needed for pgvector
        "sqlalchemy",      # Optional ORM support
        "asyncpg"          # Async PostgreSQL support
    ]
    
    for dep in dependencies:
        print(f"  Installing {dep}...")
        if not run_command(f"pip install {dep}"):
            return False
    
    print("✅ Python dependencies installed successfully")
    return True


def setup_postgresql_macos():
    """Setup PostgreSQL on macOS."""
    print_step("Setting up PostgreSQL on macOS...")
    
    # Check if Homebrew is installed
    if not run_command("which brew", check=False):
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    # Install PostgreSQL
    print("  Installing PostgreSQL...")
    if not run_command("brew install postgresql@14"):
        return False
    
    # Start PostgreSQL service
    print("  Starting PostgreSQL service...")
    if not run_command("brew services start postgresql@14"):
        return False
    
    print("✅ PostgreSQL installed and started")
    return True


def setup_postgresql_linux():
    """Setup PostgreSQL on Linux."""
    print_step("Setting up PostgreSQL on Linux...")
    
    # Detect Linux distribution
    if Path("/etc/ubuntu-release").exists() or Path("/etc/debian_version").exists():
        # Ubuntu/Debian
        print("  Installing PostgreSQL on Ubuntu/Debian...")
        commands = [
            "sudo apt update",
            "sudo apt install -y postgresql postgresql-contrib",
            "sudo systemctl start postgresql",
            "sudo systemctl enable postgresql"
        ]
    elif Path("/etc/redhat-release").exists():
        # CentOS/RHEL
        print("  Installing PostgreSQL on CentOS/RHEL...")
        commands = [
            "sudo yum install -y postgresql postgresql-server",
            "sudo postgresql-setup initdb",
            "sudo systemctl start postgresql",
            "sudo systemctl enable postgresql"
        ]
    else:
        print("❌ Unsupported Linux distribution")
        return False
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print("✅ PostgreSQL installed and started")
    return True


def install_pgvector():
    """Install pgvector extension."""
    print_step("Installing pgvector extension...")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("  Installing pgvector on macOS...")
        if not run_command("brew install pgvector"):
            return False
    elif system == "linux":
        print("  Installing pgvector on Linux...")
        # Try to install from package manager first
        if not run_command("sudo apt install -y postgresql-14-pgvector", check=False):
            # If not available, build from source
            print("  Building pgvector from source...")
            commands = [
                "git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector",
                "cd /tmp/pgvector && make",
                "cd /tmp/pgvector && sudo make install"
            ]
            for cmd in commands:
                if not run_command(cmd):
                    return False
    else:
        print("❌ Unsupported operating system")
        return False
    
    print("✅ pgvector extension installed")
    return True


def create_database_and_user():
    """Create database and user for the application."""
    print_step("Creating database and user...")
    
    # Database configuration
    db_config = {
        "database": "farming_guide",
        "user": "farming_bot",
        "password": "secure_password_123"  # Change this!
    }
    
    # Create database and user
    sql_commands = [
        f"CREATE DATABASE {db_config['database']};",
        f"CREATE USER {db_config['user']} WITH ENCRYPTED PASSWORD '{db_config['password']}';",
        f"GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['user']};",
        f"ALTER USER {db_config['user']} CREATEDB;",
        f"\\c {db_config['database']}",
        f"CREATE EXTENSION IF NOT EXISTS vector;",
        f"GRANT ALL ON SCHEMA public TO {db_config['user']};"
    ]
    
    # Write SQL commands to temporary file
    sql_file = Path("/tmp/setup_farming_db.sql")
    with open(sql_file, "w") as f:
        f.write("\n".join(sql_commands))
    
    # Execute SQL commands
    print("  Creating database and user...")
    if not run_command(f"sudo -u postgres psql -f {sql_file}"):
        return False
    
    # Clean up
    sql_file.unlink()
    
    print("✅ Database and user created successfully")
    return True, db_config


def create_config_file(db_config: Dict[str, str]):
    """Create configuration file for PostgreSQL."""
    print_step("Creating configuration file...")
    
    config_content = f"""# PostgreSQL Configuration for Agricultural Advisor Bot
# Generated by setup script

# Database connection (choose one method)
DATABASE_URL=postgresql://{db_config['user']}:{db_config['password']}@localhost:5432/{db_config['database']}

# Alternative individual parameters
DB_HOST=localhost
DB_PORT=5432
DB_NAME={db_config['database']}
DB_USER={db_config['user']}
DB_PASSWORD={db_config['password']}

# Vector database settings
VECTOR_DB_TYPE=postgresql
VECTOR_DB_TABLE=document_embeddings
VECTOR_DB_DIMENSION=1536
"""
    
    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Write configuration
    config_file = config_dir / "postgresql.env"
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print(f"✅ Configuration file created: {config_file}")
    return True


def test_postgresql_connection(db_config: Dict[str, str]) -> bool:
    """Test PostgreSQL connection."""
    print_step("Testing PostgreSQL connection...")
    
    try:
        # Create a simple test script
        test_script = f"""
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='{db_config['database']}',
        user='{db_config['user']}',
        password='{db_config['password']}'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f"✅ PostgreSQL connection successful: {{version[0]}}")
    
    # Test pgvector
    cursor.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    cursor.execute('SELECT extversion FROM pg_extension WHERE extname = \\'vector\\';')
    vector_version = cursor.fetchone()
    if vector_version:
        print(f"✅ pgvector extension available: v{{vector_version[0]}}")
    else:
        print("❌ pgvector extension not found")
        
    conn.close()
    print("✅ Database connection test passed")
except Exception as e:
    print(f"❌ Database connection test failed: {{e}}")
"""
        
        # Write and execute test script
        test_file = Path("/tmp/test_pg_connection.py")
        with open(test_file, "w") as f:
            f.write(test_script)
        
        result = run_command(f"python {test_file}")
        test_file.unlink()
        
        return result
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def create_migration_example():
    """Create example migration script."""
    print_step("Creating migration example...")
    
    example_script = '''#!/usr/bin/env python3
"""
Example: Migrate from FAISS to PostgreSQL
Run this script to migrate your existing FAISS knowledge base to PostgreSQL.
"""

from scripts.data_pipeline.database_migration import DatabaseMigrator
import json

def main():
    print("🚀 Starting FAISS to PostgreSQL migration...")
    
    # Initialize migrator
    migrator = DatabaseMigrator()
    
    # Check current status
    status = migrator.get_migration_status()
    print("\\nCurrent Status:")
    print(json.dumps(status, indent=2))
    
    # Perform migration if recommended
    if status.get('migration_recommended', False):
        print("\\n🔄 Migration recommended. Starting migration...")
        
        success = migrator.migrate_faiss_to_postgresql()
        
        if success:
            print("\\n✅ Migration completed successfully!")
            print("   Your knowledge base is now running on PostgreSQL")
            print("   Your FAISS data has been backed up for safety")
        else:
            print("\\n❌ Migration failed!")
            print("   Check the logs for details")
            print("   Your original FAISS data is still intact")
    else:
        print("\\n📋 No migration needed at this time")
    
    print("\\n🎯 Next steps:")
    print("   1. Update your configuration to use PostgreSQL")
    print("   2. Test your bot with the new database")
    print("   3. Monitor performance and storage usage")

if __name__ == "__main__":
    main()
'''
    
    # Write example script
    example_file = Path("migrate_to_postgresql.py")
    with open(example_file, "w") as f:
        f.write(example_script)
    
    # Make it executable
    os.chmod(example_file, 0o755)
    
    print(f"✅ Migration example created: {example_file}")
    return True


def main():
    """Main setup function."""
    print_header("PostgreSQL Vector Database Setup")
    print("Setting up PostgreSQL with pgvector for Agricultural Advisor Bot")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        sys.exit(1)
    
    # Detect operating system
    system = platform.system().lower()
    print(f"📋 Detected OS: {system}")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Setup PostgreSQL based on OS
    if system == "darwin":
        if not setup_postgresql_macos():
            print("❌ Failed to setup PostgreSQL on macOS")
            sys.exit(1)
    elif system == "linux":
        if not setup_postgresql_linux():
            print("❌ Failed to setup PostgreSQL on Linux")
            sys.exit(1)
    else:
        print("❌ Unsupported operating system")
        sys.exit(1)
    
    # Install pgvector
    if not install_pgvector():
        print("❌ Failed to install pgvector")
        sys.exit(1)
    
    # Create database and user
    success, db_config = create_database_and_user()
    if not success:
        print("❌ Failed to create database and user")
        sys.exit(1)
    
    # Create configuration file
    if not create_config_file(db_config):
        print("❌ Failed to create configuration file")
        sys.exit(1)
    
    # Test connection
    if not test_postgresql_connection(db_config):
        print("❌ Database connection test failed")
        sys.exit(1)
    
    # Create migration example
    if not create_migration_example():
        print("❌ Failed to create migration example")
        sys.exit(1)
    
    # Success message
    print_header("Setup Complete!")
    print("✅ PostgreSQL with pgvector is now ready for use!")
    print("\n🎯 Next Steps:")
    print("   1. Review and update config/postgresql.env with your credentials")
    print("   2. Run 'python migrate_to_postgresql.py' to migrate from FAISS")
    print("   3. Update your bot configuration to use PostgreSQL")
    print("   4. Test your bot with the new database")
    
    print("\n📊 Benefits of PostgreSQL:")
    print("   • Production-ready with ACID compliance")
    print("   • Concurrent access and better performance")
    print("   • Rich querying with SQL filters")
    print("   • Better backup and recovery options")
    print("   • Scalable for future growth")
    
    print(f"\n🔐 Database Credentials:")
    print(f"   Database: {db_config['database']}")
    print(f"   User: {db_config['user']}")
    print(f"   Password: {db_config['password']}")
    print("   ⚠️  Change the password in config/postgresql.env!")


if __name__ == "__main__":
    main() 