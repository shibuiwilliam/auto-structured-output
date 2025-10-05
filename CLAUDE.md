# CLAUDE.md - Auto Structured Output Library

## Overview

This project is a Python library that automatically extracts output formats from natural language prompts and defines them as OpenAI Structured Outputs. It features two modes of operation: standard mode for clear prompts and high reasoning mode for inferring structure from vague requirements.

**Current Status:**
- **Version:** 0.1.0
- **Tests:** 74 passing (14 extractor + 13 schema_generator + 12 model_builder + 35 validators)
- **Source Files:** 7 modules (~1,207 total lines)
- **Python Version:** 3.12+
- **Build System:** hatchling
- **Package Manager:** uv (recommended) or pip

For OpenAI Structured Outputs specification, see:
https://platform.openai.com/docs/guides/structured-outputs

### Supported Schemas

Structured Outputs supports a subset of the JSON Schema language, defined by the `SupportedType` and `StringFormat` enums in `model.py`.

**Supported types (SupportedType enum):**
- String
- Number
- Boolean
- Integer
- Object
- Array
- Null
- Enum
- anyOf

**Supported string formats (StringFormat enum):**
- date-time → datetime
- date → date
- time → time
- duration → str
- email → str
- hostname → str
- ipv4 → str
- ipv6 → str
- uuid → str

**Note:** The `uri` format is NOT supported by OpenAI Structured Outputs and should be avoided.

**Number/Integer constraints:**
- `multipleOf` — The number must be a multiple of this value
- `maximum` — The number must be less than or equal to this value
- `exclusiveMaximum` — The number must be less than this value
- `minimum` — The number must be greater than or equal to this value
- `exclusiveMinimum` — The number must be greater than this value

**Array constraints:**
- `minItems` — The array must have at least this many items
- `maxItems` — The array must have at most this many items
- `items` — Type definition for array elements

## Key Features

1. **Two-Mode Operation**:
   - **Standard Mode (gpt-4o)**: For prompts with clear output structure
   - **High Reasoning Mode (gpt-5)**: For inferring structure from vague or implicit requirements
2. **Automatic Retry with Error Feedback**: Self-correcting schema generation with intelligent retry mechanism
3. **Natural Language Prompt Parsing**: Identifies output format instructions within prompts
4. **Automatic Structured Output Generation**: Extracts output structure in JSON format using OpenAI API
5. **Conversion to Pydantic Models**: Automatically converts extracted structure to pydantic.BaseModel classes
6. **OpenAI API Integration**: Uses generated models as response_format parameter
7. **Schema Persistence**: Save and load schemas as JSON files for reuse across sessions
8. **Centralized Type System**: Uses enums for type safety and single source of truth

## Architecture

```
┌─────────────────────┐
│  Natural Language   │
│      Prompt         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Schema Extraction (SchemaGenerator)    │
│  ┌────────────────┐  ┌────────────────┐ │
│  │ Standard Mode  │  │ High Reasoning │ │
│  │   (gpt-4o)     │  │    (gpt-5)     │ │
│  └────────────────┘  └────────────────┘ │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   Schema Validation (SchemaValidator)   │
│  - Type validation (SupportedType enum) │
│  - Format validation (StringFormat enum)│
│  - Constraint validation                │
└──────────┬──────────────────────────────┘
           │
           │ Valid?
           ├─ No ──────────┐
           │               │
           │               ▼
           │  ┌──────────────────────────┐
           │  │ Retry with Error Feedback│
           │  │ (max_retries: default 3) │
           │  └────────────┬─────────────┘
           │               │
           │               │
           │               │
           │ Yes           │
           │◄──────────────┘
           ▼
┌─────────────────────────────────────────┐
│  Pydantic Model Builder                 │
│  - Uses SupportedType.to_type_mapping() │
│  - Uses StringFormat.to_format_mapping()│
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  BaseModel Class    │
└─────────────────────┘
```

## Directory Structure

```
auto-structured-output/
├── auto_structured_output/      # Main package (renamed from src/)
│   ├── __init__.py              # Public API exports
│   ├── model.py                 # SupportedType & StringFormat enums
│   ├── extractor.py             # Main extraction logic with save/load
│   ├── schema_generator.py      # JSON schema generation (2 modes)
│   ├── model_builder.py         # Pydantic model construction
│   ├── prompts.py               # OpenAI prompt templates
│   └── validators.py            # Schema validation logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_extractor.py        # 14 tests
│   ├── test_schema_generator.py # 13 tests
│   ├── test_model_builder.py    # 12 tests
│   ├── test_validators.py       # 35 tests
│   └── README.md
├── examples/
│   ├── __init__.py
│   ├── basic_usage.py           # 5 basic examples
│   ├── advanced_examples.py     # 6 advanced examples
│   ├── high_reasoning_examples.py # 6 high reasoning examples
│   └── schemas/                 # Example schema files
├── pyproject.toml               # Project config with hatchling
├── uv.lock
├── Makefile
├── .gitignore
├── .env.example
├── CLAUDE.md                    # This file
└── README.md
```

## Implementation Details

### 1. StructureExtractor Class (`extractor.py`)

Main class for extracting structure from natural language prompts with two modes.

```python
from auto_structured_output.extractor import StructureExtractor
from openai import OpenAI

# Initialize with OpenAI client and retry configuration
client = OpenAI(api_key="your-api-key")
extractor = StructureExtractor(client, max_retries=3)  # Default: 3 retry attempts

# Standard mode (clear structure) - uses gpt-4o by default
UserModel = extractor.extract_structure(
    "Extract user information with name (string), age (integer), and email (string with email format)"
)

# High reasoning mode (vague/unclear structure) - uses gpt-5 by default
InsightModel = extractor.extract_structure(
    "Analyze customer feedback and extract actionable insights",
    use_high_reasoning=True
)

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

Handles JSON schema generation and validation using OpenAI API with configurable models and automatic retry.

```python
from auto_structured_output.schema_generator import SchemaGenerator
from openai import OpenAI

client = OpenAI(api_key="your-api-key")
generator = SchemaGenerator(max_retries=3)  # Configure retry attempts (default: 3)

# Model configuration via environment variables:
# BASIC_PREDICTION_MODEL (default: "gpt-4o")
# HIGH_PREDICTION_MODEL (default: same as BASIC_PREDICTION_MODEL)

# Extract schema from prompt - standard mode
# Automatically retries with error feedback if validation fails
schema = generator.extract_from_prompt(
    "Extract user with name (string), age (integer), and email (string with email format)",
    client
)

# Extract schema from prompt - high reasoning mode
schema = generator.extract_from_prompt(
    "Analyze customer feedback and extract insights",
    client,
    use_high_reasoning=True
)

# Validate schema (delegates to SchemaValidator)
validated_schema = generator.validate_schema(schema)
```

**Automatic Retry Mechanism:**

The retry mechanism is implemented as a loop in the `extract_from_prompt` method:

```python
for attempt in range(self.max_retries):
    try:
        # Generate schema via OpenAI API
        schema = self._call_api(client, model, messages)
        last_schema = schema

        # Validate schema
        SchemaValidator.validate_schema(schema)

        # If validation succeeds, return
        return schema

    except ValueError as e:
        last_error = str(e)

        # If last attempt, raise error
        if attempt == self.max_retries - 1:
            raise ValueError(f"Failed after {self.max_retries} attempts. Last error: {last_error}")

        # Otherwise, build retry messages with error feedback
        messages = get_schema_retry_messages(
            original_prompt=prompt,
            previous_schema=last_schema,
            error_message=last_error,
            use_high_reasoning=use_high_reasoning
        )
```

**Key Components:**
- **Validation in loop**: `SchemaValidator.validate_schema(schema)` called on each attempt
- **Error feedback**: Validation errors passed to `get_schema_retry_messages()` in `prompts.py`
- **Conversation history**: Builds message chain (system → user → assistant → user with error)
- **Retry limit**: Configurable via `max_retries` parameter (default: 3)
- **Exception handling**: Raises `ValueError` after exhausting all attempts

Uses centralized prompt templates from `prompts.py` for consistent schema extraction. All validation logic has been migrated to `SchemaValidator` class for better separation of concerns.

**Retry Prompt Template (`prompts.py`):**

The `get_schema_retry_messages()` function builds the retry conversation:

```python
def get_schema_retry_messages(
    original_prompt: str,
    previous_schema: dict | None,
    error_message: str,
    use_high_reasoning: bool = False
) -> list[dict[str, str]]:
    # Start with original messages (system + user)
    messages = get_schema_extraction_messages(original_prompt, use_high_reasoning)

    # Add previous failed schema as assistant response
    if previous_schema:
        messages.append({
            "role": "assistant",
            "content": json.dumps(previous_schema, ensure_ascii=False)
        })

    # Add error feedback as user message with fix instructions
    retry_prompt = f"""The previous schema had validation errors...
    **Validation Error:** {error_message}
    **Instructions:** 1. Read error 2. Fix issue 3. Verify constraints..."""

    messages.append({"role": "user", "content": retry_prompt})
    return messages
```

This creates a conversation flow that helps the LLM understand what went wrong and how to fix it.

### 3. ModelBuilder Class (`model_builder.py`)

Converts JSON schemas to Pydantic BaseModel classes using `pydantic.create_model()`. Uses centralized `SupportedType` and `StringFormat` enums for type mapping.

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

**Type Mapping (via SupportedType enum):**
- string → str
- integer → int
- number → float
- boolean → bool
- array → list[T]
- object → nested BaseModel
- null → type(None)
- enum → Literal[...]
- anyOf → Union[...]

**Format Support (via StringFormat enum):**
- date-time → datetime
- date → date
- time → time
- duration → str
- email → str
- hostname → str
- ipv4 → str
- ipv6 → str
- uuid → str

### 4. SchemaValidator Class (`validators.py`)

Comprehensive validation utilities for JSON schemas. Uses `SupportedType` and `StringFormat` enums for validation.

```python
from auto_structured_output.validators import SchemaValidator

# Validate type (uses SupportedType.is_supported_type())
SchemaValidator.validate_type("string")  # Returns True
SchemaValidator.validate_type("null")    # Returns True

# Validate string format (uses StringFormat.is_supported_format())
SchemaValidator.validate_string_format("email")  # Returns True
SchemaValidator.validate_string_format("uri")    # Raises ValueError (not supported)

# Validate number constraints
SchemaValidator.validate_number_constraints({
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.5
})

# Validate array constraints
SchemaValidator.validate_array_constraints({
    "minItems": 1,
    "maxItems": 10,
    "items": {"type": "string"}
})

# Validate enum
SchemaValidator.validate_enum(["active", "inactive", "suspended"])

# Validate required fields
SchemaValidator.validate_required_fields(
    required=["name", "age"],
    properties={"name": {"type": "string"}, "age": {"type": "integer"}}
)

# Validate complete schema (comprehensive validation)
validated_schema = SchemaValidator.validate_schema(schema)
```

**Key Improvements:**
- All validation now uses centralized enums from `model.py`
- Complete schema validation with `validate_schema()` method
- Handles metadata fields (title, default, examples)
- Single source of truth for supported types and formats

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
pytest --cov=auto_structured_output tests/

# Run specific test file
pytest tests/test_extractor.py

# Run with verbose output
make test-verbose
```

### Test Coverage

- **test_extractor.py** (14 tests): Structure extraction, save/load functionality, error handling
- **test_schema_generator.py** (13 tests): Schema extraction, validation, edge cases
- **test_model_builder.py** (12 tests): Model building with various types and constraints
- **test_validators.py** (35 tests): All validation utilities, constraint checking, and enum-based validation

All tests use mocks to avoid actual OpenAI API calls during testing.

### Test Results

```
============================== 74 passed in 0.06s ==============================
```

## Error Handling

```python
from auto_structured_output.extractor import (
    ExtractionError,
    SchemaValidationError,
    ModelBuildError
)

try:
    model = extractor.extract_structure("invalid prompt")
except SchemaValidationError as e:
    print(f"Schema validation failed: {e}")
except ModelBuildError as e:
    print(f"Model building failed: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

**Exception Hierarchy:**
- `ExtractionError` - Base exception for extraction errors
- `SchemaValidationError` - Schema validation failures (inherits from ExtractionError)
- `ModelBuildError` - Model building failures (inherits from ExtractionError)

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
description = "Automatically extract structured outputs from natural language prompts using OpenAI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "openai>=2.1.0",
    "pydantic>=2.11.9",
]
authors = [
    {name = "shibuiwilliam", email = "shibuiyusuke@gmail.com"},
]

[dependency-groups]
dev = [
    "hatchling>=1.27.0",
    "isort>=6.1.0",
    "mypy>=1.18.2",
    "pytest>=8.4.2",
    "pytest-asyncio>=1.2.0",
    "pytest-mock>=3.15.1",
    "python-dotenv>=1.1.1",
    "ruff>=0.13.3",
]
```

## Development

### Code Quality

```bash
# Format code
make lint_fmt

# Lint code
make lint

# Type checking
make mypy
```

### Project Structure

All source code is in the `src/auto_structured_output/` directory:
- Use `from auto_structured_output.extractor import StructureExtractor` for imports
- All code, comments, and documentation are in English
- Type hints are used throughout (Python 3.12+ syntax)

## Best Practices

1. **Choose the Right Mode**:
   - Use **standard mode** when prompt clearly specifies output structure
   - Use **high reasoning mode** when structure needs to be inferred from context

2. **Configure Retry Limits**: Adjust `max_retries` based on your use case
   - Default (3) works well for most scenarios
   - Increase for complex schemas that may need multiple corrections
   - Decrease to fail fast during development/testing

3. **Reuse Schemas**: Save frequently used schemas to JSON files and load them as needed

4. **Validation**: Always validate schemas before building models (handled automatically)

5. **Error Handling**: Catch specific exceptions for better error messages

6. **Prompt Design**:
   - Standard mode: Be specific about field names, types, and constraints
   - High reasoning mode: Focus on business context and requirements

7. **Type Safety**: Use the generated models with type checkers like mypy

8. **Model Configuration**: Set environment variables for custom models:
   ```bash
   export BASIC_PREDICTION_MODEL="gpt-4o"
   export HIGH_PREDICTION_MODEL="gpt-5"
   ```

9. **Avoid Unsupported Features**: Do not use `uri` format (not supported by OpenAI)

10. **Monitor Retries**: In production, consider logging when retries occur to identify problematic prompts

## Recent Improvements

### Automatic Retry with Error Feedback

Implemented self-correcting schema generation:
- **Automatic retry**: Retries schema generation if validation fails (default: 3 attempts)
- **Error feedback loop**: Includes validation errors in retry prompts for intelligent correction
- **Conversation-based correction**: Uses LLM conversation history (system → user → assistant → user) to provide context
- **Customizable retries**: Configure `max_retries` parameter per use case via `StructureExtractor` and `SchemaGenerator`
- **Improved reliability**: Significantly reduces schema generation failures

**Files Modified:**
- `schema_generator.py`: Added `max_retries` parameter and retry loop in `extract_from_prompt()`
- `prompts.py`: Added `get_schema_retry_messages()` function for building retry conversation
- `extractor.py`: Added `max_retries` parameter to `StructureExtractor.__init__()`

### Enum Refactoring (see ENUM_REFACTORING.md)

All type and format validation now uses centralized enums:
- `SupportedType` enum for type validation and mapping
- `StringFormat` enum for format validation and mapping
- Eliminated ~50 lines of duplicate code
- Single source of truth for all type/format information
- Better IDE support and type safety

### High Reasoning Mode

Added support for inferring structure from vague prompts:
- Uses gpt-5 model with enhanced reasoning capabilities
- Specialized prompts for deep analysis and structure inference
- Examples in `examples/high_reasoning_examples.py`
- Configurable via `use_high_reasoning=True` parameter

### Validation Consolidation

All validation logic consolidated in `SchemaValidator`:
- `validate_schema()` for complete schema validation
- Separation of concerns between schema generation and validation
- Better maintainability and testability
- Metadata field support (title, default, examples)

**Note:** With the addition of retry functionality, `SchemaGenerator` is now 143 lines (includes retry loop and error handling).
