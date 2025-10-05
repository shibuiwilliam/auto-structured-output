# Auto Structured Output

**Stop writing Pydantic models by hand.** Just describe what you want in plain English, and let AI generate type-safe schemas for you.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-74%20passed-brightgreen.svg)]()

## What is this?

Turn natural language into validated Pydantic models automatically:

```python
from auto_structured_output import StructureExtractor
from openai import OpenAI

client = OpenAI()
extractor = StructureExtractor(client)

# Just describe what you want in plain English
prompt = "Extract user with name, age, and email"
UserModel = extractor.extract_structure(prompt)

# Use it immediately with OpenAI's Structured Outputs
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    response_format=UserModel
)

user = response.choices[0].message.parsed
print(user.name, user.age, user.email)  # Fully typed and validated!
```

**That's it.** No manual schema writing, no trial and error with JSON schemas, no Pydantic boilerplate.

## Why use this?

**Before:**
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str = Field(description="User's full name")
    age: int = Field(ge=0, le=150)
    email: EmailStr
    status: Literal["active", "inactive", "suspended"]
    address: Address
    created_at: datetime
```

**After:**
```python
UserModel = extractor.extract_structure("""
    Extract user with name, age (0-150), email,
    status (active/inactive/suspended), address (street, city, country),
    and created_at timestamp
""")
```

### What you get

- ✅ **Zero boilerplate** - Describe in plain English, get production-ready models
- ✅ **Self-correcting** - Automatically retries and fixes validation errors
- ✅ **Type-safe** - Full Pydantic validation with proper Python types
- ✅ **Smart inference** - Can figure out structure from vague requirements (using `gpt-5`)
- ✅ **Reusable** - Save schemas as JSON, load them later (no API calls)
- ✅ **Fast** - Uses `gpt-4o` by default for quick generation

## Installation

```bash
# Clone and install
git clone https://github.com/yourusername/auto-structured-output.git
cd auto-structured-output

# Using uv (recommended - handles Python 3.12+ automatically)
uv sync

# Or using pip
pip install -e .
```

**Requirements:** Python 3.12+, OpenAI API key

## Quick Start

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."
```

```python
from auto_structured_output import StructureExtractor
from openai import OpenAI

client = OpenAI()
extractor = StructureExtractor(client)

# Describe what you want in natural language
prompt = "Extract user with name, age, and email address"
UserModel = extractor.extract_structure(prompt)

# Use it with OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    response_format=UserModel
)

user = response.choices[0].message.parsed
print(user)  # Fully typed and validated!
```

## Common Use Cases

### 1. Clear Structure (Standard Mode - Default)

When you know exactly what fields you need:

```python
# Explicit structure
ProductModel = extractor.extract_structure("""
    Extract product with:
    - id (string)
    - name (string)
    - price (positive number)
    - in_stock (boolean)
    - categories (array of strings)
""")
```

### 2. Vague Requirements (High Reasoning Mode)

When you're not sure what fields you need, let AI figure it out:

```python
# Just describe the intent - AI infers the structure
FeedbackModel = extractor.extract_structure(
    "Analyze customer feedback and extract actionable insights",
    use_high_reasoning=True  # Uses gpt-5 for deep reasoning
)

# AI automatically infers fields like:
# - sentiment, product_quality, delivery_experience,
#   satisfaction_score, key_issues, recommendations, etc.
```

**When to use high reasoning:**
- ❓ "I need to analyze customer reviews" (not clear what fields)
- ❓ "Extract insights from meeting notes" (structure unclear)
- ✅ Use `use_high_reasoning=True` and let AI design the structure

### 3. Complex Nested Structures

```python
OrderModel = extractor.extract_structure("""
    Extract order with:
    - order_id (string)
    - customer (name, email, phone)
    - items (array of: product_id, quantity, price)
    - shipping_address (street, city, zip, country)
    - total_amount (number)
""")
```

### 4. Save & Reuse Schemas

```python
# Extract once
UserModel = extractor.extract_structure("Extract user with name and email")

# Save for later (no API calls needed to reload)
StructureExtractor.save_extracted_json(UserModel, "user_schema.json")

# Load in another script/session
LoadedModel = StructureExtractor.load_from_json("user_schema.json")
```

## What Can You Extract?

### ✅ Supported Types

The library supports all OpenAI Structured Output types:

- **Primitives**: string, integer, number, boolean
- **Arrays**: `["tag1", "tag2"]`
- **Objects**: Nested structures
- **Enums**: `Literal["active", "inactive"]`
- **Unions**: `str | int` via anyOf

### ✅ Validation & Constraints

```python
# Numbers with constraints
"age (integer, between 0 and 150)"
"price (positive number)"
"score (multiple of 0.5)"

# Arrays with limits
"tags (array of strings, minimum 1, maximum 10 items)"

# Enums (becomes Literal types)
"status (active, inactive, or suspended)"

# Formats
"email (email format)"          # → EmailStr
"created_at (datetime format)"  # → datetime
"user_id (UUID format)"         # → UUID
```

### ❌ Not Supported

- `uri` format (OpenAI limitation)

## Advanced Features

### Automatic Error Correction

The library automatically retries if schema validation fails:

```python
# Default: 3 retry attempts
extractor = StructureExtractor(client)

# Custom retry limit for complex schemas
extractor = StructureExtractor(client, max_retries=5)
```

If the first attempt fails validation, it automatically:
1. Captures the error message
2. Adds it to the prompt as feedback
3. Asks AI to fix the issue
4. Validates again

This happens transparently - you just get a working schema.

### Custom Model Configuration

```python
import os

# Use different models
os.environ["BASIC_PREDICTION_MODEL"] = "gpt-4o"  # Standard mode (default)
os.environ["HIGH_PREDICTION_MODEL"] = "gpt-o1"  # High reasoning mode
```

### Error Handling

```python
from auto_structured_output import ExtractionError, SchemaValidationError

try:
    model = extractor.extract_structure("Extract user data")
except SchemaValidationError as e:
    print(f"Schema failed validation after retries: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

## Examples

Check out the `examples/` directory:

```bash
python examples/basic_usage.py              # 5 simple examples
python examples/advanced_examples.py        # 6 complex structures
python examples/high_reasoning_examples.py  # 6 vague requirement examples
```

## How It Works

```
Natural Language → AI (gpt-4o/gpt-5) → JSON Schema → Validation → Retry if needed → Pydantic Model
```

1. **Extract**: Send your natural language prompt to OpenAI
2. **Validate**: Check if the generated schema is valid
3. **Retry**: If invalid, send error feedback and try again (up to 3 times)
4. **Build**: Convert the validated schema to a Pydantic model

All happens automatically. You just get a working model.

## FAQ & Tips

**Q: When should I use high reasoning mode?**
- Use it when you're not sure what fields you need
- Example: "Analyze customer feedback" → AI figures out the structure
- Default mode is faster and cheaper for clear structures

**Q: How do I reduce API costs?**
- Save schemas with `save_extracted_json()` and reuse them
- Use standard mode (gpt-4o) instead of high reasoning (gpt-5)
- Cache your `StructureExtractor` instance

**Q: What if validation fails after retries?**
- Check your prompt - be more specific about field types
- Increase `max_retries` for complex schemas
- Review the error message - it tells you what's wrong

**Q: Can I use this with Azure OpenAI?**
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="...",
    api_version="2024-02-15-preview",
    azure_endpoint="https://your-resource.openai.azure.com"
)
extractor = StructureExtractor(client)
```

## Development

```bash
# Clone and setup
git clone https://github.com/shibuiwilliam/auto-structured-output.git
cd auto-structured-output
uv sync --all-groups

# Run tests
make test

# Format and lint
make lint_fmt

# Precommit hooks
pre-commit install

pre-commit run --all-files
```

See [CLAUDE.md](CLAUDE.md) for implementation details.

## API Reference

### Main Class

```python
from auto_structured_output import StructureExtractor

extractor = StructureExtractor(
    client,                  # OpenAI or AzureOpenAI client
    max_retries=3           # Retry attempts (default: 3)
)

# Extract structure
Model = extractor.extract_structure(
    prompt,                  # Natural language description
    use_high_reasoning=False # Use gpt-5 for vague prompts (default: False)
)

# Save/load schemas
StructureExtractor.save_extracted_json(Model, "schema.json")
LoadedModel = StructureExtractor.load_from_json("schema.json")
```

### Exceptions

```python
from auto_structured_output import (
    ExtractionError,        # Base exception
    SchemaValidationError,  # Schema validation failed
    ModelBuildError         # Model building failed
)
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
BASIC_PREDICTION_MODEL=gpt-4o     # Default model
HIGH_PREDICTION_MODEL=gpt-5       # High reasoning model
```

## Contributing

Contributions welcome! Open an issue or PR.

## License

MIT License - see [LICENSE](LICENSE)

---

Built with [OpenAI's Structured Outputs API](https://platform.openai.com/docs/guides/structured-outputs) and [Pydantic](https://docs.pydantic.dev/)
