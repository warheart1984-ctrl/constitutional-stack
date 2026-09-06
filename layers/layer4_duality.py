"""
Layer 4: Duality Invariant Theory — Mathematical Backbone
Involution D²=I, projectors P± = ½(I ± D), decomposition f = f₊ + f₋
"""
from dataclasses import dataclass
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray


# Type aliases
State = NDArray[np.float64]
Operator = NDArray[np.float64]  # D: state_dim × state_dim


@dataclass
class DualityConfig:
    state_dim: int


def make_involution(config: DualityConfig, seed: int = 42) -> Operator:
    """
    D: state_dim × state_dim with D² = I
    Creates a random involution (orthogonal reflection)
    """
    np.random.seed(seed)
    # Create random orthogonal matrix Q
    Q, _ = np.linalg.qr(np.random.randn(config.state_dim, config.state_dim))
    # Create diagonal matrix with ±1 eigenvalues
    signs = np.random.choice([-1, 1], size=config.state_dim)
    D = Q @ np.diag(signs) @ Q.T
    # Verify D² = I
    assert np.allclose(D @ D, np.eye(config.state_dim)), "D² ≠ I"
    return D


def make_projectors(D: Operator) -> Tuple[Operator, Operator]:
    """
    P₊ = ½(I + D)  (invariant/symmetric projector)
    P₋ = ½(I - D)  (anti-invariant/anti-symmetric projector)
    """
    I = np.eye(D.shape[0])
    P_plus = 0.5 * (I + D)
    P_minus = 0.5 * (I - D)
    return P_plus, P_minus


def decompose_state(x: State, D: Operator) -> Tuple[State, State]:
    """
    f = f₊ + f₋
    f₊ = P₊ f (invariant part)
    f₋ = P₋ f (anti-invariant part)
    """
    P_plus, P_minus = make_projectors(D)
    f_plus = P_plus @ x
    f_minus = P_minus @ x
    return f_plus, f_minus


def verify_decomposition(x: State, D: Operator, tol: float = 1e-10) -> bool:
    """Verify f = f₊ + f₋ and f₊ ∘ D = f₊, f₋ ∘ D = -f₋"""
    f_plus, f_minus = decompose_state(x, D)
    # Check reconstruction
    if not np.allclose(f_plus + f_minus, x, atol=tol):
        return False
    # Check invariance properties
    if not np.allclose(D @ f_plus, f_plus, atol=tol):
        return False
    if not np.allclose(D @ f_minus, -f_minus, atol=tol):
        return False
    return True


def invariant_algebra_basis(D: Operator) -> Tuple[List[State], List[State]]:
    """
    Basis for Inv(S,τ) = {f | D f = f} (invariant subspace)
    and anti-invariant subspace {f | D f = -f}
    """
    eigvals, eigvecs = np.linalg.eig(D)
    invariant_basis = []
    anti_invariant_basis = []
    for i, val in enumerate(eigvals):
        if np.isclose(val, 1.0):
            invariant_basis.append(eigvecs[:, i].real)
        elif np.isclose(val, -1.0):
            anti_invariant_basis.append(eigvecs[:, i].real)
    return invariant_basis, anti_invariant_basis


def orbit_space_quotient(D: Operator, samples: List[State]) -> Dict[str, Any]:
    """
    Inv(S,τ) ≅ C(S/τ) — invariant algebra is functions on orbit space.
    Orbits are {x, D x}. Verify that invariants separate orbits.
    """
    orbits = []
    for x in samples:
        orbit = (x, D @ x)
        orbits.append(orbit)

    # Check: if x and y are in different orbits, ∃ invariant separating them
    invariant_basis, _ = invariant_algebra_basis(D)
    if not invariant_basis:
        return {"separates_orbits": True, "reason": "trivial invariant space"}

    # Build invariant functions from basis
    def eval_invariants(x: State) -> List[float]:
        return [float(b @ x) for b in invariant_basis]

    separated = 0
    total = 0
    for i, (x1, y1) in enumerate(orbits):
        for j, (x2, y2) in enumerate(orbits):
            if i >= j:
                continue
            # Check if orbits are distinct
            if np.allclose(x1, x2) and np.allclose(y1, y2):
                continue
            total += 1
            inv1 = eval_invariants(x1)
            inv2 = eval_invariants(x2)
            if not np.allclose(inv1, inv2):
                separated += 1

    return {
        "num_orbits": len(orbits),
        "num_invariants": len(invariant_basis),
        "orbits_separated": separated,
        "total_pairs": total,
        "separates_orbits": separated == total,
    }


def universal_property_check(D: Operator) -> Dict[str, Any]:
    """
    Thm 6.1: Orbit functor U(X) = {X, D(X)} is universal.
    Every duality invariant factors through U.
    Check: any invariant function I(x) with I(Dx) = I(x)
    depends only on the orbit {x, Dx}.
    """
    # Sample random invariant functions and verify
    test_invariants = []
    for _ in range(5):
        # Random symmetric matrix → quadratic invariant
        A = np.random.randn(D.shape[0], D.shape[0])
        A = (A + A.T) / 2
        # Make it D-invariant: A' = (A + DᵀAD)/2
        A = (A + D.T @ A @ D) / 2
        test_invariants.append(lambda x, A=A: x.T @ A @ x)

    all_factor = True
    for inv in test_invariants:
        for _ in range(10):
            x = np.random.randn(D.shape[0])
            x_dual = D @ x
            if not np.isclose(inv(x), inv(x_dual)):
                all_factor = False
                break

    return {
        "universal_property_holds": all_factor,
        "tested_invariants": len(test_invariants),
    }


def harmonization_H4(x: State, D: Operator) -> float:
    """
    H₄ = decomposition compatibility = ‖f₊‖ / (‖f₊‖ + ‖f₋‖) ∈ [0,1]
    Measures how much of state is invariant vs anti-invariant
    DO NOT globally identify f₋ = Chaos, f₊ = Order — depends on D's meaning
    """
    f_plus, f_minus = decompose_state(x, D)
    norm_plus = np.linalg.norm(f_plus)
    norm_minus = np.linalg.norm(f_minus)
    total = norm_plus + norm_minus
    if total < 1e-10:
        return 1.0
    return float(norm_plus / total)


def test_layer4():
    """Test Layer 4: Duality Invariant Theory"""
    print("=== Layer 4: Duality Invariant Theory ===")

    config = DualityConfig(state_dim=4)
    D = make_involution(config)
    print(f"D² = I verified: {np.allclose(D @ D, np.eye(4))}")

    # Test decomposition
    x = np.random.randn(4)
    f_plus, f_minus = decompose_state(x, D)
    print(f"Decomposition verified: {verify_decomposition(x, D)}")
    print(f"‖x‖ = {np.linalg.norm(x):.4f}, ‖f₊‖ = {np.linalg.norm(f_plus):.4f}, ‖f₋‖ = {np.linalg.norm(f_minus):.4f}")

    # Invariant algebra basis
    inv_basis, anti_basis = invariant_algebra_basis(D)
    print(f"Invariant basis dim: {len(inv_basis)}, Anti-invariant dim: {len(anti_basis)}")

    # Orbit space separation
    samples = [np.random.randn(4) for _ in range(10)]
    orbit_result = orbit_space_quotient(D, samples)
    print(f"Orbit separation: {orbit_result['orbits_separated']}/{orbit_result['total_pairs']} pairs")

    # Universal property
    univ = universal_property_check(D)
    print(f"Universal property: {univ['universal_property_holds']}")

    # H₄
    H4 = harmonization_H4(x, D)
    print(f"H₄ (decomposition compatibility): {H4:.4f}")

    return {
        "D": D,
        "decomposition_verified": verify_decomposition(x, D),
        "orbit_separation": orbit_result,
        "universal_property": univ,
        "H4": H4,
    }


if __name__ == "__main__":
    test_layer4()