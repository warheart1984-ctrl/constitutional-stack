"""
Parameter Sweep Framework
Systematic exploration of constitutional stack parameter spaces.
"""
from typing import Dict, List, Any, Callable, Tuple
from dataclasses import dataclass
import numpy as np
import itertools
import json


@dataclass
class SweepResult:
    params: Dict[str, Any]
    metrics: Dict[str, float]
    passed: bool
    failure_mode: str = ""


class ParameterSweep:
    """Generic parameter sweep runner"""
    
    def __init__(self, param_space: Dict[str, List[Any]], test_fn: Callable):
        self.param_space = param_space
        self.test_fn = test_fn
        self.results: List[SweepResult] = []
    
    def generate_combinations(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations"""
        keys = list(self.param_space.keys())
        values = list(self.param_space.values())
        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))
        return combinations
    
    def run(self, max_combinations: int = None) -> List[SweepResult]:
        """Run sweep over all combinations"""
        combinations = self.generate_combinations()
        if max_combinations:
            combinations = combinations[:max_combinations]
        
        self.results = []
        for i, params in enumerate(combinations):
            try:
                metrics, passed, failure_mode = self.test_fn(params)
                self.results.append(SweepResult(
                    params=params,
                    metrics=metrics,
                    passed=passed,
                    failure_mode=failure_mode,
                ))
            except Exception as e:
                self.results.append(SweepResult(
                    params=params,
                    metrics={},
                    passed=False,
                    failure_mode=f"error: {str(e)}",
                ))
            
            if i % 50 == 0:
                print(f"  Completed {i}/{len(combinations)} combinations")
        
        return self.results
    
    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        failure_modes = {}
        for r in self.results:
            if not r.passed:
                failure_modes[r.failure_mode] = failure_modes.get(r.failure_mode, 0) + 1
        
        return {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total if total > 0 else 0,
            "failure_modes": failure_modes,
        }
    
    def save(self, filepath: str):
        """Save results to JSON"""
        data = {
            "param_space": {k: [str(v) for v in vals] for k, vals in self.param_space.items()},
            "results": [
                {
                    "params": r.params,
                    "metrics": r.metrics,
                    "passed": r.passed,
                    "failure_mode": r.failure_mode,
                }
                for r in self.results
            ],
            "summary": self.summary(),
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Layer-specific parameter spaces

LAYER1_PARAM_SPACE = {
    "learning_rate": [0.01, 0.05, 0.1, 0.2, 0.5],
    "state_dim": [2, 3, 5, 10],
    "evidence_noise": [0.01, 0.05, 0.1, 0.2, 0.5],
    "reference_distance": [0.5, 1.0, 2.0, 5.0],
}

LAYER2_PARAM_SPACE = {
    "adaptation_rate": [0.01, 0.05, 0.1, 0.2, 0.5],
    "noise_level": [0.001, 0.01, 0.05, 0.1, 0.2],
    "consequence_dim": [2, 3, 5, 10],
    "generations": [10, 20, 50, 100],
}

LAYER3_PARAM_SPACE = {
    "epsilon": [0.01, 0.05, 0.1, 0.2, 0.5, 1.0],
    "trace_noise": [0.001, 0.01, 0.05, 0.1, 0.2],
    "state_dim": [2, 3, 5],
    "trace_dim": [3, 5, 10, 20],
}

LAYER4_PARAM_SPACE = {
    "state_dim": [2, 3, 4, 5, 8, 16],
    "involution_type": ["reflection", "permutation", "householder"],
}

LAYER5_PARAM_SPACE = {
    "a": [0.5, 1.0, 2.0, 5.0],
    "omega": [0.5, 1.0, 2.0, 5.0],
    "v": [0.1, 0.5, 1.0, 2.0],
    "M": [0.1, 0.172, 0.25, 0.5],
    "phi_uncertainty_deg": [0.1, 0.5, 1.0, 2.0, 5.0],
}

LAYER6_PARAM_SPACE = {
    "hard_constraint_weight": [1.0, 2.0, 5.0, 10.0, 100.0],
    "soft_constraint_weight": [0.1, 0.5, 1.0, 2.0],
    "verdict_threshold": [0.5, 0.7, 0.8, 0.9, 0.95, 0.99],
}

LAYER7_PARAM_SPACE = {
    "lyapunov_threshold": [0.5, 0.6, 0.7, 0.8, 0.9],
    "intervention_gain": [0.1, 0.2, 0.5, 1.0, 2.0],
    "audit_frequency": [1, 5, 10, 20],
    "max_cycles": [50, 100, 200],
}

LAYER8_PARAM_SPACE = {
    "D_h": [0.01, 0.05, 0.1, 0.2, 0.5],
    "v_max": [0.1, 0.5, 1.0, 2.0, 5.0],
    "dt": [0.001, 0.005, 0.01, 0.05],
    "grid_size": [32, 64, 128, 256],
}

LAYER9_PARAM_SPACE = {
    "num_layers": [9],  # fixed
    "invariant_count_per_layer": [1, 2, 3, 5],
}