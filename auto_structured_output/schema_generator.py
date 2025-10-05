"""Module for generating and validating JSON schemas"""

import json
import os
from typing import Any

from openai import AzureOpenAI, OpenAI

from .prompts import get_schema_extraction_messages, get_schema_retry_messages
from .validators import SchemaValidator


class SchemaGenerator:
    """Class responsible for generating and validating JSON schemas"""

    def __init__(self, max_retries: int = 3):
        """Initialize SchemaGenerator

        Args:
            max_retries: Maximum number of retry attempts for schema generation (default: 3)
        """
        self.basic_prediction_model = os.getenv("BASIC_PREDICTION_MODEL", "gpt-4o")
        self.high_reasoning_model = os.getenv("HIGH_PREDICTION_MODEL", self.basic_prediction_model)
        self.max_retries = max_retries

    def extract_from_prompt(
        self,
        prompt: str,
        client: OpenAI | AzureOpenAI,
        use_high_reasoning: bool = False,
    ) -> dict[str, Any]:
        """Extract schema from prompt with automatic retry on validation failure

        Args:
            prompt: Natural language prompt describing the output format
            client: OpenAI API client
            use_high_reasoning: If True, use gpt-5 with enhanced reasoning for inferring
                              structure from unclear prompts. If False, use gpt-4o for
                              prompts with clearly defined structure.

        Returns:
            Extracted and validated JSON Schema

        Raises:
            ValueError: If the response from OpenAI API is invalid or schema validation
                       fails after all retry attempts

        Notes:
            - use_high_reasoning=False (default): Use gpt-4o for fast extraction when
              the expected structure is clearly defined in the prompt
            - use_high_reasoning=True: Use gpt-5 with extended reasoning to infer
              optimal structure when the prompt lacks clear structural definition
            - Automatically retries with error feedback if validation fails
        """
        messages = get_schema_extraction_messages(prompt, use_high_reasoning=use_high_reasoning)
        model = self.high_reasoning_model if use_high_reasoning else self.basic_prediction_model

        last_error = None
        last_schema = None

        for attempt in range(self.max_retries):
            try:
                # Generate schema
                schema = self._call_api(client, model, messages)
                last_schema = schema

                # Validate schema
                SchemaValidator.validate_schema(schema)

                # If validation succeeds, return the schema
                return schema

            except ValueError as e:
                last_error = str(e)

                # If this is the last attempt, raise the error
                if attempt == self.max_retries - 1:
                    raise ValueError(
                        f"Failed to generate valid schema after {self.max_retries} attempts. Last error: {last_error}"
                    ) from e

                # Otherwise, add error feedback and retry
                messages = get_schema_retry_messages(
                    original_prompt=prompt,
                    previous_schema=last_schema,
                    error_message=last_error,
                    use_high_reasoning=use_high_reasoning,
                )

        # This should not be reached, but just in case
        raise ValueError(f"Failed to generate valid schema. Last error: {last_error}")

    def _call_api(
        self,
        client: OpenAI | AzureOpenAI,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Call OpenAI API to generate schema

        Args:
            client: OpenAI API client
            model: Model name to use
            messages: Messages for the API call

        Returns:
            Generated JSON Schema

        Raises:
            ValueError: If API response is invalid
        """
        response = client.chat.completions.create(  # type: ignore[call-overload]
            model=model,
            messages=messages,  # type: ignore[arg-type]
            response_format={"type": "json_object"},  # type: ignore[typeddict-item]
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
