# Changelog

All notable changes to the psrcdataportal package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-16

### Added
- Initial release of psrcdataportal package
- Factory functions for creating database and portal connectors
- Support for both tabular and spatial data exports
- Comprehensive configuration management with YAML and environment variables
- Input validation and data quality checks
- Automated metadata creation and updates
- Spatial data processing utilities
- Custom exception classes for better error handling
- Full type hints throughout the codebase
- Comprehensive test suite with pytest
- Example usage scripts
- Complete documentation with API reference

### Features
- **DatabaseConnector**: Manages SQL Server database connections with SQLAlchemy
- **PortalConnector**: Handles ArcGIS Online/Portal for ArcGIS connections
- **PortalResource**: Exports data from databases to portal with metadata
- **Configuration Management**: YAML-based config with environment variable overrides
- **Validation Utilities**: Input validation for parameters and data
- **Spatial Utilities**: Geometry processing and spatial reference handling
- **Metadata Management**: Automated XML metadata creation and updates
- **Error Handling**: Custom exceptions with detailed error messages
- **Logging**: Configurable logging with multiple levels
- **Testing**: Comprehensive test coverage with mocking

### Technical Details
- Python 3.8+ support
- PEP 8 compliant code formatting
- Google-style docstrings
- Modern Python packaging with pyproject.toml
- Continuous integration ready
- Type checking with mypy
- Code formatting with black
- Import sorting with isort

### Dependencies
- pandas >= 1.3.0
- geopandas >= 0.10.0
- sqlalchemy >= 1.4.0
- pyodbc >= 4.0.0
- pyyaml >= 5.4.0
- shapely >= 1.8.0
- arcgis >= 2.0.0

### Documentation
- Comprehensive README with usage examples
- API reference documentation
- Configuration guide
- Error handling examples
- Development setup instructions
- Contributing guidelines

### Examples
- Basic usage example with tabular and spatial data
- Environment setup and validation
- Error handling demonstrations
- Configuration examples

### Testing
- Unit tests for all major components
- Integration test framework
- Mock objects for external dependencies
- Test fixtures for common scenarios
- Coverage reporting setup

## [Unreleased]

### Planned Features
- Command-line interface (CLI) tool
- Batch processing capabilities
- Advanced spatial data processing
- Custom metadata templates
- Performance optimizations
- Additional export formats
- Enhanced error recovery
- Monitoring and metrics
- Documentation website
- Video tutorials

---

## Release Notes

### Version 1.0.0

This is the initial release of the psrcdataportal package, representing a complete rewrite and modernization of the original PSRC data export tools. The package has been redesigned from the ground up with the following goals:

1. **Modern Python Practices**: Full type hints, PEP 8 compliance, and modern packaging
2. **Improved Usability**: Simple factory functions and comprehensive documentation
3. **Better Error Handling**: Custom exceptions with detailed error messages
4. **Enhanced Configuration**: Flexible YAML-based configuration with environment variables
5. **Comprehensive Testing**: Full test suite with high coverage
6. **Professional Documentation**: Complete API reference and usage examples

### Breaking Changes from Original Code

This version represents a complete rewrite and is not backward compatible with the original scripts. Key changes include:

- **New API**: Factory functions replace direct class instantiation
- **Configuration**: Environment variables and YAML files replace hard-coded values
- **Error Handling**: Custom exceptions replace generic error handling
- **Validation**: Comprehensive input validation added throughout
- **Structure**: Modular package structure replaces monolithic scripts

### Migration Guide

To migrate from the original scripts:

1. **Environment Setup**: Set up environment variables for credentials
2. **Configuration**: Create YAML configuration files if needed
3. **Code Updates**: Replace direct class usage with factory functions
4. **Error Handling**: Update exception handling to use new custom exceptions
5. **Testing**: Add tests using the new test framework

### Known Limitations

- Spatial data export currently uses shapefiles instead of file geodatabases (ArcPy dependency)
- Some advanced ArcGIS features may require additional configuration
- Large dataset exports may need memory optimization for very large datasets

### Support

For questions, issues, or feature requests:
- GitHub Issues: https://github.com/psrc/psrcdataportal/issues
- Email: datateam@psrc.org
- Documentation: https://psrcdataportal.readthedocs.io/

### Acknowledgments

Special thanks to the PSRC Data Team for their feedback and testing during development, and to the open source GIS community for the excellent tools and libraries that make this package possible.
