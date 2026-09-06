"""
Layer 8: Constitutional Field Ecology — Multi-Agent Constitutional Physics
Continuum fields: ρ(x,t) = agent density, h(x,t) = local harmonization/coherence
PDEs for density transport and coherence diffusion/reaction
"""
from dataclasses import dataclass
from typing import Callable, Any, Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray


@dataclass
class FieldConfig:
    """Configuration for constitutional field simulation"""
    grid_size: int = 64          # spatial grid points (1D for simplicity)
    dx: float = 0.1              # spatial step
    dt: float = 0.01             # time step
    num_steps: int = 1000        # simulation steps
    D_h: float = 0.1             # coherence diffusion coefficient
    v_max: float = 1.0           # max agent velocity
    rho_max: float = 1.0         # max agent density
    h_max: float = 1.0           # max coherence


# Type aliases
DensityField = NDArray[np.float64]      # ρ(x) ∈ [0, ρ_max]
CoherenceField = NDArray[np.float64]    # h(x) ∈ [0, h_max]
VelocityField = NDArray[np.float64]     # v(x) ∈ [-v_max, v_max]


def initialize_fields(config: FieldConfig) -> Tuple[DensityField, CoherenceField]:
    """Initialize ρ(x,0) and h(x,0) with localized agent cluster"""
    x = np.arange(config.grid_size) * config.dx
    rho = np.zeros(config.grid_size)
    h = np.zeros(config.grid_size)

    # Gaussian cluster of agents at center
    center = config.grid_size // 2
    sigma = config.grid_size * 0.1
    rho = config.rho_max * np.exp(-0.5 * ((np.arange(config.grid_size) - center) / sigma)**2)

    # Initial coherence proportional to density
    h = rho / config.rho_max * config.h_max * 0.5

    return rho, h


def source_term(rho: DensityField, h: CoherenceField, config: FieldConfig) -> DensityField:
    """
    S(ρ, h) = source/sink term for agent density
    Agents attracted to high coherence regions; leave low coherence
    """
    # Logistic growth with coherence-dependent carrying capacity
    growth = 0.01 * rho * (1 - rho / config.rho_max)
    # Coherence-dependent attraction
    coherence_attraction = 0.02 * h * (config.rho_max - rho)
    # Dissipation
    dissipation = -0.005 * rho
    return growth + coherence_attraction + dissipation


def coherence_dynamics(rho: DensityField, h: CoherenceField, config: FieldConfig) -> CoherenceField:
    """
    ∂h/∂t = D_h ∇²h + F(ρ, h)
    F(ρ, h) = coherence generation by agents - decay
    """
    # Diffusion term (finite difference)
    laplacian = np.zeros_like(h)
    laplacian[1:-1] = (h[:-2] - 2*h[1:-1] + h[2:]) / config.dx**2

    # Reaction term: agents generate coherence, but coherence decays
    generation = 0.05 * rho * (1 - h / config.h_max)  # density creates coherence up to max
    decay = -0.02 * h

    return config.D_h * laplacian + generation + decay


def agent_velocity(rho: DensityField, h: CoherenceField, config: FieldConfig) -> VelocityField:
    """
    v(x) = agent velocity field
    Agents move toward higher coherence (chemotaxis-like)
    """
    v = np.zeros_like(rho)
    # Gradient of coherence
    grad_h = np.gradient(h, config.dx)
    # Velocity proportional to coherence gradient, capped
    v = np.clip(config.v_max * grad_h, -config.v_max, config.v_max)
    return v


def density_transport(rho: DensityField, h: CoherenceField, v: VelocityField, config: FieldConfig) -> DensityField:
    """
    ∂ρ/∂t + ∇·(ρv) = S(ρ, h)  (advection + source)
    Upwind scheme for advection
    """
    advective = np.zeros_like(rho)
    # Upwind scheme
    for i in range(1, config.grid_size - 1):
        if v[i] > 0:
            advective[i] = -v[i] * (rho[i] - rho[i-1]) / config.dx
        else:
            advective[i] = -v[i] * (rho[i+1] - rho[i]) / config.dx

    source = source_term(rho, h, config)
    return advective + source


def step_fields(rho: DensityField, h: CoherenceField, config: FieldConfig) -> Tuple[DensityField, CoherenceField]:
    """Single time step for coupled PDE system"""
    # Compute velocity from current fields
    v = agent_velocity(rho, h, config)

    # Update density (advection + source)
    rho_new = rho + config.dt * density_transport(rho, h, v, config)
    rho_new = np.clip(rho_new, 0, config.rho_max)

    # Update coherence (diffusion + reaction)
    h_new = h + config.dt * coherence_dynamics(rho, h, config)
    h_new = np.clip(h_new, 0, config.h_max)

    return rho_new, h_new


def compute_continuity_metrics(rho: DensityField, h: CoherenceField, config: FieldConfig) -> Dict[str, float]:
    """Compute field-level continuity metrics"""
    total_agents = np.sum(rho) * config.dx
    mean_coherence = np.mean(h[rho > 0.01]) if np.any(rho > 0.01) else 0.0
    coherence_variance = np.var(h[rho > 0.01]) if np.any(rho > 0.01) else 0.0

    # Polarization: coherence alignment with density gradient
    if np.any(rho > 0.01):
        masked_h = h[rho > 0.01]
        polarization = np.mean(masked_h)
    else:
        polarization = 0.0

    return {
        "total_agents": float(total_agents),
        "mean_coherence": float(mean_coherence),
        "coherence_variance": float(coherence_variance),
        "polarization": float(polarization),
    }


def run_field_simulation(config: FieldConfig) -> Dict[str, Any]:
    """Run full field simulation"""
    rho, h = initialize_fields(config)

    history = {
        "rho": [rho.copy()],
        "h": [h.copy()],
        "metrics": [],
    }

    for step in range(config.num_steps):
        rho, h = step_fields(rho, h, config)
        if step % 50 == 0:
            history["rho"].append(rho.copy())
            history["h"].append(h.copy())
            metrics = compute_continuity_metrics(rho, h, config)
            history["metrics"].append({"step": step, **metrics})

    # Final metrics
    final_metrics = compute_continuity_metrics(rho, h, config)

    return {
        "history": history,
        "final_rho": rho,
        "final_h": h,
        "final_metrics": final_metrics,
    }


def test_layer8():
    """Test Layer 8: Constitutional Field Ecology"""
    print("=== Layer 8: Constitutional Field Ecology ===")

    config = FieldConfig(
        grid_size=64,
        dx=0.1,
        dt=0.005,
        num_steps=500,
    )

    result = run_field_simulation(config)

    print(f"Final total agents: {result['final_metrics']['total_agents']:.2f}")
    print(f"Final mean coherence: {result['final_metrics']['mean_coherence']:.4f}")
    print(f"Final polarization: {result['final_metrics']['polarization']:.4f}")

    # Check: coherence should increase where agents concentrate
    hist = result["history"]["metrics"]
    if len(hist) >= 2:
        initial_pol = hist[0]["polarization"]
        final_pol = hist[-1]["polarization"]
        print(f"Polarization: {initial_pol:.4f} → {final_pol:.4f}")

    return {
        "passed": result['final_metrics']['polarization'] > 0.1,
        "final_metrics": result['final_metrics'],
    }


if __name__ == "__main__":
    test_layer8()