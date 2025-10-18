"""Pytest configuration and fixtures"""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openai import OpenAI


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create a mock OpenAI client"""
    client = MagicMock(spec=OpenAI)
    return client


@pytest.fixture
def sample_user_schema() -> dict[str, object]:
    """Sample user schema for testing"""
    return {
        "type": "object",
        "title": "UserModel",
        "properties": {
            "name": {"type": "string", "description": "User's name"},
            "age": {"type": "integer", "description": "User's age", "minimum": 0},
            "email": {
                "type": "string",
                "format": "email",
                "description": "User's email",
            },
        },
        "required": ["name", "age", "email"],
        "additionalProperties": False,
    }


@pytest.fixture
def sample_nested_schema() -> dict[str, object]:
    """Sample nested schema for testing"""
    return {
        "type": "object",
        "title": "ProfileModel",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "profile": {
                "type": "object",
                "title": "UserProfile",
                "properties": {
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                },
                "required": ["first_name", "last_name"],
                "additionalProperties": False,
                "description": "User profile information",
            },
        },
        "required": ["user_id", "profile"],
        "additionalProperties": False,
    }


@pytest.fixture
def sample_array_schema() -> dict[str, object]:
    """Sample schema with array fields"""
    return {
        "type": "object",
        "title": "CourseModel",
        "properties": {
            "course_id": {"type": "string", "description": "Course ID"},
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of topics",
            },
        },
        "required": ["course_id", "topics"],
        "additionalProperties": False,
    }


@pytest.fixture
def sample_enum_schema() -> dict[str, object]:
    """Sample schema with enum field"""
    return {
        "type": "object",
        "title": "ProductModel",
        "properties": {
            "product_id": {"type": "string", "description": "Product ID"},
            "status": {
                "type": "string",
                "enum": ["available", "out_of_stock", "discontinued"],
                "description": "Product status",
            },
        },
        "required": ["product_id", "status"],
        "additionalProperties": False,
    }


@pytest.fixture
def temp_schema_file(tmp_path: Path, sample_user_schema: dict[str, object]) -> Path:
    """Create a temporary schema file"""
    schema_file = tmp_path / "test_schema.json"
    with open(schema_file, "w") as f:
        json.dump(sample_user_schema, f)
    return schema_file


@pytest.fixture
def mock_openai_response() -> object:
    """Mock OpenAI API response"""

    def _create_response(schema_dict: dict[str, object]) -> MagicMock:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(schema_dict)
        return mock_response

    return _create_response
