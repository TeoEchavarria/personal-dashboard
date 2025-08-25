"""
Configuration Management Module
Centralized configuration handling for the dashboard application.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration manager."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
        self._env_config = self._load_env_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error loading config file: {e}")
            return {}
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            # Health Connect Gateway Configuration
            'hcg': {
                'base_url': os.getenv("HCG_BASE_URL", "https://api.hcgateway.shuchir.dev").rstrip("/"),
                'username': os.getenv("HCG_USERNAME"),
                'password': os.getenv("HCG_PASSWORD"),
                'tick_seconds': int(os.getenv("TICK_SECONDS", "180")),
                'methods_mode': os.getenv("METHODS", "CORE").upper()
            },
            
            # Application Settings
            'app': {
                'name': os.getenv("APP_NAME", "Personal Dashboard"),
                'version': os.getenv("APP_VERSION", "1.0.0"),
                'debug': os.getenv("DEBUG", "False").lower() == "true",
                'port': int(os.getenv("PORT", "8501"))
            },
            
            # Data Settings
            'data': {
                'directory': os.getenv("DATA_DIRECTORY", "data/"),
                'state_directory': os.getenv("STATE_DIRECTORY", "state/")
            },
            
            # API Settings
            'api': {
                'timeout': int(os.getenv("API_TIMEOUT", "30")),
                'retry_attempts': int(os.getenv("API_RETRY_ATTEMPTS", "3"))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'hcg.base_url')."""
        keys = key.split('.')
        value = self._env_config
        
        # First try environment config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        
        if value is not None:
            return value
        
        # Fallback to YAML config
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_hcg_config(self) -> Dict[str, Any]:
        """Get Health Connect Gateway specific configuration."""
        return {
            'base_url': self.get('hcg.base_url'),
            'username': self.get('hcg.username'),
            'password': self.get('hcg.password'),
            'tick_seconds': self.get('hcg.tick_seconds'),
            'methods_mode': self.get('hcg.methods_mode')
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application specific configuration."""
        return {
            'name': self.get('app.name'),
            'version': self.get('app.version'),
            'debug': self.get('app.debug'),
            'port': self.get('app.port')
        }
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data specific configuration."""
        return {
            'directory': self.get('data.directory'),
            'state_directory': self.get('data.state_directory')
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API specific configuration."""
        return {
            'timeout': self.get('api.timeout'),
            'retry_attempts': self.get('api.retry_attempts')
        }
    
    def get_hcg_methods(self) -> List[str]:
        """Get the list of methods to collect based on configuration."""
        methods_mode = self.get('hcg.methods_mode', 'CORE')
        
        if methods_mode == 'ALL':
            return self.get('health_connect.all_methods', [])
        else:
            return self.get('health_connect.core_methods', [])
    
    def get_hcg_core_methods(self) -> List[str]:
        """Get core methods list."""
        return self.get('health_connect.core_methods', [])
    
    def get_hcg_all_methods(self) -> List[str]:
        """Get all methods list."""
        return self.get('health_connect.all_methods', [])
    
    def validate_hcg_config(self) -> bool:
        """Validate that required HCG configuration is present."""
        config = self.get_hcg_config()
        required_fields = ['username', 'password']
        
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            print(f"Missing required HCG configuration: {missing_fields}")
            return False
        
        return True

# Global configuration instance
config = Config()
