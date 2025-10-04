"""Module providing schema validation logic"""

from typing import Any

from .model import StringFormat, SupportedType


class SchemaValidator:
    """Class for validating JSON Schemas

    Provides comprehensive validation for JSON Schema objects following
    OpenAI Structured Outputs specifications.
    """

    @classmethod
    def validate_type(cls, type_value: str | list[str]) -> bool:
        """Validate type validity

        Args:
            type_value: Type to validate

        Returns:
            True if type is valid

        Raises:
            ValueError: If type is not supported
        """
        if isinstance(type_value, list):
            for t in type_value:
                if not SupportedType.is_supported_type(t):
                    raise ValueError(f"Type not supported: {t}")
            return True

        if not SupportedType.is_supported_type(type_value):
            raise ValueError(f"Type not supported: {type_value}")

        return True

    @classmethod
    def validate_string_format(cls, format_value: str) -> bool:
        """Validate string format validity

        Args:
            format_value: Format to validate

        Returns:
            True if format is valid

        Raises:
            ValueError: If format is not supported
        """
        if not StringFormat.is_supported_format(format_value):
            raise ValueError(f"String format not supported: {format_value}")

        return True

    @classmethod
    def validate_number_constraints(cls, constraints: dict[str, Any]) -> bool:
        """Validate number constraint validity

        Args:
            constraints: Constraints to validate

        Returns:
            True if constraints are valid

        Raises:
            ValueError: If constraints are invalid
        """
        valid_constraints = {
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
        }

        # Common JSON Schema metadata fields that should be ignored
        metadata_fields = {"type", "description", "title", "default", "examples"}

        for key in constraints:
            if key not in valid_constraints and key not in metadata_fields:
                raise ValueError(f"Number constraint not supported: {key}")

        # Validate multipleOf
        if "multipleOf" in constraints:
            if not isinstance(constraints["multipleOf"], (int, float)):
                raise ValueError("multipleOf must be a number")
            if constraints["multipleOf"] <= 0:
                raise ValueError("multipleOf must be a positive number")

        # Validate maximum and minimum
        if "maximum" in constraints and "exclusiveMaximum" in constraints:
            raise ValueError("Cannot specify both maximum and exclusiveMaximum")

        if "minimum" in constraints and "exclusiveMinimum" in constraints:
            raise ValueError("Cannot specify both minimum and exclusiveMinimum")

        return True

    @classmethod
    def validate_array_constraints(cls, constraints: dict[str, Any]) -> bool:
        """Validate array constraint validity

        Args:
            constraints: Constraints to validate

        Returns:
            True if constraints are valid

        Raises:
            ValueError: If constraints are invalid
        """
        valid_constraints = {"minItems", "maxItems", "items"}

        # Common JSON Schema metadata fields that should be ignored
        metadata_fields = {"type", "description", "title", "default", "examples"}

        for key in constraints:
            if key not in valid_constraints and key not in metadata_fields:
                raise ValueError(f"Array constraint not supported: {key}")

        # Validate minItems
        if "minItems" in constraints:
            if not isinstance(constraints["minItems"], int):
                raise ValueError("minItems must be an integer")
            if constraints["minItems"] < 0:
                raise ValueError("minItems must be 0 or greater")

        # Validate maxItems
        if "maxItems" in constraints:
            if not isinstance(constraints["maxItems"], int):
                raise ValueError("maxItems must be an integer")
            if constraints["maxItems"] < 0:
                raise ValueError("maxItems must be 0 or greater")

        # Validate minItems <= maxItems
        if "minItems" in constraints and "maxItems" in constraints:
            if constraints["minItems"] > constraints["maxItems"]:
                raise ValueError("minItems must be less than or equal to maxItems")

        return True

    @classmethod
    def validate_required_fields(cls, required: list[str], properties: dict[str, Any]) -> bool:
        """Validate required fields validity

        Args:
            required: List of required fields
            properties: Property definitions

        Returns:
            True if required fields are valid

        Raises:
            ValueError: If required fields are invalid
        """
        if not isinstance(required, list):
            raise ValueError("required must be a list")

        for field in required:
            if not isinstance(field, str):
                raise ValueError(f"Required field name must be a string: {field}")

            if field not in properties:
                raise ValueError(f"Required field '{field}' is not defined in properties")

        return True

    @classmethod
    def validate_enum(cls, enum_values: list[Any]) -> bool:
        """Validate enum validity

        Args:
            enum_values: List of enum values

        Returns:
            True if enum is valid

        Raises:
            ValueError: If enum is invalid
        """
        if not isinstance(enum_values, list):
            raise ValueError("enum must be a list")

        if len(enum_values) == 0:
            raise ValueError("enum must have at least one value")

        # Check for duplicates
        if len(enum_values) != len(set(map(str, enum_values))):
            raise ValueError("enum values contain duplicates")

        return True

    @classmethod
    def validate_schema(cls, schema: dict[str, Any]) -> dict[str, Any]:
        """Validate complete JSON schema

        Args:
            schema: JSON Schema to validate

        Returns:
            Validated JSON Schema

        Raises:
            ValueError: If schema is invalid
        """
        # Check required top-level fields
        if "type" not in schema:
            raise ValueError("Schema must have a 'type' field")

        if schema["type"] != "object":
            raise ValueError("Top-level schema must be of type 'object'")

        if "properties" not in schema:
            raise ValueError("Schema must have a 'properties' field")

        # Validate properties recursively
        cls._validate_properties(schema["properties"])

        # Validate required field if present
        if "required" in schema:
            try:
                cls.validate_required_fields(schema["required"], schema["properties"])
            except ValueError as e:
                raise ValueError(f"Invalid required fields: {e}") from e

        return schema

    @classmethod
    def _validate_properties(cls, properties: dict[str, Any]) -> None:
        """Validate properties recursively

        Args:
            properties: Properties dictionary to validate

        Raises:
            ValueError: If properties are invalid
        """
        if not isinstance(properties, dict):
            raise ValueError("properties must be a dictionary")

        for field_name, field_info in properties.items():
            if not isinstance(field_info, dict):
                raise ValueError(f"Field '{field_name}' definition is invalid")

            # Validate type if present
            if "type" in field_info:
                field_type = field_info["type"]
                try:
                    cls.validate_type(field_type)
                except ValueError as e:
                    raise ValueError(f"Invalid type for field '{field_name}': {e}") from e

                # Validate string format
                if field_type == "string" and "format" in field_info:
                    try:
                        cls.validate_string_format(field_info["format"])
                    except ValueError as e:
                        raise ValueError(f"Invalid format for field '{field_name}': {e}") from e

                # Validate number/integer constraints
                if field_type in ("number", "integer"):
                    try:
                        cls.validate_number_constraints(field_info)
                    except ValueError as e:
                        raise ValueError(f"Invalid constraints for field '{field_name}': {e}") from e

                # Validate array constraints
                if field_type == "array":
                    try:
                        cls.validate_array_constraints(field_info)
                    except ValueError as e:
                        raise ValueError(f"Invalid array constraints for field '{field_name}': {e}") from e

                    # Recursively validate array items if they're objects
                    if "items" in field_info:
                        items = field_info["items"]
                        if isinstance(items, dict) and "type" in items:
                            if items["type"] == "object" and "properties" in items:
                                cls._validate_properties(items["properties"])

                # Validate nested objects
                if field_type == "object" and "properties" in field_info:
                    cls._validate_properties(field_info["properties"])

            # Validate enum
            if "enum" in field_info:
                try:
                    cls.validate_enum(field_info["enum"])
                except ValueError as e:
                    raise ValueError(f"Invalid enum for field '{field_name}': {e}") from e

            # Validate anyOf
            if "anyOf" in field_info:
                if not isinstance(field_info["anyOf"], list):
                    raise ValueError(f"'anyOf' for field '{field_name}' must be a list")
