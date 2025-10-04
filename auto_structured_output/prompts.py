"""Module providing prompt templates for OpenAI"""

SCHEMA_EXTRACTION_SYSTEM_PROMPT = """You are an expert at generating JSON Schemas for structured outputs.
Strictly follow the OpenAI Structured Outputs specifications when generating schemas.

[Important Constraints]
- Fully comply with OpenAI Structured Outputs specifications
- Use only supported types
- Add appropriate validation constraints
- Always include descriptions for fields
- Set additionalProperties to false
"""

SCHEMA_EXTRACTION_USER_PROMPT_TEMPLATE = """Analyze the following prompt and define the expected output structure in JSON Schema format compatible with OpenAI Structured Outputs.

[Prompt]
{prompt}

[Requirements]
Generate a JSON Schema that meets the following requirements:

1. Supported types (use only these types):
   - String, Number, Boolean, Integer, Object, Array, Enum, anyOf

2. Available formats for String type:
   - date-time, time, date, duration, email, hostname, ipv4, ipv6, uuid

3. Available constraints for Number/Integer types:
   - multipleOf: Multiple of a number
   - maximum: Maximum value (inclusive)
   - exclusiveMaximum: Maximum value (exclusive)
   - minimum: Minimum value (inclusive)
   - exclusiveMinimum: Minimum value (exclusive)

4. Available constraints for Array type:
   - minItems: Minimum number of items
   - maxItems: Maximum number of items
   - items: Type definition for array elements

5. Other requirements:
   - Include field names, types, required/optional status, default values, and descriptions
   - Support nested structures
   - Define enum as a list of values without duplicates
   - Set additionalProperties to false

[Output Format]
Output in the following JSON format:

{{
  "type": "object",
  "title": "Appropriate model name (PascalCase)",
  "properties": {{
    "field_name": {{
      "type": "type",
      "description": "Field description (required)"
    }}
  }},
  "required": ["list of required field names"],
  "additionalProperties": false
}}

[Example]
Input prompt: "Output username, age, and email address"

Output JSON Schema:
{{
  "type": "object",
  "title": "UserModel",
  "properties": {{
    "name": {{
      "type": "string",
      "description": "User name"
    }},
    "age": {{
      "type": "integer",
      "description": "User age",
      "minimum": 0
    }},
    "email": {{
      "type": "string",
      "format": "email",
      "description": "Email address"
    }}
  }},
  "required": ["name", "age", "email"],
  "additionalProperties": false
}}
"""


def get_schema_extraction_messages(prompt: str) -> list[dict[str, str]]:
    """Generate messages for schema extraction

    Args:
        prompt: User's natural language prompt

    Returns:
        List of messages to send to OpenAI API
    """
    return [
        {"role": "system", "content": SCHEMA_EXTRACTION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": SCHEMA_EXTRACTION_USER_PROMPT_TEMPLATE.format(prompt=prompt),
        },
    ]
