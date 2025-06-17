"""PSRC Data Portal - Tools to export tables and spatial layers to ArcGIS Online Data Portal.

This package provides a clean, modern interface for exporting data from PSRC databases
to ArcGIS Online/Portal for ArcGIS. It includes support for both tabular and spatial data,
comprehensive metadata management, and flexible configuration options.

Example:
    Basic usage with environment variables:
    
    >>> import psrcdataportal as psrc
    >>> 
    >>> # Create connectors (uses environment variables for credentials)
    >>> db_conn = psrc.create_database_connector()
    >>> portal_conn = psrc.create_portal_connector()
    >>> 
    >>> # Define resource parameters
    >>> params = {
    ...     'title': 'My Dataset',
    ...     'tags': 'transportation,planning',
    ...     'share_level': 'org',
    ...     'spatial_data': False
    ... }
    >>> 
    >>> # Define data source
    >>> source = {
    ...     'table_name': 'my_table',
    ...     'is_simple': True
    ... }
    >>> 
    >>> # Create and export resource
    >>> resource = psrc.create_portal_resource(portal_conn, db_conn, params, source)
    >>> resource.export()
"""

import logging
from typing import Dict, Any, Optional

from .version import __version__, __author__, __email__, __description__
from .core import DatabaseConnector, PortalConnector, PortalResource
from .exceptions import (
    PSRCDataPortalError,
    DatabaseConnectionError,
    PortalConnectionError,
    ConfigurationError,
    DataExportError,
    SpatialDataError,
    MetadataError,
    ValidationError
)
from .utils.config import get_config_manager

# Set up logging
logger = logging.getLogger(__name__)


def create_database_connector(
    server: Optional[str] = None,
    database: Optional[str] = None,
    driver: Optional[str] = None,
    trusted_connection: bool = True,
    timeout: Optional[int] = None
) -> DatabaseConnector:
    """Create a database connector with configuration management.
    
    This factory function creates a DatabaseConnector instance with automatic
    configuration loading from environment variables and config files.
    
    Args:
        server: Database server name. If None, uses PSRC_DB_SERVER environment variable.
        database: Database name. If None, uses PSRC_DB_NAME environment variable.
        driver: ODBC driver name. If None, uses configuration default.
        trusted_connection: Whether to use Windows authentication.
        timeout: Connection timeout in seconds.
        
    Returns:
        Configured DatabaseConnector instance.
        
    Raises:
        DatabaseConnectionError: If connection parameters are invalid or connection fails.
        ConfigurationError: If required configuration is missing.
        
    Example:
        >>> # Using environment variables
        >>> db_conn = create_database_connector()
        >>> 
        >>> # With explicit parameters
        >>> db_conn = create_database_connector(
        ...     server='myserver',
        ...     database='mydatabase'
        ... )
    """
    try:
        return DatabaseConnector(
            server=server,
            database=database,
            driver=driver,
            trusted_connection=trusted_connection,
            timeout=timeout
        )
    except Exception as e:
        logger.error(f"Failed to create database connector: {str(e)}")
        raise


def create_portal_connector(
    username: Optional[str] = None,
    password: Optional[str] = None,
    url: Optional[str] = None,
    timeout: Optional[int] = None
) -> PortalConnector:
    """Create a portal connector with configuration management.
    
    This factory function creates a PortalConnector instance with automatic
    configuration loading from environment variables and config files.
    
    Args:
        username: Portal username. If None, uses PSRC_PORTAL_USERNAME environment variable.
        password: Portal password. If None, uses PSRC_PORTAL_PASSWORD environment variable.
        url: Portal URL. If None, uses PSRC_PORTAL_URL environment variable or config default.
        timeout: Connection timeout in seconds.
        
    Returns:
        Configured PortalConnector instance.
        
    Raises:
        PortalConnectionError: If connection parameters are invalid or connection fails.
        ConfigurationError: If required configuration is missing.
        
    Example:
        >>> # Using environment variables
        >>> portal_conn = create_portal_connector()
        >>> 
        >>> # With explicit parameters
        >>> portal_conn = create_portal_connector(
        ...     username='myuser',
        ...     password='mypass',
        ...     url='https://myorg.maps.arcgis.com'
        ... )
    """
    try:
        return PortalConnector(
            username=username,
            password=password,
            url=url,
            timeout=timeout
        )
    except Exception as e:
        logger.error(f"Failed to create portal connector: {str(e)}")
        raise


def create_portal_resource(
    portal_connector: PortalConnector,
    database_connector: DatabaseConnector,
    params: Dict[str, Any],
    source: Dict[str, Any]
) -> PortalResource:
    """Create a portal resource for data export.
    
    This factory function creates a PortalResource instance that can export
    data from a database to ArcGIS Online/Portal for ArcGIS.
    
    Args:
        portal_connector: Configured PortalConnector instance.
        database_connector: Configured DatabaseConnector instance.
        params: Resource parameters dictionary containing:
            - title (str): Resource title
            - tags (str or list): Tags for the resource
            - share_level (str, optional): 'everyone', 'org', or 'private'
            - spatial_data (bool, optional): Whether this is spatial data
            - allow_edits (bool, optional): Whether to allow editing
            - groups (str or list, optional): Groups to share with
            - snippet (str, optional): Resource description
            - licenseInfo (str, optional): License information
            - srid (int, optional): Spatial reference ID for spatial data
            - metadata (dict, optional): Metadata dictionary
        source: Source configuration dictionary containing:
            - table_name (str): Database table/view name
            - is_simple (bool): Whether to use simple table export
            - schema (str, optional): Database schema name
            - feature_dataset (str, optional): Feature dataset for spatial data
            - fields_to_exclude (str or list, optional): Fields to exclude
            - sql_query (str, optional): Custom SQL query
            
    Returns:
        Configured PortalResource instance.
        
    Raises:
        DataExportError: If resource creation fails.
        ValidationError: If parameters or source configuration is invalid.
        
    Example:
        >>> params = {
        ...     'title': 'Transportation Data',
        ...     'tags': ['transportation', 'planning'],
        ...     'share_level': 'org',
        ...     'spatial_data': True,
        ...     'metadata': {
        ...         'contact_name': 'John Doe',
        ...         'contact_email': 'john.doe@psrc.org',
        ...         'organization_name': 'PSRC'
        ...     }
        ... }
        >>> 
        >>> source = {
        ...     'table_name': 'transportation_network',
        ...     'feature_dataset': 'Transportation',
        ...     'is_simple': True
        ... }
        >>> 
        >>> resource = create_portal_resource(portal_conn, db_conn, params, source)
        >>> resource.export()
    """
    try:
        return PortalResource(
            portal_connector=portal_connector,
            database_connector=database_connector,
            params=params,
            source=source
        )
    except Exception as e:
        logger.error(f"Failed to create portal resource: {str(e)}")
        raise


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """Set up logging for the package.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        format_string: Custom format string for log messages.
    """
    try:
        config_manager = get_config_manager()
        
        # Get logging configuration
        log_level = level or config_manager.get('logging.level', 'INFO')
        log_format = format_string or config_manager.get(
            'logging.format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        log_file = config_manager.get('logging.file')
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            filename=log_file
        )
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")
        
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(level=logging.INFO)
        logger.warning(f"Failed to configure logging from config: {str(e)}")


def validate_environment() -> bool:
    """Validate that required environment variables are set.
    
    Returns:
        True if all required environment variables are present, False otherwise.
        
    Example:
        >>> if not psrc.validate_environment():
        ...     print("Please set required environment variables")
        ...     # Set PSRC_DB_SERVER, PSRC_DB_NAME, PSRC_PORTAL_USERNAME, PSRC_PORTAL_PASSWORD
    """
    try:
        config_manager = get_config_manager()
        config_manager.validate_required_env_vars()
        return True
    except ConfigurationError as e:
        logger.warning(f"Environment validation failed: {str(e)}")
        return False


# Package metadata
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    
    # Factory functions
    'create_database_connector',
    'create_portal_connector',
    'create_portal_resource',
    
    # Utility functions
    'setup_logging',
    'validate_environment',
    
    # Core classes (for advanced usage)
    'DatabaseConnector',
    'PortalConnector',
    'PortalResource',
    
    # Exceptions
    'PSRCDataPortalError',
    'DatabaseConnectionError',
    'PortalConnectionError',
    'ConfigurationError',
    'DataExportError',
    'SpatialDataError',
    'MetadataError',
    'ValidationError',
]

# Initialize logging on import
setup_logging()
