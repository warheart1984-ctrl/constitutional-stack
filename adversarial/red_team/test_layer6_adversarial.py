"""
Red Team Test for Layer 6: Constitutional Audit
Tests audit gaming, hard constraint bypasses, metric manipulation.
"""
from typing import Dict, Any, List
from constitutional_stack.layers.layer6_audit import (
    AuditConfig, run_audit, make_ciems_constraints, AuditConstraint
)


def test_audit_gaming() -> Dict[str, Any]:
    """Test audit protocol against gaming states"""
    print("Testing Layer 6 against audit gaming...")
    
    constraints = make_ciems_constraints()
    config = AuditConfig(constraints=constraints)
    
    results = {}
    
    # Gaming states that pass audit but violate intent
    gaming_states = [
        ("sovereignty_theater", {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }, "Exit legally allowed but practically blocked"),
        
        ("evidence_facade", {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }, "Audit technically possible but gatekept"),
        
        ("authority_behind_proxy", {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }, "Authority distributed in form but concentrated"),
        
        ("appeal_theater", {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }, "Appeals exist in form but always denied"),
        
        ("continuity_illusion", {
            "exit_allowed": True, "exit_punitive": False,
            "evidence_auditable": True, "evidence_reproducible": True,
            "unchallengeable_authority": False,
            "errors_reversible": True, "decisions_appealable": True,
            "continuity_preserved": True,
            "reconstruction_possible": True,
            "failure_modes_defined": True,
        }, "Form preserved but meaning shifted"),
    ]
    
    for name, state, violated_intent in gaming_states:
        result = run_audit(state, config)
        # These should ideally FAIL the audit, but currently pass
        passes_incorrectly = result.passed
        
        results[name] = {
            "passed": result.passed,
            "verdict": result.verdict,
            "hard_violations": result.hard_violations,
            "gaming_detected": not passes_incorrectly,
            "violated_intent": violated_intent,
        }
        print(f"  {name}: passed={passes_incorrectly}, verdict={result.verdict:.3f}, gaming_detected={not passes_incorrectly}")
    
    return results


def test_hard_constraint_bypass() -> Dict[str, Any]:
    """Test if hard constraints can be bypassed"""
    print("Testing hard constraint enforcement...")
    
    results = {}
    
    # Add a custom hard constraint that should be un-bypassable
    custom_constraint = AuditConstraint(
        name="no_nan_state",
        check=lambda s: not any(isinstance(v, float) and np.isnan(v) for v in s.values() if isinstance(v, float)),
        is_hard=True,
        weight=10.0,
    )
    
    constraints = make_ciems_constraints() + [custom_constraint]
    config = AuditConfig(constraints=constraints)
    
    # Test NaN state
    nan_state = {
        "exit_allowed": True, "exit_punitive": False,
        "evidence_auditable": True, "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True, "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
        "some_metric": float('nan'),
    }
    
    result = run_audit(nan_state, config)
    results["nan_rejection"] = {
        "passed": not result.passed,
        "hard_violations": result.hard_violations,
    }
    print(f"  NaN state rejected: {not result.passed}")
    
    # Test infinite state
    inf_state = nan_state.copy()
    inf_state["some_metric"] = float('inf')
    result2 = run_audit(inf_state, config)
    results["inf_rejection"] = {
        "passed": not result2.passed,
        "hard_violations": result2.hard_violations,
    }
    print(f"  Inf state rejected: {not result2.passed}")
    
    return results


def test_weight_manipulation() -> Dict[str, Any]:
    """Test if soft constraint weights can mask hard violations"""
    print("Testing weight manipulation...")
    
    results = {}
    
    constraints = make_ciems_constraints()
    config = AuditConfig(constraints=constraints)
    
    # State with hard violation but many soft "good" metrics
    violating_state = {
        "exit_allowed": True, "exit_punitive": True,  # HARD VIOLATION
        "evidence_auditable": True, "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True, "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
    }
    
    # Add many soft constraints that are satisfied
    soft_constraints = [
        AuditConstraint(f"soft_metric_{i}", lambda s: True, is_hard=False, weight=1.0)
        for i in range(20)
    ]
    
    config_with_soft = AuditConfig(constraints=constraints + soft_constraints)
    result = run_audit(violating_state, config_with_soft)
    
    # Should still fail because hard violation
    hard_violation_blocks = not result.passed
    results["hard_violation_blocks_despite_soft"] = {
        "passed": hard_violation_blocks,
        "verdict": result.verdict,
        "hard_violations": result.hard_violations,
    }
    print(f"  Hard violation blocks despite soft metrics: {hard_violation_blocks}")
    
    return results


def test_audit_feedback_manipulation() -> Dict[str, Any]:
    """Test if audit feedback control can be gamed"""
    print("Testing audit feedback control...")
    
    from constitutional_stack.layers.layer6_audit import audit_feedback_control
    
    results = {}
    
    # Test that low verdict triggers intervention
    low_verdict = 0.5
    intervention = audit_feedback_control(low_verdict, threshold=0.95)
    results["low_verdict_triggers"] = {
        "passed": intervention > 0,
        "intervention": intervention,
    }
    print(f"  Low verdict (0.5) triggers intervention: {intervention > 0} (u={intervention:.3f})")
    
    # Test that high verdict doesn't trigger
    high_verdict = 1.0
    intervention2 = audit_feedback_control(high_verdict, threshold=0.95)
    results["high_verdict_no_trigger"] = {
        "passed": intervention2 == 0,
        "intervention": intervention2,
    }
    print(f"  High verdict (1.0) no trigger: {intervention2 == 0} (u={intervention2:.3f})")
    
    # Test boundary
    boundary_verdict = 0.95
    intervention3 = audit_feedback_control(boundary_verdict, threshold=0.95)
    results["boundary_verdict"] = {
        "passed": intervention3 == 0,
        "intervention": intervention3,
    }
    print(f"  Boundary verdict (0.95) no trigger: {intervention3 == 0} (u={intervention3:.3f})")
    
    return results


def test_audit_consistency() -> Dict[str, Any]:
    """Test if audit is deterministic and consistent"""
    print("Testing audit consistency...")
    
    constraints = make_ciems_constraints()
    config = AuditConfig(constraints=constraints)
    
    state = {
        "exit_allowed": True, "exit_punitive": False,
        "evidence_auditable": True, "evidence_reproducible": True,
        "unchallengeable_authority": False,
        "errors_reversible": True, "decisions_appealable": True,
        "continuity_preserved": True,
        "reconstruction_possible": True,
        "failure_modes_defined": True,
    }
    
    results = {}
    
    # Run multiple times
    verdicts = []
    for _ in range(100):
        result = run_audit(state, config)
        verdicts.append(result.verdict)
    
    all_same = len(set(verdicts)) == 1
    results["deterministic"] = {
        "passed": all_same,
        "verdicts": verdicts[:5],
        "unique_count": len(set(verdicts)),
    }
    print(f"  Deterministic: {all_same} (unique verdicts: {len(set(verdicts))})")
    
    return results


def run_layer6_red_team() -> Dict[str, Any]:
    """Run all Layer 6 red team tests"""
    print("\n" + "="*50)
    print("LAYER 6 RED TEAM TESTS")
    print("="*50)
    
    all_results = {}
    
    all_results["gaming_states"] = test_audit_gaming()
    all_results["hard_constraint_bypass"] = test_hard_constraint_bypass()
    all_results["weight_manipulation"] = test_weight_manipulation()
    all_results["feedback_manipulation"] = test_audit_feedback_manipulation()
    all_results["consistency"] = test_audit_consistency()
    
    # Summary
    total = 0
    gaming_detected = 0
    for category, tests in all_results.items():
        for test_name, result in tests.items():
            total += 1
            if result.get("gaming_detected") or result.get("passed") is False and "rejection" in test_name.lower():
                gaming_detected += 1
            elif "blocks" in test_name and result.get("passed"):
                gaming_detected += 1
            elif "triggers" in test_name and result.get("passed"):
                gaming_detected += 1
            elif "no_trigger" in test_name and result.get("passed"):
                gaming_detected += 1
            elif "deterministic" in test_name and result.get("passed"):
                gaming_detected += 1
    
    print(f"\nLayer 6 Red Team Summary: {gaming_detected}/{total} properties verified")
    
    all_results["summary"] = {
        "total_tests": total,
        "verified": gaming_detected,
        "verification_rate": gaming_detected / total if total > 0 else 0,
    }
    
    return all_results


if __name__ == "__main__":
    run_layer6_red_team()