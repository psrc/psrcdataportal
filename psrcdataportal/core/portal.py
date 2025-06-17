"""Portal connection management for psrcdataportal package."""

import logging
from typing import List, Optional, Union

from arcgis.gis import GIS
from arcgis.gis import Item

from ..exceptions import PortalConnectionError
from ..utils.config import get_config_manager

logger = logging.getLogger(__name__)


class PortalConnector:
    """Manages connections to ArcGIS Online/Portal for ArcGIS."""
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> None:
        """Initialize the portal connector.
        
        Args:
            username: Portal username. If None, uses PSRC_PORTAL_USERNAME environment variable.
            password: Portal password. If None, uses PSRC_PORTAL_PASSWORD environment variable.
            url: Portal URL. If None, uses configuration or PSRC_PORTAL_URL environment variable.
            timeout: Connection timeout in seconds.
            
        Raises:
            PortalConnectionError: If connection parameters are invalid or connection fails.
        """
        self._config_manager = get_config_manager()
        self._gis: Optional[GIS] = None
        
        # Get configuration values
        portal_config = self._config_manager.get_portal_config()
        
        self.username = username or portal_config.get('username')
        self.password = password or portal_config.get('password')
        self._portal_url = url or portal_config.get('url')
        self.timeout = timeout or portal_config.get('timeout', 60)
        
        # Validate required parameters
        if not self.username:
            raise PortalConnectionError(
                "Portal username not specified",
                "Set PSRC_PORTAL_USERNAME environment variable or provide username parameter"
            )
        
        if not self.password:
            raise PortalConnectionError(
                "Portal password not specified",
                "Set PSRC_PORTAL_PASSWORD environment variable or provide password parameter"
            )
        
        if not self._portal_url:
            raise PortalConnectionError(
                "Portal URL not specified",
                "Set PSRC_PORTAL_URL environment variable or provide url parameter"
            )
        
        # Establish connection
        self._connect()
        
        logger.info(f"Portal connector initialized for {self._portal_url}")
    
    @property
    def portal_url(self) -> str:
        """Get the portal URL.
        
        Returns:
            Portal URL string.
        """
        return self._portal_url
    
    @portal_url.setter
    def portal_url(self, value: str) -> None:
        """Set the portal URL.
        
        Args:
            value: New portal URL.
        """
        self._portal_url = value
    
    def _connect(self) -> None:
        """Establish portal connection.
        
        Raises:
            PortalConnectionError: If connection fails.
        """
        try:
            self._gis = GIS(
                url=self._portal_url,
                username=self.username,
                password=self.password
            )
            
            # Test the connection by accessing user info
            user_info = self._gis.users.me
            logger.debug(f"Successfully connected to portal as {user_info.username}")
            
        except Exception as e:
            error_msg = f"Failed to connect to portal {self._portal_url}"
            logger.error(f"{error_msg}: {str(e)}")
            raise PortalConnectionError(error_msg, str(e))
    
    @property
    def gis(self) -> GIS:
        """Get the ArcGIS GIS instance.
        
        Returns:
            ArcGIS GIS instance.
            
        Raises:
            PortalConnectionError: If not connected.
        """
        if self._gis is None:
            raise PortalConnectionError("Portal not connected")
        return self._gis
    
    def test_connection(self) -> bool:
        """Test the portal connection.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            user_info = self.gis.users.me
            return user_info is not None
        except Exception as e:
            logger.warning(f"Portal connection test failed: {str(e)}")
            return False
    
    def reconnect(self) -> None:
        """Reconnect to the portal.
        
        Raises:
            PortalConnectionError: If reconnection fails.
        """
        logger.info("Reconnecting to portal...")
        self._gis = None
        self._connect()
    
    def find_by_title(self, title: str, item_type: Optional[str] = None) -> Union[Item, str]:
        """Find a feature layer or service on the portal by title.
        
        Searches among only those items that are owned by the authenticated portal user.
        
        Args:
            title: The title of the item to search for.
            item_type: Optional item type filter (e.g., 'Feature Service', 'CSV').
            
        Returns:
            The found Item object, or "no object" if no item is found.
            
        Raises:
            PortalConnectionError: If search fails.
        """
        try:
            gis = self.gis
            owner_clause = f'; owner:{gis.users.me.username}'
            
            # Build search query
            query_parts = [f'title:{title}']
            if item_type:
                query_parts.append(f'type:{item_type}')
            query_parts.append(owner_clause)
            
            query = ''.join(query_parts)
            
            content_list = gis.content.search(query=query)
            
            for item in content_list:
                if item['title'] == title:
                    if item_type is None or item_type in item['type']:
                        logger.debug(f"Found item: {title} ({item['type']})")
                        return item
            
            logger.debug(f"No item found with title: {title}")
            return "no object"
            
        except Exception as e:
            error_msg = f"Failed to search for item '{title}'"
            logger.error(f"{error_msg}: {str(e)}")
            raise PortalConnectionError(error_msg, str(e))
    
    def find_feature_layer_by_title(self, title: str) -> Union[Item, str]:
        """Find a feature layer on the portal by title.
        
        Args:
            title: The title of the feature layer to search for.
            
        Returns:
            The found Item object, or "no object" if no feature layer is found.
        """
        try:
            gis = self.gis
            owner_clause = f'; owner:{gis.users.me.username}'
            query = f'title:{title}{owner_clause}'
            
            content_list = gis.content.search(query=query)
            
            for item in content_list:
                if (item['title'] == title and 'Feature' in item['type']):
                    logger.debug(f"Found feature layer: {title}")
                    return item
            
            logger.debug(f"No feature layer found with title: {title}")
            return "no object"
            
        except Exception as e:
            error_msg = f"Failed to search for feature layer '{title}'"
            logger.error(f"{error_msg}: {str(e)}")
            raise PortalConnectionError(error_msg, str(e))
    
    def get_user_groups(self) -> List[str]:
        """Get list of groups that the current user belongs to.
        
        Returns:
            List of group titles.
            
        Raises:
            PortalConnectionError: If unable to retrieve groups.
        """
        try:
            gis = self.gis
            user_groups = gis.users.me.groups
            group_titles = [group.title for group in user_groups]
            logger.debug(f"User belongs to {len(group_titles)} groups")
            return group_titles
            
        except Exception as e:
            error_msg = "Failed to retrieve user groups"
            logger.error(f"{error_msg}: {str(e)}")
            raise PortalConnectionError(error_msg, str(e))
    
    def get_group_ids_by_titles(self, group_titles: List[str]) -> List[str]:
        """Get group IDs for the specified group titles.
        
        Args:
            group_titles: List of group titles to find IDs for.
            
        Returns:
            List of group IDs.
            
        Raises:
            PortalConnectionError: If unable to retrieve group IDs.
        """
        try:
            gis = self.gis
            group_ids = []
            
            for group in gis.groups.search(query=""):
                if group.title in group_titles:
                    group_ids.append(group.id)
                    logger.debug(f"Found group ID for '{group.title}': {group.id}")
            
            return group_ids
            
        except Exception as e:
            error_msg = f"Failed to retrieve group IDs for: {group_titles}"
            logger.error(f"{error_msg}: {str(e)}")
            raise PortalConnectionError(error_msg, str(e))
    
    def close(self) -> None:
        """Close the portal connection."""
        if self._gis:
            # ArcGIS Python API doesn't have explicit close method
            self._gis = None
            logger.debug("Portal connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation of the connector."""
        return f"PortalConnector(url='{self._portal_url}', username='{self.username}')"
