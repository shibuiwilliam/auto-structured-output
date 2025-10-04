"""Tests for SchemaGenerator"""

import pytest

from auto_structured_output.schema_generator import SchemaGenerator


class TestSchemaGenerator:
    """Test suite for SchemaGenerator class"""

    def test_extract_from_prompt(self, mock_openai_client, sample_user_schema, mock_openai_response):
        """Test extracting schema from prompt"""
        generator = SchemaGenerator()

        # Mock the OpenAI response
        mock_openai_client.chat.completions.create.return_value = mock_openai_response(sample_user_schema)

        result = generator.extract_from_prompt("test prompt", mock_openai_client)

        assert result == sample_user_schema
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_extract_from_prompt_empty_response(self, mock_openai_client):
        """Test handling empty response from OpenAI"""
        generator = SchemaGenerator()

        # Mock empty response
        mock_response = type(
            "obj",
            (object,),
            {"choices": [type("obj", (object,), {"message": type("obj", (object,), {"content": None})()})()]},
        )()
        mock_openai_client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="Response from OpenAI API is empty"):
            generator.extract_from_prompt("test prompt", mock_openai_client)

    def test_extract_from_prompt_invalid_json(self, mock_openai_client):
        """Test handling invalid JSON response"""
        generator = SchemaGenerator()

        # Mock invalid JSON response
        mock_response = type(
            "obj",
            (object,),
            {"choices": [type("obj", (object,), {"message": type("obj", (object,), {"content": "invalid json"})()})()]},
        )()
        mock_openai_client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="not valid JSON"):
            generator.extract_from_prompt("test prompt", mock_openai_client)

    def test_validate_schema_valid(self, sample_user_schema):
        """Test validating a valid schema"""
        generator = SchemaGenerator()
        result = generator.validate_schema(sample_user_schema)
        assert result == sample_user_schema

    def test_validate_schema_missing_type(self):
        """Test validation fails when type is missing"""
        generator = SchemaGenerator()
        schema = {"properties": {"name": {"type": "string"}}}

        with pytest.raises(ValueError, match="must have a 'type' field"):
            generator.validate_schema(schema)

    def test_validate_schema_invalid_type(self):
        """Test validation fails when type is not 'object'"""
        generator = SchemaGenerator()
        schema = {"type": "string", "properties": {}}

        with pytest.raises(ValueError, match="must be of type 'object'"):
            generator.validate_schema(schema)

    def test_validate_schema_missing_properties(self):
        """Test validation fails when properties are missing"""
        generator = SchemaGenerator()
        schema = {"type": "object"}

        with pytest.raises(ValueError, match="must have a 'properties' field"):
            generator.validate_schema(schema)

    def test_validate_schema_invalid_required(self):
        """Test validation fails when required field is not a list"""
        generator = SchemaGenerator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": "name",  # Should be a list
        }

        with pytest.raises(ValueError, match="must be a list"):
            generator.validate_schema(schema)

    def test_validate_schema_required_field_not_in_properties(self):
        """Test validation fails when required field is not defined"""
        generator = SchemaGenerator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name", "age"],  # age not in properties
        }

        with pytest.raises(ValueError, match="not defined in properties"):
            generator.validate_schema(schema)

    def test_validate_properties_unsupported_type(self):
        """Test validation fails with unsupported type"""
        generator = SchemaGenerator()
        schema = {
            "type": "object",
            "properties": {"field": {"type": "unknown_type"}},
        }

        with pytest.raises(ValueError, match="not supported"):
            generator.validate_schema(schema)

    def test_validate_nested_object(self, sample_nested_schema):
        """Test validating nested object schema"""
        generator = SchemaGenerator()
        result = generator.validate_schema(sample_nested_schema)
        assert result == sample_nested_schema

    def test_validate_array_schema(self, sample_array_schema):
        """Test validating array schema"""
        generator = SchemaGenerator()
        result = generator.validate_schema(sample_array_schema)
        assert result == sample_array_schema

    def test_validate_anyof_invalid(self):
        """Test validation fails when anyOf is not a list"""
        generator = SchemaGenerator()
        schema = {
            "type": "object",
            "properties": {"field": {"anyOf": "invalid"}},  # Should be a list
        }

        with pytest.raises(ValueError, match="must be a list"):
            generator.validate_schema(schema)
