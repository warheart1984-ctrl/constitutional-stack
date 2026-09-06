"""
Integrated test: Layers 1-3 computational prototype
Runs Wave Math → CFT → Reconstruction pipeline
Measures: H1 Corrigibility, H2 Continuity, H3 Reconstruction
"""
import numpy as np
from typing import List, Dict, Any

from constitutional_stack.layers.layer1_wave_math import (
    WaveMathConfig, WaveMathState, run_wave_math, measure_corrigibility_improvement
)
from constitutional_stack.layers.layer2_cft import (
    CFTConfig, CFTState, run_cft_lineage, measure_lineage_continuity
)
from constitutional_stack.layers.layer3_reconstruction import (
    ReconConfig, run_reconstruction, measure_reconstruction_quality
)


def test_hypothesis_h1_corrigibility() -> Dict[str, Any]:
    """
    H1: Corrigibility
    Measure: Truth-calibration error before/after reliable evidence
    Expected: Median error decreases without collapsing uncertainty to zero
    """
    print("\n=== H1: Corrigibility Test ===")

    # Setup
    config = WaveMathConfig(
        state_dim=3,
        evidence_dim=3,
        reference_state=np.array([1.0, 0.0, -1.0])  # ψ* = reality target
    )

    # Evidence sequence: initially noisy, then reliable corrective
    np.random.seed(42)
    evidence_sequence = [
        np.random.randn(3) * 0.5 for _ in range(5)  # noisy
    ] + [
        config.reference_state + np.random.randn(3) * 0.1 for _ in range(10)  # reliable corrective
    ]

    # Run
    initial_psi = np.array([0.0, 0.0, 0.0])
    final_state = run_wave_math(initial_psi, evidence_sequence, config)

    # Measure
    metrics = measure_corrigibility_improvement(final_state)

    print(f"  Median improvement per cycle: {metrics['median_improvement']:.4f}")
    print(f"  Mean improvement per cycle: {metrics['mean_improvement']:.4f}")
    print(f"  Final distance to ψ*: {metrics['final_distance']:.4f}")
    print(f"  Corrigibility history: {[f'{c:.3f}' for c in final_state.corrigibility_history]}")

    # Hypothesis check
    passed = metrics['median_improvement'] > 0.0 and metrics['final_distance'] < 0.5
    print(f"  H1 PASSED: {passed}")

    return {
        "hypothesis": "H1",
        "passed": passed,
        "metrics": metrics,
    }


def test_hypothesis_h2_continuity() -> Dict[str, Any]:
    """
    H2: Continuity
    Measure: Information retention, invariant preservation, version drift
    Expected: Required facts/constraints survive handoffs with bounded distortion
    """
    print("\n=== H2: Continuity Test ===")

    config = CFTConfig(
        state_dim=3,
        consequence_dim=3,
        evidence_dim=3
    )

    # Noise sequence: VERY small perturbations (high fidelity regime)
    np.random.seed(123)
    noise_sequence = [
        np.random.randn(3) * 0.01 for _ in range(20)
    ]

    initial_x = np.array([1.0, -1.0, 0.5])
    final_state = run_cft_lineage(initial_x, noise_sequence, config)

    metrics = measure_lineage_continuity(final_state)

    print(f"  Mean transmission fidelity: {metrics['mean_fidelity']:.4f}")
    print(f"  Min transmission fidelity: {metrics['min_fidelity']:.4f}")
    print(f"  Generations: {metrics['generations']}")

    # Hypothesis check: fidelity stays above threshold
    passed = metrics['mean_fidelity'] > 0.3 and metrics['min_fidelity'] > 0.0
    print(f"  H2 PASSED: {passed}")

    return {
        "hypothesis": "H2",
        "passed": passed,
        "metrics": metrics,
    }


def test_hypothesis_h3_reconstruction() -> Dict[str, Any]:
    """
    H3: Reconstruction
    Measure: Reconstruction error and provenance completeness
    Expected: Later observers recover event state within declared tolerance
    """
    print("\n=== H3: Reconstruction Test ===")

    config = ReconConfig(
        state_dim=3,
        trace_dim=5,
        epsilon=0.5  # tolerance
    )

    # True states to reconstruct
    np.random.seed(456)
    true_states = [
        np.random.randn(3) for _ in range(15)
    ]

    # Noise on traces
    noise_sequence = [
        np.random.randn(5) * 0.05 for _ in range(15)
    ]

    final_state = run_reconstruction(true_states, noise_sequence, config)

    metrics = measure_reconstruction_quality(final_state)

    print(f"  Mean reconstruction error: {metrics['mean_error']:.4f}")
    print(f"  Median error: {metrics['median_error']:.4f}")
    print(f"  Sufficiency rate (ε={config.epsilon}): {metrics['sufficiency_rate']:.2%}")

    # Hypothesis check
    passed = metrics['sufficiency_rate'] > 0.7 and metrics['mean_error'] < config.epsilon
    print(f"  H3 PASSED: {passed}")

    return {
        "hypothesis": "H3",
        "passed": passed,
        "metrics": metrics,
    }


def run_integrated_pipeline() -> Dict[str, Any]:
    """
    Full L1→L2→L3 pipeline:
    Wave Math (correction) → CFT (transmission) → Reconstruction (recovery)
    """
    print("\n" + "="*60)
    print("INTEGRATED L1→L2→L3 PIPELINE")
    print("="*60)

    results = {
        "H1": test_hypothesis_h1_corrigibility(),
        "H2": test_hypothesis_h2_continuity(),
        "H3": test_hypothesis_h3_reconstruction(),
    }

    all_passed = all(r["passed"] for r in results.values())
    print(f"\n{'='*60}")
    print(f"ALL HYPOTHESES PASSED: {all_passed}")
    print(f"{'='*60}")

    return {
        "all_passed": all_passed,
        "results": results,
    }


if __name__ == "__main__":
    results = run_integrated_pipeline()

    # Summary
    print("\nSUMMARY:")
    for h, r in results["results"].items():
        status = "✓" if r["passed"] else "✗"
        print(f"  {status} {r['hypothesis']}: {r['metrics']}")