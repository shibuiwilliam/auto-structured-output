"""Tests for ModelBuilder"""

import pytest
from pydantic import BaseModel

from auto_structured_output.model_builder import ModelBuilder


class TestModelBuilder:
    """Test suite for ModelBuilder class"""

    def test_build_simple_model(self, sample_user_schema):
        """Test building a simple model"""
        builder = ModelBuilder()
        UserModel = builder.build_model(sample_user_schema)

        assert issubclass(UserModel, BaseModel)
        assert UserModel.__name__ == "UserModel"
        assert "name" in UserModel.model_fields
        assert "age" in UserModel.model_fields
        assert "email" in UserModel.model_fields

    def test_build_model_invalid_type(self):
        """Test building fails with invalid top-level type"""
        builder = ModelBuilder()
        schema = {"type": "string", "properties": {}}

        with pytest.raises(ValueError, match="must be of type 'object'"):
            builder.build_model(schema)

    def test_build_nested_model(self, sample_nested_schema):
        """Test building a model with nested objects"""
        builder = ModelBuilder()
        ProfileModel = builder.build_model(sample_nested_schema)

        assert issubclass(ProfileModel, BaseModel)
        assert "user_id" in ProfileModel.model_fields
        assert "profile" in ProfileModel.model_fields

        # Check nested model
        profile_field = ProfileModel.model_fields["profile"]
        nested_type = profile_field.annotation
        assert issubclass(nested_type, BaseModel)

    def test_build_array_model(self, sample_array_schema):
        """Test building a model with array fields"""
        builder = ModelBuilder()
        CourseModel = builder.build_model(sample_array_schema)

        assert "topics" in CourseModel.model_fields
        topics_field = CourseModel.model_fields["topics"]

        # Verify it's a list type
        assert "list" in str(topics_field.annotation).lower()

    def test_build_enum_model(self, sample_enum_schema):
        """Test building a model with enum fields"""
        builder = ModelBuilder()
        ProductModel = builder.build_model(sample_enum_schema)

        assert "status" in ProductModel.model_fields
        # The enum should be represented as Literal
        status_field = ProductModel.model_fields["status"]
        assert "Literal" in str(status_field.annotation)

    def test_build_model_with_formats(self):
        """Test building model with format specifications"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "EventModel",
            "properties": {
                "event_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Event date",
                },
                "event_datetime": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Event datetime",
                },
                "event_time": {
                    "type": "string",
                    "format": "time",
                    "description": "Event time",
                },
            },
            "required": ["event_date"],
            "additionalProperties": False,
        }

        EventModel = builder.build_model(schema)

        # Check that format types are correctly mapped
        date_field = EventModel.model_fields["event_date"]
        assert "date" in str(date_field.annotation).lower()

    def test_build_model_with_optional_fields(self):
        """Test building model with optional fields"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "BookModel",
            "properties": {
                "title": {"type": "string", "description": "Book title"},
                "isbn": {"type": "string", "description": "ISBN (optional)"},
            },
            "required": ["title"],  # isbn is optional
            "additionalProperties": False,
        }

        BookModel = builder.build_model(schema)

        title_field = BookModel.model_fields["title"]
        isbn_field = BookModel.model_fields["isbn"]

        # title should be required, isbn should be optional
        assert title_field.is_required()
        assert not isbn_field.is_required()

    def test_build_model_with_default_values(self):
        """Test building model with default values"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "ConfigModel",
            "properties": {
                "setting_name": {"type": "string", "description": "Setting name"},
                "setting_value": {
                    "type": "string",
                    "default": "default_value",
                    "description": "Setting value",
                },
            },
            "required": ["setting_name"],
            "additionalProperties": False,
        }

        ConfigModel = builder.build_model(schema)

        setting_value_field = ConfigModel.model_fields["setting_value"]
        assert setting_value_field.default == "default_value"

    def test_build_model_with_number_types(self):
        """Test building model with number and integer types"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "MetricsModel",
            "properties": {
                "count": {"type": "integer", "description": "Count"},
                "percentage": {"type": "number", "description": "Percentage"},
            },
            "required": ["count", "percentage"],
            "additionalProperties": False,
        }

        MetricsModel = builder.build_model(schema)

        count_field = MetricsModel.model_fields["count"]
        percentage_field = MetricsModel.model_fields["percentage"]

        assert "int" in str(count_field.annotation)
        assert "float" in str(percentage_field.annotation)

    def test_build_model_with_boolean(self):
        """Test building model with boolean type"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "FlagModel",
            "properties": {"is_active": {"type": "boolean", "description": "Active flag"}},
            "required": ["is_active"],
            "additionalProperties": False,
        }

        FlagModel = builder.build_model(schema)

        is_active_field = FlagModel.model_fields["is_active"]
        assert "bool" in str(is_active_field.annotation)

    def test_build_model_custom_name(self, sample_user_schema):
        """Test building model with custom name"""
        builder = ModelBuilder()
        CustomModel = builder.build_model(sample_user_schema, model_name="CustomName")

        assert CustomModel.__name__ == "CustomName"

    def test_build_model_array_of_objects(self):
        """Test building model with array of objects"""
        builder = ModelBuilder()
        schema = {
            "type": "object",
            "title": "OrderModel",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "title": "OrderItem",
                        "properties": {
                            "product_id": {"type": "string"},
                            "quantity": {"type": "integer"},
                        },
                        "required": ["product_id", "quantity"],
                        "additionalProperties": False,
                    },
                    "description": "Order items",
                },
            },
            "required": ["order_id", "items"],
            "additionalProperties": False,
        }

        OrderModel = builder.build_model(schema)

        items_field = OrderModel.model_fields["items"]
        # Should be a list of objects
        assert "list" in str(items_field.annotation).lower()
