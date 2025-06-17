"""Tests for validation utilities."""

import pytest
import pandas as pd

from psrcdataportal.utils.validation import (
    validate_required_parameters,
    validate_share_level,
    validate_tags,
    validate_groups,
    validate_dataframe,
    validate_sql_query,
    validate_resource_parameters,
)
from psrcdataportal.exceptions import ValidationError


class TestValidateRequiredParameters:
    """Test validate_required_parameters function."""
    
    def test_valid_parameters(self):
        """Test with all required parameters present."""
        params = {'title': 'Test', 'tags': 'test,sample'}
        required = ['title', 'tags']
        
        # Should not raise an exception
        validate_required_parameters(params, required)
    
    def test_missing_parameters(self):
        """Test with missing required parameters."""
        params = {'title': 'Test'}
        required = ['title', 'tags']
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_parameters(params, required)
        
        assert "Missing parameters: tags" in str(exc_info.value)
    
    def test_empty_parameters(self):
        """Test with empty required parameters."""
        params = {'title': 'Test', 'tags': ''}
        required = ['title', 'tags']
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_parameters(params, required)
        
        assert "Empty parameters: tags" in str(exc_info.value)


class TestValidateShareLevel:
    """Test validate_share_level function."""
    
    @pytest.mark.parametrize("level,expected", [
        ("everyone", "everyone"),
        ("org", "org"),
        ("private", "private"),
        ("EVERYONE", "everyone"),
        ("  org  ", "org"),
    ])
    def test_valid_share_levels(self, level, expected):
        """Test valid share levels."""
        result = validate_share_level(level)
        assert result == expected
    
    def test_invalid_share_level(self):
        """Test invalid share level."""
        with pytest.raises(ValidationError) as exc_info:
            validate_share_level("invalid")
        
        assert "Invalid share level" in str(exc_info.value)
    
    def test_non_string_share_level(self):
        """Test non-string share level."""
        with pytest.raises(ValidationError) as exc_info:
            validate_share_level(123)
        
        assert "Share level must be a string" in str(exc_info.value)


class TestValidateTags:
    """Test validate_tags function."""
    
    def test_string_tags_comma_separated(self):
        """Test comma-separated string tags."""
        result = validate_tags("tag1,tag2,tag3")
        assert result == ["tag1", "tag2", "tag3"]
    
    def test_string_tags_semicolon_separated(self):
        """Test semicolon-separated string tags."""
        result = validate_tags("tag1;tag2;tag3")
        assert result == ["tag1", "tag2", "tag3"]
    
    def test_list_tags(self):
        """Test list of tags."""
        result = validate_tags(["tag1", "tag2", "tag3"])
        assert result == ["tag1", "tag2", "tag3"]
    
    def test_tags_with_whitespace(self):
        """Test tags with whitespace."""
        result = validate_tags("  tag1  ,  tag2  ,  tag3  ")
        assert result == ["tag1", "tag2", "tag3"]
    
    def test_trailing_comma(self):
        """Test tags with trailing comma."""
        result = validate_tags("tag1,tag2,tag3,")
        assert result == ["tag1", "tag2", "tag3"]
    
    def test_empty_tags(self):
        """Test empty tags."""
        with pytest.raises(ValidationError) as exc_info:
            validate_tags("")
        
        assert "At least one valid tag is required" in str(exc_info.value)
    
    def test_invalid_tags_type(self):
        """Test invalid tags type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_tags(123)
        
        assert "Tags must be a string or list of strings" in str(exc_info.value)


class TestValidateGroups:
    """Test validate_groups function."""
    
    def test_string_groups(self):
        """Test semicolon-separated string groups."""
        result = validate_groups("group1;group2;group3")
        assert result == ["group1", "group2", "group3"]
    
    def test_list_groups(self):
        """Test list of groups."""
        result = validate_groups(["group1", "group2", "group3"])
        assert result == ["group1", "group2", "group3"]
    
    def test_empty_groups(self):
        """Test empty groups."""
        result = validate_groups("")
        assert result == []
    
    def test_groups_with_whitespace(self):
        """Test groups with whitespace."""
        result = validate_groups("  group1  ;  group2  ")
        assert result == ["group1", "group2"]


class TestValidateDataframe:
    """Test validate_dataframe function."""
    
    def test_valid_dataframe(self, sample_dataframe):
        """Test valid DataFrame."""
        # Should not raise an exception
        validate_dataframe(sample_dataframe)
    
    def test_empty_dataframe(self):
        """Test empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValidationError) as exc_info:
            validate_dataframe(df)
        
        assert "DataFrame is empty" in str(exc_info.value)
    
    def test_insufficient_rows(self, sample_dataframe):
        """Test DataFrame with insufficient rows."""
        with pytest.raises(ValidationError) as exc_info:
            validate_dataframe(sample_dataframe, min_rows=10)
        
        assert "minimum required: 10" in str(exc_info.value)
    
    def test_non_dataframe(self):
        """Test non-DataFrame input."""
        with pytest.raises(ValidationError) as exc_info:
            validate_dataframe("not a dataframe")
        
        assert "Input must be a pandas DataFrame" in str(exc_info.value)


class TestValidateSqlQuery:
    """Test validate_sql_query function."""
    
    def test_valid_select_query(self):
        """Test valid SELECT query."""
        sql = "SELECT * FROM table_name"
        result = validate_sql_query(sql)
        assert result == sql
    
    def test_query_with_whitespace(self):
        """Test query with leading/trailing whitespace."""
        sql = "  SELECT * FROM table_name  "
        result = validate_sql_query(sql)
        assert result == "SELECT * FROM table_name"
    
    def test_non_select_query(self):
        """Test non-SELECT query."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sql_query("UPDATE table_name SET col = 1")
        
        assert "SQL query must start with SELECT" in str(exc_info.value)
    
    def test_empty_query(self):
        """Test empty query."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sql_query("")
        
        assert "SQL query cannot be empty" in str(exc_info.value)
    
    def test_non_string_query(self):
        """Test non-string query."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sql_query(123)
        
        assert "SQL query must be a string" in str(exc_info.value)


class TestValidateResourceParameters:
    """Test validate_resource_parameters function."""
    
    def test_valid_parameters(self):
        """Test valid resource parameters."""
        params = {
            'title': 'Test Resource',
            'tags': 'test,sample',
            'share_level': 'org',
            'spatial_data': True,
            'allow_edits': False
        }
        
        result = validate_resource_parameters(params)
        
        assert result['title'] == 'Test Resource'
        assert result['tags'] == ['test', 'sample']
        assert result['share_level'] == 'org'
        assert result['spatial_data'] is True
        assert result['allow_edits'] is False
    
    def test_missing_required_parameters(self):
        """Test missing required parameters."""
        params = {'title': 'Test Resource'}
        
        with pytest.raises(ValidationError) as exc_info:
            validate_resource_parameters(params)
        
        assert "Missing parameters: tags" in str(exc_info.value)
    
    def test_invalid_share_level(self):
        """Test invalid share level."""
        params = {
            'title': 'Test Resource',
            'tags': 'test',
            'share_level': 'invalid'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_resource_parameters(params)
        
        assert "Invalid share level" in str(exc_info.value)
    
    def test_invalid_boolean_parameter(self):
        """Test invalid boolean parameter."""
        params = {
            'title': 'Test Resource',
            'tags': 'test',
            'allow_edits': 'yes'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_resource_parameters(params)
        
        assert "must be a boolean" in str(exc_info.value)
    
    def test_srid_conversion(self):
        """Test SRID string to integer conversion."""
        params = {
            'title': 'Test Resource',
            'tags': 'test',
            'srid': '2285'
        }
        
        result = validate_resource_parameters(params)
        assert result['srid'] == 2285
    
    def test_invalid_srid(self):
        """Test invalid SRID."""
        params = {
            'title': 'Test Resource',
            'tags': 'test',
            'srid': 'invalid'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_resource_parameters(params)
        
        assert "SRID must be a valid integer" in str(exc_info.value)
