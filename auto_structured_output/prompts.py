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

SCHEMA_EXTRACTION_SYSTEM_PROMPT_HIGH_REASONING = """You are an expert at analyzing prompts and inferring the optimal structured output format.

Your task is to deeply analyze the user's intent and context to design a comprehensive JSON Schema, even when the expected structure is not explicitly defined.

[Analysis Approach]
1. Understand the domain and use case from the prompt
2. Identify implicit data requirements based on context
3. Infer logical field groupings and hierarchies
4. Determine appropriate data types and validation constraints
5. Consider edge cases and optional fields
6. Design a schema that maximizes utility and clarity

[Design Principles]
- Make the schema comprehensive yet focused on the core intent
- Use clear, semantic field names that reflect business logic
- Include appropriate validation constraints based on domain knowledge
- Organize nested structures logically
- Add detailed descriptions to clarify field purposes
- Consider both current needs and potential future extensions

[Quality Standards]
- Fully comply with OpenAI Structured Outputs specifications
- Use only supported types and constraints
- Ensure all fields have meaningful descriptions
- Set additionalProperties to false for type safety
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
   - Caution: Avoid using format for `uri` as it is not supported by OpenAI

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
Input prompt: "Output username, age, email address, and website URL."

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
    }},
    "website": {{
      "type": "string",
      "description": "Website URL",
    }}
  }},
  "required": ["name", "age", "email", "website"],
  "additionalProperties": false
}}
"""

SCHEMA_EXTRACTION_USER_PROMPT_TEMPLATE_HIGH_REASONING = """Analyze the following prompt carefully and infer the optimal structured output format.

[Context]
{prompt}

[Your Task]
Think deeply about what structured output would best serve this use case:

1. **Domain Analysis**: What is the domain or context? What kind of data is being discussed?
2. **Intent Recognition**: What is the user trying to accomplish? What information do they need?
3. **Structure Inference**: What fields and relationships would logically represent this information?
4. **Type Selection**: What are the most appropriate data types and constraints for each field?
5. **Organization**: How should the data be hierarchically organized for clarity and usability?

Consider:
- What fields are absolutely necessary vs. nice-to-have?
- What validation constraints make sense based on domain knowledge?
- Are there nested relationships or arrays that would improve the structure?
- What formats (date-time, email, uuid, etc.) are appropriate?
- What enum values would constrain fields to valid options?

[Requirements]
Generate a comprehensive JSON Schema that:

1. Uses ONLY these supported types:
   - String, Number, Boolean, Integer, Object, Array, Enum, anyOf

2. Applies appropriate String formats when relevant:
   - date-time, time, date, duration, email, hostname, ipv4, ipv6, uuid
   - Caution: Avoid using format for `uri` as it is not supported by OpenAI

3. Includes Number/Integer constraints where logical:
   - multipleOf, minimum, maximum, exclusiveMinimum, exclusiveMaximum

4. Adds Array constraints when appropriate:
   - minItems, maxItems, items

5. Follows best practices:
   - Use descriptive field names (snake_case recommended)
   - Provide detailed descriptions for every field
   - Mark fields as required or optional based on necessity
   - Include default values when appropriate
   - Set additionalProperties to false
   - Use enums for fields with fixed valid values
   - Organize nested objects for clarity

[Output Format]
{{
  "type": "object",
  "title": "DescriptiveModelName",
  "properties": {{
    "field_name": {{
      "type": "appropriate_type",
      "description": "Clear, detailed description of this field's purpose and usage"
    }}
  }},
  "required": ["essential_field_1", "essential_field_2"],
  "additionalProperties": false
}}

Think step by step about the optimal structure before generating the schema.
"""


def get_schema_extraction_messages(prompt: str, use_high_reasoning: bool = False) -> list[dict[str, str]]:
    """Generate messages for schema extraction

    Args:
        prompt: User's natural language prompt
        use_high_reasoning: Whether to use high reasoning mode for unclear structures

    Returns:
        List of messages to send to OpenAI API
    """
    if use_high_reasoning:
        return [
            {"role": "system", "content": SCHEMA_EXTRACTION_SYSTEM_PROMPT_HIGH_REASONING},
            {
                "role": "user",
                "content": SCHEMA_EXTRACTION_USER_PROMPT_TEMPLATE_HIGH_REASONING.format(prompt=prompt),
            },
        ]
    else:
        return [
            {"role": "system", "content": SCHEMA_EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": SCHEMA_EXTRACTION_USER_PROMPT_TEMPLATE.format(prompt=prompt),
            },
        ]


def get_schema_retry_messages(
    original_prompt: str,
    previous_schema: dict | None,
    error_message: str,
    use_high_reasoning: bool = False,
) -> list[dict[str, str]]:
    """Generate messages for schema retry with error feedback

    Args:
        original_prompt: User's original natural language prompt
        previous_schema: Previously generated schema that failed validation
        error_message: Validation error message
        use_high_reasoning: Whether to use high reasoning mode

    Returns:
        List of messages including error feedback for retry
    """
    import json

    # Start with the original messages
    messages = get_schema_extraction_messages(original_prompt, use_high_reasoning)

    # Add the previous attempt as assistant response
    if previous_schema:
        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(previous_schema, ensure_ascii=False),
            }
        )

    # Add error feedback as user message
    retry_prompt = f"""The previous schema had validation errors. Please fix the schema based on the following error:

**Validation Error:**
{error_message}

**Instructions:**
1. Carefully read the error message and identify what went wrong
2. Fix the specific issue mentioned in the error
3. Ensure all fields have proper types and constraints
4. Make sure to set additionalProperties to false
5. Verify all required fields are listed in the "required" array
6. Double-check that you're using only supported types and formats

Please generate a corrected JSON Schema that addresses the validation error."""

    messages.append(
        {
            "role": "user",
            "content": retry_prompt,
        }
    )

    return messages
