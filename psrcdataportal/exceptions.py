"""Custom exceptions for psrcdataportal package."""

from typing import Optional


class PSRCDataPortalError(Exception):
    """Base exception class for psrcdataportal package."""
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize the exception.
        
        Args:
            message: The error message.
            details: Optional additional details about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class DatabaseConnectionError(PSRCDataPortalError):
    """Exception raised when database connection fails."""
    pass


class PortalConnectionError(PSRCDataPortalError):
    """Exception raised when portal connection fails."""
    pass


class ConfigurationError(PSRCDataPortalError):
    """Exception raised when configuration is invalid or missing."""
    pass


class DataExportError(PSRCDataPortalError):
    """Exception raised when data export fails."""
    pass


class SpatialDataError(PSRCDataPortalError):
    """Exception raised when spatial data processing fails."""
    pass


class MetadataError(PSRCDataPortalError):
    """Exception raised when metadata processing fails."""
    pass


class ValidationError(PSRCDataPortalError):
    """Exception raised when data validation fails."""
    pass
