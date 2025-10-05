"""Module for building Pydantic models from JSON schemas"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, create_model

from .model import StringFormat, SupportedType


class ModelBuilder:
    """Class for building Pydantic models from JSON schemas"""

    def build_model(self, schema: dict[str, Any], model_name: str | None = None) -> type[BaseModel]:
        """Generate pydantic.BaseModel class from schema

        Args:
            schema: JSON Schema definition
            model_name: Model name (uses schema title if omitted)

        Returns:
            Dynamically generated BaseModel class

        Raises:
            ValueError: If schema is invalid
        """
        if schema.get("type") != "object":
            raise ValueError("Top-level schema must be of type 'object'")

        name = model_name or schema.get("title", "DynamicModel")
        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))

        fields = {}

        for field_name, field_info in properties.items():
            field_type = self._get_field_type(field_info)
            description = field_info.get("description")
            default_value = field_info.get("default", ...)

            # Handle required fields
            if field_name in required_fields:
                if description:
                    fields[field_name] = (field_type, Field(..., description=description))
                else:
                    fields[field_name] = (field_type, ...)
            else:
                # Handle optional fields
                if default_value is ...:
                    default_value = None
                    # Make it Optional type
                    field_type = Optional[field_type]  # type: ignore[valid-type, assignment]

                if description:
                    fields[field_name] = (
                        field_type,
                        Field(default_value, description=description),
                    )
                else:
                    fields[field_name] = (field_type, default_value)

        # Generate class using create_model
        model_class: type[BaseModel] = create_model(name, **fields)  # type: ignore[call-overload]

        return model_class

    def _get_field_type(self, field_info: dict[str, Any]) -> type:
        """Resolve field type

        Args:
            field_info: Field information dictionary

        Returns:
            Resolved type

        Raises:
            ValueError: If type is not supported
        """
        # Handle anyOf
        if "anyOf" in field_info:
            return self._handle_any_of(field_info["anyOf"])

        # Handle enum
        if "enum" in field_info:
            return self._handle_enum(field_info)

        type_str = field_info.get("type", "string")

        # Handle multiple types (e.g., ["string", "null"])
        if isinstance(type_str, list):
            types = []
            for t in type_str:
                if SupportedType.is_supported_type(t):
                    types.append(SupportedType.from_str(t).to_type_mapping())
                else:
                    types.append(str)
            # Create Union type
            if len(types) == 1:
                return types[0]
            # Python 3.10+ Union notation
            result_type: type = types[0]
            for t in types[1:]:
                result_type = result_type | t  # type: ignore[assignment]
            return result_type

        # Handle format specification
        if "format" in field_info:
            if StringFormat.is_supported_format(field_info["format"]):
                return StringFormat(field_info["format"]).to_format_mapping()

        # Handle array type
        if type_str == "array":
            return self._handle_array(field_info)

        # Handle object type
        if type_str == "object":
            return self._handle_object(field_info)

        # Map basic types
        if SupportedType.is_supported_type(type_str):
            return SupportedType.from_str(type_str).to_type_mapping()
        return str

    def _handle_array(self, field_info: dict[str, Any]) -> type:
        """Handle array type

        Args:
            field_info: Field information dictionary

        Returns:
            list type or list[T] type
        """
        if "items" not in field_info:
            return list

        items_info = field_info["items"]
        item_type = self._get_field_type(items_info)

        return list[item_type]  # type: ignore[valid-type]

    def _handle_object(self, field_info: dict[str, Any]) -> type:
        """Handle object type (nested models)

        Args:
            field_info: Field information dictionary

        Returns:
            BaseModel class or dict type
        """
        if "properties" not in field_info:
            return dict

        # For nested objects, recursively build model
        nested_model_name = field_info.get("title", "NestedModel")
        return self.build_model(field_info, nested_model_name)

    def _handle_enum(self, field_info: dict[str, Any]) -> type:
        """Handle Enum type

        Args:
            field_info: Field information dictionary

        Returns:
            Literal type
        """
        enum_values = field_info["enum"]
        if not enum_values:
            return str

        # Create Literal type
        return Literal[tuple(enum_values)]  # type: ignore[return-value]

    def _handle_any_of(self, any_of_list: list[dict[str, Any]]) -> type:
        """Handle anyOf type

        Args:
            any_of_list: anyOf definition list

        Returns:
            Union type
        """
        if not any_of_list:
            return str

        types = [self._get_field_type(schema) for schema in any_of_list]

        if len(types) == 1:
            return types[0]

        # Create Union type
        result_type: type = types[0]
        for t in types[1:]:
            result_type = result_type | t  # type: ignore[assignment]

        return result_type
