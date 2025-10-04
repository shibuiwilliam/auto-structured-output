# -*- coding: utf-8 -*-
"""
auto-structured-output - Utilities for structured output extraction and validation.
"""

from .extractor import (
    ExtractionError,
    ModelBuildError,
    SchemaValidationError,
    StructureExtractor,
)
from .model_builder import ModelBuilder
from .schema_generator import SchemaGenerator
from .validators import SchemaValidator

__version__ = "0.1.0"

__all__ = [
    "StructureExtractor",
    "SchemaGenerator",
    "ModelBuilder",
    "SchemaValidator",
    "ExtractionError",
    "SchemaValidationError",
    "ModelBuildError",
]
