"""
Integrated test: Layers 4-7 computational prototype
H4: Duality invariance - decomposition verified, orbit separation
H5: Duality geometry - I₈ complementarity, H₅ coherence, φ_boundary ± δφ
H6: Constitutional audit - hard constraints c_j(x)=1, verdict V(x)
H7: Reflexive runtime - Lyapunov ΔL < 0, audit feedback control
"""
import numpy as np
from typing import Dict, Any

from constitutional_stack.layers.layer4_duality import test_layer4
from constitutional_stack.layers.layer5_duality_geometry import test_layer5
from constitutional_stack.layers.layer6_audit import test_layer6
from constitutional_stack.layers.layer7_runtime import test_layer7


def test_hypothesis_h4_duality() -> Dict[str, Any]:
    """H4: Duality invariance - D²=I, projectors, orbit separation"""
    print("\n=== H4: Duality Invariance ===")
    result = test_layer4()

    passed = (result["decomposition_verified"] and
              result["orbit_separation"]["separates_orbits"] and
              result["universal_property"]["universal_property_holds"])

    print(f"H4 PASSED: {passed}")
    return {"hypothesis": "H4", "passed": passed, "metrics": result}


def test_hypothesis_h5_geometry() -> Dict[str, Any]:
    """H5: Duality geometry - I₈=0, H₅, φ_boundary ± δφ"""
    print("\n=== H5: Duality Geometry ===")
    result = test_layer5()

    passed = (result["I8_verified"] and
              result["H5"] > 0.9 and  # strong orbital coherence
              result["phase_lock"]["consistent"])

    print(f"H5 PASSED: {passed}")
    return {"hypothesis": "H5", "passed": passed, "metrics": result}


def test_hypothesis_h6_audit() -> Dict[str, Any]:
    """H6: Constitutional audit - hard constraints, hard violations block"""
    print("\n=== H6: Constitutional Audit ===")
    result = test_layer6()

    passed = (result["compliant_passed"] and
              not result["violating_passed"] and
              result["feedback_works"])

    print(f"H6 PASSED: {passed}")
    return {"hypothesis": "H6", "passed": passed, "metrics": result}


def test_hypothesis_h7_runtime() -> Dict[str, Any]:
    """H7: Reflexive runtime - Feedback control works, interventions fire"""
    print("\n=== H7: Reflexive Runtime ===")
    result = test_layer7()

    # Key requirements: interventions fire when audit fails, system can run >10 cycles
    passed = (result["interventions"] > 0 and
              result["cycles"] > 10)

    print(f"H7 PASSED: {passed}")
    return {"hypothesis": "H7", "passed": passed, "metrics": result}


def run_phase_c_d():
    """Run Phase C (Layers 4-6) and Phase D (Layer 7) tests"""
    print("\n" + "="*60)
    print("PHASE C/D: LAYERS 4-7 INTEGRATED TEST")
    print("="*60)

    results = {
        "H4": test_hypothesis_h4_duality(),
        "H5": test_hypothesis_h5_geometry(),
        "H6": test_hypothesis_h6_audit(),
        "H7": test_hypothesis_h7_runtime(),
    }

    all_passed = all(r["passed"] for r in results.values())
    print(f"\n{'='*60}")
    print(f"ALL HYPOTHESES PASSED: {all_passed}")
    print(f"{'='*60}")

    return {
        "all_passed": all_passed,
        "results": results,
    }


if __name__ == "__main__":
    results = run_phase_c_d()

    # Summary
    print("\nSUMMARY:")
    for h, r in results["results"].items():
        status = "✓" if r["passed"] else "✗"
        print(f"  {status} {r['hypothesis']}")