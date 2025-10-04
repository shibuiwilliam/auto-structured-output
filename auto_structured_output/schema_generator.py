"""Module for generating and validating JSON schemas"""

import json
from typing import Any

from openai import AzureOpenAI, OpenAI

from .prompts import get_schema_extraction_messages


class SchemaGenerator:
    """Class responsible for generating and validating JSON schemas"""

    def extract_from_prompt(self, prompt: str, client: OpenAI | AzureOpenAI) -> dict[str, Any]:
        """Extract schema from prompt

        Args:
            prompt: Natural language prompt describing the output format
            client: OpenAI API client

        Returns:
            Extracted JSON Schema

        Raises:
            ValueError: If the response from OpenAI API is invalid
        """
        messages = get_schema_extraction_messages(prompt)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Response from OpenAI API is empty")

        try:
            schema = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Response from OpenAI API is not valid JSON: {e}") from e

        return schema

    def validate_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Validate schema validity

        Args:
            schema: JSON Schema to validate

        Returns:
            Validated JSON Schema

        Raises:
            ValueError: If schema is invalid
        """
        # Check required fields
        if "type" not in schema:
            raise ValueError("Schema must have a 'type' field")

        if schema["type"] != "object":
            raise ValueError("Top-level schema must be of type 'object'")

        if "properties" not in schema:
            raise ValueError("Schema must have a 'properties' field")

        # Validate properties
        self._validate_properties(schema["properties"])

        # Validate required field
        if "required" in schema:
            if not isinstance(schema["required"], list):
                raise ValueError("'required' field must be a list")

            for field in schema["required"]:
                if field not in schema["properties"]:
                    raise ValueError(f"Required field '{field}' is not defined in properties")

        return schema

    def _validate_properties(self, properties: dict[str, Any]) -> None:
        """Validate properties recursively

        Args:
            properties: Properties dictionary to validate

        Raises:
            ValueError: If properties are invalid
        """
        if not isinstance(properties, dict):
            raise ValueError("properties must be a dictionary")

        supported_types = {
            "string",
            "number",
            "integer",
            "boolean",
            "object",
            "array",
            "null",
        }

        for field_name, field_info in properties.items():
            if not isinstance(field_info, dict):
                raise ValueError(f"Field '{field_name}' definition is invalid")

            if "type" in field_info:
                field_type = field_info["type"]
                if isinstance(field_type, list):
                    # Multiple types case (like anyOf)
                    for t in field_type:
                        if t not in supported_types:
                            raise ValueError(f"Type '{t}' for field '{field_name}' is not supported")
                elif field_type not in supported_types:
                    raise ValueError(f"Type '{field_type}' for field '{field_name}' is not supported")

                # Validate nested objects
                if field_type == "object" and "properties" in field_info:
                    self._validate_properties(field_info["properties"])

                # Validate arrays
                if field_type == "array" and "items" in field_info:
                    items = field_info["items"]
                    if isinstance(items, dict) and "type" in items:
                        if items["type"] == "object" and "properties" in items:
                            self._validate_properties(items["properties"])

            # Validate anyOf
            if "anyOf" in field_info:
                if not isinstance(field_info["anyOf"], list):
                    raise ValueError(f"'anyOf' for field '{field_name}' must be a list")
