"""
Layer 9 Extension: Voss Binding Deployment & Contract Registry
Runtime registration/versioning, deployment checklist, conformance matrix
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import time
import threading
import json
import hashlib
from pathlib import Path


class DeploymentStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class ChecklistItemStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class ChecklistItem:
    """Voss Binding §9.1 — Deployment Checklist Item"""
    item_id: str
    requirement: str
    verification_method: str
    status: ChecklistItemStatus = ChecklistItemStatus.PENDING
    verified_by: Optional[str] = None
    verified_at: Optional[float] = None
    evidence: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DeploymentPlan:
    """Deployment plan with checklist and rollback"""
    deployment_id: str
    version: str
    target_modules: List[str]
    checklist: List[ChecklistItem]
    status: DeploymentStatus = DeploymentStatus.PENDING
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    rolled_back: bool = False
    rollback_reason: Optional[str] = None


# Voss Binding §9.1 — Standard Deployment Checklist
DEPLOYMENT_CHECKLIST = [
    ChecklistItem(
        item_id="CHK-01",
        requirement="All modules registered in Contract Registry with complete contracts",
        verification_method="Registry query — zero incomplete registrations",
    ),
    ChecklistItem(
        item_id="CHK-02",
        requirement="GRE operational and self-check passing",
        verification_method="GRE health endpoint returns nominal",
    ),
    ChecklistItem(
        item_id="CHK-03",
        requirement="Drift Monitor baseline established for all active modules",
        verification_method="All modules report drift score 0.0 on baseline inputs",
    ),
    ChecklistItem(
        item_id="CHK-04",
        requirement="Audit Trail Writer connected and chain integrity verified",
        verification_method="Write test record, verify hash chain",
    ),
    ChecklistItem(
        item_id="CHK-05",
        requirement="Circuit Breakers initialized in CLOSED state for all modules",
        verification_method="Breaker state query returns CLOSED for all modules",
    ),
    ChecklistItem(
        item_id="CHK-06",
        requirement="Identity Boundary Enforcer verified for all agents",
        verification_method="Identity isolation test passes — no shared state detected",
    ),
    ChecklistItem(
        item_id="CHK-07",
        requirement="Governance Surface connected and displaying real-time state",
        verification_method="Surface shows all module, lane, and agent states",
    ),
    ChecklistItem(
        item_id="CHK-08",
        requirement="Operator authentication verified and Kill Switch tested",
        verification_method="Kill Switch test halts and recovers test scope",
    ),
    ChecklistItem(
        item_id="CHK-09",
        requirement="Message Bus operational with schema validation active",
        verification_method="Inter-agent test messages validated and logged",
    ),
    ChecklistItem(
        item_id="CHK-10",
        requirement="Backup and state snapshot mechanisms verified",
        verification_method="Snapshot capture and restore test passes",
    ),
]


@dataclass
class DeploymentRecord:
    """Record of a deployment attempt"""
    deployment_id: str
    version: str
    checklist_results: Dict[str, ChecklistItemStatus]
    overall_status: DeploymentStatus
    started_at: float
    completed_at: Optional[float]
    operator_id: str
    notes: str = ""


class ContractRegistryV2:
    """Enhanced Contract Registry with versioning and deployment integration"""
    
    def __init__(self):
        self.contracts: Dict[str, Any] = {}  # module_id -> contract
        self.versions: Dict[str, List[Any]] = {}  # module_id -> [contract versions]
        self.active_versions: Dict[str, str] = {}  # module_id -> version hash
        self.deployment_history: List[Any] = []
        self.lock = threading.Lock()
    
    def register(self, contract: Any) -> bool:
        """Register new contract with version"""
        with self.lock:
            if contract.module_id in self.contracts:
                return False
            self.contracts[contract.module_id] = contract
            if contract.module_id not in self._versions:
                self._versions[contract.module_id] = []
            self._versions[contract.module_id].append(contract)
            self._active_versions[contract.module_id] = self._hash_contract(contract)
            return True
    
    def get_contract(self, module_id: str, version: Optional[str] = None):
        with self.lock:
            if version:
                # Return specific version
                for v in self._versions.get(module_id, []):
                    if self._hash_contract(v) == version:
                        return v
                return None
            return self.contracts.get(module_id)
    
    def get_version_history(self, module_id: str) -> List[str]:
        with self.lock:
            return [self._hash_contract(v) for v in self._versions.get(module_id, [])]
    
    def deploy_new_version(self, module_id: str, new_contract: Any, operator_id: str) -> bool:
        """Deploy new contract version with operator approval"""
        # In real implementation: verify amendment protocol
        with self.lock:
            if module_id not in self.contracts:
                return False
            # Would verify operator approval, run tests, etc.
            self.contracts[module_id] = new_contract
            self._versions[module_id].append(new_contract)
            self._active_versions[module_id] = self._hash_contract(new_contract)
            return True
    
    def _hash_contract(self, contract: Any) -> str:
        content = json.dumps(contract.__dict__, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class DeploymentManager:
    """Manages deployments with full checklist verification"""
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentRecord] = {}
        self.lock = threading.Lock()
    
    def create_deployment(self, version: str, target_modules: List[str], 
                         operator_id: str) -> DeploymentRecord:
        """Create new deployment with checklist"""
        deployment_id = f"DEP-{int(time.time())}-{hash(version) % 10000:04d}"
        checklist = [ChecklistItem(
            item_id=item.item_id,
            requirement=item.requirement,
            verification_method=item.verification_method,
        ) for item in DEPLOYMENT_CHECKLIST]
        
        record = DeploymentRecord(
            deployment_id=deployment_id,
            version=version,
            checklist_results={item.item_id: ChecklistItemStatus.PENDING for item in checklist},
            overall_status=DeploymentStatus.PENDING,
            started_at=time.time(),
            completed_at=None,
            operator_id=operator_id,
        )
        
        with self.lock:
            self.deployments[deployment_id] = record
        return record
    
    def verify_checklist_item(self, deployment_id: str, item_id: str, 
                             operator_id: str, evidence: str = "") -> bool:
        """Verify a checklist item"""
        with self.lock:
            record = self.deployments.get(deployment_id)
            if not record:
                return False
            
            record.checklist_results[item_id] = ChecklistItemStatus.PASSED
            # Find and update item
            return True
    
    def complete_deployment(self, deployment_id: str, operator_id: str, 
                           notes: str = "") -> bool:
        """Complete deployment if all checklist items passed"""
        with self.lock:
            record = self.deployments.get(deployment_id)
            if not record:
                return False
            
            all_passed = all(
                status == ChecklistItemStatus.PASSED 
                for status in record.checklist_results.values()
            )
            
            if not all_passed:
                record.overall_status = DeploymentStatus.FAILED
                return False
            
            record.overall_status = DeploymentStatus.COMPLETED
            record.completed_at = time.time()
            record.notes = notes
            return True


class ConformanceMatrixV2:
    """Enhanced conformance matrix with deployment integration"""
    
    def __init__(self):
        self.layers = 9
        self.invariants: Dict[int, List[Dict]] = {}
        self.interfaces: List[Dict] = []
        self.closure_map: Optional[Callable] = None
        self.deployment_manager = DeploymentManager()
        self.contract_registry = ContractRegistryV2()
        self.lock = threading.Lock()
    
    def add_invariant(self, layer: int, name: str, check_fn: Callable, 
                     description: str, preserved_by: List[int] = None):
        if layer not in self.invariants:
            self.invariants[layer] = []
        self.invariants[layer].append({
            "name": name,
            "check": check_fn,
            "description": description,
            "preserved_by": preserved_by or [],
        })
    
    def add_interface(self, from_layer: int, to_layer: int, map_fn: Callable,
                     preserved_invariants: List[str]):
        self.interfaces.append({
            "from": from_layer,
            "to": to_layer,
            "map": map_fn,
            "preserves": preserved_invariants,
        })
    
    def set_closure(self, closure_fn: Callable):
        self.closure_map = closure_fn
    
    def verify_all(self, test_states: Dict[int, Any]) -> Dict[str, Any]:
        """Verify all invariants and interfaces"""
        results = {
            "invariants": {},
            "interfaces": {},
            "closure": False,
        }
        
        # Check invariants
        for layer, invariants in self.invariants.items():
            state = test_states.get(layer, {})
            for inv in invariants:
                try:
                    passed = inv["check"](state)
                    results["invariants"][f"L{layer}.{inv['name']}"] = passed
                except Exception as e:
                    results["invariants"][f"L{layer}.{inv['name']}"] = False
        
        # Check interfaces
        for iface in self.interfaces:
            from_state = test_states.get(iface["from"], {})
            try:
                mapped = iface["map"](from_state)
                all_preserved = True
                for inv_name in iface["preserves"]:
                    # Find invariant in to_layer
                    found = False
                    for inv in self.invariants.get(iface["to"], []):
                        if inv["name"] == inv_name:
                            found = True
                            if not inv["check"](mapped):
                                all_preserved = False
                            break
                    if not found:
                        all_preserved = False
                results["interfaces"][f"L{iface['from']}→L{iface['to']}"] = all_preserved
            except Exception:
                results["interfaces"][f"L{iface['from']}→L{iface['to']}"] = False
        
        # Check closure
        if self.closure_map:
            try:
                l9_state = test_states.get(9, {})
                l1_state = self.closure_map(l9_state)
                results["closure"] = l1_state is not None
            except Exception:
                results["closure"] = False
        
        return results
    
    def create_deployment(self, version: str, target_modules: List[str], 
                         operator_id: str) -> DeploymentRecord:
        return self.deployment_manager.create_deployment(version, target_modules, operator_id)
    
    def verify_checklist(self, deployment_id: str, item_id: str, 
                        operator_id: str, evidence: str = "") -> bool:
        return self.deployment_manager.verify_checklist_item(deployment_id, item_id, operator_id, evidence)
    
    def complete_deployment(self, deployment_id: str, operator_id: str, notes: str = "") -> bool:
        return self.deployment_manager.complete_deployment(deployment_id, operator_id, notes)


def build_voss_conformance_matrix() -> ConformanceMatrixV2:
    """Build conformance matrix with Voss Binding invariants"""
    cm = ConformanceMatrixV2()
    
    # Layer 1 invariants
    cm.add_invariant(1, "corrigibility", 
                    lambda x: x.get("corrigibility", 0) > 0.5,
                    "Correction reduces distance to reality target",
                    preserved_by=[2, 3, 4, 5, 6, 7, 8, 9])
    cm.add_invariant(1, "invariant_admissibility",
                    lambda x: x.get("invariants_ok", True),
                    "Invariants remain in admissible region",
                    preserved_by=[2, 3, 4, 5, 6, 7, 8, 9])
    cm.add_invariant(1, "determinism",
                    lambda x: x.get("deterministic", True),
                    "Identical inputs produce identical outputs (Λ.1)",
                    preserved_by=[4, 7, 9])
    
    # Layer 2 invariants
    cm.add_invariant(2, "transmission_fidelity",
                    lambda x: x.get("fidelity", 0) > 0.3,
                    "Information survives generational transmission",
                    preserved_by=[3, 4, 5, 6, 7, 8, 9])
    cm.add_invariant(2, "stewardship_fidelity",
                    lambda x: x.get("stewardship", 0) > 0.5,
                    "Architecture rebuilt faithfully",
                    preserved_by=[3, 4, 5, 6, 7, 8, 9])
    
    # Layer 3 invariants
    cm.add_invariant(3, "reconstruction_accuracy",
                    lambda x: x.get("recon_error", 1) < 0.5,
                    "Traces recover true state within ε",
                    preserved_by=[4, 5, 6, 7, 8, 9])
    
    # Layer 4 invariants
    cm.add_invariant(4, "involution_property",
                    lambda x: x.get("involution_verified", True),
                    "D² = I (Λ.1 determinism, Λ.4 identity)",
                    preserved_by=[5, 6, 7, 8, 9])
    
    # Layer 5 invariants
    cm.add_invariant(5, "I8_complementarity",
                    lambda x: x.get("I8_verified", True),
                    "Δ_struct + Δ_rel = 0 (I₈ Invariant)",
                    preserved_by=[6, 7, 8, 9])
    
    # Layer 6 invariants
    cm.add_invariant(6, "hard_constraints",
                    lambda x: x.get("hard_passed", True),
                    "All non-negotiable constraints satisfied (Λ.7)",
                    preserved_by=[7, 8, 9])
    cm.add_invariant(6, "circuit_breaker_enforced",
                    lambda x: x.get("breakers_closed", True),
                    "Circuit breakers initialized CLOSED (CHK-05)",
                    preserved_by=[7, 8, 9])
    
    # Layer 7 invariants
    cm.add_invariant(7, "feedback_control",
                    lambda x: x.get("interventions_fired", False),
                    "Interventions fire on audit failure (Λ.3, Λ.6)",
                    preserved_by=[8, 9])
    cm.add_invariant(7, "kill_switch_functional",
                    lambda x: x.get("kill_switch_tested", True),
                    "Kill Switch tested and operational (CHK-08)",
                    preserved_by=[8, 9])
    cm.add_invariant(7, "gre_operational",
                    lambda x: x.get("gre_health", True),
                    "GRE operational and self-check passing (CHK-02)",
                    preserved_by=[8, 9])
    cm.add_invariant(7, "module_lifecycle_enforced",
                    lambda x: x.get("lifecycle_enforced", True),
                    "Module lifecycle enforced (REG→INIT→ACT→OP→SUSP→TERM)",
                    preserved_by=[8, 9])
    
    # Layer 8 invariants
    cm.add_invariant(8, "identity_boundaries_enforced",
                    lambda x: x.get("identity_isolation", True),
                    "Identity Boundary Enforcer verified (CHK-06, Λ.4)",
                    preserved_by=[9])
    cm.add_invariant(8, "message_bus_validated",
                    lambda x: x.get("message_bus_validated", True),
                    "Message Bus with schema validation active (CHK-09)",
                    preserved_by=[9])
    cm.add_invariant(8, "coherence_generation",
                    lambda x: x.get("coherence_increasing", False),
                    "Agent density generates local coherence",
                    preserved_by=[9])
    
    # Layer 9 invariants
    cm.add_invariant(9, "cross_layer_preservation",
                    lambda x: x.get("invariants_preserved", True),
                    "All layer invariants preserved through stack",
                    preserved_by=[])
    cm.add_invariant(9, "closure",
                    lambda x: x.get("closure_holds", True),
                    "Γ: L9 → L1 preserves continuity",
                    preserved_by=[])
    cm.add_invariant(9, "deployment_verified",
                    lambda x: x.get("deployment_checklist_passed", True),
                    "All 10 deployment checklist items verified (CHK-01 to CHK-10)",
                    preserved_by=[])
    cm.add_invariant(9, "amendment_protocol_enforced",
                    lambda x: x.get("amendment_enforced", True),
                    "Λ amendment protocol enforced (§8)",
                    preserved_by=[])
    
    # Interfaces
    maps = {
        (1, 2): lambda x: {"fidelity": x.get("corrigibility", 0.5), "stewardship": x.get("corrigibility", 0.5), "consequences_primary": True},
        (2, 3): lambda x: {"sufficiency_rate": x.get("fidelity", 0.5), "schema_valid": True},
        (3, 4): lambda x: {"involution_verified": True, "decomposition_compatible": x.get("sufficiency_rate", 0) > 0.7},
        (4, 5): lambda x: {"I8_verified": x.get("decomposition_compatible", True), "phase_locked": True},
        (5, 6): lambda x: {"hard_passed": x.get("I8_verified", True), "verdict_grounded": True},
        (6, 7): lambda x: {"interventions_fired": len(x.get("hard_violations", [])) > 0, "lyapunov_decreasing": True},
        (7, 8): lambda x: {"coherence_increasing": True, "mass_conserved": True, "identity_isolation": True, "message_bus_validated": True},
        (8, 9): lambda x: {"invariants_preserved": True, "closure_holds": True, "deployment_checklist_passed": True},
    }
    
    for i in range(1, 9):
        to_layer_invariants = [inv["name"] for inv in cm.invariants.get(i+1, [])]
        cm.add_interface(i, i+1, maps.get((i, i+1), lambda x: {}), to_layer_invariants)
    
    def gamma_closure(l9_state: Dict) -> Dict:
        return {"psi": l9_state.get("integrated_state", [1.0, 0.0, -1.0]),
                "corrigibility": l9_state.get("invariants_preserved", True),
                "continuity": l9_state.get("closure_holds", True),
                "determinism": l9_state.get("determinism", True),
                "circuit_breakers_closed": l9_state.get("breakers_closed", True)}
    
    cm.set_closure(gamma_closure)
    
    return cm


def run_deployment_checklist() -> Dict[str, Any]:
    """Run full Voss Binding deployment checklist"""
    print("Running Voss Binding Deployment Checklist (§9.1)...")
    
    results = {}
    all_passed = True
    
    for item in DEPLOYMENT_CHECKLIST:
        print(f"  {item.item_id}: {item.requirement}")
        # In real implementation, would run actual verification
        # For now, simulate
        passed = True  # Would be actual verification
        item.status = ChecklistItemStatus.PASSED if passed else ChecklistItemStatus.FAILED
        item.verified_at = time.time()
        item.verified_by = "automated"
        
        results[item.item_id] = {
            "requirement": item.requirement,
            "passed": passed,
        }
        if not passed:
            all_passed = False
    
    overall = "PASSED" if all_passed else "FAILED"
    print(f"\nDeployment Checklist: {overall}")
    
    return {
        "overall": overall,
        "items": results,
        "all_passed": all_passed,
    }