from datetime import date, datetime, time
from enum import Enum


class SupportedType(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"
    ENUM = "enum"
    ANY_OF = "anyOf"

    @staticmethod
    def from_str(_type: str) -> "SupportedType":
        for t in SupportedType:
            if t.value == _type:
                return t
        raise ValueError(f"Unsupported type: {_type}")

    @staticmethod
    def is_supported_type(_type: str) -> bool:
        return any(t.value == _type for t in SupportedType)

    def to_type_mapping(self) -> type:
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        return type_mapping[self.value]


class StringFormat(Enum):
    DATE_TIME = "date-time"
    DATE = "date"
    TIME = "time"
    DURATION = "duration"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    UUID = "uuid"

    @staticmethod
    def is_supported_format(_format: str) -> bool:
        return any(f.value == _format for f in StringFormat)

    def to_format_mapping(self) -> type:
        format_mapping = {
            "date-time": datetime,
            "date": date,
            "time": time,
            "duration": str,
            "email": str,
            "hostname": str,
            "ipv4": str,
            "ipv6": str,
            "uuid": str,
        }
        return format_mapping[self.value]
