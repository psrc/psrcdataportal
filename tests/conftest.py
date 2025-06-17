"""Pytest configuration and fixtures for psrcdataportal tests."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

from psrcdataportal.core.database import DatabaseConnector
from psrcdataportal.core.portal import PortalConnector
from psrcdataportal.utils.config import ConfigManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Sample configuration dictionary for testing."""
    return {
        'database': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': True,
            'timeout': 30
        },
        'portal': {
            'default_url': 'https://test.maps.arcgis.com',
            'timeout': 60
        },
        'paths': {
            'workspace': './test_workspace',
            'sde_folder': './test_sde',
            'sde_name': 'test.sde'
        },
        'spatial': {
            'default_srid': 2285,
            'sde_instance': 'TestServer',
            'sde_database': 'TestDB'
        }
    }


@pytest.fixture
def mock_config_manager(sample_config):
    """Mock ConfigManager for testing."""
    mock_manager = Mock(spec=ConfigManager)
    mock_manager.get.side_effect = lambda key, default=None: _get_nested_value(sample_config, key, default)
    mock_manager.get_database_config.return_value = sample_config['database']
    mock_manager.get_portal_config.return_value = sample_config['portal']
    mock_manager.config = sample_config
    return mock_manager


def _get_nested_value(data, key_path, default=None):
    """Helper function to get nested dictionary values using dot notation."""
    keys = key_path.split('.')
    current = data
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


@pytest.fixture
def mock_database_connector():
    """Mock DatabaseConnector for testing."""
    mock_conn = Mock(spec=DatabaseConnector)
    mock_conn.server = 'test_server'
    mock_conn.database = 'test_db'
    mock_conn.engine = Mock()
    mock_conn.sql_conn = mock_conn.engine
    mock_conn.test_connection.return_value = True
    return mock_conn


@pytest.fixture
def mock_portal_connector():
    """Mock PortalConnector for testing."""
    mock_conn = Mock(spec=PortalConnector)
    mock_conn.username = 'test_user'
    mock_conn.portal_url = 'https://test.maps.arcgis.com'
    
    # Mock GIS instance
    mock_gis = Mock()
    mock_gis.users.me.username = 'test_user'
    mock_gis.users.me.groups = []
    mock_conn.gis = mock_gis
    
    mock_conn.test_connection.return_value = True
    mock_conn.find_by_title.return_value = "no object"
    mock_conn.get_group_ids_by_titles.return_value = []
    
    return mock_conn


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['A', 'B', 'C', 'D', 'E'],
        'value': [10.5, 20.3, 30.1, 40.8, 50.2],
        'category': ['X', 'Y', 'X', 'Z', 'Y']
    })


@pytest.fixture
def sample_geodataframe():
    """Sample GeoDataFrame for testing."""
    geometries = [
        Point(0, 0),
        Point(1, 1),
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Point(2, 2),
        Point(3, 3)
    ]
    
    return gpd.GeoDataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Point A', 'Point B', 'Polygon C', 'Point D', 'Point E'],
        'value': [10.5, 20.3, 30.1, 40.8, 50.2],
        'Shape_wkt': geometries
    }, geometry='Shape_wkt')


@pytest.fixture
def sample_resource_params():
    """Sample resource parameters for testing."""
    return {
        'title': 'Test Resource',
        'tags': ['test', 'sample'],
        'share_level': 'org',
        'spatial_data': False,
        'allow_edits': False,
        'snippet': 'Test resource for unit tests',
        'metadata': {
            'contact_name': 'Test User',
            'contact_email': 'test@example.com',
            'organization_name': 'Test Organization'
        }
    }


@pytest.fixture
def sample_source_config():
    """Sample source configuration for testing."""
    return {
        'table_name': 'test_table',
        'is_simple': True,
        'schema': 'dbo',
        'fields_to_exclude': []
    }


@pytest.fixture
def mock_sqlalchemy_engine():
    """Mock SQLAlchemy engine for testing."""
    mock_engine = Mock()
    mock_connection = Mock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    mock_engine.connect.return_value.__exit__.return_value = None
    return mock_engine


@pytest.fixture
def mock_arcgis_item():
    """Mock ArcGIS item for testing."""
    mock_item = Mock()
    mock_item.title = 'Test Item'
    mock_item.type = 'Feature Service'
    mock_item.update.return_value = True
    mock_item.publish.return_value = mock_item
    mock_item.share.return_value = True
    return mock_item


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    test_env_vars = {
        'PSRC_DB_SERVER': 'test_server',
        'PSRC_DB_NAME': 'test_db',
        'PSRC_PORTAL_USERNAME': 'test_user',
        'PSRC_PORTAL_PASSWORD': 'test_pass',
        'PSRC_PORTAL_URL': 'https://test.maps.arcgis.com'
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def mock_file_operations(monkeypatch):
    """Mock file operations for testing."""
    mock_path = Mock()
    mock_path.exists.return_value = True
    mock_path.mkdir.return_value = None
    mock_path.iterdir.return_value = []
    
    monkeypatch.setattr('pathlib.Path', lambda x: mock_path)
    return mock_path


# Markers for different test types
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
