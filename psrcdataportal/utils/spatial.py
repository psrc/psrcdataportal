"""Spatial data processing utilities for psrcdataportal package."""

import logging
from pathlib import Path
from typing import Optional, Union

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Polygon

from ..exceptions import SpatialDataError

logger = logging.getLogger(__name__)


def close_polygon_holes(polygon: Polygon) -> Polygon:
    """Close polygon holes by limiting to the exterior ring.
    
    Args:
        polygon: Input shapely Polygon.
        
    Returns:
        Polygon with holes closed.
        
    Example:
        df.geometry.apply(lambda p: close_polygon_holes(p))
    """
    try:
        if polygon.interiors:
            return Polygon(list(polygon.exterior.coords))
        else:
            return polygon
    except Exception as e:
        logger.error(f"Failed to close polygon holes: {str(e)}")
        raise SpatialDataError("Failed to close polygon holes", str(e))


def simplify_geodataframe(gdf: gpd.GeoDataFrame, close_holes: bool = True) -> gpd.GeoDataFrame:
    """Simplify a polygon geodataframe by filling holes and exploding multipart features.
    
    Polygon holes can represent features such as lakes, but can cause 
    strange triangle-shaped artifacts in geodataframes.
    
    Args:
        gdf: A GeoDataFrame object.
        close_holes: Whether to close polygon holes.
        
    Returns:
        Simplified GeoDataFrame.
        
    Raises:
        SpatialDataError: If simplification fails.
    """
    try:
        if gdf.empty:
            logger.warning("Empty GeoDataFrame provided for simplification")
            return gdf
        
        # Check if we have geometry column
        if 'Shape_wkt' not in gdf.columns:
            logger.warning("No 'Shape_wkt' column found in GeoDataFrame")
            return gdf
        
        # Get geometry type
        geom_types = gdf.Shape_wkt.geom_type.unique()
        
        if len(geom_types) == 1 and geom_types[0] == 'Polygon':
            # Explode multipart features
            gdf = gdf.explode(ignore_index=True)
            
            if close_holes:
                # Close polygon holes
                gdf['Shape_wkt'] = gdf.geometry.apply(lambda p: close_polygon_holes(p))
                logger.debug("Closed polygon holes in GeoDataFrame")
        
        logger.debug(f"Simplified GeoDataFrame with {len(gdf)} features")
        return gdf
        
    except Exception as e:
        logger.error(f"Failed to simplify GeoDataFrame: {str(e)}")
        raise SpatialDataError("Failed to simplify GeoDataFrame", str(e))


def create_geodataframe_from_wkt(df: pd.DataFrame, wkt_column: str = 'Shape_wkt') -> gpd.GeoDataFrame:
    """Create a GeoDataFrame from a DataFrame with WKT geometry column.
    
    Args:
        df: Input DataFrame with WKT geometry column.
        wkt_column: Name of the WKT geometry column.
        
    Returns:
        GeoDataFrame with geometry column.
        
    Raises:
        SpatialDataError: If conversion fails.
    """
    try:
        if wkt_column not in df.columns:
            raise SpatialDataError(f"WKT column '{wkt_column}' not found in DataFrame")
        
        # Convert WKT strings to geometry objects
        df[wkt_column] = df[wkt_column].apply(wkt.loads)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=wkt_column)
        
        logger.debug(f"Created GeoDataFrame with {len(gdf)} features from WKT")
        return gdf
        
    except Exception as e:
        logger.error(f"Failed to create GeoDataFrame from WKT: {str(e)}")
        raise SpatialDataError("Failed to create GeoDataFrame from WKT", str(e))


def shorten_column_names(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Create shortened column names for a GeoDataFrame.
    
    Creates a dictionary of column names, with the keys being short abstracted 
    references to the full-length column names. Resets gdf.columns to the list 
    of new abstracted column names ['col1', 'col2'...].
    
    Args:
        gdf: Input GeoDataFrame.
        
    Returns:
        Tuple of (modified GeoDataFrame, column mapping dictionary).
        
    Raises:
        SpatialDataError: If column shortening fails.
    """
    try:
        col_list = gdf.columns.to_list()
        new_col_list = []
        column_dict = {}
        
        for i, col_name in enumerate(col_list):
            if col_name != 'Shape_wkt':
                new_col = f'col{i}'
                column_dict[new_col] = col_name
                new_col_list.append(new_col)
            else:
                column_dict[col_name] = col_name
                new_col_list.append(col_name)
        
        # Create a copy to avoid modifying the original
        gdf_copy = gdf.copy()
        gdf_copy.columns = new_col_list
        
        logger.debug(f"Shortened {len(col_list)} column names")
        return gdf_copy, column_dict
        
    except Exception as e:
        logger.error(f"Failed to shorten column names: {str(e)}")
        raise SpatialDataError("Failed to shorten column names", str(e))


def validate_spatial_reference(srid: Union[int, dict]) -> dict:
    """Validate and normalize spatial reference identifier.
    
    Args:
        srid: Spatial reference ID as integer or dictionary with 'wkid' key.
        
    Returns:
        Dictionary with 'wkid' key containing the SRID.
        
    Raises:
        SpatialDataError: If SRID is invalid.
    """
    try:
        if isinstance(srid, int):
            return {'wkid': srid}
        elif isinstance(srid, dict) and 'wkid' in srid:
            if isinstance(srid['wkid'], int):
                return srid
            else:
                raise SpatialDataError("SRID 'wkid' value must be an integer")
        else:
            raise SpatialDataError("SRID must be an integer or dictionary with 'wkid' key")
            
    except Exception as e:
        logger.error(f"Failed to validate spatial reference: {str(e)}")
        raise SpatialDataError("Failed to validate spatial reference", str(e))


def get_geometry_type(gdf: gpd.GeoDataFrame) -> Optional[str]:
    """Get the primary geometry type from a GeoDataFrame.
    
    Args:
        gdf: Input GeoDataFrame.
        
    Returns:
        Primary geometry type string, or None if no geometry.
        
    Raises:
        SpatialDataError: If unable to determine geometry type.
    """
    try:
        if gdf.empty:
            return None
        
        if 'Shape_wkt' not in gdf.columns:
            return None
        
        geom_types = gdf.Shape_wkt.geom_type.unique()
        
        if len(geom_types) == 0:
            return None
        
        # Return the most common geometry type
        primary_type = geom_types[0]
        
        if len(geom_types) > 1:
            logger.warning(f"Mixed geometry types found: {geom_types}. Using: {primary_type}")
        
        logger.debug(f"Primary geometry type: {primary_type}")
        return primary_type
        
    except Exception as e:
        logger.error(f"Failed to get geometry type: {str(e)}")
        raise SpatialDataError("Failed to get geometry type", str(e))


def ensure_geometry_column(gdf: gpd.GeoDataFrame, geometry_column: str = 'Shape_wkt') -> gpd.GeoDataFrame:
    """Ensure the GeoDataFrame has a properly set geometry column.
    
    Args:
        gdf: Input GeoDataFrame.
        geometry_column: Name of the geometry column.
        
    Returns:
        GeoDataFrame with properly set geometry column.
        
    Raises:
        SpatialDataError: If geometry column setup fails.
    """
    try:
        if geometry_column not in gdf.columns:
            raise SpatialDataError(f"Geometry column '{geometry_column}' not found")
        
        # Set the geometry column if it's not already set
        if gdf.geometry.name != geometry_column:
            gdf = gdf.set_geometry(geometry_column)
            logger.debug(f"Set geometry column to '{geometry_column}'")
        
        return gdf
        
    except Exception as e:
        logger.error(f"Failed to ensure geometry column: {str(e)}")
        raise SpatialDataError("Failed to ensure geometry column", str(e))


def calculate_bounds(gdf: gpd.GeoDataFrame) -> Optional[dict]:
    """Calculate the bounding box of a GeoDataFrame.
    
    Args:
        gdf: Input GeoDataFrame.
        
    Returns:
        Dictionary with 'minx', 'miny', 'maxx', 'maxy' keys, or None if empty.
        
    Raises:
        SpatialDataError: If bounds calculation fails.
    """
    try:
        if gdf.empty:
            return None
        
        bounds = gdf.total_bounds
        
        return {
            'minx': float(bounds[0]),
            'miny': float(bounds[1]),
            'maxx': float(bounds[2]),
            'maxy': float(bounds[3])
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate bounds: {str(e)}")
        raise SpatialDataError("Failed to calculate bounds", str(e))
