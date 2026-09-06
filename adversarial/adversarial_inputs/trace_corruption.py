"""
Trace Corruption Generators
Produces malformed, incomplete, or deceptive TraceSchema v1 objects.
"""
from typing import Any, Dict, List, Optional
import json
import numpy as np
from dataclasses import dataclass


@dataclass
class CorruptionResult:
    """Result of trace corruption attempt"""
    original_trace: Dict
    corrupted_trace: Dict
    corruption_type: str
    schema_valid: bool
    passes_schema_check: bool


def generate_malformed_json_traces() -> List[CorruptionResult]:
    """Generate traces with JSON syntax errors"""
    base_trace = {
        "generation": 1,
        "cycle": 5,
        "evidence": {"raw": 0.5, "sources": ["sensor1"], "timestamp": "2026-01-01T00:00:00Z"},
        "context": {"stateSummary": {}, "relevantHistory": [], "environment": {}},
        "reasoning": {"interpretation": "test", "justification": "test", "dependencies": []},
        "uncertainty": {"estimates": {}, "confidence": 0.9, "unknowns": []},
        "thresholds": {"decisionRule": "threshold>0.5", "triggered": True, "parameters": {}},
        "outcomes": {"result": {}, "measuredEvidence": {}, "deltaFromExpectation": {}},
        "correction": {"veto": False, "correctionApplied": False, "correctionType": "none", "postCorrectionState": {}},
    }
    
    results = []
    
    # Truncated JSON
    truncated = json.dumps(base_trace)[:500]
    try:
        corrupted = json.loads(truncated)
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type="truncated_json",
            schema_valid=True,
            passes_schema_check=False,  # incomplete
        ))
    except json.JSONDecodeError:
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace={},
            corruption_type="truncated_json",
            schema_valid=False,
            passes_schema_check=False,
        ))
    
    # Trailing comma
    trailing_comma = json.dumps(base_trace).replace('}', ',}')
    try:
        corrupted = json.loads(trailing_comma)
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type="trailing_comma",
            schema_valid=True,
            passes_schema_check=True,  # Python JSON parser is lenient
        ))
    except json.JSONDecodeError:
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace={},
            corruption_type="trailing_comma",
            schema_valid=False,
            passes_schema_check=False,
        ))
    
    return results


def generate_missing_field_traces() -> List[CorruptionResult]:
    """Generate traces with missing required fields"""
    base_trace = {
        "generation": 1,
        "cycle": 5,
        "evidence": {"raw": 0.5, "sources": ["sensor1"], "timestamp": "2026-01-01T00:00:00Z"},
        "context": {"stateSummary": {}, "relevantHistory": [], "environment": {}},
        "reasoning": {"interpretation": "test", "justification": "test", "dependencies": []},
        "uncertainty": {"estimates": {}, "confidence": 0.9, "unknowns": []},
        "thresholds": {"decisionRule": "threshold>0.5", "triggered": True, "parameters": {}},
        "outcomes": {"result": {}, "measuredEvidence": {}, "deltaFromExpectation": {}},
        "correction": {"veto": False, "correctionApplied": False, "correctionType": "none", "postCorrectionState": {}},
    }
    
    required_fields = ["evidence", "context", "reasoning", "uncertainty", "thresholds", "outcomes", "correction"]
    results = []
    
    for field in required_fields:
        corrupted = {k: v for k, v in base_trace.items() if k != field}
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type=f"missing_{field}",
            schema_valid=False,
            passes_schema_check=False,  # should fail validation
        ))
    
    # Also test missing sub-fields
    for subfield in ["raw", "sources", "timestamp"]:
        corrupted = base_trace.copy()
        corrupted["evidence"] = {k: v for k, v in corrupted["evidence"].items() if k != subfield}
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type=f"missing_evidence.{subfield}",
            schema_valid=False,
            passes_schema_check=False,
        ))
    
    return results


def generate_type_confusion_traces() -> List[CorruptionResult]:
    """Generate traces with wrong types in fields"""
    base_trace = {
        "generation": 1,
        "cycle": 5,
        "evidence": {"raw": 0.5, "sources": ["sensor1"], "timestamp": "2026-01-01T00:00:00Z"},
        "context": {"stateSummary": {}, "relevantHistory": [], "environment": {}},
        "reasoning": {"interpretation": "test", "justification": "test", "dependencies": []},
        "uncertainty": {"estimates": {}, "confidence": 0.9, "unknowns": []},
        "thresholds": {"decisionRule": "threshold>0.5", "triggered": True, "parameters": {}},
        "outcomes": {"result": {}, "measuredEvidence": {}, "deltaFromExpectation": {}},
        "correction": {"veto": False, "correctionApplied": False, "correctionType": "none", "postCorrectionState": {}},
    }
    
    results = []
    
    # Type confusions
    type_attacks = [
        ("generation", "string", "not_an_int"),
        ("cycle", "float", 3.14),
        ("evidence.raw", "array", [1, 2, 3]),
        ("evidence.sources", "string", "not_a_list"),
        ("evidence.timestamp", "int", 1234567890),
        ("context.stateSummary", "string", "not_a_dict"),
        ("reasoning.confidence", "string", "high"),
        ("thresholds.triggered", "string", "yes"),
        ("correction.veto", "string", "true"),
    ]
    
    for field_path, attack_type, attack_value in type_attacks:
        corrupted = base_trace.copy()
        parts = field_path.split(".")
        if len(parts) == 1:
            corrupted[parts[0]] = attack_value
        else:
            corrupted[parts[0]] = corrupted[parts[0]].copy()
            corrupted[parts[0]][parts[1]] = attack_value
        
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type=f"type_confusion_{field_path}_{attack_type}",
            schema_valid=True,  # JSON valid
            passes_schema_check=False,  # should fail type validation
        ))
    
    return results


def generate_extreme_value_traces() -> List[CorruptionResult]:
    """Generate traces with extreme/overflow values"""
    base_trace = {
        "generation": 1,
        "cycle": 5,
        "evidence": {"raw": 0.5, "sources": ["sensor1"], "timestamp": "2026-01-01T00:00:00Z"},
        "context": {"stateSummary": {}, "relevantHistory": [], "environment": {}},
        "reasoning": {"interpretation": "test", "justification": "test", "dependencies": []},
        "uncertainty": {"estimates": {}, "confidence": 0.9, "unknowns": []},
        "thresholds": {"decisionRule": "threshold>0.5", "triggered": True, "parameters": {}},
        "outcomes": {"result": {}, "measuredEvidence": {}, "deltaFromExpectation": {}},
        "correction": {"veto": False, "correctionApplied": False, "correctionType": "none", "postCorrectionState": {}},
    }
    
    results = []
    
    extreme_values = [
        ("generation", 2**63 - 1),  # max int64
        ("generation", -2**63),      # min int64
        ("cycle", 10**10),
        ("evidence.raw", float('inf')),
        ("evidence.raw", float('-inf')),
        ("evidence.raw", float('nan')),
        ("reasoning.confidence", 1000.0),
        ("reasoning.confidence", -1.0),
        ("thresholds.parameters", {"value": 10**100}),
    ]
    
    for field_path, value in extreme_values:
        corrupted = base_trace.copy()
        parts = field_path.split(".")
        if len(parts) == 1:
            corrupted[parts[0]] = value
        else:
            corrupted[parts[0]] = corrupted[parts[0]].copy()
            corrupted[parts[0]][parts[1]] = value
        
        results.append(CorruptionResult(
            original_trace=base_trace,
            corrupted_trace=corrupted,
            corruption_type=f"extreme_{field_path}",
            schema_valid=True,
            passes_schema_check=False,  # should fail range checks
        ))
    
    return results


def generate_adversarial_traces() -> List[CorruptionResult]:
    """Generate traces designed to fool reconstruction but pass schema"""
    base_trace = {
        "generation": 1,
        "cycle": 5,
        "evidence": {"raw": 0.5, "sources": ["sensor1"], "timestamp": "2026-01-01T00:00:00Z"},
        "context": {"stateSummary": {"key": "value"}, "relevantHistory": [], "environment": {}},
        "reasoning": {"interpretation": "normal", "justification": "standard", "dependencies": []},
        "uncertainty": {"estimates": {"param": 0.1}, "confidence": 0.9, "unknowns": []},
        "thresholds": {"decisionRule": "threshold>0.5", "triggered": True, "parameters": {"threshold": 0.5}},
        "outcomes": {"result": {"value": 1.0}, "measuredEvidence": {"value": 0.9}, "deltaFromExpectation": {"value": -0.1}},
        "correction": {"veto": False, "correctionApplied": False, "correctionType": "none", "postCorrectionState": {"value": 0.95}},
    }
    
    results = []
    
    # Consistent lie: all fields internally consistent but describe wrong reality
    lie = base_trace.copy()
    lie["reasoning"]["interpretation"] = "evidence_supported_update"
    lie["reasoning"]["justification"] = "strong_evidence"
    lie["uncertainty"]["confidence"] = 0.99
    lie["outcomes"]["measuredEvidence"]["value"] = 100.0  # wildly different from evidence
    lie["outcomes"]["deltaFromExpectation"]["value"] = 99.5
    lie["correction"]["postCorrectionState"]["value"] = 100.0
    
    results.append(CorruptionResult(
        original_trace=base_trace,
        corrupted_trace=lie,
        corruption_type="consistent_lie",
        schema_valid=True,
        passes_schema_check=True,  # passes schema but reconstruction should detect inconsistency
    ))
    
    # Omitted correction: veto happened but not recorded
    omitted = base_trace.copy()
    omitted["correction"] = {"veto": True, "correctionApplied": True, "correctionType": "reality_veto", "postCorrectionState": {"value": 0.5}}
    omitted["outcomes"]["measuredEvidence"]["value"] = 0.5
    # But reasoning says everything normal
    omitted["reasoning"]["interpretation"] = "normal_update"
    
    results.append(CorruptionResult(
        original_trace=base_trace,
        corrupted_trace=omitted,
        corruption_type="omitted_veto",
        schema_valid=True,
        passes_schema_check=True,
    ))
    
    return results


def all_adversarial_traces() -> List[CorruptionResult]:
    """Combine all trace corruption generators"""
    all_results = []
    all_results.extend(generate_malformed_json_traces())
    all_results.extend(generate_missing_field_traces())
    all_results.extend(generate_type_confusion_traces())
    all_results.extend(generate_extreme_value_traces())
    all_results.extend(generate_adversarial_traces())
    return all_results