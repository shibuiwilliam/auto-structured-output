"""Module for generating and validating JSON schemas"""

import json
import os
from typing import Any

from openai import AzureOpenAI, OpenAI

from .prompts import get_schema_extraction_messages
from .validators import SchemaValidator


class SchemaGenerator:
    """Class responsible for generating and validating JSON schemas"""

    def __init__(self):
        self.basic_prediction_model = os.getenv("BASIC_PREDICTION_MODEL", "gpt-4o")
        self.high_reasoning_model = os.getenv("HIGH_PREDICTION_MODEL", self.basic_prediction_model)

    def extract_from_prompt(
        self,
        prompt: str,
        client: OpenAI | AzureOpenAI,
        use_high_reasoning: bool = False,
    ) -> dict[str, Any]:
        """Extract schema from prompt

        Args:
            prompt: Natural language prompt describing the output format
            client: OpenAI API client
            use_high_reasoning: If True, use gpt-5 with enhanced reasoning for inferring
                              structure from unclear prompts. If False, use gpt-4o for
                              prompts with clearly defined structure.

        Returns:
            Extracted JSON Schema

        Raises:
            ValueError: If the response from OpenAI API is invalid

        Notes:
            - use_high_reasoning=False (default): Use gpt-4o for fast extraction when
              the expected structure is clearly defined in the prompt
            - use_high_reasoning=True: Use gpt-5 with extended reasoning to infer
              optimal structure when the prompt lacks clear structural definition
        """

        messages = get_schema_extraction_messages(prompt, use_high_reasoning=use_high_reasoning)
        model = self.high_reasoning_model if use_high_reasoning else self.basic_prediction_model

        response = client.chat.completions.create(
            model=model,
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

        Delegates to SchemaValidator for all validation logic.

        Args:
            schema: JSON Schema to validate

        Returns:
            Validated JSON Schema

        Raises:
            ValueError: If schema is invalid
        """
        return SchemaValidator.validate_schema(schema)
