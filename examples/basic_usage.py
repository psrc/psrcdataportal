"""Basic usage example for psrcdataportal package.

This example demonstrates how to use the psrcdataportal package to export
data from a PSRC database to ArcGIS Online.

Prerequisites:
1. Set up environment variables (see .env.example)
2. Ensure you have access to PSRC databases
3. Have an ArcGIS Online account with appropriate permissions
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import psrcdataportal
sys.path.insert(0, str(Path(__file__).parent.parent))

import psrcdataportal as psrc


def main():
    """Main example function."""
    print("PSRC Data Portal - Basic Usage Example")
    print("=" * 40)
    
    # Step 1: Validate environment setup
    print("1. Validating environment setup...")
    if not psrc.validate_environment():
        print("❌ Environment validation failed!")
        print("Please ensure the following environment variables are set:")
        print("- PSRC_DB_SERVER")
        print("- PSRC_DB_NAME") 
        print("- PSRC_PORTAL_USERNAME")
        print("- PSRC_PORTAL_PASSWORD")
        print("\nSee .env.example for a template.")
        return False
    
    print("✅ Environment validation passed!")
    
    # Step 2: Create database connector
    print("\n2. Creating database connector...")
    try:
        db_conn = psrc.create_database_connector()
        print(f"✅ Connected to database: {db_conn.server}/{db_conn.database}")
        
        # Test the connection
        if db_conn.test_connection():
            print("✅ Database connection test passed!")
        else:
            print("❌ Database connection test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create database connector: {e}")
        return False
    
    # Step 3: Create portal connector
    print("\n3. Creating portal connector...")
    try:
        portal_conn = psrc.create_portal_connector()
        print(f"✅ Connected to portal: {portal_conn.portal_url}")
        
        # Test the connection
        if portal_conn.test_connection():
            print("✅ Portal connection test passed!")
        else:
            print("❌ Portal connection test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create portal connector: {e}")
        return False
    
    # Step 4: Example 1 - Export tabular data
    print("\n4. Example 1: Exporting tabular data...")
    try:
        # Define resource parameters for tabular data
        tabular_params = {
            'title': 'Example Tabular Dataset',
            'tags': ['example', 'test', 'tabular'],
            'share_level': 'org',  # Share with organization only
            'spatial_data': False,
            'snippet': 'Example tabular dataset exported using psrcdataportal',
            'metadata': {
                'contact_name': 'Data Team',
                'contact_email': 'datateam@psrc.org',
                'organization_name': 'Puget Sound Regional Council',
                'summary': 'This is an example dataset for demonstration purposes.',
                'data_source': 'PSRC Database',
                'time_period': '2024'
            }
        }
        
        # Define data source (using a simple table)
        tabular_source = {
            'sql_query': '''
                SELECT TOP 10
                    'Sample' as category,
                    ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as id,
                    GETDATE() as created_date,
                    'Example data row' as description
            ''',
            'is_simple': False
        }
        
        # Create and export the resource
        print("   Creating tabular resource...")
        tabular_resource = psrc.create_portal_resource(
            portal_conn, 
            db_conn, 
            tabular_params, 
            tabular_source
        )
        
        print("   Exporting tabular data...")
        tabular_resource.export()
        print("✅ Tabular data export completed!")
        
    except Exception as e:
        print(f"❌ Tabular data export failed: {e}")
        # Continue with other examples
    
    # Step 5: Example 2 - Export spatial data (if available)
    print("\n5. Example 2: Exporting spatial data...")
    try:
        # Define resource parameters for spatial data
        spatial_params = {
            'title': 'Example Spatial Dataset',
            'tags': ['example', 'test', 'spatial', 'gis'],
            'share_level': 'org',
            'spatial_data': True,
            'allow_edits': False,
            'srid': 2285,  # Washington State Plane South (feet)
            'snippet': 'Example spatial dataset exported using psrcdataportal',
            'metadata': {
                'contact_name': 'GIS Team',
                'contact_email': 'gis@psrc.org',
                'organization_name': 'Puget Sound Regional Council',
                'summary': 'This is an example spatial dataset for demonstration purposes.',
                'data_source': 'PSRC Spatial Database',
                'time_period': '2024'
            }
        }
        
        # Define spatial data source
        # Note: This example assumes you have a spatial table available
        # Modify the table_name and feature_dataset as needed
        spatial_source = {
            'table_name': 'example_spatial_layer',
            'feature_dataset': 'Examples',
            'is_simple': True,
            'fields_to_exclude': ['internal_id', 'temp_field']
        }
        
        print("   Creating spatial resource...")
        spatial_resource = psrc.create_portal_resource(
            portal_conn,
            db_conn,
            spatial_params,
            spatial_source
        )
        
        print("   Exporting spatial data...")
        spatial_resource.export()
        print("✅ Spatial data export completed!")
        
    except Exception as e:
        print(f"❌ Spatial data export failed: {e}")
        print("   This is expected if the example spatial table doesn't exist.")
    
    # Step 6: Clean up connections
    print("\n6. Cleaning up connections...")
    try:
        db_conn.close()
        portal_conn.close()
        print("✅ Connections closed successfully!")
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Basic usage example completed!")
    print("\nNext steps:")
    print("- Modify the examples above for your specific data")
    print("- Check the exported items in your ArcGIS Online organization")
    print("- Explore advanced features in other example files")
    
    return True


def check_prerequisites():
    """Check if prerequisites are met."""
    print("Checking prerequisites...")
    
    # Check if environment variables are set
    required_vars = [
        'PSRC_DB_SERVER',
        'PSRC_DB_NAME',
        'PSRC_PORTAL_USERNAME',
        'PSRC_PORTAL_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True


if __name__ == "__main__":
    # Set up logging for the example
    psrc.setup_logging(level="INFO")
    
    print("PSRC Data Portal Package - Basic Usage Example")
    print("This example demonstrates basic package functionality.\n")
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\nPlease set up your environment variables before running this example.")
        print("See .env.example for a template.")
        sys.exit(1)
    
    # Run the main example
    success = main()
    
    if success:
        print("\n🎉 Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed. Please check the error messages above.")
        sys.exit(1)
