"""Portal resource export functionality for psrcdataportal package."""

import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import geopandas as gpd
from arcgis.features import FeatureLayerCollection
from arcgis.gis._impl._content_manager import SharingLevel

from ..exceptions import DataExportError, SpatialDataError
from ..utils.config import get_config_manager
from ..utils.metadata import MetadataManager, build_field_mappings
from ..utils.spatial import (
    create_geodataframe_from_wkt,
    simplify_geodataframe,
    validate_spatial_reference
)
from ..utils.validation import (
    validate_resource_parameters,
    validate_source_config,
    validate_metadata_dict,
    validate_dataframe
)
from .database import DatabaseConnector
from .portal import PortalConnector

logger = logging.getLogger(__name__)


class PortalResource:
    """A publishable resource for ArcGIS Online/Portal."""
    
    def __init__(
        self,
        portal_connector: PortalConnector,
        database_connector: DatabaseConnector,
        params: Dict[str, Any],
        source: Dict[str, Any]
    ) -> None:
        """Initialize a portal resource.
        
        Args:
            portal_connector: PortalConnector instance.
            database_connector: DatabaseConnector instance.
            params: Resource parameters dictionary.
            source: Source configuration dictionary.
            
        Raises:
            DataExportError: If initialization fails.
        """
        try:
            self.portal_connector = portal_connector
            self.database_connector = database_connector
            self._config_manager = get_config_manager()
            self._metadata_manager = MetadataManager()
            
            # Validate and store parameters
            self.params = validate_resource_parameters(params)
            self.source = validate_source_config(source)
            
            # Validate metadata if present
            if 'metadata' in params:
                self.metadata = validate_metadata_dict(params['metadata'])
            else:
                self.metadata = {}
            
            # Set up resource properties
            self._setup_resource_properties()
            
            # Set up paths and configuration
            self._setup_paths()
            
            logger.info(f"Portal resource initialized: {self.title}")
            
        except Exception as e:
            logger.error(f"Failed to initialize portal resource: {str(e)}")
            raise DataExportError("Failed to initialize portal resource", str(e))
    
    def _setup_resource_properties(self) -> None:
        """Set up resource properties from parameters."""
        self.title = self.params['title']
        self.tags = self.params['tags']
        self.groups = self.params.get('groups', [])
        self.share_level = self.params.get('share_level', 'org')
        self.allow_edits = self.params.get('allow_edits', False)
        self.is_spatial = self.params.get('spatial_data', False)
        
        # Set up SRID
        srid_value = self.params.get('srid', self._config_manager.get('spatial.default_srid', 2285))
        self.srid = validate_spatial_reference(srid_value)
        
        # Build resource properties for ArcGIS API
        self.resource_properties = {
            'title': self.title,
            'tags': self.tags,
            'snippet': self.params.get('snippet', ''),
            'licenseInfo': self.params.get('licenseInfo', '')
        }
    
    def _setup_paths(self) -> None:
        """Set up working paths and directories."""
        self.workspace_path = Path(self._config_manager.get('paths.workspace', './workspace'))
        self.sde_folder = self._config_manager.get('paths.sde_folder', './sde')
        self.sde_name = self._config_manager.get('paths.sde_name', 'elmergeo.sde')
        self.sde_instance = self._config_manager.get('spatial.sde_instance', 'SQLserver')
        self.sde_database = self._config_manager.get('spatial.sde_database', 'ElmerGeo')
    
    def _prepare_workspace(self) -> Path:
        """Prepare the workspace directory.
        
        Returns:
            Path to the prepared workspace.
        """
        try:
            if self.workspace_path.exists():
                # Clean existing files but preserve metadata directory
                for item in self.workspace_path.iterdir():
                    if item.name != 'metadata':
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
            else:
                self.workspace_path.mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"Prepared workspace: {self.workspace_path}")
            return self.workspace_path
            
        except Exception as e:
            logger.error(f"Failed to prepare workspace: {str(e)}")
            raise DataExportError("Failed to prepare workspace", str(e))
    
    def _build_sql_query(self) -> str:
        """Build SQL query based on source configuration.
        
        Returns:
            SQL query string.
        """
        try:
            if 'sql_query' in self.source:
                # Use custom SQL query
                return self.source['sql_query']
            elif self.source.get('is_simple', False):
                # Build simple query from table name
                schema = self.source.get('schema', 'dbo')
                table_name = self.source['table_name']
                
                if self.is_spatial:
                    # Get columns for spatial layer
                    columns = self._get_layer_columns(table_name)
                    columns_clause = self._build_columns_clause(columns)
                    return f"SELECT {columns_clause} FROM {schema}.{table_name}"
                else:
                    return f"SELECT * FROM {schema}.{table_name}"
            else:
                raise DataExportError("No valid source configuration found")
                
        except Exception as e:
            logger.error(f"Failed to build SQL query: {str(e)}")
            raise DataExportError("Failed to build SQL query", str(e))
    
    def _get_layer_columns(self, table_name: str) -> List[str]:
        """Get column names for a database table/layer.
        
        Args:
            table_name: Name of the table/layer.
            
        Returns:
            List of column names.
        """
        try:
            sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            """
            
            df = pd.read_sql(sql, self.database_connector.engine, params=[table_name])
            columns = df['COLUMN_NAME'].tolist()
            
            # Filter out system columns
            system_columns = ['GDB_GEOMATTR_DATA', 'SDE_STATE_ID']
            filtered_columns = [col for col in columns if col not in system_columns]
            
            logger.debug(f"Retrieved {len(filtered_columns)} columns for {table_name}")
            return filtered_columns
            
        except Exception as e:
            logger.error(f"Failed to get layer columns: {str(e)}")
            raise DataExportError("Failed to get layer columns", str(e))
    
    def _build_columns_clause(self, columns: List[str]) -> str:
        """Build SQL columns clause with spatial handling.
        
        Args:
            columns: List of column names.
            
        Returns:
            SQL columns clause string.
        """
        try:
            # Convert Shape column to WKT for spatial data
            processed_columns = []
            for col in columns:
                if col.lower() == 'shape':
                    processed_columns.append('Shape.STAsText() as Shape_wkt')
                else:
                    processed_columns.append(col)
            
            return ', '.join(processed_columns)
            
        except Exception as e:
            logger.error(f"Failed to build columns clause: {str(e)}")
            raise DataExportError("Failed to build columns clause", str(e))
    
    def _export_tabular_data(self) -> tuple[pd.DataFrame, Path]:
        """Export tabular data to CSV.
        
        Returns:
            Tuple of (DataFrame, CSV file path).
        """
        try:
            # Build and execute query
            sql_query = self._build_sql_query()
            logger.debug(f"Executing query: {sql_query[:100]}...")
            
            df = pd.read_sql(sql_query, self.database_connector.engine)
            validate_dataframe(df)
            
            # Prepare workspace and save CSV
            workspace = self._prepare_workspace()
            csv_path = workspace / f"{self.title}.csv"
            
            df.to_csv(csv_path, index=False)
            logger.info(f"Exported {len(df)} rows to {csv_path}")
            
            return df, csv_path
            
        except Exception as e:
            logger.error(f"Failed to export tabular data: {str(e)}")
            raise DataExportError("Failed to export tabular data", str(e))
    
    def _export_spatial_data(self) -> Path:
        """Export spatial data to file geodatabase.
        
        Returns:
            Path to the zipped geodatabase.
        """
        try:
            # This is a simplified version - full implementation would require ArcPy
            # For now, we'll export to a format that can be handled without ArcPy
            sql_query = self._build_sql_query()
            logger.debug(f"Executing spatial query: {sql_query[:100]}...")
            
            df = pd.read_sql(sql_query, self.database_connector.engine)
            validate_dataframe(df)
            
            # Convert to GeoDataFrame
            gdf = create_geodataframe_from_wkt(df)
            
            # Simplify if configured
            if self._config_manager.get('spatial.simplify_polygons', True):
                close_holes = self._config_manager.get('spatial.close_holes', True)
                gdf = simplify_geodataframe(gdf, close_holes)
            
            # Prepare workspace
            workspace = self._prepare_workspace()
            
            # For now, export as shapefile (would need ArcPy for full GDB support)
            shapefile_path = workspace / f"{self.title}.shp"
            gdf.to_file(shapefile_path)
            
            # Create zip file
            zip_path = self._create_shapefile_zip(shapefile_path)
            logger.info(f"Exported {len(gdf)} features to {zip_path}")
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Failed to export spatial data: {str(e)}")
            raise SpatialDataError("Failed to export spatial data", str(e))
    
    def _create_shapefile_zip(self, shapefile_path: Path) -> Path:
        """Create a zip file containing all shapefile components.
        
        Args:
            shapefile_path: Path to the main .shp file.
            
        Returns:
            Path to the created zip file.
        """
        try:
            zip_path = shapefile_path.with_suffix('.zip')
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                # Add all shapefile components
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    component_path = shapefile_path.with_suffix(ext)
                    if component_path.exists():
                        zip_file.write(component_path, component_path.name)
            
            logger.debug(f"Created shapefile zip: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Failed to create shapefile zip: {str(e)}")
            raise DataExportError("Failed to create shapefile zip", str(e))
    
    def _publish_new_item(self, data_path: Path, df: Optional[pd.DataFrame] = None) -> Any:
        """Publish a new item to the portal.
        
        Args:
            data_path: Path to the data file.
            df: Optional DataFrame for field mapping.
            
        Returns:
            Published item.
        """
        try:
            gis = self.portal_connector.gis
            
            # Set up item properties
            item_properties = self.resource_properties.copy()
            if self.is_spatial:
                item_properties['type'] = 'Shapefile'  # or 'File Geodatabase'
            else:
                item_properties['type'] = 'CSV'
            
            # Add the item
            item = gis.content.add(item_properties, data=str(data_path))
            
            # Publish the item
            if self.is_spatial:
                publish_params = {
                    'name': self.title,
                    'targetSR': self.srid
                }
            else:
                publish_params = {
                    'name': self.title,
                    'type': 'csv',
                    'locationType': 'none'
                }
                
                if df is not None:
                    field_mappings = build_field_mappings(df)
                    publish_params['layerInfo'] = {'fields': field_mappings}
            
            published_item = item.publish(publish_parameters=publish_params)
            logger.info(f"Published new item: {self.title}")
            
            return published_item
            
        except Exception as e:
            logger.error(f"Failed to publish new item: {str(e)}")
            raise DataExportError("Failed to publish new item", str(e))
    
    def _update_existing_item(self, data_path: Path, df: Optional[pd.DataFrame] = None) -> Any:
        """Update an existing item on the portal.
        
        Args:
            data_path: Path to the data file.
            df: Optional DataFrame for field mapping.
            
        Returns:
            Updated item.
        """
        try:
            # Find existing item
            item_type = 'Shapefile' if self.is_spatial else 'CSV'
            existing_item = self.portal_connector.find_by_title(self.title, item_type)
            
            if existing_item == "no object":
                raise DataExportError(f"Existing item not found: {self.title}")
            
            # Update the item
            item_properties = self.resource_properties.copy()
            item_properties['type'] = item_type
            
            existing_item.update(data=str(data_path), item_properties=item_properties)
            
            # Republish
            if self.is_spatial:
                publish_params = {
                    'name': self.title,
                    'targetSR': self.srid
                }
            else:
                publish_params = {
                    'name': self.title,
                    'type': 'csv',
                    'locationType': 'none'
                }
                
                if df is not None:
                    field_mappings = build_field_mappings(df)
                    publish_params['layerInfo'] = {'fields': field_mappings}
            
            published_item = existing_item.publish(
                publish_parameters=publish_params,
                overwrite=True
            )
            
            logger.info(f"Updated existing item: {self.title}")
            return published_item
            
        except Exception as e:
            logger.error(f"Failed to update existing item: {str(e)}")
            raise DataExportError("Failed to update existing item", str(e))
    
    def _apply_sharing_and_metadata(self, item: Any) -> None:
        """Apply sharing settings and metadata to a published item.
        
        Args:
            item: Published item to configure.
        """
        try:
            # Update metadata if available
            if self.metadata:
                metadata_path = self.workspace_path / 'metadata.xml'
                self._metadata_manager.update_metadata_xml(
                    metadata_path,
                    self.metadata,
                    self.resource_properties
                )
                item.update(metadata=str(metadata_path))
            
            # Set sharing level
            group_ids = []
            if self.groups:
                group_ids = self.portal_connector.get_group_ids_by_titles(self.groups)
            
            if self.share_level == 'everyone':
                item.share(everyone=True, groups=group_ids)
            elif self.share_level == 'org':
                item.share(org=True, groups=group_ids)
            else:
                item.share(everyone=False, groups=group_ids)
            
            # Set editability for spatial layers
            if self.is_spatial:
                self._set_layer_editability(item)
            
            logger.debug(f"Applied sharing and metadata to {self.title}")
            
        except Exception as e:
            logger.error(f"Failed to apply sharing and metadata: {str(e)}")
            raise DataExportError("Failed to apply sharing and metadata", str(e))
    
    def _set_layer_editability(self, item: Any) -> None:
        """Set editability settings for a spatial layer.
        
        Args:
            item: Published spatial item.
        """
        try:
            flc = FeatureLayerCollection.fromitem(item)
            
            if self.allow_edits:
                capabilities = 'Create,Delete,Query,Update,Editing'
            else:
                capabilities = 'Query'
            
            capabilities_dict = {
                'capabilities': capabilities,
                'syncEnabled': False
            }
            
            flc.manager.update_definition(capabilities_dict)
            logger.debug(f"Set editability for {self.title}: {capabilities}")
            
        except Exception as e:
            logger.error(f"Failed to set layer editability: {str(e)}")
            # Don't raise error as this is not critical
    
    def export(self, update_existing: bool = True) -> None:
        """Export the resource to the portal.
        
        Args:
            update_existing: Whether to update existing items or create new ones.
        """
        try:
            logger.info(f"Starting export of {self.title} (spatial: {self.is_spatial})")
            
            if self.is_spatial:
                # Export spatial data
                data_path = self._export_spatial_data()
                df = None
            else:
                # Export tabular data
                df, data_path = self._export_tabular_data()
            
            # Publish or update
            if update_existing:
                try:
                    item = self._update_existing_item(data_path, df)
                except DataExportError:
                    # If update fails, create new
                    logger.info("Update failed, creating new item")
                    item = self._publish_new_item(data_path, df)
            else:
                item = self._publish_new_item(data_path, df)
            
            # Apply sharing and metadata
            self._apply_sharing_and_metadata(item)
            
            logger.info(f"Successfully exported {self.title}")
            
        except Exception as e:
            logger.error(f"Failed to export resource: {str(e)}")
            raise DataExportError("Failed to export resource", str(e))
