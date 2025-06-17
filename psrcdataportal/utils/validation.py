"""Data validation utilities for psrcdataportal package."""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_required_parameters(params: Dict[str, Any], required_keys: List[str]) -> None:
    """Validate that required parameters are present and not empty.
    
    Args:
        params: Dictionary of parameters to validate.
        required_keys: List of required parameter keys.
        
    Raises:
        ValidationError: If required parameters are missing or empty.
    """
    missing_keys = []
    empty_keys = []
    
    for key in required_keys:
        if key not in params:
            missing_keys.append(key)
        elif not params[key] or (isinstance(params[key], str) and not params[key].strip()):
            empty_keys.append(key)
    
    if missing_keys or empty_keys:
        error_parts = []
        if missing_keys:
            error_parts.append(f"Missing parameters: {', '.join(missing_keys)}")
        if empty_keys:
            error_parts.append(f"Empty parameters: {', '.join(empty_keys)}")
        
        raise ValidationError(
            "Required parameters validation failed",
            "; ".join(error_parts)
        )


def validate_share_level(share_level: str) -> str:
    """Validate and normalize share level parameter.
    
    Args:
        share_level: Share level string to validate.
        
    Returns:
        Validated share level string.
        
    Raises:
        ValidationError: If share level is invalid.
    """
    valid_levels = ['everyone', 'org', 'private']
    
    if not isinstance(share_level, str):
        raise ValidationError("Share level must be a string")
    
    normalized_level = share_level.lower().strip()
    
    if normalized_level not in valid_levels:
        raise ValidationError(
            f"Invalid share level: {share_level}",
            f"Valid options are: {', '.join(valid_levels)}"
        )
    
    return normalized_level


def validate_tags(tags: Union[str, List[str]]) -> List[str]:
    """Validate and normalize tags parameter.
    
    Args:
        tags: Tags as string (comma/semicolon separated) or list of strings.
        
    Returns:
        List of validated tag strings.
        
    Raises:
        ValidationError: If tags format is invalid.
    """
    try:
        if isinstance(tags, str):
            # Remove trailing comma/semicolon if present
            tags = tags.rstrip(',;')
            # Split on comma or semicolon
            import re
            tag_list = re.split('[,;]', tags)
        elif isinstance(tags, list):
            tag_list = tags
        else:
            raise ValidationError("Tags must be a string or list of strings")
        
        # Clean and validate each tag
        cleaned_tags = []
        for tag in tag_list:
            if isinstance(tag, str):
                cleaned_tag = tag.strip()
                if cleaned_tag:  # Only add non-empty tags
                    cleaned_tags.append(cleaned_tag)
            else:
                logger.warning(f"Skipping non-string tag: {tag}")
        
        if not cleaned_tags:
            raise ValidationError("At least one valid tag is required")
        
        return cleaned_tags
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate tags: {str(e)}")
        raise ValidationError("Failed to validate tags", str(e))


def validate_groups(groups: Union[str, List[str]]) -> List[str]:
    """Validate and normalize groups parameter.
    
    Args:
        groups: Groups as string (semicolon separated) or list of strings.
        
    Returns:
        List of validated group strings.
        
    Raises:
        ValidationError: If groups format is invalid.
    """
    try:
        if isinstance(groups, str):
            if not groups.strip():
                return []
            group_list = groups.split(';')
        elif isinstance(groups, list):
            group_list = groups
        else:
            raise ValidationError("Groups must be a string or list of strings")
        
        # Clean and validate each group
        cleaned_groups = []
        for group in group_list:
            if isinstance(group, str):
                cleaned_group = group.strip()
                if cleaned_group:  # Only add non-empty groups
                    cleaned_groups.append(cleaned_group)
            else:
                logger.warning(f"Skipping non-string group: {group}")
        
        return cleaned_groups
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate groups: {str(e)}")
        raise ValidationError("Failed to validate groups", str(e))


def validate_dataframe(df: pd.DataFrame, min_rows: int = 1) -> None:
    """Validate that a DataFrame meets basic requirements.
    
    Args:
        df: DataFrame to validate.
        min_rows: Minimum number of rows required.
        
    Raises:
        ValidationError: If DataFrame validation fails.
    """
    try:
        if not isinstance(df, pd.DataFrame):
            raise ValidationError("Input must be a pandas DataFrame")
        
        if df.empty:
            raise ValidationError("DataFrame is empty")
        
        if len(df) < min_rows:
            raise ValidationError(
                f"DataFrame has {len(df)} rows, minimum required: {min_rows}"
            )
        
        if len(df.columns) == 0:
            raise ValidationError("DataFrame has no columns")
        
        logger.debug(f"DataFrame validation passed: {len(df)} rows, {len(df.columns)} columns")
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate DataFrame: {str(e)}")
        raise ValidationError("Failed to validate DataFrame", str(e))


def validate_sql_query(sql: str) -> str:
    """Validate and clean SQL query string.
    
    Args:
        sql: SQL query string to validate.
        
    Returns:
        Cleaned SQL query string.
        
    Raises:
        ValidationError: If SQL query is invalid.
    """
    try:
        if not isinstance(sql, str):
            raise ValidationError("SQL query must be a string")
        
        cleaned_sql = sql.strip()
        
        if not cleaned_sql:
            raise ValidationError("SQL query cannot be empty")
        
        # Basic SQL injection prevention - check for dangerous keywords
        dangerous_keywords = [
            'drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update',
            'exec', 'execute', 'sp_', 'xp_'
        ]
        
        sql_lower = cleaned_sql.lower()
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                logger.warning(f"Potentially dangerous SQL keyword detected: {keyword}")
                # Don't raise error, just log warning as some keywords might be legitimate
        
        # Ensure query starts with SELECT
        if not sql_lower.startswith('select'):
            raise ValidationError("SQL query must start with SELECT")
        
        return cleaned_sql
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate SQL query: {str(e)}")
        raise ValidationError("Failed to validate SQL query", str(e))


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """Validate file path string.
    
    Args:
        file_path: File path to validate.
        must_exist: Whether the file must already exist.
        
    Returns:
        Validated file path string.
        
    Raises:
        ValidationError: If file path is invalid.
    """
    try:
        if not isinstance(file_path, str):
            raise ValidationError("File path must be a string")
        
        cleaned_path = file_path.strip()
        
        if not cleaned_path:
            raise ValidationError("File path cannot be empty")
        
        from pathlib import Path
        path_obj = Path(cleaned_path)
        
        if must_exist and not path_obj.exists():
            raise ValidationError(f"File does not exist: {cleaned_path}")
        
        return cleaned_path
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate file path: {str(e)}")
        raise ValidationError("Failed to validate file path", str(e))


def validate_metadata_dict(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metadata dictionary structure and content.
    
    Args:
        metadata: Metadata dictionary to validate.
        
    Returns:
        Validated metadata dictionary.
        
    Raises:
        ValidationError: If metadata validation fails.
    """
    try:
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
        
        # Required metadata fields
        required_fields = [
            'contact_name',
            'contact_email',
            'organization_name'
        ]
        
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise ValidationError(
                "Required metadata fields missing",
                f"Missing: {', '.join(missing_fields)}"
            )
        
        # Validate email format if present
        if 'contact_email' in metadata and metadata['contact_email']:
            email = metadata['contact_email']
            if not isinstance(email, str) or '@' not in email:
                raise ValidationError("Invalid email format in contact_email")
        
        # Validate phone format if present
        if 'contact_phone' in metadata and metadata['contact_phone']:
            phone = metadata['contact_phone']
            if not isinstance(phone, str):
                raise ValidationError("Contact phone must be a string")
        
        return metadata
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate metadata: {str(e)}")
        raise ValidationError("Failed to validate metadata", str(e))


def validate_source_config(source: Dict[str, Any]) -> Dict[str, Any]:
    """Validate source configuration dictionary.
    
    Args:
        source: Source configuration dictionary to validate.
        
    Returns:
        Validated source configuration dictionary.
        
    Raises:
        ValidationError: If source configuration is invalid.
    """
    try:
        if not isinstance(source, dict):
            raise ValidationError("Source configuration must be a dictionary")
        
        # Check for required fields based on source type
        if source.get('is_simple', False):
            required_fields = ['table_name', 'feature_dataset']
            missing_fields = [field for field in required_fields if field not in source]
            if missing_fields:
                raise ValidationError(
                    "Required source fields missing for simple source",
                    f"Missing: {', '.join(missing_fields)}"
                )
        
        # Validate fields_to_exclude if present
        if 'fields_to_exclude' in source:
            fields_to_exclude = source['fields_to_exclude']
            if isinstance(fields_to_exclude, str):
                # Convert comma-separated string to list
                source['fields_to_exclude'] = [f.strip() for f in fields_to_exclude.split(',')]
            elif not isinstance(fields_to_exclude, list):
                raise ValidationError("fields_to_exclude must be a string or list")
        else:
            source['fields_to_exclude'] = []
        
        return source
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate source configuration: {str(e)}")
        raise ValidationError("Failed to validate source configuration", str(e))


def validate_resource_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate resource parameters dictionary.
    
    Args:
        params: Resource parameters dictionary to validate.
        
    Returns:
        Validated and normalized parameters dictionary.
        
    Raises:
        ValidationError: If parameters validation fails.
    """
    try:
        if not isinstance(params, dict):
            raise ValidationError("Parameters must be a dictionary")
        
        # Required parameters
        required_params = ['title', 'tags']
        validate_required_parameters(params, required_params)
        
        # Validate and normalize specific parameters
        validated_params = params.copy()
        
        # Validate tags
        validated_params['tags'] = validate_tags(params['tags'])
        
        # Validate share level if present
        if 'share_level' in params:
            validated_params['share_level'] = validate_share_level(params['share_level'])
        
        # Validate groups if present
        if 'groups' in params:
            validated_params['groups'] = validate_groups(params['groups'])
        
        # Validate boolean parameters
        boolean_params = ['allow_edits', 'spatial_data']
        for param in boolean_params:
            if param in params:
                if not isinstance(params[param], bool):
                    raise ValidationError(f"Parameter '{param}' must be a boolean")
        
        # Validate SRID if present
        if 'srid' in params:
            srid = params['srid']
            if isinstance(srid, str):
                try:
                    validated_params['srid'] = int(srid)
                except ValueError:
                    raise ValidationError("SRID must be a valid integer")
            elif not isinstance(srid, int):
                raise ValidationError("SRID must be an integer")
        
        return validated_params
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Failed to validate resource parameters: {str(e)}")
        raise ValidationError("Failed to validate resource parameters", str(e))
