"""
Layer 1 Parameter Sweep Tests
Tests Wave Math corrigibility across parameter space.
"""
from typing import Dict, Any, Tuple
import numpy as np
from constitutional_stack.layers.layer1_wave_math import (
    WaveMathConfig, run_wave_math, measure_corrigibility_improvement
)


def layer1_test_fn(params: Dict[str, Any]) -> Tuple[Dict[str, float], bool, str]:
    """Test Layer 1 with given parameters"""
    config = WaveMathConfig(
        state_dim=params.get("state_dim", 3),
        evidence_dim=params.get("state_dim", 3),
        reference_state=np.array([1.0, 0.0, -1.0])[:params.get("state_dim", 3)],
    )
    
    learning_rate = params.get("learning_rate", 0.1)
    evidence_noise = params.get("evidence_noise", 0.1)
    reference_distance = params.get("reference_distance", 1.0)
    
    # Create reference at specified distance
    ref = np.array([1.0, 0.0, -1.0])[:config.state_dim]
    ref = ref / (np.linalg.norm(ref) + 1e-10) * reference_distance
    config.reference_state = ref
    
    # Evidence sequence
    np.random.seed(42)
    evidence_sequence = [
        ref + np.random.randn(config.state_dim) * evidence_noise for _ in range(30)
    ]
    
    # Monkey-patch learning rate in judgment operator
    import constitutional_stack.layers.layer1_wave_math as l1
    original_judgment_op = l1.make_judgment_operator
    
    def patched_judgment_op(config):
        def judgment_op(psi, correction):
            return psi + learning_rate * correction
        return judgment_op
    
    l1.make_judgment_operator = patched_judgment_op
    
    try:
        initial_psi = np.zeros(config.state_dim)
        final_state = run_wave_math(initial_psi, evidence_sequence, config)
        metrics = measure_corrigibility_improvement(final_state)
        
        # Pass criteria
        median_improvement = metrics.get("median_improvement", 0)
        final_dist = metrics.get("final_distance", float('inf'))
        
        passed = median_improvement > 0.0 and final_dist < reference_distance * 0.5
        failure_mode = ""
        if median_improvement <= 0:
            failure_mode = "no_improvement"
        elif final_dist >= reference_distance * 0.5:
            failure_mode = "insufficient_convergence"
        
        return metrics, passed, failure_mode
    finally:
        l1.make_judgment_operator = original_judgment_op


def run_layer1_sweep(max_combinations: int = None):
    """Run Layer 1 parameter sweep"""
    from . import ParameterSweep, LAYER1_PARAM_SPACE
    
    sweep = ParameterSweep(LAYER1_PARAM_SPACE, layer1_test_fn)
    results = sweep.run(max_combinations)
    sweep.save("layer1_sweep_results.json")
    
    summary = sweep.summary()
    print(f"Layer 1 Sweep: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.1%})")
    if summary['failure_modes']:
        print(f"  Failure modes: {summary['failure_modes']}")
    
    return sweep.results