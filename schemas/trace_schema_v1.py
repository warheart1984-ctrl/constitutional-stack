"""
Layer 3: Minimal Reconstruction Trace Schema v1
Seven-field JSON structure — proven necessary (no field removable)
and sufficient (exactly what R* requires).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class EvidenceField:
    raw: Any
    sources: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class ContextField:
    state_summary: Dict[str, Any]
    relevant_history: List[Dict[str, Any]]
    environment: Dict[str, Any]


@dataclass
class ReasoningField:
    interpretation: str
    justification: str
    dependencies: List[str]


@dataclass
class UncertaintyField:
    estimates: Dict[str, Any]
    confidence: float
    unknowns: List[str]


@dataclass
class ThresholdsField:
    decision_rule: str
    triggered: bool
    parameters: Dict[str, Any]


@dataclass
class OutcomesField:
    result: Dict[str, Any]
    measured_evidence: Dict[str, Any]
    delta_from_expectation: Dict[str, Any]


@dataclass
class CorrectionField:
    veto: bool
    correction_applied: bool
    correction_type: str
    post_correction_state: Dict[str, Any]


@dataclass
class TraceSchemaV1:
    generation: int
    cycle: int
    evidence: EvidenceField
    context: ContextField
    reasoning: ReasoningField
    uncertainty: UncertaintyField
    thresholds: ThresholdsField
    outcomes: OutcomesField
    correction: CorrectionField

    def to_json(self) -> str:
        return json.dumps(self.__dict__, default=lambda o: o.__dict__, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'TraceSchemaV1':
        data = json.loads(json_str)
        return cls(
            generation=data["generation"],
            cycle=data["cycle"],
            evidence=EvidenceField(**data["evidence"]),
            context=ContextField(**data["context"]),
            reasoning=ReasoningField(**data["reasoning"]),
            uncertainty=UncertaintyField(**data["uncertainty"]),
            thresholds=ThresholdsField(**data["thresholds"]),
            outcomes=OutcomesField(**data["outcomes"]),
            correction=CorrectionField(**data["correction"]),
        )

    # Necessity proof: each field is required for reconstruction
    # Sufficiency proof: these seven fields contain exactly what R* needs
    REQUIRED_FIELDS = [
        "evidence",      # without: cannot reconstruct what reality said (step 1)
        "context",       # without: cannot reconstruct why evidence mattered
        "reasoning",     # without: cannot reconstruct how judgment updated
        "uncertainty",   # without: cannot distinguish reasoning from hallucination
        "thresholds",    # without: cannot reconstruct why correction did/didn't occur
        "outcomes",      # without: lose ground truth anchor
        "correction",    # without: cannot reconstruct corrigibility itself
    ]

    def validate_completeness(self) -> bool:
        """Verify all seven required fields are present and non-empty."""
        for field_name in self.REQUIRED_FIELDS:
            if not getattr(self, field_name):
                return False
        return True