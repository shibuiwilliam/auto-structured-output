"""Tests for StructureExtractor"""

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from auto_structured_output.extractor import (
    ExtractionError,
    SchemaValidationError,
    StructureExtractor,
)
from auto_structured_output.model_builder import ModelBuilder


class TestStructureExtractor:
    """Test suite for StructureExtractor class"""

    def test_extract_structure_success(self, mock_openai_client, sample_user_schema, mock_openai_response):
        """Test successful structure extraction"""
        extractor = StructureExtractor(mock_openai_client)

        # Mock the OpenAI response
        mock_openai_client.chat.completions.create.return_value = mock_openai_response(sample_user_schema)

        UserModel = extractor.extract_structure("Extract user information")

        assert issubclass(UserModel, BaseModel)
        assert "name" in UserModel.model_fields
        assert "age" in UserModel.model_fields
        assert "email" in UserModel.model_fields

    def test_extract_structure_invalid_schema(self, mock_openai_client, mock_openai_response):
        """Test extraction fails with invalid schema"""
        extractor = StructureExtractor(mock_openai_client)

        # Mock response with invalid schema (missing required fields)
        invalid_schema = {"type": "string"}  # Not an object
        mock_openai_client.chat.completions.create.return_value = mock_openai_response(invalid_schema)

        with pytest.raises(SchemaValidationError):
            extractor.extract_structure("test prompt")

    def test_extract_structure_api_error(self, mock_openai_client):
        """Test extraction handles API errors"""
        extractor = StructureExtractor(mock_openai_client)

        # Mock API error
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(ExtractionError, match="Failed to extract schema"):
            extractor.extract_structure("test prompt")

    def test_save_extracted_json(self, tmp_path, sample_user_schema):
        """Test saving extracted model to JSON file"""

        builder = ModelBuilder()
        UserModel = builder.build_model(sample_user_schema)

        output_file = tmp_path / "user_model.json"

        # Save the model
        StructureExtractor.save_extracted_json(UserModel, output_file)

        # Verify file exists and contains valid JSON
        assert output_file.exists()

        with open(output_file) as f:
            saved_schema = json.load(f)

        assert saved_schema["type"] == "object"
        assert "properties" in saved_schema

    def test_save_extracted_json_creates_directory(self, tmp_path, sample_user_schema):
        """Test that save creates parent directories"""

        builder = ModelBuilder()
        UserModel = builder.build_model(sample_user_schema)

        # Path with non-existent parent directory
        output_file = tmp_path / "nested" / "dir" / "schema.json"

        StructureExtractor.save_extracted_json(UserModel, output_file)

        assert output_file.exists()

    def test_load_from_json(self, temp_schema_file):
        """Test loading schema from JSON file"""
        LoadedModel = StructureExtractor.load_from_json(temp_schema_file)

        assert issubclass(LoadedModel, BaseModel)
        assert "name" in LoadedModel.model_fields
        assert "age" in LoadedModel.model_fields
        assert "email" in LoadedModel.model_fields

    def test_load_from_json_file_not_found(self, tmp_path):
        """Test loading from non-existent file raises error"""
        non_existent_file = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError, match="Schema file not found"):
            StructureExtractor.load_from_json(non_existent_file)

    def test_load_from_json_invalid_json(self, tmp_path):
        """Test loading from file with invalid JSON"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json")

        with pytest.raises(ValueError, match="Expecting value"):
            StructureExtractor.load_from_json(invalid_file)

    def test_load_from_json_invalid_schema(self, tmp_path):
        """Test loading from file with invalid schema"""
        invalid_schema_file = tmp_path / "invalid_schema.json"
        invalid_schema = {"type": "string"}  # Not a valid object schema

        with open(invalid_schema_file, "w") as f:
            json.dump(invalid_schema, f)

        with pytest.raises(SchemaValidationError):
            StructureExtractor.load_from_json(invalid_schema_file)

    def test_save_and_load_roundtrip(self, tmp_path, sample_user_schema):
        """Test save and load roundtrip preserves model"""

        builder = ModelBuilder()
        OriginalModel = builder.build_model(sample_user_schema)

        # Save
        schema_file = tmp_path / "roundtrip.json"
        StructureExtractor.save_extracted_json(OriginalModel, schema_file)

        # Load
        LoadedModel = StructureExtractor.load_from_json(schema_file)

        # Compare field names
        original_fields = set(OriginalModel.model_fields.keys())
        loaded_fields = set(LoadedModel.model_fields.keys())

        assert original_fields == loaded_fields

    def test_save_extracted_json_with_path_object(self, tmp_path, sample_user_schema):
        """Test saving with Path object"""

        builder = ModelBuilder()
        UserModel = builder.build_model(sample_user_schema)

        output_file = Path(tmp_path) / "schema.json"

        StructureExtractor.save_extracted_json(UserModel, output_file)

        assert output_file.exists()

    def test_load_from_json_with_path_object(self, temp_schema_file):
        """Test loading with Path object"""
        path_object = Path(temp_schema_file)

        LoadedModel = StructureExtractor.load_from_json(path_object)

        assert issubclass(LoadedModel, BaseModel)

    def test_extract_structure_with_nested_schema(self, mock_openai_client, sample_nested_schema, mock_openai_response):
        """Test extracting nested structure"""
        extractor = StructureExtractor(mock_openai_client)

        mock_openai_client.chat.completions.create.return_value = mock_openai_response(sample_nested_schema)

        ProfileModel = extractor.extract_structure("Extract profile information")

        assert issubclass(ProfileModel, BaseModel)
        assert "user_id" in ProfileModel.model_fields
        assert "profile" in ProfileModel.model_fields

    def test_extract_structure_with_array_schema(self, mock_openai_client, sample_array_schema, mock_openai_response):
        """Test extracting schema with arrays"""
        extractor = StructureExtractor(mock_openai_client)

        mock_openai_client.chat.completions.create.return_value = mock_openai_response(sample_array_schema)

        CourseModel = extractor.extract_structure("Extract course information")

        assert issubclass(CourseModel, BaseModel)
        assert "topics" in CourseModel.model_fields
