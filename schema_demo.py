from core.schema import Evidence, EntityType, StatusEnum, ConfidenceLevel
from core.normalizer import Normalizer


raw_inputs = [
    (EntityType.EMAIL, "  User.Name@Domain.COM "),
    (EntityType.USERNAME, " @Somename_123 "),
    (EntityType.PHONE, "+380 (97) 123-45-67")
]

print("\n=== Automated Normalization & Evidence Creation ===")

for entity_type, raw_val in raw_inputs:
    norm_val = Normalizer.normalize(entity_type, raw_val)
    
    evidence = Evidence(
        entity_type=entity_type,
        raw_value=raw_val,
        normalized_value=norm_val,
        source_name="normalization_test",
        status=StatusEnum.FOUND,
        confidence=ConfidenceLevel.HIGH
    )
    
    print(f"\n[+] Raw: '{raw_val}'")
    print(f"    Normalized: '{evidence.normalized_value}'")
    print(f"    Type: {evidence.entity_type.value}")
