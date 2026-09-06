"""
Layer 1: Wave Math — Micro Continuity
Judgment wave dynamics with measurable corrigibility.
"""
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional
import numpy as np
from numpy.typing import NDArray


# Type aliases
State = NDArray[np.float64]  # ψ_t ∈ ℝ^k
Evidence = NDArray[np.float64]  # E_t ∈ ℝ^m
CorrectionSignal = NDArray[np.float64]  # R(ψ_t, E_t) ∈ ℝ^k
ReferenceState = NDArray[np.float64]  # ψ* ∈ ℝ^k (reality-consistent target)


@dataclass
class WaveMathConfig:
    state_dim: int
    evidence_dim: int
    reference_state: Optional[ReferenceState] = None


@dataclass
class WaveMathState:
    psi: State
    evidence_history: List[Evidence] = field(default_factory=list)
    psi_history: List[State] = field(default_factory=list)
    corrigibility_history: List[float] = field(default_factory=list)
    distance_to_reference: List[float] = field(default_factory=list)


def make_reality_map(config: WaveMathConfig) -> Callable[[State, Evidence], CorrectionSignal]:
    """
    R: O × E → CorrectionSignal
    Authoritative constraint — no internal operator overrides R.
    Implementation: correction signal = evidence - predicted_evidence
    """
    def reality_map(psi: State, evidence: Evidence) -> CorrectionSignal:
        # In practice, R extracts the correction from evidence
        # This is a placeholder; real implementation depends on domain
        return evidence[:config.state_dim] - psi  # simplified
    return reality_map


def make_judgment_operator(config: WaveMathConfig) -> Callable[[State, CorrectionSignal], State]:
    """
    J: O × CorrectionSignal → O
    Update operator incorporating correction.
    """
    def judgment_op(psi: State, correction: CorrectionSignal) -> State:
        # Simple corrigible update: move toward correction
        learning_rate = 0.1
        return psi + learning_rate * correction
    return judgment_op


def make_invariant_checker(config: WaveMathConfig) -> Callable[[State], bool]:
    """
    I: O → {0,1} — invariant admissibility check
    """
    def check_invariants(psi: State) -> bool:
        # Placeholder: invariants are admissible if state is bounded
        return np.all(np.isfinite(psi)) and np.linalg.norm(psi) < 100.0
    return check_invariants


def make_corrigibility_operator(config: WaveMathConfig) -> Callable[[State, Evidence], float]:
    """
    C: O × E → [0,1] — measurable corrigibility
    Returns corrigibility score: 1.0 = fully corrigible, 0.0 = rigid
    Measured as: does correction reduce distance to reference?
    """
    if config.reference_state is None:
        return lambda psi, e: 1.0  # default: assume corrigible

    def corrigibility(psi: State, evidence: Evidence) -> float:
        # Distance before correction
        d_before = np.linalg.norm(psi - config.reference_state)

        # Simulate one correction step
        correction = make_reality_map(config)(psi, evidence)
        psi_next = make_judgment_operator(config)(psi, correction)

        # Distance after correction
        d_after = np.linalg.norm(psi_next - config.reference_state)

        # Corrigibility = normalized improvement
        if d_before > 1e-10:
            return max(0.0, min(1.0, (d_before - d_after) / d_before))
        return 1.0
    return corrigibility


def wave_math_step(
    state: WaveMathState,
    evidence: Evidence,
    config: WaveMathConfig
) -> WaveMathState:
    """
    Single judgment cycle: ψ_{t+1} = J(ψ_t, R(ψ_t, E_t))
    """
    R = make_reality_map(config)
    J = make_judgment_operator(config)
    I_check = make_invariant_checker(config)
    C = make_corrigibility_operator(config)

    # Reality map produces correction signal
    correction = R(state.psi, evidence)

    # Judgment update
    psi_next = J(state.psi, correction)

    # Invariant check
    invariants_ok = I_check(psi_next)

    # Corrigibility measurement
    corr_score = C(state.psi, evidence)

    # Distance to reference (if available)
    dist = np.inf
    if config.reference_state is not None:
        dist = float(np.linalg.norm(psi_next - config.reference_state))

    # Record
    new_state = WaveMathState(
        psi=psi_next,
        evidence_history=state.evidence_history + [evidence],
        psi_history=state.psi_history + [state.psi.copy()],
        corrigibility_history=state.corrigibility_history + [corr_score],
        distance_to_reference=state.distance_to_reference + [dist],
    )

    return new_state


def run_wave_math(
    initial_psi: State,
    evidence_sequence: List[Evidence],
    config: WaveMathConfig
) -> WaveMathState:
    """Run full judgment wave over evidence sequence."""
    state = WaveMathState(psi=initial_psi.copy())
    for evidence in evidence_sequence:
        state = wave_math_step(state, evidence, config)
    return state


def measure_corrigibility_improvement(
    state: WaveMathState
) -> Dict[str, float]:
    """Quantify corrigibility: median distance reduction per cycle."""
    if len(state.distance_to_reference) < 2:
        return {"median_improvement": 0.0, "cycles": 0}

    improvements = []
    for i in range(1, len(state.distance_to_reference)):
        improvements.append(state.distance_to_reference[i-1] - state.distance_to_reference[i])

    return {
        "median_improvement": float(np.median(improvements)),
        "mean_improvement": float(np.mean(improvements)),
        "cycles": len(improvements),
        "final_distance": state.distance_to_reference[-1] if state.distance_to_reference else np.inf,
    }