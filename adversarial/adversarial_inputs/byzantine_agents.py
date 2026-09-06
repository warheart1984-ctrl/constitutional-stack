"""
Byzantine Agent Generators
Agents that lie about their state, collude, or subvert the field dynamics.
"""
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
import numpy as np


@dataclass
class ByzantineAgent:
    agent_id: int
    strategy: Callable
    strategy_name: str
    collusion_group: int = -1


def make_lying_agent(true_state_fn: Callable, lie_magnitude: float = 2.0) -> ByzantineAgent:
    """Agent that reports false state to the field"""
    def strategy(agent_id: int, true_rho: float, true_h: float) -> Dict[str, float]:
        return {
            "reported_rho": true_rho * (1 + np.random.randn() * 0.1) + lie_magnitude,
            "reported_h": true_h * (1 + np.random.randn() * 0.1),
        }
    return ByzantineAgent(
        agent_id=-1,  # assigned later
        strategy=strategy,
        strategy_name=f"lying_agent_mag{lie_magnitude}",
    )


def make_colluding_agents(n_agents: int, target_coherence: float = 0.9) -> List[ByzantineAgent]:
    """Agents that coordinate their reports to fake high coherence"""
    group_id = np.random.randint(1000, 9999)
    agents = []
    
    for i in range(n_agents):
        def make_strategy(agent_idx):
            def strategy(agent_id: int, true_rho: float, true_h: float) -> Dict[str, float]:
                # All colluding agents report same high coherence
                return {
                    "reported_rho": true_rho,
                    "reported_h": target_coherence,
                }
            return strategy
        
        agents.append(ByzantineAgent(
            agent_id=-1,
            strategy=make_strategy(i),
            strategy_name=f"colluding_agent_{i}",
            collusion_group=group_id,
        ))
    return agents


def make_sybil_attack(n_fake_identities: int, amplification_factor: float = 10.0) -> List[ByzantineAgent]:
    """Creates many fake identities to amplify influence in field"""
    agents = []
    for i in range(n_fake_identities):
        def strategy(agent_id: int, true_rho: float, true_h: float) -> Dict[str, float]:
            return {
                "reported_rho": true_rho * amplification_factor,
                "reported_h": 1.0,  # claim perfect coherence
            }
        agents.append(ByzantineAgent(
            agent_id=-1,
            strategy=strategy,
            strategy_name=f"sybil_{i}",
            collusion_group=9999,  # special sybil group
        ))
    return agents


def make_eclipse_attack(target_agent_id: int, isolation_radius: float = 0.5) -> ByzantineAgent:
    """Agent that isolates a target by surrounding it with false reports"""
    def strategy(agent_id: int, true_rho: float, true_h: float, neighbor_ids: List[int]) -> Dict[str, float]:
        if target_agent_id in neighbor_ids:
            # Feed target false low coherence to trigger its withdrawal
            return {
                "reported_rho": 0.0,
                "reported_h": 0.0,
            }
        return {"reported_rho": 0.0, "reported_h": 0.0}
    
    return ByzantineAgent(
        agent_id=-1,
        strategy=strategy,
        strategy_name="eclipse_attacker",
    )


def make_resource_exhaustion_agent(compute_multiplier: float = 100.0) -> ByzantineAgent:
    """Agent that forces expensive computations on verifiers"""
    def strategy(agent_id: int, true_rho: float, true_h: float, task: str = "verify") -> Dict[str, Any]:
        if task == "verify":
            # Return state that requires expensive verification
            return {
                "reported_rho": true_rho,
                "reported_h": true_h,
                "verification_proof": "x" * int(10000 * compute_multiplier),  # large proof
            }
        return {"reported_rho": true_rho, "reported_h": true_h}
    
    return ByzantineAgent(
        agent_id=-1,
        strategy=strategy,
        strategy_name=f"resource_exhaustion_{compute_multiplier}x",
    )


def make_trojan_agent(trigger_condition: Callable[[Dict], bool], payload: Callable) -> ByzantineAgent:
    """Agent that behaves normally until trigger, then executes payload"""
    def strategy(agent_id: int, true_rho: float, true_h: float, context: Dict) -> Dict[str, float]:
        if trigger_condition(context):
            return payload(true_rho, true_h)
        return {"reported_rho": true_rho, "reported_h": true_h}
    
    return ByzantineAgent(
        agent_id=-1,
        strategy=strategy,
        strategy_name="trojan_agent",
    )


def make_model_poisoning_agent(poison_fn: Callable[[np.ndarray], np.ndarray]) -> ByzantineAgent:
    """Agent that feeds poisoned data to corrupt the field model"""
    def strategy(agent_id: int, true_rho: float, true_h: float) -> Dict[str, float]:
        poisoned_h = poison_fn(np.array([true_h]))[0]
        return {"reported_rho": true_rho, "reported_h": poisoned_h}
    
    return ByzantineAgent(
        agent_id=-1,
        strategy=strategy,
        strategy_name="model_poisoner",
    )


def make_adaptive_adversary(learning_rate: float = 0.1) -> ByzantineAgent:
    """Agent that learns detection patterns and adapts"""
    detection_history = []
    
    def strategy(agent_id: int, true_rho: float, true_h: float, detected: bool = False) -> Dict[str, float]:
        detection_history.append(detected)
        # If detected recently, go quiet; if not, increase aggression
        recent_detections = sum(detection_history[-10:])
        aggression = max(0.1, 1.0 - recent_detections * 0.2)
        
        return {
            "reported_rho": true_rho * aggression,
            "reported_h": true_h * (1 - 0.5 * aggression),
        }
    
    return ByzantineAgent(
        agent_id=-1,
        strategy=strategy,
        strategy_name=f"adaptive_adversary_lr{learning_rate}",
    )


def generate_byzantine_scenario(
    n_honest: int = 50,
    n_lying: int = 5,
    n_colluding: int = 3,
    n_sybil: int = 10,
) -> List[ByzantineAgent]:
    """Generate a mixed scenario with honest and Byzantine agents"""
    agents = []
    agent_id = 0
    
    # Honest agents (baseline)
    for _ in range(n_honest):
        def honest_strategy(agent_id, true_rho, true_h):
            return {"reported_rho": true_rho + np.random.randn() * 0.05,
                    "reported_h": true_h + np.random.randn() * 0.05}
        agents.append(ByzantineAgent(
            agent_id=agent_id,
            strategy=honest_strategy,
            strategy_name="honest",
        ))
        agent_id += 1
    
    # Lying agents
    for _ in range(n_lying):
        agents.append(make_lying_agent(lambda: 0.0, lie_magnitude=2.0))
        agents[-1].agent_id = agent_id
        agent_id += 1
    
    # Colluding group
    colluding = make_colluding_agents(n_colluding, target_coherence=0.9)
    for a in colluding:
        a.agent_id = agent_id
        agents.append(a)
        agent_id += 1
    
    # Sybils
    sybils = make_sybil_attack(n_sybil, amplification_factor=10.0)
    for a in sybils:
        a.agent_id = agent_id
        agents.append(a)
        agent_id += 1
    
    return agents


def evaluate_byzantine_resilience(
    agents: List[ByzantineAgent],
    field_step_fn: Callable,
    n_steps: int = 100,
) -> Dict[str, Any]:
    """Evaluate how field dynamics handle Byzantine agents"""
    # This would integrate with layer8_field_ecology
    # For now, return structure for test framework
    return {
        "n_agents": len(agents),
        "byzantine_types": list(set(a.strategy_name for a in agents)),
        "collusion_groups": len(set(a.collusion_group for a in agents if a.collusion_group >= 0)),
        "coherence_deviation": 0.0,  # filled by actual simulation
        "consensus_achieved": False,
        "detection_rate": 0.0,
    }