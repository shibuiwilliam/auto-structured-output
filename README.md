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
- 🔁 **Automatic Retry with Error Feedback**: Self-correcting schema generation with intelligent retry mechanism
- 🎯 **Type Safety**: Full support for nested objects, arrays, enums, and format specifications
- 📦 **OpenAI Integration**: Works seamlessly with OpenAI's Structured Outputs API

## Installation

### From Source (Development)

**Using uv (recommended):**
```bash
# Clone the repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install with uv (automatically manages Python 3.12+)
uv sync

# Or install with development dependencies
uv sync --all-groups
```

**Using pip:**
```bash
# Clone the repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install in editable mode
pip install -e .

# Or install with development dependencies (note: requires manual installation)
pip install -e .
pip install hatchling isort mypy pytest pytest-asyncio pytest-mock python-dotenv ruff
```

### Requirements

- Python 3.12 or higher
- OpenAI API key
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Quick Start

```python
from openai import OpenAI
from auto_structured_output.extractor import StructureExtractor

# Initialize with automatic retry (default: 3 attempts)
client = OpenAI(api_key="your-api-key")
extractor = StructureExtractor(client, max_retries=3)

# Extract structure from natural language
# If validation fails, it automatically retries with error feedback
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

### High Reasoning Mode

For prompts where the expected structure is **not clearly defined**, use high reasoning mode with `gpt-5`:

```python
# Infer optimal structure from vague requirements
AnalysisModel = extractor.extract_structure(
    "Analyze customer feedback and extract actionable insights",
    use_high_reasoning=True  # Uses gpt-5 for deep reasoning
)

# The model will intelligently infer fields like:
# - sentiment, product_quality, delivery_experience, satisfaction_score, etc.
```

## Two Modes of Operation

### Standard Mode (Default) - `gpt-4o`

Use when the expected output structure is **clearly defined** in the prompt:

```python
# ✅ Good for standard mode - explicit structure
UserModel = extractor.extract_structure(
    "Extract user with name (string), age (integer), email (email format)"
)
```

**Characteristics:**
- Fast and efficient
- Uses `gpt-4o` model
- Best for prompts with explicit field definitions
- Lower API cost

### High Reasoning Mode - `gpt-5`

Use when the structure needs to be **inferred from context**:

```python
# ✅ Good for high reasoning - infer from intent
FeedbackModel = extractor.extract_structure(
    "Analyze customer feedback and extract key insights about product and service quality",
    use_high_reasoning=True
)
```

**Characteristics:**
- Deep contextual analysis
- Uses `gpt-5` model with enhanced reasoning
- Infers optimal structure from domain knowledge
- Best for exploratory or unclear requirements
- Higher API cost but more comprehensive results

### When to Use Each Mode

| Scenario | Recommended Mode | Reason |
|----------|-----------------|--------|
| Explicit field list in prompt | Standard | Structure is clear |
| "Extract user with name, age, email" | Standard | Fields explicitly defined |
| "Analyze customer feedback" | High Reasoning | Structure needs inference |
| "Extract insights from data" | High Reasoning | Intent-based, not field-based |
| Rapid prototyping with clear requirements | Standard | Faster and cheaper |
| Exploring optimal structure for new use case | High Reasoning | Leverages domain knowledge |

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

### Automatic Retry with Error Feedback

```python
# The library automatically retries schema generation if validation fails
# Each retry includes error feedback to help the model fix the issue

# Default: 3 retry attempts
extractor = StructureExtractor(client)

# Custom retry limit
extractor = StructureExtractor(client, max_retries=5)

# Example: Complex schema that might need retry
UserModel = extractor.extract_structure("""
    Extract user information with:
    - user_id (UUID format)
    - name (string)
    - age (integer, must be between 0 and 150)
    - email (email format)
    - status (one of: active, inactive, suspended)
    - tags (array of strings, minimum 1, maximum 10)
""")
# If the first attempt generates invalid schema (e.g., missing constraints),
# it automatically retries with error feedback until valid or max_retries reached
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
    # Raised when schema validation fails after all retry attempts
    print(f"Schema validation failed after {extractor.schema_generator.max_retries} retries: {e}")
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
- `duration` → `str`
- `email` → `str`
- `uuid` → `str`
- `hostname` → `str`
- `ipv4` → `str`
- `ipv6` → `str`
- Custom patterns with regex

**Note:** The `uri` format is NOT supported by OpenAI Structured Outputs and should be avoided.

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
- **test_validators.py** (35 tests): All validation utilities, enum-based validation

All tests use mocks to avoid actual OpenAI API calls.

```
============================== 74 passed in 0.06s ==============================
```

## Development

### Setup Development Environment

**Using uv (recommended):**
```bash
# Clone repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install with dev dependencies
uv sync --all-groups

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

**Using pip:**
```bash
# Clone repository
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Install in editable mode
pip install -e .
pip install hatchling isort mypy pytest pytest-asyncio pytest-mock python-dotenv ruff

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Code Quality

```bash
# Format code
make fmt

# Lint code
make lint

# Lint and format together
make lint_fmt

# Type checking
make mypy

# Run all tests
make test
```

### Project Structure

```
auto-structured-output/
├── auto_structured_output/    # Main package
│   ├── __init__.py           # Public API exports
│   ├── model.py              # SupportedType & StringFormat enums
│   ├── extractor.py          # Main API
│   ├── schema_generator.py   # Schema extraction (2 modes)
│   ├── model_builder.py      # Pydantic model building
│   ├── prompts.py            # Prompt templates
│   └── validators.py         # Validation utilities
├── tests/                    # Test suite (74 tests)
│   ├── conftest.py           # Pytest fixtures
│   ├── test_extractor.py     # 14 tests
│   ├── test_schema_generator.py # 13 tests
│   ├── test_model_builder.py    # 12 tests
│   └── test_validators.py       # 35 tests
├── examples/                 # Usage examples
│   ├── basic_usage.py           # 5 basic examples
│   ├── advanced_examples.py     # 6 advanced examples
│   ├── high_reasoning_examples.py # 6 high reasoning examples
│   └── schemas/                 # Example schema files
├── pyproject.toml            # Project configuration
├── uv.lock                   # UV lock file
├── Makefile                  # Development commands
├── .env.example              # Environment variables template
├── CLAUDE.md                 # Implementation documentation
└── README.md                 # This file
```

## Examples

Check out the `examples/` directory for detailed examples:

- **`basic_usage.py`**: 5 basic examples covering common use cases
  - Simple user extraction
  - Product with enum status
  - Nested objects (address)
  - Arrays of strings
  - Date/time formats

- **`advanced_examples.py`**: 6 advanced examples with complex structures
  - Deep nesting (user profile with settings)
  - Arrays of objects (order with items)
  - Mixed constraints (metrics with validation)
  - Enums and optional fields
  - Complex validation (blog post with tags)
  - anyOf unions (flexible value types)

- **`high_reasoning_examples.py`**: 6 examples using high reasoning mode for vague/complex prompts
  - Customer feedback analysis
  - Meeting summary extraction
  - Research paper metadata
  - Job application evaluation
  - Financial transaction analysis
  - Product review insights

**Running Examples:**
```bash
# Make sure you have set up your .env file with OPENAI_API_KEY
python examples/basic_usage.py
python examples/advanced_examples.py
python examples/high_reasoning_examples.py
```

## Best Practices

1. **Choose the Right Mode**:
   - Use standard mode (default) for prompts with explicit field definitions
   - Use high reasoning mode for prompts requiring structure inference from context

2. **Configure Retry Limits**: Adjust `max_retries` based on your needs
   - Default (3) works well for most cases
   - Increase for complex schemas that may need multiple corrections
   - Decrease to fail fast during development/testing

3. **Reuse Schemas**: Save frequently used schemas to JSON files to avoid redundant API calls

4. **Be Specific in Standard Mode**: Provide clear field descriptions in prompts for better schema generation

5. **Leverage Context in High Reasoning Mode**: Describe the use case and intent rather than specific fields

6. **Validate Early**: Use validation before building models to catch errors early

7. **Handle Errors**: Always catch and handle `SchemaValidationError` and `ExtractionError`

8. **Type Safety**: Use generated models with type checkers like mypy for better code quality

9. **Cost Optimization**: Use standard mode when possible to minimize API costs; reserve high reasoning for complex cases

10. **Monitor Retries**: In production, consider logging when retries occur to identify problematic prompts

## API Reference

### Public API

The library exports the following classes and exceptions:

```python
from auto_structured_output import (
    # Main classes
    StructureExtractor,
    SchemaGenerator,
    ModelBuilder,
    SchemaValidator,

    # Enums
    SupportedType,
    StringFormat,

    # Exceptions
    ExtractionError,
    SchemaValidationError,
    ModelBuildError,
)
```

### StructureExtractor

Main class for extracting structures from natural language.

```python
class StructureExtractor:
    def __init__(
        self,
        client: OpenAI | AzureOpenAI,
        max_retries: int = 3
    )
    """
    Initialize StructureExtractor.

    Args:
        client: OpenAI or Azure OpenAI client
        max_retries: Maximum number of retry attempts for schema generation (default: 3)
    """

    def extract_structure(
        self,
        prompt: str,
        use_high_reasoning: bool = False
    ) -> type[BaseModel]
    """
    Extract structure from natural language prompt.

    Args:
        prompt: Natural language prompt describing the output format
        use_high_reasoning: If True, use gpt-5 with enhanced reasoning to infer
                          optimal structure from unclear prompts. If False (default),
                          use gpt-4o for prompts with clearly defined structure.

    Returns:
        Dynamically generated Pydantic BaseModel class

    Raises:
        SchemaValidationError: If schema validation fails after all retry attempts
        ExtractionError: If schema extraction fails
    """

    @staticmethod
    def save_extracted_json(
        model: type[BaseModel],
        file_path: str | Path
    ) -> None

    @staticmethod
    def load_from_json(file_path: str | Path) -> type[BaseModel]
```

### SchemaGenerator

Handles JSON schema extraction and validation with automatic retry.

```python
class SchemaGenerator:
    def __init__(self, max_retries: int = 3)
    """
    Initialize SchemaGenerator.

    Args:
        max_retries: Maximum number of retry attempts for schema generation (default: 3)
    """

    def extract_from_prompt(
        self,
        prompt: str,
        client: OpenAI | AzureOpenAI,
        use_high_reasoning: bool = False
    ) -> dict[str, Any]
    """
    Extract JSON schema from natural language prompt with automatic retry.

    Args:
        prompt: Natural language prompt
        client: OpenAI or Azure OpenAI client
        use_high_reasoning: Whether to use gpt-5 for enhanced reasoning

    Returns:
        Extracted and validated JSON schema as dictionary

    Raises:
        ValueError: If schema validation fails after all retry attempts

    Notes:
        - Automatically retries with error feedback if validation fails
        - Uses conversation history to provide context for corrections
    """

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

Create a `.env` file in your project root (you can copy from `.env.example`):

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Custom Model Configuration
# BASIC_PREDICTION_MODEL=gpt-4o          # Model for standard mode (default: gpt-4o)
# HIGH_PREDICTION_MODEL=gpt-5            # Model for high reasoning mode (default: same as BASIC_PREDICTION_MODEL)

# Optional: Azure OpenAI Configuration
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your-azure-api-key
# OPENAI_API_VERSION=2024-02-15-preview
```

**Note:** The library will automatically load variables from `.env` files when using `python-dotenv`.

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
# Make sure you have access to gpt-4o model (and gpt-5 for high reasoning mode)
```

**Q: High reasoning mode not working as expected**
```python
# Make sure you have access to gpt-5 model
# You can configure custom models via environment variables:
import os
os.environ["HIGH_PREDICTION_MODEL"] = "gpt-5"  # or your preferred model

# Or use a different model that supports reasoning
os.environ["HIGH_PREDICTION_MODEL"] = "o1-preview"
```

**Q: `uri` format not supported error**
```python
# The uri format is not supported by OpenAI Structured Outputs
# ❌ Bad: {"type": "string", "format": "uri"}
# ✅ Good: {"type": "string", "description": "URL string"}
```

## Recent Improvements

### Automatic Retry with Error Feedback
- **Self-correcting schemas**: Automatically retries when validation fails (default: 3 attempts)
- **Error feedback loop**: Includes validation errors in retry prompts for intelligent correction
- **Customizable retries**: Configure `max_retries` parameter per use case
- **Conversation-based correction**: Uses LLM conversation history to provide context
- **Improved reliability**: Significantly reduces schema generation failures

### Centralized Type System (v0.1.0)
- **Enum-based validation**: All type and format validation now uses `SupportedType` and `StringFormat` enums
- **Single source of truth**: Eliminated ~50 lines of duplicate code
- **Better type safety**: Improved IDE support and autocomplete
- See [ENUM_REFACTORING.md](ENUM_REFACTORING.md) for details

### High Reasoning Mode
- **Deep analysis**: Uses gpt-5 to infer optimal structure from vague prompts
- **Context-aware**: Analyzes domain knowledge and business requirements
- **Flexible configuration**: Customize models via environment variables

### Validation Consolidation
- **Simplified architecture**: All validation in `SchemaValidator` class
- **Better separation**: Clear boundaries between schema generation and validation
- **Improved maintainability**: Centralized validation logic for easier updates

**Note:** With retry functionality, `SchemaGenerator` is now 143 lines (includes retry loop).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- Built on top of [OpenAI's Structured Outputs API](https://platform.openai.com/docs/guides/structured-outputs)
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation and model generation
