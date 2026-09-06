"""
Layer 3: Reconstruction Sufficiency — Meta Continuity
Inverse problem: y = A(x) + η, x̂ = R*(y), ε_recon = ‖x - x̂‖ ≤ ε
"""
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
import json

from constitutional_stack.schemas.trace_schema_v1 import TraceSchemaV1


# Type aliases
TrueState = NDArray[np.float64]  # x ∈ ℝ^k (ground truth state)
Trace = NDArray[np.float64]  # y ∈ ℝ^m (observed trace)
ReconstructedState = NDArray[np.float64]  # x̂ ∈ ℝ^k


@dataclass
class ReconConfig:
    state_dim: int
    trace_dim: int
    epsilon: float = 0.1  # reconstruction sufficiency threshold


@dataclass
class ReconState:
    true_states: List[TrueState] = field(default_factory=list)
    traces: List[Trace] = field(default_factory=list)
    reconstructions: List[ReconstructedState] = field(default_factory=list)
    errors: List[float] = field(default_factory=list)
    sufficiency_flags: List[bool] = field(default_factory=list)


def make_forward_model(config: ReconConfig) -> Callable[[TrueState], Trace]:
    """
    A: x → y (forward model generating traces from true state)
    """
    # Simplified linear forward model: y = W x + noise
    W = np.random.randn(config.trace_dim, config.state_dim) * 0.5

    def forward(x: TrueState) -> Trace:
        return W @ x
    return forward


def make_forward_model(config: ReconConfig) -> Tuple[Callable[[TrueState], Trace], NDArray]:
    """
    A: x → y (forward model generating traces from true state)
    Returns (forward_function, forward_matrix) so reconstructor can use same matrix
    """
    # Linear forward model: y = W x + noise
    W = np.random.randn(config.trace_dim, config.state_dim) * 0.5

    def forward(x: TrueState) -> Trace:
        return W @ x
    return forward, W


def make_reconstructor(config: ReconConfig, W: NDArray) -> Callable[[Trace], ReconstructedState]:
    """
    R*: y → x̂ (reconstruction operator)
    Uses same W matrix as forward model for consistent pseudo-inverse
    """
    W_pinv = np.linalg.pinv(W)

    def reconstruct(y: Trace) -> ReconstructedState:
        # Step 1: StateReconstructor - decode evidence & context
        x_hat = W_pinv @ y

        # Step 2: OperatorInferrer - infer update rule
        # (simplified: identity for now)

        # Step 3: OutcomeDecoder - decode outcome
        return x_hat

    return reconstruct


def reconstruction_error(x_true: TrueState, x_recon: ReconstructedState) -> float:
    """ε_recon = ‖x - x̂‖"""
    return float(np.linalg.norm(x_true - x_recon))


def is_reconstruction_sufficient(error: float, epsilon: float) -> bool:
    """Reconstruction sufficiency: ‖x - x̂‖ ≤ ε"""
    return error <= epsilon


def run_reconstruction(
    true_states: List[TrueState],
    noise_sequence: List[Trace],
    config: ReconConfig
) -> ReconState:
    """Run reconstruction pipeline over sequence."""
    A, W = make_forward_model(config)
    R_star = make_reconstructor(config, W)

    state = ReconState()

    for i, (x_true, noise) in enumerate(zip(true_states, noise_sequence)):
        # Generate trace
        trace = A(x_true) + noise

        # Reconstruct
        x_recon = R_star(trace)

        # Measure error
        error = reconstruction_error(x_true, x_recon)
        sufficient = is_reconstruction_sufficient(error, config.epsilon)

        # Record
        state.true_states.append(x_true)
        state.traces.append(trace)
        state.reconstructions.append(x_recon)
        state.errors.append(error)
        state.sufficiency_flags.append(sufficient)

    return state


def trace_to_schema_v1(
    gen: int,
    cycle: int,
    evidence_raw: Any,
    state_summary: Dict,
    interpretation: str,
    confidence: float,
    decision_rule: str,
    result: Dict,
    veto: bool,
) -> TraceSchemaV1:
    """Helper: create TraceSchemaV1 from reconstruction components."""
    from constitutional_stack.schemas.trace_schema_v1 import (
        EvidenceField, ContextField, ReasoningField,
        UncertaintyField, ThresholdsField, OutcomesField, CorrectionField
    )

    return TraceSchemaV1(
        generation=gen,
        cycle=cycle,
        evidence=EvidenceField(
            raw=evidence_raw,
            sources=["reconstruction_pipeline"],
            timestamp=""
        ),
        context=ContextField(
            stateSummary=state_summary,
            relevantHistory=[],
            environment={}
        ),
        reasoning=ReasoningField(
            interpretation=interpretation,
            justification="reconstruction_step",
            dependencies=[]
        ),
        uncertainty=UncertaintyField(
            estimates={},
            confidence=confidence,
            unknowns=[]
        ),
        thresholds=ThresholdsField(
            decisionRule=decision_rule,
            triggered=False,
            parameters={}
        ),
        outcomes=OutcomesField(
            result=result,
            measuredEvidence={},
            deltaFromExpectation={}
        ),
        correction=CorrectionField(
            veto=veto,
            correctionApplied=False,
            correctionType="none",
            postCorrectionState={}
        )
    )


def measure_reconstruction_quality(state: ReconState) -> Dict[str, Any]:
    """Quantify reconstruction metrics."""
    if not state.errors:
        return {"mean_error": np.inf, "sufficiency_rate": 0.0, "cycles": 0}

    return {
        "mean_error": float(np.mean(state.errors)),
        "median_error": float(np.median(state.errors)),
        "max_error": float(np.max(state.errors)),
        "sufficiency_rate": float(np.mean(state.sufficiency_flags)),
        "cycles": len(state.errors),
    }