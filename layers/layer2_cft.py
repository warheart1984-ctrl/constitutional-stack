"""
Layer 2: CFT — Macro Continuity
Consequence transmission across generations with information-theoretic fidelity.
"""
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray


# Type aliases
GenState = NDArray[np.float64]  # x_n ∈ ℝ^k (generation state)
Consequence = NDArray[np.float64]  # k_n ∈ ℝ^m (consequence vector)
Evidence = NDArray[np.float64]  # E_n ∈ ℝ^m (macro evidence)


@dataclass
class CFTConfig:
    state_dim: int
    consequence_dim: int
    evidence_dim: int


@dataclass
class CFTState:
    x: GenState
    x_history: List[GenState] = field(default_factory=list)
    consequence_history: List[Consequence] = field(default_factory=list)
    evidence_history: List[Evidence] = field(default_factory=list)
    transmission_fidelity_history: List[float] = field(default_factory=list)


def make_consequence_map(config: CFTConfig) -> Callable[[GenState], Consequence]:
    """
    K: O → K — extract consequences from micro state
    """
    def K(x: GenState) -> Consequence:
        # Simplified: consequences are a projection of state
        return x[:config.consequence_dim]
    return K


def make_transmission_operator(config: CFTConfig) -> Callable[[Consequence, Evidence], Evidence]:
    """
    T: K_t → E_{t+1} — consequence-to-evidence compiler
    """
    def T(k: Consequence, noise: Evidence) -> Evidence:
        # Evidence for next generation = consequences + noise
        return k[:config.evidence_dim] + noise[:config.evidence_dim]
    return T


def make_stewardship_operator(config: CFTConfig) -> Callable[[GenState, Evidence], GenState]:
    """
    S: (Θ_t, E_{t+1}) → Θ_{t+1} — architecture rebuilder
    """
    def S(theta: GenState, evidence: Evidence) -> GenState:
        # Next generation architecture adapts to evidence
        adaptation_rate = 0.1
        return theta + adaptation_rate * (evidence[:config.state_dim] - theta)
    return S


def mutual_information(x: NDArray, y: NDArray, bins: int = 10) -> float:
    """
    Estimate I(X;Y) for continuous variables via histogram discretization.
    Handles multi-dimensional arrays by computing MI per dimension and averaging.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # If 1D, compute directly
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    if y.ndim == 1:
        y = y.reshape(-1, 1)

    # Ensure same shape
    if x.shape != y.shape:
        # Pad or truncate
        min_len = min(x.shape[0], y.shape[0])
        x = x[:min_len]
        y = y[:min_len]

    # Compute MI per dimension and average
    mi_sum = 0.0
    n_dims = min(x.shape[1], y.shape[1])
    for dim in range(n_dims):
        xi = x[:, dim]
        yi = y[:, dim]

        hist_2d, _, _ = np.histogram2d(xi, yi, bins=bins)
        pxy = hist_2d / np.sum(hist_2d) if np.sum(hist_2d) > 0 else hist_2d
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        mi = 0.0
        for i in range(bins):
            for j in range(bins):
                if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi += pxy[i, j] * np.log(pxy[i, j] / (px[i] * py[j]))
        mi_sum += mi

    return mi_sum / max(1, n_dims)


def transmission_fidelity(
    x_before: GenState,
    x_after: GenState,
    config: CFTConfig
) -> float:
    """
    H₂ = Transmission fidelity = I(x_n; x_{n+1}) / H(x_n) → [0,1]
    Normalized mutual information as coherence measure.
    """
    mi = mutual_information(x_before, x_after)

    # Entropy of x_before (using probability mass, not density)
    hist, _ = np.histogram(x_before.flatten(), bins=20, density=False)
    total = np.sum(hist)
    if total > 0:
        probs = hist / total
        probs = probs[probs > 0]
        h_x = -np.sum(probs * np.log(probs))
    else:
        h_x = 1.0

    if h_x > 1e-10:
        return min(1.0, mi / h_x)
    return 0.0


def cft_generation_step(
    state: CFTState,
    noise: Evidence,
    config: CFTConfig
) -> CFTState:
    """
    Single generation: x_{n+1} = T_n(x_n, η_n)
    """
    K = make_consequence_map(config)
    T = make_transmission_operator(config)
    S = make_stewardship_operator(config)

    # Extract consequences from current state
    consequence = K(state.x)

    # Transmit to next generation
    evidence_next = T(consequence, noise)

    # Stewardship rebuilds architecture
    x_next = S(state.x, evidence_next)

    # Measure transmission fidelity
    fidelity = transmission_fidelity(state.x, x_next, config)

    # Record
    new_state = CFTState(
        x=x_next,
        x_history=state.x_history + [state.x.copy()],
        consequence_history=state.consequence_history + [consequence],
        evidence_history=state.evidence_history + [evidence_next],
        transmission_fidelity_history=state.transmission_fidelity_history + [fidelity],
    )

    return new_state


def run_cft_lineage(
    initial_x: GenState,
    noise_sequence: List[Evidence],
    config: CFTConfig
) -> CFTState:
    """Run full lineage over noise sequence."""
    state = CFTState(x=initial_x.copy())
    for noise in noise_sequence:
        state = cft_generation_step(state, noise, config)
    return state


def measure_lineage_continuity(state: CFTState) -> Dict[str, float]:
    """Quantify lineage continuity metrics."""
    if len(state.transmission_fidelity_history) == 0:
        return {"mean_fidelity": 0.0, "min_fidelity": 0.0, "generations": 0}

    return {
        "mean_fidelity": float(np.mean(state.transmission_fidelity_history)),
        "min_fidelity": float(np.min(state.transmission_fidelity_history)),
        "generations": len(state.transmission_fidelity_history),
        "final_fidelity": state.transmission_fidelity_history[-1],
    }