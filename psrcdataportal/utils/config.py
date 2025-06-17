"""Configuration management for psrcdataportal package."""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from ..exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading and environment variable handling."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """Initialize the configuration manager.
        
        Args:
            config_file: Optional path to custom configuration file.
                        If None, uses default configuration.
        """
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        
        if config_file:
            self._load_custom_config(config_file)
        
        self._apply_environment_overrides()
    
    def _load_default_config(self) -> None:
        """Load the default configuration file."""
        try:
            default_config_path = Path(__file__).parent.parent / "config" / "default.yaml"
            with open(default_config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file) or {}
            logger.debug(f"Loaded default configuration from {default_config_path}")
        except FileNotFoundError:
            raise ConfigurationError(
                "Default configuration file not found",
                f"Expected at: {default_config_path}"
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(
                "Failed to parse default configuration file",
                str(e)
            )
    
    def _load_custom_config(self, config_file: Union[str, Path]) -> None:
        """Load and merge custom configuration file.
        
        Args:
            config_file: Path to custom configuration file.
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise ConfigurationError(
                    f"Custom configuration file not found: {config_path}"
                )
            
            with open(config_path, 'r', encoding='utf-8') as file:
                custom_config = yaml.safe_load(file) or {}
            
            # Deep merge custom config with default config
            self._config = self._deep_merge(self._config, custom_config)
            logger.debug(f"Loaded custom configuration from {config_path}")
            
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse custom configuration file: {config_file}",
                str(e)
            )
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary.
            override: Dictionary to merge into base.
            
        Returns:
            Merged dictionary.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'PSRC_DB_SERVER': ['database', 'server'],
            'PSRC_DB_NAME': ['database', 'name'],
            'PSRC_DB_DRIVER': ['database', 'driver'],
            'PSRC_DB_TIMEOUT': ['database', 'timeout'],
            'PSRC_PORTAL_URL': ['portal', 'default_url'],
            'PSRC_PORTAL_TIMEOUT': ['portal', 'timeout'],
            'PSRC_WORKSPACE_PATH': ['paths', 'workspace'],
            'PSRC_SDE_FOLDER': ['paths', 'sde_folder'],
            'PSRC_SDE_NAME': ['paths', 'sde_name'],
            'PSRC_DEFAULT_SRID': ['spatial', 'default_srid'],
            'PSRC_SDE_INSTANCE': ['spatial', 'sde_instance'],
            'PSRC_SDE_DATABASE': ['spatial', 'sde_database'],
            'PSRC_LOG_LEVEL': ['logging', 'level'],
            'PSRC_LOG_FILE': ['logging', 'file'],
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                if config_path[-1] in ['timeout', 'default_srid']:
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {env_value}")
                        continue
                
                # Set the value in the config
                current = self._config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[config_path[-1]] = env_value
                
                logger.debug(f"Applied environment override: {env_var} -> {'.'.join(config_path)}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration key (e.g., 'database.server').
            default: Default value if key is not found.
            
        Returns:
            Configuration value or default.
        """
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration with environment variable overrides.
        
        Returns:
            Database configuration dictionary.
        """
        config = self.get('database', {}).copy()
        
        # Add environment variables for sensitive data
        if os.getenv('PSRC_DB_SERVER'):
            config['server'] = os.getenv('PSRC_DB_SERVER')
        if os.getenv('PSRC_DB_NAME'):
            config['name'] = os.getenv('PSRC_DB_NAME')
        
        return config
    
    def get_portal_config(self) -> Dict[str, Any]:
        """Get portal configuration with environment variable overrides.
        
        Returns:
            Portal configuration dictionary.
        """
        config = self.get('portal', {}).copy()
        
        # Add environment variables for sensitive data
        if os.getenv('PSRC_PORTAL_USERNAME'):
            config['username'] = os.getenv('PSRC_PORTAL_USERNAME')
        if os.getenv('PSRC_PORTAL_PASSWORD'):
            config['password'] = os.getenv('PSRC_PORTAL_PASSWORD')
        if os.getenv('PSRC_PORTAL_URL'):
            config['url'] = os.getenv('PSRC_PORTAL_URL')
        else:
            config['url'] = config.get('default_url')
        
        return config
    
    def validate_required_env_vars(self) -> None:
        """Validate that required environment variables are set.
        
        Raises:
            ConfigurationError: If required environment variables are missing.
        """
        required_vars = [
            'PSRC_DB_SERVER',
            'PSRC_DB_NAME',
            'PSRC_PORTAL_USERNAME',
            'PSRC_PORTAL_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ConfigurationError(
                "Required environment variables are missing",
                f"Missing: {', '.join(missing_vars)}"
            )
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary.
        
        Returns:
            Complete configuration dictionary.
        """
        return self._config.copy()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[Union[str, Path]] = None) -> ConfigManager:
    """Get the global configuration manager instance.
    
    Args:
        config_file: Optional path to custom configuration file.
        
    Returns:
        ConfigManager instance.
    """
    global _config_manager
    
    if _config_manager is None or config_file is not None:
        _config_manager = ConfigManager(config_file)
    
    return _config_manager


def get_config(key_path: str, default: Any = None) -> Any:
    """Get a configuration value using the global config manager.
    
    Args:
        key_path: Dot-separated path to the configuration key.
        default: Default value if key is not found.
        
    Returns:
        Configuration value or default.
    """
    return get_config_manager().get(key_path, default)
