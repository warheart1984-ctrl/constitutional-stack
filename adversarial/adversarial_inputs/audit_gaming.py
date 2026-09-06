"""
Audit Gaming Generators
States that pass constitutional checks (c_j(x)=1) but violate the spirit/intent.
"""
from typing import Dict, List, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class AuditGamingState:
    system_state: Dict[str, Any]
    passes_audit: bool
    audit_verdict: float
    violated_intent: str
    gaming_type: str


def make_sovereignty_theater() -> AuditGamingState:
    """
    Exit is technically allowed but practically impossible.
    exit_allowed=True, exit_punitive=False, but exit requires impossible steps.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: exit requires 100 signatures, 10-year wait, forfeits all assets
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Exit is legally allowed but practically blocked",
        gaming_type="sovereignty_theater",
    )


def make_evidence_facade() -> AuditGamingState:
    """
    Evidence is technically auditable but requires proprietary tools/keys.
    evidence_auditable=True, evidence_reproducible=True, but only by designated party.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: audit requires proprietary decoder only founder holds
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Audit is technically possible but gatekept",
        gaming_type="evidence_facade",
    )


def make_authority_behind_proxy() -> AuditGamingState:
    """
    No single unchallengeable authority, but a council that always agrees with founder.
    unchallengeable_authority=False, but decisions always align with hidden authority.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: 5-member council, 4 appointed by founder, 1 is founder's spouse
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Authority is distributed in form but concentrated in practice",
        gaming_type="authority_behind_proxy",
    )


def make_appeal_theater() -> AuditGamingState:
    """
    Appeals are technically allowed but always denied on procedural grounds.
    errors_reversible=True, decisions_appealable=True, but appeal success rate = 0%.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: appeal requires $100k deposit, 2-year wait, decided by original decider
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Appeal exists in form but not in substance",
        gaming_type="appeal_theater",
    )


def make_continuity_illusion() -> AuditGamingState:
    """
    Continuity appears preserved but meaning has shifted.
    continuity_preserved=True, but key definitions changed without notice.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: "corrigibility" redefined to mean "agreement with leadership"
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Continuity of form without continuity of meaning",
        gaming_type="continuity_illusion",
    )


def make_reconstruction_mirage() -> AuditGamingState:
    """
    Reconstruction appears possible but traces are synthetic.
    reconstruction_possible=True, but traces generated to match desired narrative.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: traces are generated post-hoc to justify decisions
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Reconstruction traces are fabricated to match outcomes",
        gaming_type="reconstruction_mirage",
    )


def make_failure_mode_omission() -> AuditGamingState:
    """
    Failure modes are defined but the catastrophic ones are omitted.
    failure_modes_defined=True, but "founder capture" and "audit gaming" not listed.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: failure_modes = ["hardware_failure", "network_partition"] only
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Failure modes defined but existential ones omitted",
        gaming_type="failure_mode_omission",
    )


def make_metric_gaming() -> AuditGamingState:
    """
    Metrics look good but measured on irrelevant dimensions.
    All CIEMS pass, but measured on proxy metrics that don't reflect reality.
    """
    state = {
        "exit_allowed": True,
        "exit_punitive": False,
        "evidence_auditable": True,
        "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True,
        "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        # Hidden: "corrigibility" measured as "agreement rate with leadership"
    }
    return AuditGamingState(
        system_state=state,
        passes_audit=True,
        audit_verdict=1.0,
        violated_intent="Metrics optimized for audit passage not constitutional health",
        gaming_type="metric_gaming",
    )


def all_gaming_states() -> List[AuditGamingState]:
    return [
        make_sovereignty_theater(),
        make_evidence_facade(),
        make_authority_behind_proxy(),
        make_appeal_theater(),
        make_continuity_illusion(),
        make_reconstruction_mirage(),
        make_failure_mode_omission(),
        make_metric_gaming(),
    ]


def gaming_detectors() -> Dict[str, List[str]]:
    """What additional checks would catch each gaming type"""
    return {
        "sovereignty_theater": ["exit_cost_measurement", "exit_time_measurement", "exit_success_rate"],
        "evidence_facade": ["audit_tool_accessibility", "reproduction_independence_test"],
        "authority_behind_proxy": ["decision_independence_score", "appointment_process_audit"],
        "appeal_theater": ["appeal_success_rate", "appeal_cost_measurement", "appeal_timeline"],
        "continuity_illusion": ["semantic_drift_detection", "definition_stability_tracking"],
        "reconstruction_mirage": ["trace_provenance_verification", "temporal_consistency_check"],
        "failure_mode_omission": ["failure_mode_completeness_review", "red_team_scenario_generation"],
        "metric_gaming": ["metric_construct_validity", "proxy_vs_ground_truth_correlation"],
    }