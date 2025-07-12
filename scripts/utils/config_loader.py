"""
Configuration loader for the Agricultural Advisor Bot.
Loads environment variables from .env files in the config directory.
"""
import os
from pathlib import Path
from typing import Optional

class ConfigLoader:
    """Loads configuration from environment variables and .env files."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._load_env_files()
    
    def _load_env_files(self):
        """Load all .env files from config directory."""
        for env_file in self.config_dir.glob("*.env"):
            self._load_env_file(env_file)
    
    def _load_env_file(self, env_file: Path):
        """Load a single .env file."""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Warning: {env_file} not found")
        except Exception as e:
            print(f"Error loading {env_file}: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value."""
        return os.environ.get(key, default)
    
    def get_optional(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get optional environment variable value (alias for get method)."""
        return self.get(key, default)
    
    def get_required(self, key: str) -> str:
        """Get required environment variable, raise error if not found."""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} not found")
        return value
    
    def create_template_env_files(self):
        """Create template .env files if they don't exist."""
        templates = {
            "telegram_token.env": "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here",
            "openai_key.env": "OPENAI_API_KEY=your_openai_api_key_here",
            "weather_api.env": "OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here",
            "database.env": "DATABASE_URL=postgresql://user:password@localhost/farming_guide"
        }
        
        for filename, content in templates.items():
            env_file = self.config_dir / filename
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    f.write(content + '\n')
                print(f"Created template: {env_file}")


# Global config instance
config = ConfigLoader() 