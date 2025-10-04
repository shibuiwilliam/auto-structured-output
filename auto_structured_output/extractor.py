"""Main module for extracting structure from natural language prompts"""

import json
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from .model_builder import ModelBuilder
from .schema_generator import SchemaGenerator


class ExtractionError(Exception):
    """Error during structure extraction"""

    pass


class SchemaValidationError(ExtractionError):
    """Schema validation error"""

    pass


class ModelBuildError(ExtractionError):
    """Model building error"""

    pass


class StructureExtractor:
    """Main class for extracting structure from natural language prompts"""

    def __init__(self, openai_client: OpenAI):
        """Initialize

        Args:
            openai_client: OpenAI API client
        """
        self.client = openai_client
        self.schema_generator = SchemaGenerator()
        self.model_builder = ModelBuilder()

    def extract_structure(self, prompt: str, use_high_reasoning: bool = False) -> type[BaseModel]:
        """Extract structure from prompt and return Pydantic model

        Args:
            prompt: Natural language prompt describing the output format
            use_high_reasoning: If True, use gpt-5 with enhanced reasoning to infer
                              optimal structure from unclear prompts. If False (default),
                              use gpt-4o for prompts with clearly defined structure.

        Returns:
            Class inheriting from pydantic.BaseModel

        Raises:
            ExtractionError: If structure extraction fails
            SchemaValidationError: If schema validation fails
            ModelBuildError: If model building fails

        Examples:
            >>> # Standard mode - clearly defined structure
            >>> UserModel = extractor.extract_structure(
            ...     "Extract user with name (string), age (integer), email (email format)"
            ... )

            >>> # High reasoning mode - infer structure from context
            >>> AnalysisModel = extractor.extract_structure(
            ...     "Analyze this customer feedback and extract key insights",
            ...     use_high_reasoning=True
            ... )
        """
        try:
            # 1. Extract structure using OpenAI
            schema_json = self._extract_schema_from_prompt(prompt, use_high_reasoning)

            # 2. Validate JSON schema
            validated_schema = self._validate_schema(schema_json)

            # 3. Convert to Pydantic model
            model_class = self._build_model(validated_schema)

            return model_class

        except SchemaValidationError:
            raise
        except ModelBuildError:
            raise
        except Exception as e:
            raise ExtractionError(f"Error occurred during structure extraction: {e}") from e

    @staticmethod
    def save_extracted_json(model: type[BaseModel], file_path: str | Path) -> None:
        """Save a Pydantic model's JSON schema to a file

        Args:
            model: Pydantic BaseModel class to save
            file_path: Path to save the JSON schema file

        Raises:
            IOError: If file cannot be written
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Get the JSON schema from the Pydantic model
        schema = model.model_json_schema()

        with path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_json(file_path: str | Path) -> type[BaseModel]:
        """Load a schema from a JSON file and build a Pydantic model

        Args:
            file_path: Path to the JSON schema file

        Returns:
            Class inheriting from pydantic.BaseModel

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or schema is malformed
            SchemaValidationError: If schema validation fails
            ModelBuildError: If model building fails
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {file_path}")

        with path.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validate and build the model using static instances
        schema_generator = SchemaGenerator()
        model_builder = ModelBuilder()

        try:
            validated_schema = schema_generator.validate_schema(schema)
        except ValueError as e:
            raise SchemaValidationError(f"Failed to validate schema: {e}") from e

        try:
            return model_builder.build_model(validated_schema)
        except Exception as e:
            raise ModelBuildError(f"Failed to build model: {e}") from e

    def _extract_schema_from_prompt(self, prompt: str, use_high_reasoning: bool = False) -> dict[str, Any]:
        """Extract JSON schema from prompt (internal method)

        Args:
            prompt: Natural language prompt
            use_high_reasoning: Whether to use high reasoning mode

        Returns:
            Extracted JSON Schema

        Raises:
            ExtractionError: If schema extraction fails
        """
        try:
            return self.schema_generator.extract_from_prompt(prompt, self.client, use_high_reasoning)
        except Exception as e:
            raise ExtractionError(f"Failed to extract schema: {e}") from e

    def _validate_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Validate schema (internal method)

        Args:
            schema: JSON Schema to validate

        Returns:
            Validated JSON Schema

        Raises:
            SchemaValidationError: If schema validation fails
        """
        try:
            return self.schema_generator.validate_schema(schema)
        except ValueError as e:
            raise SchemaValidationError(f"Failed to validate schema: {e}") from e

    def _build_model(self, schema: dict[str, Any]) -> type[BaseModel]:
        """Build Pydantic model from schema (internal method)

        Args:
            schema: JSON Schema

        Returns:
            BaseModel class

        Raises:
            ModelBuildError: If model building fails
        """
        try:
            return self.model_builder.build_model(schema)
        except Exception as e:
            raise ModelBuildError(f"Failed to build model: {e}") from e
