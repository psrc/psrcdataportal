# PSRC Data Portal

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tools to export tables and spatial layers from PSRC databases to ArcGIS Online Data Portal.

## Overview

The `psrcdataportal` package provides a modern, clean interface for exporting data from Puget Sound Regional Council (PSRC) databases to ArcGIS Online/Portal for ArcGIS. It supports both tabular and spatial data exports with comprehensive metadata management, flexible configuration options, and robust error handling.

## Features

- **Simple Factory Functions**: Easy-to-use factory functions for creating database and portal connections
- **Environment Variable Support**: Secure credential management through environment variables
- **Flexible Configuration**: YAML-based configuration with environment variable overrides
- **Comprehensive Validation**: Input validation and data quality checks
- **Metadata Management**: Automated metadata creation and updates
- **Spatial Data Support**: Full support for spatial data export with geometry processing
- **Error Handling**: Detailed error messages and logging
- **Type Safety**: Full type hints throughout the codebase
- **Modern Python**: Follows PEP 8 and modern Python best practices

## Installation

### Prerequisites

- Python 3.8 or higher
- Access to PSRC databases
- ArcGIS Online/Portal for ArcGIS account
- ODBC Driver 17 for SQL Server (or compatible)

### Install from PyPI

```bash
pip install psrcdataportal
```

### Install from Source

```bash
git clone https://github.com/psrc/psrcdataportal.git
cd psrcdataportal
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/psrc/psrcdataportal.git
cd psrcdataportal
pip install -e ".[dev]"
```

## Quick Start

### 1. Set Up Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Database Configuration
PSRC_DB_SERVER=your_sql_server_name
PSRC_DB_NAME=your_database_name

# Portal Configuration
PSRC_PORTAL_USERNAME=your_portal_username
PSRC_PORTAL_PASSWORD=your_portal_password
PSRC_PORTAL_URL=https://psregcncl.maps.arcgis.com
```

### 2. Basic Usage

```python
import psrcdataportal as psrc

# Validate environment setup
if not psrc.validate_environment():
    print("Please check your environment variables")
    exit(1)

# Create connectors using environment variables
db_conn = psrc.create_database_connector()
portal_conn = psrc.create_portal_connector()

# Define resource parameters
params = {
    'title': 'Transportation Network',
    'tags': ['transportation', 'planning', 'network'],
    'share_level': 'org',
    'spatial_data': True,
    'allow_edits': False,
    'metadata': {
        'contact_name': 'John Doe',
        'contact_email': 'john.doe@psrc.org',
        'organization_name': 'Puget Sound Regional Council',
        'summary': 'Regional transportation network data'
    }
}

# Define data source
source = {
    'table_name': 'transportation_network',
    'feature_dataset': 'Transportation',
    'is_simple': True,
    'fields_to_exclude': ['internal_id', 'temp_field']
}

# Create and export resource
resource = psrc.create_portal_resource(portal_conn, db_conn, params, source)
resource.export()
```

### 3. Tabular Data Export

```python
import psrcdataportal as psrc

# Create connectors
db_conn = psrc.create_database_connector()
portal_conn = psrc.create_portal_connector()

# Export tabular data
params = {
    'title': 'Population Forecasts',
    'tags': ['demographics', 'forecasts', 'planning'],
    'share_level': 'everyone',
    'spatial_data': False,
    'snippet': 'Regional population forecasts by jurisdiction'
}

source = {
    'table_name': 'population_forecasts',
    'is_simple': True
}

resource = psrc.create_portal_resource(portal_conn, db_conn, params, source)
resource.export()
```

### 4. Custom SQL Query

```python
import psrcdataportal as psrc

# Create connectors
db_conn = psrc.create_database_connector()
portal_conn = psrc.create_portal_connector()

# Use custom SQL query
params = {
    'title': 'Transit Ridership Summary',
    'tags': ['transit', 'ridership', 'summary'],
    'share_level': 'org',
    'spatial_data': False
}

source = {
    'sql_query': '''
        SELECT 
            route_id,
            route_name,
            SUM(daily_ridership) as total_ridership,
            AVG(daily_ridership) as avg_ridership
        FROM transit_ridership 
        WHERE year = 2023
        GROUP BY route_id, route_name
        ORDER BY total_ridership DESC
    ''',
    'is_simple': False
}

resource = psrc.create_portal_resource(portal_conn, db_conn, params, source)
resource.export()
```

## Configuration

### Environment Variables

The package supports the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `PSRC_DB_SERVER` | Database server name | Yes |
| `PSRC_DB_NAME` | Database name | Yes |
| `PSRC_PORTAL_USERNAME` | Portal username | Yes |
| `PSRC_PORTAL_PASSWORD` | Portal password | Yes |
| `PSRC_PORTAL_URL` | Portal URL | No* |
| `PSRC_DB_DRIVER` | ODBC driver name | No |
| `PSRC_DB_TIMEOUT` | Database timeout (seconds) | No |
| `PSRC_PORTAL_TIMEOUT` | Portal timeout (seconds) | No |
| `PSRC_WORKSPACE_PATH` | Workspace directory path | No |
| `PSRC_DEFAULT_SRID` | Default spatial reference ID | No |
| `PSRC_LOG_LEVEL` | Logging level | No |

*Uses default PSRC portal URL if not specified

### Custom Configuration

You can also provide a custom YAML configuration file:

```python
from psrcdataportal.utils.config import get_config_manager

# Load custom configuration
config_manager = get_config_manager('path/to/custom_config.yaml')
```

## API Reference

### Factory Functions

#### `create_database_connector()`

Creates a database connector with automatic configuration.

**Parameters:**
- `server` (str, optional): Database server name
- `database` (str, optional): Database name  
- `driver` (str, optional): ODBC driver name
- `trusted_connection` (bool): Use Windows authentication (default: True)
- `timeout` (int, optional): Connection timeout in seconds

**Returns:** `DatabaseConnector` instance

#### `create_portal_connector()`

Creates a portal connector with automatic configuration.

**Parameters:**
- `username` (str, optional): Portal username
- `password` (str, optional): Portal password
- `url` (str, optional): Portal URL
- `timeout` (int, optional): Connection timeout in seconds

**Returns:** `PortalConnector` instance

#### `create_portal_resource()`

Creates a portal resource for data export.

**Parameters:**
- `portal_connector` (PortalConnector): Portal connector instance
- `database_connector` (DatabaseConnector): Database connector instance
- `params` (dict): Resource parameters
- `source` (dict): Source configuration

**Returns:** `PortalResource` instance

### Resource Parameters

The `params` dictionary supports the following keys:

| Key | Type | Description | Required |
|-----|------|-------------|----------|
| `title` | str | Resource title | Yes |
| `tags` | str/list | Tags for the resource | Yes |
| `share_level` | str | Sharing level ('everyone', 'org', 'private') | No |
| `spatial_data` | bool | Whether this is spatial data | No |
| `allow_edits` | bool | Whether to allow editing | No |
| `groups` | str/list | Groups to share with | No |
| `snippet` | str | Resource description | No |
| `licenseInfo` | str | License information | No |
| `srid` | int | Spatial reference ID | No |
| `metadata` | dict | Metadata dictionary | No |

### Source Configuration

The `source` dictionary supports the following keys:

| Key | Type | Description | Required |
|-----|------|-------------|----------|
| `table_name` | str | Database table/view name | Yes* |
| `is_simple` | bool | Use simple table export | No |
| `schema` | str | Database schema name | No |
| `feature_dataset` | str | Feature dataset for spatial data | No** |
| `fields_to_exclude` | str/list | Fields to exclude | No |
| `sql_query` | str | Custom SQL query | No* |

*Either `table_name` or `sql_query` is required
**Required for spatial data with `is_simple=True`

## Error Handling

The package provides comprehensive error handling with custom exception types:

```python
import psrcdataportal as psrc
from psrcdataportal import (
    DatabaseConnectionError,
    PortalConnectionError,
    ValidationError,
    DataExportError
)

try:
    db_conn = psrc.create_database_connector()
except DatabaseConnectionError as e:
    print(f"Database connection failed: {e}")
except ValidationError as e:
    print(f"Configuration error: {e}")

try:
    resource.export()
except DataExportError as e:
    print(f"Export failed: {e}")
```

## Logging

The package uses Python's standard logging module. Configure logging level through environment variables or programmatically:

```python
import psrcdataportal as psrc

# Set up logging
psrc.setup_logging(level="DEBUG")

# Or use environment variable
# PSRC_LOG_LEVEL=DEBUG
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run with coverage
pytest --cov=psrcdataportal --cov-report=html
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/psrc/psrcdataportal.git
cd psrcdataportal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Format code
black psrcdataportal/

# Sort imports
isort psrcdataportal/

# Type checking
mypy psrcdataportal/

# Linting
flake8 psrcdataportal/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/psrc/psrcdataportal/issues)
- **Documentation**: [Read the Docs](https://psrcdataportal.readthedocs.io/)
- **Email**: datateam@psrc.org

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Acknowledgments

- Puget Sound Regional Council (PSRC) Data Team
- ArcGIS Python API developers
- Open source GIS community
