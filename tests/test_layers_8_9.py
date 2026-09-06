"""
Integrated test: Phase E (Layer 8) and Phase F (Layer 9)
H8: Multi-agent field ecology - ρ(x,t), h(x,t) PDEs, coherence generation
H9: Cross-layer conformance matrix - φ_i preserve invariants, Γ closure
"""
import numpy as np
from typing import Dict, Any

from constitutional_stack.layers.layer8_field_ecology import test_layer8
from constitutional_stack.layers.layer9_unified import test_layer9


def test_hypothesis_h8_field_ecology() -> Dict[str, Any]:
    """H8: Field ecology - coherence increases with agent density, PDE dynamics"""
    print("\n=== H8: Constitutional Field Ecology ===")
    result = test_layer8()

    # Key: polarization increases (agents self-organize into coherent clusters)
    passed = (result["passed"] and
              result["final_metrics"]["polarization"] > 0.1)

    print(f"H8 PASSED: {passed}")
    return {"hypothesis": "H8", "passed": passed, "metrics": result}


def test_hypothesis_h9_conformance() -> Dict[str, Any]:
    """H9: Cross-layer conformance - invariants preserved, closure holds"""
    print("\n=== H9: Cross-Layer Conformance ===")
    result = test_layer9()

    passed = (result["all_preserved"] and
              result["closure_works"])

    print(f"H9 PASSED: {passed}")
    return {"hypothesis": "H9", "passed": passed, "metrics": result}


def run_phase_e_f():
    """Run Phase E (Layer 8) and Phase F (Layer 9) tests"""
    print("\n" + "="*60)
    print("PHASE E/F: LAYERS 8-9 INTEGRATED TEST")
    print("="*60)

    results = {
        "H8": test_hypothesis_h8_field_ecology(),
        "H9": test_hypothesis_h9_conformance(),
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
    results = run_phase_e_f()

    # Summary
    print("\nSUMMARY:")
    for h, r in results["results"].items():
        status = "✓" if r["passed"] else "✗"
        print(f"  {status} {r['hypothesis']}")