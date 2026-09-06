"""
Layer 8 Extension: Voss Binding Message Bus
Schema-validated inter-agent communication (§4.2 Identity Boundary Enforcer)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import threading
import time
import uuid
import hashlib
from collections import defaultdict


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class MessageSchema:
    """Schema for message validation"""
    message_type: str
    required_fields: List[str]
    field_types: Dict[str, type]
    field_constraints: Dict[str, Callable] = field(default_factory=dict)


@dataclass
class Message:
    """Schema-validated message for inter-agent communication"""
    message_id: str
    message_type: str
    sender_id: str
    receiver_id: str
    timestamp: float
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    schema_hash: str = ""
    signature: str = ""
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


class IdentityToken:
    """Cryptographic identity token for agent verification"""
    
    def __init__(self, agent_id: str, public_key: str = ""):
        self.agent_id = agent_id
        self.public_key = public_key or hashlib.sha256(agent_id.encode()).hexdigest()[:32]
        self.created_at = time.time()
        self.revoked = False
    
    def verify(self, message: Message) -> bool:
        """Verify message came from this identity"""
        return message.sender_id == self.agent_id and not self.revoked


class IdentityLeakDetector:
    """Voss Binding §4.2 — Continuous identity boundary monitoring"""
    
    def __init__(self):
        self.agent_spaces: Dict[str, Dict[str, Any]] = {}
        self.config_namespaces: Dict[str, Set[str]] = defaultdict(set)
        self.memory_refs: Dict[str, Set[int]] = defaultdict(set)  # id(obj) -> agents
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str, config: Dict[str, Any]):
        with self.lock:
            self.agent_spaces[agent_id] = {"config": config, "state_refs": set()}
            for k in config.keys():
                self.config_namespaces[agent_id].add(k)
    
    def track_state_reference(self, agent_id: str, state_obj: Any):
        with self.lock:
            self.agent_spaces[agent_id]["state_refs"].add(id(state_obj))
            self.memory_refs[id(state_obj)].add(agent_id)
    
    def check_leaks(self) -> List[Dict[str, Any]]:
        """Detect identity boundary violations"""
        leaks = []
        with self.lock:
            # Check shared memory references
            for obj_id, agents in self.memory_refs.items():
                if len(agents) > 1:
                    leaks.append({
                        "type": "shared_memory",
                        "object_id": obj_id,
                        "agents": list(agents),
                        "severity": "critical",
                    })
            
            # Check config namespace collisions
            all_keys = {}
            for agent_id, keys in self.config_namespaces.items():
                for key in keys:
                    if key in all_keys:
                        leaks.append({
                            "type": "config_collision",
                            "key": key,
                            "agents": [all_keys[key], agent_id],
                            "severity": "high",
                        })
                    else:
                        all_keys[key] = agent_id
        return leaks


@dataclass
class MessageRoute:
    """Routing information for message delivery"""
    sender_id: str
    receiver_id: str
    message_type: str
    delivered: bool = False
    delivery_time: float = 0.0
    attempts: int = 0


class MessageBus:
    """Voss Binding §4.2 — Governed Message Bus with schema validation"""
    
    def __init__(self):
        self.schemas: Dict[str, MessageSchema] = {}
        self.queues: Dict[str, List[Message]] = defaultdict(list)
        self.routes: List[MessageRoute] = []
        self.identity_tokens: Dict[str, IdentityToken] = {}
        self.leak_detector = IdentityLeakDetector()
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.Lock()
        self.metrics = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "schema_violations": 0,
            "identity_violations": 0,
        }
    
    def register_schema(self, schema: MessageSchema):
        """Register a message schema for validation"""
        with self.lock:
            self.schemas[schema.message_type] = schema
    
    def register_agent(self, agent_id: str, config: Dict[str, Any]):
        """Register agent with identity token and config"""
        with self.lock:
            self.identity_tokens[agent_id] = IdentityToken(agent_id)
            self.leak_detector.register_agent(agent_id, config)
    
    def send(self, message: Message) -> bool:
        """Send message with full validation (§4.2)"""
        with self.lock:
            self.metrics["messages_sent"] += 1
            
            # Validate sender identity
            if message.sender_id not in self.identity_tokens:
                self.metrics["messages_failed"] += 1
                return False
            
            token = self.identity_tokens[message.sender_id]
            if not token.verify(message):
                self.metrics["identity_violations"] += 1
                return False
            
            # Validate schema
            schema = self.schemas.get(message.message_type)
            if schema and not self._validate_message(message, schema):
                self.metrics["schema_violations"] += 1
                return False
            
            # Generate schema hash for audit
            message.schema_hash = self._compute_schema_hash(message)
            
            # Route to receiver queue
            self.queues[message.receiver_id].append(message)
            
            # Track route
            route = MessageRoute(
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                message_type=message.message_type,
            )
            self.routes.append(route)
            
            # Notify subscribers
            for callback in self.subscribers.get(message.message_type, []):
                try:
                    callback(message)
                except Exception:
                    pass
            
            return True
    
    def _validate_message(self, message: Message, schema: MessageSchema) -> bool:
        """Validate message against schema"""
        # Check required fields
        for field in schema.required_fields:
            if field not in message.payload:
                return False
        
        # Check field types
        for field, expected_type in schema.field_types.items():
            if field in message.payload and not isinstance(message.payload[field], expected_type):
                return False
        
        # Check constraints
        for field, constraint in schema.field_constraints.items():
            if field in message.payload and not constraint(message.payload[field]):
                return False
        
        return True
    
    def _compute_schema_hash(self, message: Message) -> str:
        content = f"{message.message_type}{message.sender_id}{message.receiver_id}{message.payload}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def receive(self, agent_id: str, max_messages: int = 10) -> List[Message]:
        """Receive messages for agent"""
        with self.lock:
            queue = self.queues.get(agent_id, [])
            messages = queue[:max_messages]
            self.queues[agent_id] = queue[max_messages:]
            
            # Update route tracking
            for msg in messages:
                for route in self.routes:
                    if (route.sender_id == msg.sender_id and 
                        route.receiver_id == msg.receiver_id and
                        route.message_type == msg.message_type and
                        not route.delivered):
                        route.delivered = True
                        route.delivery_time = time.time()
                        break
            
            self.metrics["messages_delivered"] += len(messages)
            return messages
    
    def subscribe(self, message_type: str, callback: Callable[[Message], None]):
        """Subscribe to message type"""
        with self.lock:
            self.subscribers[message_type].append(callback)
    
    def check_identity_leaks(self) -> List[Dict[str, Any]]:
        """Run identity leak detection"""
        return self.leak_detector.check_leaks()
    
    def get_metrics(self) -> Dict[str, Any]:
        with self.lock:
            return self.metrics.copy()
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        with self.lock:
            return {
                "queue_depth": len(self.queues.get(agent_id, [])),
                "registered": agent_id in self.identity_tokens,
                "token_revoked": self.identity_tokens.get(agent_id, IdentityToken("")).revoked,
            }


# Standard message schemas for AAIS
STANDARD_SCHEMAS = {
    "agent_state": MessageSchema(
        message_type="agent_state",
        required_fields=["agent_id", "state_vector", "drift_scores"],
        field_types={
            "agent_id": str,
            "state_vector": list,
            "drift_scores": dict,
        },
        field_constraints={
            "state_vector": lambda v: len(v) > 0,
            "drift_scores": lambda v: all(0 <= x <= 1 for x in v.values()),
        }
    ),
    "drift_alert": MessageSchema(
        message_type="drift_alert",
        required_fields=["agent_id", "drift_type", "score", "threshold"],
        field_types={
            "agent_id": str,
            "drift_type": str,
            "score": float,
            "threshold": float,
        },
        field_constraints={
            "score": lambda v: 0 <= v <= 1,
        }
    ),
    "operator_command": MessageSchema(
        message_type="operator_command",
        required_fields=["command", "target_agent", "parameters"],
        field_types={
            "command": str,
            "target_agent": str,
            "parameters": dict,
        },
        field_constraints={
            "command": lambda v: v in ["interrupt", "correct", "terminate", "suspend", "resume"],
        }
    ),
    "audit_record": MessageSchema(
        message_type="audit_record",
        required_fields=["module_id", "input_hash", "output_hash", "drift_score"],
        field_types={
            "module_id": str,
            "input_hash": str,
            "output_hash": str,
            "drift_score": dict,
        },
    ),
    "circuit_breaker_event": MessageSchema(
        message_type="circuit_breaker_event",
        required_fields=["module_id", "old_state", "new_state", "trigger"],
        field_types={
            "module_id": str,
            "old_state": str,
            "new_state": str,
            "trigger": str,
        },
    ),
    "governance_surface_update": MessageSchema(
        message_type="governance_surface_update",
        required_fields=["agent_id", "state", "drift_scores", "circuit_breaker_state"],
        field_types={
            "agent_id": str,
            "state": dict,
            "drift_scores": dict,
            "circuit_breaker_state": str,
        },
    ),
}


def create_standard_message_bus() -> MessageBus:
    """Create message bus with standard AAIS schemas"""
    bus = MessageBus()
    for schema in STANDARD_SCHEMAS.values():
        bus.register_schema(schema)
    return bus