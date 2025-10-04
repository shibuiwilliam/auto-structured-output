# CLAUDE.md - Auto Structured Output Library

## Overview

This project is a Python library that automatically extracts output formats from natural language prompts and defines them as OpenAI Structured Outputs.

For OpenAI Structured Outputs specification, see:
https://platform.openai.com/docs/guides/structured-outputs

### Supported Schemas

Structured Outputs supports a subset of the JSON Schema language.

**Supported types:**
- String
- Number
- Boolean
- Integer
- Object
- Array
- Enum
- anyOf

**Supported properties:**

String properties:
- `pattern` — A regular expression that the string must match
- `format` — Predefined formats: date-time, time, date, duration, email, hostname, ipv4, ipv6, uuid

Number properties:
- `multipleOf` — The number must be a multiple of this value
- `maximum` — The number must be less than or equal to this value
- `exclusiveMaximum` — The number must be less than this value
- `minimum` — The number must be greater than or equal to this value
- `exclusiveMinimum` — The number must be greater than this value

Array properties:
- `minItems` — The array must have at least this many items
- `maxItems` — The array must have at most this many items

## Key Features

1. **Natural Language Prompt Parsing**: Identifies output format instructions within prompts
2. **Automatic Structured Output Generation**: Extracts output structure in JSON format using OpenAI API
3. **Conversion to Pydantic Models**: Automatically converts extracted structure to pydantic.BaseModel classes
4. **OpenAI API Integration**: Uses generated models as response_format parameter
5. **Schema Persistence**: Save and load schemas as JSON files for reuse across sessions

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

## Directory Structure

```
auto-structured-output/
├── src/
│   ├── __init__.py
│   ├── extractor.py          # Main extraction logic with save/load
│   ├── schema_generator.py   # JSON schema generation
│   ├── model_builder.py      # Pydantic model construction
│   ├── prompts.py            # OpenAI prompt templates
│   └── validators.py         # Schema validation logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_extractor.py     # 14 tests
│   ├── test_schema_generator.py  # 13 tests
│   ├── test_model_builder.py     # 12 tests
│   ├── test_validators.py    # 28 tests
│   └── README.md
├── examples/
│   ├── __init__.py
│   ├── basic_usage.py        # 5 basic examples
│   ├── advanced_examples.py  # 6 advanced examples
│   ├── save_load_schema.py   # Save/load functionality
│   └── README.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── .gitignore
├── .env.example
└── README.md
```

## Implementation Details

### 1. StructureExtractor Class (`extractor.py`)

Main class for extracting structure from natural language prompts.

```python
from auto_structured_output.extractor import StructureExtractor
from openai import OpenAI

# Initialize with OpenAI client
client = OpenAI(api_key="your-api-key")
extractor = StructureExtractor(client)

# Extract structure from prompt
UserModel = extractor.extract_structure("Extract user information with name, age, and email")

# Use in OpenAI API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate user data"}],
    response_format=UserModel
)

# Get structured response
user_data = response.choices[0].message.parsed
```

**Static Methods for Schema Persistence:**

```python
# Save extracted model to JSON file
StructureExtractor.save_extracted_json(UserModel, "user_schema.json")

# Load model from JSON file
LoadedModel = StructureExtractor.load_from_json("user_schema.json")
```

### 2. SchemaGenerator Class (`schema_generator.py`)

Handles JSON schema generation and validation using OpenAI API.

```python
from auto_structured_output.schema_generator import SchemaGenerator
from openai import OpenAI

client = OpenAI(api_key="your-api-key")
generator = SchemaGenerator()

# Extract schema from prompt
schema = generator.extract_from_prompt(
    "Extract user with name (string), age (integer), and email (string with email format)",
    client
)

# Validate schema
validated_schema = generator.validate_schema(schema)
```

Uses centralized prompt templates from `prompts.py` for consistent schema extraction.

### 3. ModelBuilder Class (`model_builder.py`)

Converts JSON schemas to Pydantic BaseModel classes using `pydantic.create_model()`.

```python
from auto_structured_output.model_builder import ModelBuilder

builder = ModelBuilder()

schema = {
    "type": "object",
    "title": "UserModel",
    "properties": {
        "name": {"type": "string", "description": "User's name"},
        "age": {"type": "integer", "description": "User's age", "minimum": 0},
        "email": {"type": "string", "format": "email", "description": "User's email"}
    },
    "required": ["name", "age", "email"],
    "additionalProperties": False
}

UserModel = builder.build_model(schema)
```

**Type Mapping:**
- string → str
- integer → int
- number → float
- boolean → bool
- array → list[T]
- object → nested BaseModel
- enum → Literal[...]

**Format Support:**
- date-time → datetime
- date → date
- time → time
- email → EmailStr
- uuid → UUID

### 4. SchemaValidator Class (`validators.py`)

Comprehensive validation utilities for JSON schemas.

```python
from auto_structured_output.validators import SchemaValidator

# Validate type
SchemaValidator.validate_type("string")  # Returns True

# Validate string format
SchemaValidator.validate_string_format("email")  # Returns True

# Validate number constraints
SchemaValidator.validate_number_constraints({
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.5
})

# Validate array constraints
SchemaValidator.validate_array_constraints({
    "minItems": 1,
    "maxItems": 10
})

# Validate enum
SchemaValidator.validate_enum(["active", "inactive", "suspended"])

# Validate required fields
SchemaValidator.validate_required_fields(
    required=["name", "age"],
    properties={"name": {"type": "string"}, "age": {"type": "integer"}}
)
```

## Usage Examples

### Basic Usage

```python
from openai import OpenAI
from auto_structured_output.extractor import StructureExtractor

# Initialize
client = OpenAI(api_key="your-api-key")
extractor = StructureExtractor(client)

# Extract structure
UserModel = extractor.extract_structure(
    "Extract user information with name, age, and email address"
)

# Use with OpenAI API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate a sample user"}],
    response_format=UserModel
)

user = response.choices[0].message.parsed
print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")
```

### Enum Fields

```python
StatusModel = extractor.extract_structure(
    "Extract product status: available, out_of_stock, or discontinued"
)

# Generated model uses Literal type
# status: Literal["available", "out_of_stock", "discontinued"]
```

### Nested Objects

```python
ProfileModel = extractor.extract_structure("""
Extract user profile with:
- user_id (string)
- profile object containing:
  - first_name (string)
  - last_name (string)
  - bio (optional string)
""")

# Creates nested BaseModel classes automatically
```

### Arrays

```python
CourseModel = extractor.extract_structure("""
Extract course information with:
- course_id (string)
- topics (list of strings)
- students (list of student objects with name and grade)
""")

# Handles both simple arrays and arrays of objects
```

### Date/Time Formats

```python
EventModel = extractor.extract_structure("""
Extract event with:
- event_date (date format)
- event_datetime (datetime format)
- event_time (time format)
""")

# Maps to appropriate Python types: date, datetime, time
```

### Save and Load Schemas

```python
# Extract and save
UserModel = extractor.extract_structure("Extract user with name and email")
StructureExtractor.save_extracted_json(UserModel, "schemas/user.json")

# Load in another session
LoadedUserModel = StructureExtractor.load_from_json("schemas/user.json")

# Use the loaded model
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate user"}],
    response_format=LoadedUserModel
)
```

## Testing

The library includes a comprehensive test suite with **74 tests** covering all major functionality.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_extractor.py
```

### Test Coverage

- **test_extractor.py** (14 tests): Structure extraction, save/load functionality, error handling
- **test_schema_generator.py** (13 tests): Schema extraction, validation, edge cases
- **test_model_builder.py** (12 tests): Model building with various types and constraints
- **test_validators.py** (28 tests): All validation utilities and constraint checking

All tests use mocks to avoid actual OpenAI API calls during testing.

## Error Handling

```python
from auto_structured_output.extractor import (
    ExtractionError,
    SchemaValidationError
)

try:
    model = extractor.extract_structure("invalid prompt")
except SchemaValidationError as e:
    print(f"Schema validation failed: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

**Exception Hierarchy:**
- `ExtractionError` - Base exception for extraction errors
- `SchemaValidationError` - Schema validation failures (inherits from ExtractionError)

## Advanced Features

### 1. anyOf Support

```python
schema = {
    "type": "object",
    "properties": {
        "value": {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"}
            ]
        }
    }
}

# Maps to Union[str, int]
```

### 2. Validation Constraints

```python
schema = {
    "type": "object",
    "properties": {
        "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 150
        },
        "score": {
            "type": "number",
            "multipleOf": 0.5,
            "exclusiveMinimum": 0,
            "exclusiveMaximum": 100
        },
        "tags": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10
        }
    }
}
```

### 3. String Patterns

```python
schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_]{3,20}$"
        }
    }
}
```

## Dependencies

```toml
[project]
name = "auto-structured-output"
version = "0.1.0"
description = "Automatically extract structured outputs from natural language prompts"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "openai>=2.1.0",
    "pydantic>=2.11.9",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-mock>=3.15.1",
    "ruff>=0.13.3",
    "mypy>=1.18.2",
]
```

## Development

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

All source code is in the `src/auto_structured_output/` directory:
- Use `from auto_structured_output.extractor import StructureExtractor` for imports
- All code, comments, and documentation are in English
- Type hints are used throughout (Python 3.12+ syntax)

## Best Practices

1. **Reuse Schemas**: Save frequently used schemas to JSON files and load them as needed
2. **Validation**: Always validate schemas before building models
3. **Error Handling**: Catch specific exceptions for better error messages
4. **Prompt Design**: Be specific in prompts about required vs optional fields
5. **Type Safety**: Use the generated models with type checkers like mypy

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
