"""Module providing schema validation logic"""

from typing import Any


class SchemaValidator:
    """Class for validating JSON Schemas"""

    SUPPORTED_TYPES = {
        "string",
        "number",
        "integer",
        "boolean",
        "object",
        "array",
        "null",
    }

    SUPPORTED_STRING_FORMATS = {
        "date-time",
        "time",
        "date",
        "duration",
        "email",
        "hostname",
        "ipv4",
        "ipv6",
        "uuid",
    }

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
                if t not in cls.SUPPORTED_TYPES:
                    raise ValueError(f"Type not supported: {t}")
            return True

        if type_value not in cls.SUPPORTED_TYPES:
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
        if format_value not in cls.SUPPORTED_STRING_FORMATS:
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

        for key in constraints:
            if key not in valid_constraints and key not in ["type", "description"]:
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

        for key in constraints:
            if key not in valid_constraints and key not in ["type", "description"]:
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
