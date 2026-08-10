from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class EntityType(str, Enum):
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"


class StatusEnum(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"
    ERROR = "error"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Evidence(BaseModel):
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    source_name: str
    status: StatusEnum
    confidence: ConfidenceLevel
    details: Dict[str, Any] = Field(default_factory=dict)
    limitations: Optional[str] = None
