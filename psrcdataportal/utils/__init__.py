"""Utility modules for psrcdataportal package."""

from .config import ConfigManager, get_config_manager, get_config
from .metadata import MetadataManager, build_field_mappings
from .spatial import (
    close_polygon_holes,
    simplify_geodataframe,
    create_geodataframe_from_wkt,
    shorten_column_names,
    validate_spatial_reference,
    get_geometry_type,
    ensure_geometry_column,
    calculate_bounds
)
from .validation import (
    validate_required_parameters,
    validate_share_level,
    validate_tags,
    validate_groups,
    validate_dataframe,
    validate_sql_query,
    validate_file_path,
    validate_metadata_dict,
    validate_source_config,
    validate_resource_parameters
)

__all__ = [
    # Config utilities
    'ConfigManager',
    'get_config_manager',
    'get_config',
    
    # Metadata utilities
    'MetadataManager',
    'build_field_mappings',
    
    # Spatial utilities
    'close_polygon_holes',
    'simplify_geodataframe',
    'create_geodataframe_from_wkt',
    'shorten_column_names',
    'validate_spatial_reference',
    'get_geometry_type',
    'ensure_geometry_column',
    'calculate_bounds',
    
    # Validation utilities
    'validate_required_parameters',
    'validate_share_level',
    'validate_tags',
    'validate_groups',
    'validate_dataframe',
    'validate_sql_query',
    'validate_file_path',
    'validate_metadata_dict',
    'validate_source_config',
    'validate_resource_parameters',
]
