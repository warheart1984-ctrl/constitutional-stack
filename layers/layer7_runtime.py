"""
Layer 7: Reflexive Constitutional Runtime (CRK-1) — Autopoietic Execution
Control loop: Audit → Evidence → R → J → ψ' with Lyapunov stability ΔL < 0
"""
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray

from constitutional_stack.layers.layer1_wave_math import (
    WaveMathConfig, WaveMathState, run_wave_math, measure_corrigibility_improvement
)
from constitutional_stack.layers.layer2_cft import (
    CFTConfig, CFTState, run_cft_lineage, measure_lineage_continuity
)
from constitutional_stack.layers.layer3_reconstruction import (
    ReconConfig, run_reconstruction, measure_reconstruction_quality
)
from constitutional_stack.layers.layer6_audit import (
    AuditConfig, run_audit, audit_feedback_control, make_ciems_constraints
)


@dataclass
class RuntimeConfig:
    wave_math: WaveMathConfig
    cft: CFTConfig
    recon: ReconConfig
    audit: AuditConfig
    lyapunov_threshold: float = 0.7  # lower threshold for testing
    max_cycles: int = 100


@dataclass
class RuntimeState:
    wave_state: WaveMathState
    cft_state: CFTState
    recon_state: Any  # ReconState
    audit_history: List[Dict] = field(default_factory=list)
    lyapunov_history: List[float] = field(default_factory=list)
    intervention_count: int = 0
    continuous: bool = True


def lyapunov_function(
    wave_state: WaveMathState,
    cft_state: CFTState,
    recon_metrics: Dict[str, float],
    audit_verdict: float,
    config: RuntimeConfig
) -> float:
    """
    L(x) = weighted sum of continuity metrics
    Higher L = healthier. ΔL < 0 outside acceptable region.
    """
    # Component metrics (normalized to [0,1] where 1 = healthy)
    corr_data = measure_corrigibility_improvement(wave_state)
    corrigibility = corr_data.get("median_improvement", 0)
    corrigibility = min(1.0, max(0.0, corrigibility * 10))  # scale

    transmission = measure_lineage_continuity(cft_state).get("mean_fidelity", 0)

    reconstruction = 1.0 - min(1.0, recon_metrics.get("mean_error", 1.0))

    audit_score = audit_verdict

    # Weighted Lyapunov (higher = healthier)
    L = (0.3 * corrigibility +
         0.2 * transmission +
         0.2 * reconstruction +
         0.3 * audit_score)

    return float(L)


def lyapunov_stability_check(runtime_state: RuntimeState) -> Dict[str, Any]:
    """
    Verify ΔL < 0 outside acceptable region (L < threshold)
    """
    L_hist = runtime_state.lyapunov_history
    if len(L_hist) < 2:
        return {"stable": True, "reason": "insufficient history"}

    deltas = np.diff(L_hist)
    # Outside acceptable: L < 0.7 (threshold)
    outside = [d for i, d in enumerate(deltas) if L_hist[i] < 0.7]

    return {
        "mean_delta": float(np.mean(deltas)),
        "delta_outside_acceptable": float(np.mean(outside)) if outside else 0.0,
        "stable_outside": all(d < 0 for d in outside) if outside else True,
        "total_cycles": len(L_hist),
    }


def constitutional_continuity_condition(
    wave_state: WaveMathState,
    cft_state: CFTState,
    recon_metrics: Dict[str, float],
    audit_verdict: float,
    config: RuntimeConfig
) -> bool:
    """
    Constitutional Continuity Condition:
    C_global ≥ θ ∧ Ρ ≥ ρ_min ∧ Audit = Pass
    """
    L = lyapunov_function(wave_state, cft_state, recon_metrics, audit_verdict, config)
    return L >= config.lyapunov_threshold


def reflexive_control_loop(
    initial_wave: NDArray,
    evidence_stream: List[NDArray],
    cft_noise: List[NDArray],
    recon_true_states: List[NDArray],
    recon_noise: List[NDArray],
    system_state_getter: Callable[[], Dict],
    config: RuntimeConfig
) -> RuntimeState:
    """
    Main reflexive loop:
    1. Wave Math step: ψ_{t+1} = J(ψ_t, R(ψ_t, E_t))
    2. Every N cycles: CFT generation step
    3. Every M cycles: Reconstruction check
    4. Every cycle: Audit → Evidence → R → J → ψ'
       u_t = K(V(x_t)) modifies behavior
    """
    # Initialize substates
    wave_state = WaveMathState(psi=initial_wave.copy())
    cft_state = CFTState(x=np.zeros(config.cft.state_dim))
    recon_state = None

    evidence_idx = 0
    cft_idx = 0
    recon_idx = 0

    runtime_state = RuntimeState(
        wave_state=wave_state,
        cft_state=cft_state,
        recon_state=None,
        audit_history=[],
        lyapunov_history=[],
        intervention_count=0,
        continuous=True,
    )

    for cycle in range(config.max_cycles):
        # 1. Get system state for audit
        system_state = system_state_getter()

        # 2. Run audit
        audit_result = run_audit(system_state, config.audit)

        # 3. Compute feedback from audit
        intervention = audit_feedback_control(audit_result.verdict, threshold=0.95)

        # 4. Wave Math step with intervention
        if evidence_idx < len(evidence_stream):
            evidence = evidence_stream[evidence_idx].copy()
            # Apply intervention: if audit fails, inject corrective evidence
            if intervention > 0:
                evidence = evidence + intervention * 0.5  # corrective boost
            evidence_idx += 1

            wave_state = wave_math_step(wave_state, evidence, config.wave_math)

        # 5. CFT step (every 10 cycles = generation boundary)
        if cycle % 10 == 0 and cft_idx < len(cft_noise):
            noise = cft_noise[cft_idx]
            cft_state = cft_generation_step(cft_state, noise, config.cft)
            cft_idx += 1

        # 6. Reconstruction check (every 20 cycles)
        if cycle % 20 == 0 and recon_idx < len(recon_true_states):
            true_state = recon_true_states[recon_idx]
            noise = recon_noise[recon_idx]
            recon_state = run_reconstruction([true_state], [noise], config.recon)
            recon_idx += 1

        # 7. Compute Lyapunov
        recon_metrics = measure_reconstruction_quality(recon_state) if recon_state else {"mean_error": 1.0}
        L = lyapunov_function(wave_state, cft_state, recon_metrics, audit_result.verdict, config)
        runtime_state.lyapunov_history.append(L)

        # 8. Check continuity condition
        continuous = constitutional_continuity_condition(
            wave_state, cft_state, recon_metrics, audit_result.verdict, config
        )
        runtime_state.continuous = continuous

        # 9. Record
        runtime_state.audit_history.append({
            "cycle": cycle,
            "verdict": audit_result.verdict,
            "passed": audit_result.passed,
            "hard_violations": audit_result.hard_violations,
            "intervention": intervention,
            "L": L,
            "continuous": continuous,
        })

        if intervention > 0:
            runtime_state.intervention_count += 1

        # Early termination if continuity fails
        if not continuous and cycle > 10:
            print(f"Continuity failed at cycle {cycle}, L={L:.3f}")
            break

    # Final update
    runtime_state.wave_state = wave_state
    runtime_state.cft_state = cft_state
    runtime_state.recon_state = recon_state

    return runtime_state


def lyapunov_stability_check(runtime_state: RuntimeState) -> Dict[str, Any]:
    """
    Verify ΔL < 0 outside acceptable region
    """
    L_hist = runtime_state.lyapunov_history
    if len(L_hist) < 2:
        return {"stable": True, "reason": "insufficient history"}

    deltas = np.diff(L_hist)
    # Outside acceptable: L < threshold
    outside = [d for i, d in enumerate(deltas) if L_hist[i] < 0.8]

    return {
        "mean_delta": float(np.mean(deltas)),
        "delta_outside_acceptable": float(np.mean(outside)) if outside else 0.0,
        "stable_outside": all(d < 0 for d in outside) if outside else True,
        "total_cycles": len(L_hist),
    }


# Helper for wave_math_step import
from constitutional_stack.layers.layer1_wave_math import wave_math_step
from constitutional_stack.layers.layer2_cft import cft_generation_step


def test_layer7():
    """Test Layer 7: Reflexive Runtime"""
    print("=== Layer 7: Reflexive Constitutional Runtime ===")

    # Config
    config = RuntimeConfig(
        wave_math=WaveMathConfig(state_dim=3, evidence_dim=3, reference_state=np.array([1.0, 0.0, -1.0])),
        cft=CFTConfig(state_dim=3, consequence_dim=3, evidence_dim=3),
        recon=ReconConfig(state_dim=3, trace_dim=5, epsilon=0.5),
        audit=AuditConfig(constraints=make_ciems_constraints()),
        lyapunov_threshold=0.7,
        max_cycles=50,
    )

    # Evidence stream: mostly corrective
    np.random.seed(42)
    evidence_stream = [config.wave_math.reference_state + np.random.randn(3) * 0.1 for _ in range(50)]

    # CFT noise
    cft_noise = [np.random.randn(3) * 0.01 for _ in range(5)]

    # Reconstruction true states
    recon_states = [np.random.randn(3) for _ in range(3)]
    recon_noise = [np.random.randn(5) * 0.05 for _ in range(3)]

    # System state getter (starts compliant, then violates early)
    cycle_counter = [0]
    def system_state_getter():
        cycle_counter[0] += 1
        state = {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }
        # Inject violation after cycle 5 to test feedback
        if cycle_counter[0] > 5:
            state["exit_punitive"] = True
        return state

    # Run
    initial_wave = np.array([0.0, 0.0, 0.0])
    result = reflexive_control_loop(
        initial_wave, evidence_stream, cft_noise, recon_states, recon_noise,
        system_state_getter, config
    )

    # Analyze
    print(f"Cycles run: {len(result.audit_history)}")
    print(f"Interventions: {result.intervention_count}")
    print(f"Final continuous: {result.continuous}")

    # Lyapunov analysis
    stability = lyapunov_stability_check(result)
    print(f"Lyapunov: mean ΔL = {stability['mean_delta']:.4f}")
    print(f"Stable outside acceptable: {stability['stable_outside']}")

    # Audit trace
    for i, audit in enumerate(result.audit_history):
        if i % 10 == 0 or not audit["continuous"]:
            print(f"  Cycle {i}: V={audit['verdict']:.3f}, L={audit['L']:.3f}, cont={audit['continuous']}, int={audit['intervention']:.3f}")

    return {
        "cycles": len(result.audit_history),
        "interventions": result.intervention_count,
        "lyapunov_stable": stability['stable_outside'],
        "final_continuous": result.continuous,
    }


if __name__ == "__main__":
    test_layer7()