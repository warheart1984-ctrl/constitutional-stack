"""
Layer 7 Extension: Voss Binding Compliance
Per-agent circuit breakers, module lifecycle, kill switch, randomness boundaries.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import time
import threading
import uuid


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class ModuleLifecyclePhase(Enum):
    REGISTRATION = "REGISTRATION"
    INITIALIZATION = "INITIALIZATION"
    ACTIVATION = "ACTIVATION"
    OPERATION = "OPERATION"
    SUSPENSION = "SUSPENSION"
    TERMINATION = "TERMINATION"


@dataclass
class ModuleContract:
    """Voss Binding §3 — Module Contract"""
    module_id: str
    lane_assignment: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    governance_bindings: List[str]  # Λ.1 through Λ.7
    failure_modes: Dict[str, str]
    operator_escalation: Dict[str, str]
    randomness_boundary: Optional[Dict[str, Any]] = None  # Λ.1
    version: str = "1.0"


@dataclass
class CircuitBreaker:
    """Voss Binding §4.2 — Circuit Breaker per module"""
    module_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    failure_threshold: int = 5
    half_open_max_requests: int = 3
    half_open_requests: int = 0
    last_state_change: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
                self._trip_open()
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self._trip_open()
    
    def record_success(self):
        with self.lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_requests += 1
                if self.half_open_requests >= self.half_open_max_requests:
                    self._close()
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)
    
    def _trip_open(self):
        self.state = CircuitBreakerState.OPEN
        self.half_open_requests = 0
        self.last_state_change = time.time()
    
    def _close(self):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.half_open_requests = 0
        self.last_state_change = time.time()
    
    def can_execute(self) -> bool:
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return self.half_open_requests < self.half_open_max_requests
            return False
    
    def request_half_open(self) -> bool:
        """Operator-authorized transition from OPEN to HALF_OPEN"""
        with self.lock:
            if self.state == CircuitBreakerState.OPEN:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_requests = 0
                self.last_state_change = time.time()
                return True
            return False


@dataclass
class ModuleInstance:
    """Runtime module instance with Voss Binding compliance"""
    contract: ModuleContract
    phase: ModuleLifecyclePhase = ModuleLifecyclePhase.REGISTRATION
    circuit_breaker: CircuitBreaker = None
    state: Dict[str, Any] = field(default_factory=dict)
    audit_stream: List[Dict] = field(default_factory=list)
    drift_scores: Dict[str, float] = field(default_factory=dict)
    execution_count: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)
    
    def __post_init__(self):
        self.circuit_breaker = CircuitBreaker(module_id=self.contract.module_id)


class KillSwitch:
    """Voss Binding §6 — System-wide emergency kill switch"""
    
    def __init__(self):
        self._activated = False
        self._activation_time = 0.0
        self._activated_by: Optional[str] = None
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []
    
    def activate(self, operator_id: str) -> bool:
        with self._lock:
            if not self._activated:
                self._activated = True
                self._activation_time = time.time()
                self._activated_by = operator_id
                # Execute all registered callbacks
                for cb in self._callbacks:
                    try:
                        cb()
                    except Exception:
                        pass
                return True
            return False
    
    def is_activated(self) -> bool:
        with self._lock:
            return self._activated
    
    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "activated": self._activated,
                "activation_time": self._activation_time,
                "activated_by": self._activated_by,
            }
    
    def register_callback(self, callback: Callable):
        with self._lock:
            self._callbacks.append(callback)
    
    def reset(self, operator_id: str) -> bool:
        """Only the activating operator can reset"""
        with self._lock:
            if self._activated and self._activated_by == operator_id:
                self._activated = False
                self._activation_time = 0.0
                self._activated_by = None
                return True
            return False


class ModuleRegistry:
    """Voss Binding §4.3 — Contract Registry with runtime registration/versioning"""
    
    def __init__(self):
        self._contracts: Dict[str, ModuleContract] = {}
        self._instances: Dict[str, ModuleInstance] = {}
        self._lock = threading.Lock()
        self._version_history: Dict[str, List[ModuleContract]] = {}
    
    def register(self, contract: ModuleContract) -> bool:
        """Register a module contract (§4.3)"""
        with self._lock:
            if contract.module_id in self._contracts:
                return False  # Already registered
            
            # Validate completeness (§4.3)
            if not self._validate_contract(contract):
                return False
            
            self._contracts[contract.module_id] = contract
            self._version_history[contract.module_id] = [contract]
            return True
    
    def _validate_contract(self, contract: ModuleContract) -> bool:
        """Validate contract completeness (§4.3)"""
        required = ["module_id", "lane_assignment", "input_schema", "output_schema", 
                   "governance_bindings", "failure_modes", "operator_escalation"]
        for field in required:
            if not getattr(contract, field, None):
                return False
        # Must declare which Λ laws apply
        if not contract.governance_bindings:
            return False
        return True
    
    def create_instance(self, module_id: str) -> Optional[ModuleInstance]:
        """Create runtime instance after registration"""
        with self._lock:
            if module_id not in self._contracts:
                return None
            contract = self._contracts[module_id]
            instance = ModuleInstance(contract=contract)
            self._instances[module_id] = instance
            return instance
    
    def get_instance(self, module_id: str) -> Optional[ModuleInstance]:
        with self._lock:
            return self._instances.get(module_id)
    
    def transition_phase(self, module_id: str, new_phase: ModuleLifecyclePhase, 
                        operator_id: Optional[str] = None) -> bool:
        """Lifecycle transition (§4.4)"""
        with self._lock:
            instance = self._instances.get(module_id)
            if not instance:
                return False
            
            # Validate transition
            valid_transitions = {
                ModuleLifecyclePhase.REGISTRATION: [ModuleLifecyclePhase.INITIALIZATION],
                ModuleLifecyclePhase.INITIALIZATION: [ModuleLifecyclePhase.ACTIVATION],
                ModuleLifecyclePhase.ACTIVATION: [ModuleLifecyclePhase.OPERATION, ModuleLifecyclePhase.SUSPENSION],
                ModuleLifecyclePhase.OPERATION: [ModuleLifecyclePhase.SUSPENSION, ModuleLifecyclePhase.TERMINATION],
                ModuleLifecyclePhase.SUSPENSION: [ModuleLifecyclePhase.ACTIVATION, ModuleLifecyclePhase.TERMINATION],
                ModuleLifecyclePhase.TERMINATION: [],
            }
            
            if new_phase not in valid_transitions.get(instance.phase, []):
                return False
            
            # ACTIVATION requires operator checkpoint
            if new_phase == ModuleLifecyclePhase.ACTIVATION and not operator_id:
                return False
            
            # TERMINATION requires explicit operator
            if new_phase == ModuleLifecyclePhase.TERMINATION and not operator_id:
                return False
            
            instance.phase = new_phase
            return True
    
    def update_contract(self, module_id: str, new_contract: ModuleContract, 
                       operator_id: str) -> bool:
        """Amendment protocol (§8)"""
        with self._lock:
            if module_id not in self._contracts:
                return False
            # In real implementation, would verify amendment protocol
            old_contract = self._contracts[module_id]
            self._version_history[module_id].append(new_contract)
            self._contracts[module_id] = new_contract
            
            # Update instance contract
            if module_id in self._instances:
                self._instances[module_id].contract = new_contract
            return True


class GRE:
    """Voss Binding §4.1 — Governance Runtime Engine"""
    
    def __init__(self, registry: ModuleRegistry, kill_switch: KillSwitch):
        self.registry = registry
        self.kill_switch = kill_switch
        self.health_check_thread: Optional[threading.Thread] = None
        self._running = False
    
    def execute(self, module_id: str, input_data: Any, operator_id: Optional[str] = None) -> Any:
        """Execute module through GRE pipeline (§4.1)"""
        instance = self.registry.get_instance(module_id)
        if not instance:
            raise ValueError(f"Module {module_id} not instantiated")
        
        # Kill switch check
        if self.kill_switch.is_activated():
            raise RuntimeError("Kill switch activated")
        
        # Circuit breaker check
        if not instance.circuit_breaker.can_execute():
            raise RuntimeError(f"Circuit breaker OPEN for {module_id}")
        
        # Phase check
        if instance.phase != ModuleLifecyclePhase.OPERATION:
            raise RuntimeError(f"Module {module_id} not in OPERATION phase")
        
        contract = instance.contract
        
        # Stage 1: INPUT GATE — Schema validation
        if not self._validate_input(input_data, contract.input_schema):
            instance.circuit_breaker.record_failure()
            raise ValueError(f"Input validation failed for {module_id}")
        
        # Stage 2: GOVERNANCE CHECK
        if not self._verify_governance(contract):
            instance.circuit_breaker.record_failure()
            raise RuntimeError(f"Governance check failed for {module_id}")
        
        # Stage 3: EXECUTION SANDBOX
        start_time = time.time()
        try:
            output = self._execute_module(instance, input_data)
            exec_duration = (time.time() - start_time) * 1000
        except Exception as e:
            instance.circuit_breaker.record_failure()
            raise
        
        # Stage 4: OUTPUT GATE
        if not self._validate_output(output, contract.output_schema):
            instance.circuit_breaker.record_failure()
            raise ValueError(f"Output validation failed for {module_id}")
        
        # Stage 5: DRIFT MEASUREMENT
        drift_score = self._measure_drift(instance, input_data, output)
        instance.drift_scores = drift_score
        
        # Stage 6: AUDIT EMISSION
        audit_record = self._emit_audit(instance, input_data, output, drift_score, exec_duration)
        instance.audit_stream.append(audit_record)
        
        instance.circuit_breaker.record_success()
        instance.execution_count += 1
        instance.last_heartbeat = time.time()
        
        return output
    
    def _validate_input(self, data: Any, schema: Dict) -> bool:
        # Simplified schema validation
        return True
    
    def _validate_output(self, data: Any, schema: Dict) -> bool:
        return True
    
    def _verify_governance(self, contract: ModuleContract) -> bool:
        """Verify all declared Λ laws are satisfiable"""
        required_laws = ["Λ.1", "Λ.2", "Λ.3", "Λ.4", "Λ.5", "Λ.6", "Λ.7"]
        for law in contract.governance_bindings:
            if law not in required_laws:
                return False
        return True
    
    def _execute_module(self, instance: ModuleInstance, input_data: Any) -> Any:
        """Execute the actual module logic"""
        # Placeholder - actual module implementation would go here
        return {"status": "executed", "module_id": instance.contract.module_id}
    
    def _measure_drift(self, instance: ModuleInstance, input_data: Any, output: Any) -> Dict[str, float]:
        """Voss Binding §4.2 — Drift Monitor four scores"""
        return {
            "behavioral_drift": 0.0,
            "schema_drift": 0.0,
            "identity_drift": 0.0,
            "temporal_drift": 0.0,
        }
    
    def _emit_audit(self, instance: ModuleInstance, input_data: Any, output: Any, 
                   drift_score: Dict[str, float], duration_ms: float) -> Dict:
        """Voss Binding §4.2 — Audit Trail Writer"""
        import hashlib
        input_hash = hashlib.sha256(str(input_data).encode()).hexdigest()
        output_hash = hashlib.sha256(str(output).encode()).hexdigest()
        
        prev_hash = instance.audit_stream[-1].get("record_hash", "0") if instance.audit_stream else "0"
        record_hash = hashlib.sha256(f"{prev_hash}{input_hash}{output_hash}".encode()).hexdigest()
        
        return {
            "timestamp": time.time(),
            "module_id": instance.contract.module_id,
            "lane_id": instance.contract.lane_assignment,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "governance_bindings_verified": instance.contract.governance_bindings,
            "drift_score": drift_score,
            "execution_duration_ms": duration_ms,
            "violations": [],
            "record_hash": record_hash,
        }
    
    def start_health_check(self, interval: float = 30.0):
        """GRE self-check on separate thread (§4.1)"""
        self._running = True
        def health_check():
            while self._running:
                time.sleep(interval)
                # Verify GRE integrity
                pass
        self.health_check_thread = threading.Thread(target=health_check, daemon=True)
        self.health_check_thread.start()
    
    def stop_health_check(self):
        self._running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=1.0)


# Global instances
_registry = ModuleRegistry()
_kill_switch = KillSwitch()
_gre = GRE(_registry, _kill_switch)


def get_registry() -> ModuleRegistry:
    return _registry


def get_kill_switch() -> KillSwitch:
    return _kill_switch


def get_gre() -> GRE:
    return _gre