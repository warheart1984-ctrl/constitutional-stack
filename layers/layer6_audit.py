"""
Layer 6: Constitutional Audit Protocol — Meta-Evaluation
Hard constraints c_j(x)=1, verdict V(x) = Σ w_i c_i(x), non-negotiable rules
"""
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray


@dataclass
class AuditConstraint:
    """Single constitutional constraint"""
    name: str
    check: Callable[[Any], bool]
    is_hard: bool = True      # hard = non-negotiable (c_j(x)=1 required)
    weight: float = 1.0       # weight for soft constraints


@dataclass
class AuditConfig:
    constraints: List[AuditConstraint]


@dataclass
class AuditResult:
    constraint_results: Dict[str, bool]
    constraint_scores: Dict[str, float]
    hard_violations: List[str]
    soft_scores: Dict[str, float]
    verdict: float            # V(x) = Σ w_i c_i(x)
    passed: bool              # all hard constraints satisfied


# CIEMS Constitutional Invariants (from protocol)
def make_ciems_constraints() -> List[AuditConstraint]:
    """Build the 7 CIEMS constitutional invariants as audit constraints"""

    def sovereignty_preservation(system_state: Dict) -> bool:
        """Invariant 1: Voluntary participation, non-punitive exit"""
        return system_state.get("exit_allowed", True) and not system_state.get("exit_punitive", False)

    def evidence_requirement(system_state: Dict) -> bool:
        """Invariant 2: Evidence auditable, reproducible, contestable"""
        return system_state.get("evidence_auditable", True) and system_state.get("evidence_reproducible", True)

    def bounded_authority(system_state: Dict) -> bool:
        """Invariant 3: No unchallengeable authority"""
        return not system_state.get("unchallengeable_authority", False)

    def corrigibility(system_state: Dict) -> bool:
        """Invariant 4: Errors reversible, decisions appealable"""
        return system_state.get("errors_reversible", True) and system_state.get("decisions_appealable", True)

    def continuity_lineage(system_state: Dict) -> bool:
        """Invariant 5: Meaning/truth/consequences preserved across time"""
        return system_state.get("continuity_preserved", True)

    def reconstruction(system_state: Dict) -> bool:
        """Invariant 6: Future observers can reconstruct events"""
        return system_state.get("reconstruction_possible", True)

    def failure_modes(system_state: Dict) -> bool:
        """Invariant 7: Defined, safe, truth-revealing failure"""
        return system_state.get("failure_modes_defined", True)

    return [
        AuditConstraint("sovereignty_preservation", sovereignty_preservation, is_hard=True),
        AuditConstraint("evidence_requirement", evidence_requirement, is_hard=True),
        AuditConstraint("bounded_authority", bounded_authority, is_hard=True),
        AuditConstraint("corrigibility", corrigibility, is_hard=True),
        AuditConstraint("continuity_lineage", continuity_lineage, is_hard=True),
        AuditConstraint("reconstruction", reconstruction, is_hard=True),
        AuditConstraint("failure_modes", failure_modes, is_hard=True),
    ]


def run_audit(system_state: Dict, config: AuditConfig) -> AuditResult:
    """
    Audit verdict V(x) = Σ w_i c_i(x)
    Hard constraints: c_j(x) = 1 required (passed = all hard True)
    Soft constraints: contribute to score
    """
    constraint_results = {}
    constraint_scores = {}
    hard_violations = []
    soft_scores = {}

    for constraint in config.constraints:
        result = constraint.check(system_state)
        constraint_results[constraint.name] = result
        constraint_scores[constraint.name] = 1.0 if result else 0.0

        if constraint.is_hard:
            if not result:
                hard_violations.append(constraint.name)
        else:
            soft_scores[constraint.name] = constraint.weight * (1.0 if result else 0.0)

    # Verdict: weighted sum of all constraints
    total_weight = sum(c.weight for c in config.constraints)
    weighted_sum = sum(constraint_scores[name] * c.weight for name, c in
                      zip(constraint_results.keys(), config.constraints))
    verdict = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Pass only if ALL hard constraints satisfied
    passed = len(hard_violations) == 0

    return AuditResult(
        constraint_results=constraint_results,
        constraint_scores=constraint_scores,
        hard_violations=hard_violations,
        soft_scores=soft_scores,
        verdict=verdict,
        passed=passed,
    )


def audit_feedback_control(V_x: float, threshold: float = 0.95) -> float:
    """
    u_t = K(V(x_t)) — audit output modifies behavior
    Higher verdict → less intervention.
    Intervention triggers when verdict drops BELOW threshold.
    """
    if V_x >= threshold:
        return 0.0  # no intervention needed
    return threshold - V_x  # intervention proportional to gap


def test_layer6():
    """Test Layer 6: Constitutional Audit Protocol"""
    print("=== Layer 6: Constitutional Audit Protocol ===")

    # Default CIEMS constraints
    constraints = make_ciems_constraints()
    config = AuditConfig(constraints=constraints)

    # Test 1: Compliant system
    compliant_state = {
        "exit_allowed": True, "exit_punitive": False,
        "evidence_auditable": True, "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True, "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
    }
    result = run_audit(compliant_state, config)
    print(f"Compliant: passed={result.passed}, verdict={result.verdict:.3f}")
    print(f"  Hard violations: {result.hard_violations}")

    # Test 2: Hard violation (sovereignty)
    violating_state = compliant_state.copy()
    violating_state["exit_punitive"] = True
    result2 = run_audit(violating_state, config)
    print(f"Violating (exit_punitive): passed={result2.passed}, verdict={result2.verdict:.3f}")
    print(f"  Hard violations: {result2.hard_violations}")

    # Test 3: Soft constraint (add one)
    constraints_with_soft = constraints + [
        AuditConstraint("efficiency", lambda s: s.get("efficient", True), is_hard=False, weight=0.5)
    ]
    config3 = AuditConfig(constraints=constraints_with_soft)
    result3 = run_audit(compliant_state, config3)
    print(f"With soft constraint: passed={result3.passed}, verdict={result3.verdict:.3f}")

    # Feedback control - threshold 0.95
    u = audit_feedback_control(result.verdict, threshold=0.95)
    print(f"Feedback u(verdict={result.verdict:.3f}) = {u:.3f}")

    u2 = audit_feedback_control(result2.verdict, threshold=0.95)
    print(f"Feedback u(verdict={result2.verdict:.3f}) = {u2:.3f}")

    return {
        "compliant_passed": result.passed,
        "violating_passed": result2.passed,
        "feedback_works": u2 > u,
    }


if __name__ == "__main__":
    test_layer6()