# Auto Structured Output

Automatically extract structured outputs from natural language prompts using OpenAI's Structured Outputs API.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-74%20passed-brightgreen.svg)]()

## Overview

`auto-structured-output` is a Python library that bridges the gap between natural language descriptions and structured data extraction. It uses OpenAI's API to automatically generate JSON schemas from your prompts and converts them into Pydantic models, enabling type-safe structured outputs.

### Key Features

- 🤖 **Automatic Schema Generation**: Extracts JSON schemas from natural language descriptions
- 🔄 **Pydantic Model Creation**: Dynamically generates Pydantic `BaseModel` classes
- 💾 **Schema Persistence**: Save and load schemas as JSON files for reuse
- ✅ **Comprehensive Validation**: Built-in validators for all JSON Schema types and constraints
- 🎯 **Type Safety**: Full support for nested objects, arrays, enums, and format specifications
- 📦 **OpenAI Integration**: Works seamlessly with OpenAI's Structured Outputs API

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.12 or higher
- OpenAI API key

## Quick Start

```python
from openai import OpenAI
from auto_structured_output.extractor import StructureExtractor

# Initialize
client = OpenAI(api_key="your-api-key")
extractor = StructureExtractor(client)

# Extract structure from natural language
UserModel = extractor.extract_structure(
    "Extract user information with name (string), age (integer), and email (email format)"
)

# Use with OpenAI API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate a sample user"}],
    response_format=UserModel
)

# Get structured, validated data
user = response.choices[0].message.parsed
print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")
```

## Usage Examples

### Basic Types

```python
# Simple model with basic types
ProductModel = extractor.extract_structure("""
Extract product with:
- product_id (string)
- name (string)
- price (number)
- in_stock (boolean)
""")
```

### Enum Fields

```python
# Status with specific allowed values
StatusModel = extractor.extract_structure(
    "Extract status: active, inactive, or suspended"
)

# Generated model uses Literal type:
# status: Literal["active", "inactive", "suspended"]
```

### Nested Objects

```python
# Complex nested structures
ProfileModel = extractor.extract_structure("""
Extract user profile with:
- user_id (string)
- profile object containing:
  - first_name (string)
  - last_name (string)
  - bio (optional string)
  - settings object containing:
    - theme (light or dark, default: light)
    - notifications (boolean)
""")
```

### Arrays

```python
# Simple arrays
CourseModel = extractor.extract_structure("""
Extract course with:
- course_id (string)
- topics (array of strings)
""")

# Arrays of objects
OrderModel = extractor.extract_structure("""
Extract order with:
- order_id (string)
- items (array of objects with product_id and quantity)
""")
```

### Date/Time Formats

```python
# Format specifications
EventModel = extractor.extract_structure("""
Extract event with:
- event_date (date format)
- event_datetime (datetime format)
- event_time (time format)
- event_id (uuid format)
""")

# Automatically maps to Python types: date, datetime, time, UUID
```

### Validation Constraints

```python
# Number constraints
MetricsModel = extractor.extract_structure("""
Extract metrics with:
- age (integer, minimum: 0, maximum: 150)
- score (number, must be multiple of 0.5)
- rating (number, between 0 and 5)
""")

# Array constraints
TagsModel = extractor.extract_structure("""
Extract tags (array of strings, minimum 1 item, maximum 10 items)
""")
```

### Save and Load Schemas

```python
# Extract and save for later reuse
UserModel = extractor.extract_structure("Extract user with name and email")
StructureExtractor.save_extracted_json(UserModel, "schemas/user.json")

# Load in another session (no API call needed)
LoadedUserModel = StructureExtractor.load_from_json("schemas/user.json")

# Use the loaded model
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate user data"}],
    response_format=LoadedUserModel
)
```

## Advanced Usage

### Direct Schema Building

```python
from auto_structured_output.model_builder import ModelBuilder

builder = ModelBuilder()

schema = {
    "type": "object",
    "title": "UserModel",
    "properties": {
        "name": {"type": "string", "description": "User's name"},
        "age": {"type": "integer", "description": "User's age", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age", "email"],
    "additionalProperties": False
}

UserModel = builder.build_model(schema)
```

### Schema Validation

```python
from auto_structured_output.validators import SchemaValidator

# Validate types
SchemaValidator.validate_type("string")

# Validate formats
SchemaValidator.validate_string_format("email")

# Validate constraints
SchemaValidator.validate_number_constraints({
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.5
})

# Validate enums
SchemaValidator.validate_enum(["active", "inactive", "suspended"])
```

### Error Handling

```python
from auto_structured_output.extractor import (
    ExtractionError,
    SchemaValidationError
)

try:
    model = extractor.extract_structure("Extract user data")
except SchemaValidationError as e:
    print(f"Schema validation failed: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

## Supported Types and Features

### JSON Schema Types

- ✅ String (with pattern and format support)
- ✅ Number (with min/max and multipleOf constraints)
- ✅ Integer (with min/max constraints)
- ✅ Boolean
- ✅ Object (nested structures)
- ✅ Array (with minItems/maxItems constraints)
- ✅ Enum (mapped to Literal types)
- ✅ anyOf (mapped to Union types)

### String Formats

- `date-time` → `datetime`
- `date` → `date`
- `time` → `time`
- `email` → `EmailStr`
- `uuid` → `UUID`
- `hostname`, `ipv4`, `ipv6`
- Custom patterns with regex

### Validation Constraints

**Numbers:**
- `minimum`, `maximum`
- `exclusiveMinimum`, `exclusiveMaximum`
- `multipleOf`

**Arrays:**
- `minItems`, `maxItems`
- Item type validation

**Strings:**
- `pattern` (regex)
- `format` (predefined formats)

## Architecture

```
┌─────────────────────┐
│  Natural Language   │
│      Prompt         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Schema Extraction  │ ← OpenAI API (gpt-4o)
│   (SchemaGenerator) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   JSON Schema       │
│   (Validation)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Pydantic Model     │
│     Builder         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BaseModel Class    │
└─────────────────────┘
```

## Testing

The library includes a comprehensive test suite with **74 tests** covering all major functionality.

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=auto_structured_output tests/

# Run specific test file
pytest tests/test_extractor.py

# Run with verbose output
pytest -v tests/
```

### Test Coverage

- **test_extractor.py** (14 tests): Structure extraction, save/load, error handling
- **test_schema_generator.py** (13 tests): Schema extraction, validation, edge cases
- **test_model_builder.py** (12 tests): Model building with various types
- **test_validators.py** (28 tests): All validation utilities

All tests use mocks to avoid actual OpenAI API calls.

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install with dev dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make typecheck

# Run all checks
make check
```

### Project Structure

```
auto-structured-output/
├── auto_structured_output/    # Main package
│   ├── __init__.py
│   ├── extractor.py           # Main API
│   ├── schema_generator.py    # Schema extraction
│   ├── model_builder.py       # Pydantic model building
│   ├── prompts.py             # Prompt templates
│   └── validators.py          # Validation utilities
├── tests/                     # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_extractor.py
│   ├── test_schema_generator.py
│   ├── test_model_builder.py
│   └── test_validators.py
├── examples/                  # Usage examples
│   ├── basic_usage.py
│   ├── advanced_examples.py
│   └── save_load_schema.py
├── pyproject.toml             # Project configuration
└── README.md
```

## Examples

Check out the `examples/` directory for more detailed examples:

- **`basic_usage.py`**: 5 basic examples covering common use cases
- **`advanced_examples.py`**: 6 advanced examples with complex structures
- **`save_load_schema.py`**: Schema persistence and versioning

## Best Practices

1. **Reuse Schemas**: Save frequently used schemas to JSON files to avoid redundant API calls
2. **Be Specific**: Provide clear descriptions in prompts for better schema generation
3. **Validate Early**: Use validation before building models to catch errors early
4. **Handle Errors**: Always catch and handle `SchemaValidationError` and `ExtractionError`
5. **Type Safety**: Use generated models with type checkers like mypy for better code quality

## API Reference

### StructureExtractor

Main class for extracting structures from natural language.

```python
class StructureExtractor:
    def __init__(self, client: OpenAI | AzureOpenAI)

    def extract_structure(
        self,
        prompt: str,
        model_name: str | None = None
    ) -> type[BaseModel]

    @staticmethod
    def save_extracted_json(
        model: type[BaseModel],
        file_path: str | Path
    ) -> None

    @staticmethod
    def load_from_json(file_path: str | Path) -> type[BaseModel]
```

### SchemaGenerator

Handles JSON schema extraction and validation.

```python
class SchemaGenerator:
    def extract_from_prompt(
        self,
        prompt: str,
        client: OpenAI | AzureOpenAI
    ) -> dict[str, Any]

    def validate_schema(self, schema: dict[str, Any]) -> dict[str, Any]
```

### ModelBuilder

Converts JSON schemas to Pydantic models.

```python
class ModelBuilder:
    def build_model(
        self,
        schema: dict[str, Any],
        model_name: str | None = None
    ) -> type[BaseModel]
```

### SchemaValidator

Validation utilities for JSON schemas.

```python
class SchemaValidator:
    @staticmethod
    def validate_type(type_value: str | list) -> bool

    @staticmethod
    def validate_string_format(format_value: str) -> bool

    @staticmethod
    def validate_number_constraints(constraints: dict) -> bool

    @staticmethod
    def validate_array_constraints(constraints: dict) -> bool

    @staticmethod
    def validate_enum(enum_values: list) -> bool

    @staticmethod
    def validate_required_fields(
        required: list,
        properties: dict
    ) -> bool
```

## Environment Variables

Create a `.env` file in your project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Azure OpenAI Configuration
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your-azure-api-key
# OPENAI_API_VERSION=2024-02-15-preview
```

## Troubleshooting

### Common Issues

**Q: Schema validation fails with "must be of type 'object'"**
```python
# Make sure your prompt describes an object structure, not a simple type
# ❌ Bad: "Extract a string"
# ✅ Good: "Extract object with name (string)"
```

**Q: Generated model doesn't match expected structure**
```python
# Be more specific in your prompt
# ❌ Vague: "Extract user data"
# ✅ Specific: "Extract user with name (string), age (integer minimum 0), email (email format)"
```

**Q: OpenAI API errors**
```python
# Check your API key and model access
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Make sure you have access to gpt-4o model
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
