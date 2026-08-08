import re
from core.schema import EntityType


class Normalizer:
    @staticmethod
    def normalize_email(email: str) -> str:
        """Очищає email від пробілів та зводить до нижнього регістру."""
        return email.strip().lower()

    @staticmethod
    def normalize_username(username: str) -> str:
        """Очищає username від symbol @, пробілів та зводить до нижнього регістру."""
        cleaned = username.strip().lstrip("@")
        return cleaned.lower()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Залишає тільки знак + та цифри."""
        cleaned = phone.strip()
        has_plus = cleaned.startswith("+")
        digits_only = re.sub(r"\D", "", cleaned)
        return f"+{digits_only}" if has_plus else digits_only

    @classmethod
    def normalize(cls, entity_type: EntityType, raw_value: str) -> str:
        if entity_type == EntityType.EMAIL:
            return cls.normalize_email(raw_value)
        elif entity_type == EntityType.USERNAME:
            return cls.normalize_username(raw_value)
        elif entity_type == EntityType.PHONE:
            return cls.normalize_phone(raw_value)
        return raw_value.strip()
