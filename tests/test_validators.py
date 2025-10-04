"""Tests for SchemaValidator"""

import pytest

from auto_structured_output.validators import SchemaValidator


class TestSchemaValidator:
    """Test suite for SchemaValidator class"""

    def test_validate_type_string(self):
        """Test validating string type"""
        assert SchemaValidator.validate_type("string")

    def test_validate_type_integer(self):
        """Test validating integer type"""
        assert SchemaValidator.validate_type("integer")

    def test_validate_type_number(self):
        """Test validating number type"""
        assert SchemaValidator.validate_type("number")

    def test_validate_type_boolean(self):
        """Test validating boolean type"""
        assert SchemaValidator.validate_type("boolean")

    def test_validate_type_object(self):
        """Test validating object type"""
        assert SchemaValidator.validate_type("object")

    def test_validate_type_array(self):
        """Test validating array type"""
        assert SchemaValidator.validate_type("array")

    def test_validate_type_null(self):
        """Test validating null type"""
        assert SchemaValidator.validate_type("null")

    def test_validate_type_invalid(self):
        """Test validation fails with invalid type"""
        with pytest.raises(ValueError, match="Type not supported"):
            SchemaValidator.validate_type("invalid_type")

    def test_validate_type_list_valid(self):
        """Test validating list of types"""
        assert SchemaValidator.validate_type(["string", "null"])

    def test_validate_type_list_invalid(self):
        """Test validation fails with invalid type in list"""
        with pytest.raises(ValueError, match="Type not supported"):
            SchemaValidator.validate_type(["string", "invalid"])

    def test_validate_string_format_date_time(self):
        """Test validating date-time format"""
        assert SchemaValidator.validate_string_format("date-time")

    def test_validate_string_format_email(self):
        """Test validating email format"""
        assert SchemaValidator.validate_string_format("email")

    def test_validate_string_format_uuid(self):
        """Test validating uuid format"""
        assert SchemaValidator.validate_string_format("uuid")

    def test_validate_string_format_invalid(self):
        """Test validation fails with invalid format"""
        with pytest.raises(ValueError, match="String format not supported"):
            SchemaValidator.validate_string_format("invalid_format")

    def test_validate_number_constraints_valid(self):
        """Test validating valid number constraints"""
        constraints = {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "multipleOf": 0.5,
        }
        assert SchemaValidator.validate_number_constraints(constraints)

    def test_validate_number_constraints_invalid_key(self):
        """Test validation fails with unsupported constraint"""
        constraints = {"type": "number", "invalid_key": "value"}

        with pytest.raises(ValueError, match="Number constraint not supported"):
            SchemaValidator.validate_number_constraints(constraints)

    def test_validate_number_constraints_multipleOf_invalid(self):
        """Test validation fails with invalid multipleOf"""
        constraints = {"multipleOf": "not_a_number"}

        with pytest.raises(ValueError, match="multipleOf must be a number"):
            SchemaValidator.validate_number_constraints(constraints)

    def test_validate_number_constraints_multipleOf_zero(self):
        """Test validation fails with multipleOf <= 0"""
        constraints = {"multipleOf": 0}

        with pytest.raises(ValueError, match="multipleOf must be a positive number"):
            SchemaValidator.validate_number_constraints(constraints)

    def test_validate_number_constraints_both_maximum(self):
        """Test validation fails with both maximum and exclusiveMaximum"""
        constraints = {"maximum": 100, "exclusiveMaximum": 100}

        with pytest.raises(ValueError, match="Cannot specify both maximum and exclusiveMaximum"):
            SchemaValidator.validate_number_constraints(constraints)

    def test_validate_number_constraints_both_minimum(self):
        """Test validation fails with both minimum and exclusiveMinimum"""
        constraints = {"minimum": 0, "exclusiveMinimum": 0}

        with pytest.raises(ValueError, match="Cannot specify both minimum and exclusiveMinimum"):
            SchemaValidator.validate_number_constraints(constraints)

    def test_validate_array_constraints_valid(self):
        """Test validating valid array constraints"""
        constraints = {"type": "array", "minItems": 1, "maxItems": 10, "items": {}}
        assert SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_invalid_key(self):
        """Test validation fails with unsupported array constraint"""
        constraints = {"type": "array", "invalid_key": "value"}

        with pytest.raises(ValueError, match="Array constraint not supported"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_minItems_not_integer(self):
        """Test validation fails with non-integer minItems"""
        constraints = {"minItems": "not_an_int"}

        with pytest.raises(ValueError, match="minItems must be an integer"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_minItems_negative(self):
        """Test validation fails with negative minItems"""
        constraints = {"minItems": -1}

        with pytest.raises(ValueError, match="minItems must be 0 or greater"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_maxItems_not_integer(self):
        """Test validation fails with non-integer maxItems"""
        constraints = {"maxItems": "not_an_int"}

        with pytest.raises(ValueError, match="maxItems must be an integer"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_maxItems_negative(self):
        """Test validation fails with negative maxItems"""
        constraints = {"maxItems": -1}

        with pytest.raises(ValueError, match="maxItems must be 0 or greater"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_array_constraints_minItems_greater_than_maxItems(self):
        """Test validation fails when minItems > maxItems"""
        constraints = {"minItems": 10, "maxItems": 5}

        with pytest.raises(ValueError, match="minItems must be less than or equal to maxItems"):
            SchemaValidator.validate_array_constraints(constraints)

    def test_validate_required_fields_valid(self):
        """Test validating valid required fields"""
        required = ["name", "age"]
        properties = {"name": {"type": "string"}, "age": {"type": "integer"}}

        assert SchemaValidator.validate_required_fields(required, properties)

    def test_validate_required_fields_not_list(self):
        """Test validation fails when required is not a list"""
        required = "name"
        properties = {"name": {"type": "string"}}

        with pytest.raises(ValueError, match="required must be a list"):
            SchemaValidator.validate_required_fields(required, properties)

    def test_validate_required_fields_field_not_string(self):
        """Test validation fails when field name is not a string"""
        required = ["name", 123]
        properties = {"name": {"type": "string"}, "123": {"type": "integer"}}

        with pytest.raises(ValueError, match="must be a string"):
            SchemaValidator.validate_required_fields(required, properties)

    def test_validate_required_fields_field_not_in_properties(self):
        """Test validation fails when required field not in properties"""
        required = ["name", "age"]
        properties = {"name": {"type": "string"}}

        with pytest.raises(ValueError, match="not defined in properties"):
            SchemaValidator.validate_required_fields(required, properties)

    def test_validate_enum_valid(self):
        """Test validating valid enum"""
        enum_values = ["active", "inactive", "suspended"]

        assert SchemaValidator.validate_enum(enum_values)

    def test_validate_enum_not_list(self):
        """Test validation fails when enum is not a list"""
        enum_values = "active"

        with pytest.raises(ValueError, match="enum must be a list"):
            SchemaValidator.validate_enum(enum_values)

    def test_validate_enum_empty(self):
        """Test validation fails with empty enum"""
        enum_values = []

        with pytest.raises(ValueError, match="enum must have at least one value"):
            SchemaValidator.validate_enum(enum_values)

    def test_validate_enum_duplicates(self):
        """Test validation fails with duplicate enum values"""
        enum_values = ["active", "inactive", "active"]

        with pytest.raises(ValueError, match="enum values contain duplicates"):
            SchemaValidator.validate_enum(enum_values)
