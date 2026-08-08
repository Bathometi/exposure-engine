from enum import Enum
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"
    DOMAIN = "domain"
    BREACH = "breach"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class StatusEnum(str, Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"
    RATE_LIMITED = "RATE_LIMITED"


class Evidence(BaseModel):
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    source_name: str
    status: StatusEnum
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)
    limitations: Optional[str] = "Evidence collected from authenticated or public API context."
