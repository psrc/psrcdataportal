"""Database connection management for psrcdataportal package."""

import logging
from typing import Optional

import sqlalchemy
try:
    from sqlalchemy import Engine
except ImportError:
    from sqlalchemy.engine import Engine

from ..exceptions import DatabaseConnectionError
from ..utils.config import get_config_manager

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Manages database connections to PSRC SQL Server databases."""
    
    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        driver: Optional[str] = None,
        trusted_connection: bool = True,
        timeout: Optional[int] = None
    ) -> None:
        """Initialize the database connector.
        
        Args:
            server: Database server name. If None, uses configuration or environment variable.
            database: Database name. If None, uses configuration or environment variable.
            driver: ODBC driver name. If None, uses configuration default.
            trusted_connection: Whether to use Windows authentication.
            timeout: Connection timeout in seconds.
            
        Raises:
            DatabaseConnectionError: If connection parameters are invalid or connection fails.
        """
        self._config_manager = get_config_manager()
        self._engine: Optional[Engine] = None
        
        # Get configuration values
        db_config = self._config_manager.get_database_config()
        
        self.server = server or db_config.get('server')
        self.database = database or db_config.get('name')
        self.driver = driver or db_config.get('driver', 'ODBC Driver 17 for SQL Server')
        self.trusted_connection = trusted_connection
        self.timeout = timeout or db_config.get('timeout', 30)
        
        # Validate required parameters
        if not self.server:
            raise DatabaseConnectionError(
                "Database server not specified",
                "Set PSRC_DB_SERVER environment variable or provide server parameter"
            )
        
        if not self.database:
            raise DatabaseConnectionError(
                "Database name not specified",
                "Set PSRC_DB_NAME environment variable or provide database parameter"
            )
        
        # Establish connection
        self._connect()
        
        logger.info(f"Database connector initialized for {self.server}/{self.database}")
    
    def _connect(self) -> None:
        """Establish database connection.
        
        Raises:
            DatabaseConnectionError: If connection fails.
        """
        try:
            if self.trusted_connection:
                conn_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"trusted_connection=yes;"
                    f"Connection Timeout={self.timeout}"
                )
            else:
                # For future support of username/password authentication
                conn_string = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"Connection Timeout={self.timeout}"
                )
            
            engine_url = f"mssql+pyodbc:///?odbc_connect={conn_string}"
            self._engine = sqlalchemy.create_engine(
                engine_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Test the connection
            with self._engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            
            logger.debug(f"Successfully connected to {self.server}/{self.database}")
            
        except Exception as e:
            error_msg = f"Failed to connect to database {self.server}/{self.database}"
            logger.error(f"{error_msg}: {str(e)}")
            raise DatabaseConnectionError(error_msg, str(e))
    
    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine.
        
        Returns:
            SQLAlchemy Engine instance.
            
        Raises:
            DatabaseConnectionError: If not connected.
        """
        if self._engine is None:
            raise DatabaseConnectionError("Database not connected")
        return self._engine
    
    @property
    def sql_conn(self) -> Engine:
        """Get the SQL connection (alias for engine for backward compatibility).
        
        Returns:
            SQLAlchemy Engine instance.
        """
        return self.engine
    
    def test_connection(self) -> bool:
        """Test the database connection.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Database connection test failed: {str(e)}")
            return False
    
    def reconnect(self) -> None:
        """Reconnect to the database.
        
        Raises:
            DatabaseConnectionError: If reconnection fails.
        """
        logger.info("Reconnecting to database...")
        if self._engine:
            self._engine.dispose()
        self._connect()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.debug("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation of the connector."""
        return f"DatabaseConnector(server='{self.server}', database='{self.database}')"
