# Constitutional Stack — Computational Prototype

> **Constitutional Continuity = Reality-Correctable Judgment Propagated Through Lineage**

*Physical claims (Layer 5 helical geometry, Layer 8 field quantization, Layer 9 unified physics) remain open research questions per the paper's claim-class discipline.*

---

## Overview

This repository implements a **computational prototype** of the Constitutional Stack — a layered architecture formalized in *"The Constitutional Stack: A Nine-Layer Unified Constitutional Framework"* (Halstead & Pritchard, 2026).

**Status:** Computational prototype complete. **9/9 numeric checks pass.**  
**Not:** Architecture proven. Not a unified framework verified. Not a Voss Binding implementation.

The prototype demonstrates **numeric existence proofs** for each layer's core computation. It does **not** yet wire the Voss Binding (AAIS-VB-Λ-001) or the ARIS Cycle Operator (ARIS-OP-Λ-001) into a single governed runtime.

---

## Computational Checks (Toy) — Not Verified Hypotheses

| Layer | Name | Domain | Core Computation | Check | Claim Class |
|-------|------|--------|------------------|-------|-------------|
| **1** | **Wave Math** | Micro Continuity | `ψ_{t+1} = J(ψ_t, R(ψ_t,E_t))` | H1: Corrigibility ✓ | Numeric |
| **2** | **CFT** | Macro Continuity | `x_{n+1} = T(x_n, η_n)` | H2: Continuity ✓ | Numeric |
| **3** | **Reconstruction Sufficiency** | Meta Continuity | `y=A(x)+η, x̂=R*(y)` | H3: Reconstruction ✓ | Numeric |
| **4** | **Duality Invariant Theory** | Mathematical Backbone | `D²=I, P±=½(I±D)` | H4: Duality ✓ | Numeric |
| **5** | **Law of Duality** | Structural/Physical Geometry | Helix `r(t)=(a cosωt,a sinωt,vt)` | H5: Geometry ✓ | Physical-Open |
| **6** | **Constitutional Audit Protocol** | Meta-Evaluation | `c_j(x)=1` hard, `V(x)=Σw_i c_i` | H6: Audit ✓ | Architectural |
| **7** | **Reflexive Runtime (CRK-1)** | Autopoietic Execution | `u_t=K(V(x_t))`, Lyapunov `ΔL<0` | H7: Runtime ✓ | Architectural |
| **8** | **Constitutional Field Ecology** | Multi-Agent Field Physics | `∂ρ/∂t+∇·(ρv)=S`, `∂h/∂t=D∇²h+F` | H8: Field ✓ | Physical-Open |
| **9** | **Unified Constitutional Framework** | Capstone Integration | `φ_i: L_i→L_{i+1}`, `Γ: L9→L1` | H9: Conformance ✓ | Architectural |

**Claim Class Key:**  
- **Numeric** = numpy script passes on toy data  
- **Architectural** = in-process boolean checks fire  
- **Physical-Open** = fitted on parametric curve / grid update; no empirical validation  

**What the checks actually show:**

| Check | What the numpy test shows | What it cannot show |
|-------|---------------------------|---------------------|
| H1 Corrigibility | Scripted update moves ψ toward planted target | Agent becomes interruptible under Λ.6 |
| H2 Continuity | Mutual information ≈ 1 on toy chain | Identity/memory survive real runtime |
| H3 Reconstruction | `‖x-x̂‖ ≤ ε` for chosen A,η | Audit traces recover live AAIS state |
| H4 Duality | Linear algebra on defined involution matrix | Agents are non-mergeable eigenspaces |
| H5 Geometry | Fitted angle on parametric curve | Geometry of cognition or physics |
| H6 Audit | Boolean constraints fire in-process | GRE cannot be bypassed |
| H7 Runtime | Controller decreases scalar L | Fail-closed, breakers, Operator halt |
| H8 Field | Grid update moves two floats | Multi-agent identity isolation |
| H9 Conformance | 8 hand-written maps return | Stack governs Project Infinity |

**These are numeric existence proofs, not verification of a unified framework.**

---

## Voss Binding Map — Stack vs Swarm Law 7.2

The Voss Binding (AAIS-VB-Λ-001) is a **constitution** (AAIS). The ARIS Cycle Operator (ARIS-OP-Λ-001) is a **cycle-boundary operator** (ARIS). They are different documents with different IDs. See `docs/VB_LAMBDA_ENACTMENT_SPEC.md`.

The table below maps each Voss Binding primitive to: the enactment spec section, the stack layer, the prototype's implementation status, and **what exists in Swarm Law 7.2** (`/home/jon/swarmlaw-gov-v2`). The Swarm Law 7.2 codebase (`crates/governor/`, `crates/governor/src/`, `crates/merkle-audit/`, `crates/gateway/`) is a **working enactment** further along the plane.

| Binding Primitive | Enactment Spec (§) | Stack Layer | This Repo | Swarm Law 7.2 (crates/governor, merkle-audit, gateway) |
|-------------------|-------------------|-------------|-----------|--------------------------------------------------------|
| **Λ.1–Λ.7 Laws** | §2 Seven Laws | **L6** Audit | ⚠️ 7 CIEMS ≠ Λ.1–Λ.7 | **`policy.rs`** = `Policy::validate()` enforces Λ.1–Λ.7; `law_gate()` is the singleton |
| **GRE Pipeline** | §4.1 GRE | **L7** Runtime | ⚠️ Pipeline stages; no singleton | **`Governor`** = `evaluate()` = full 6-stage pipeline; `law_gate()` is the singleton enforcer |
| **Circuit Breaker** | §4.2 | **L7** Runtime | ⚠️ System-level only; no per-module registry | **`ReplayGuard`** = Redis SET NX/PX + `noeviction` check; LWT claim in Scylla = durable replay authority |
| **Message Bus** | §4.2 | **L8** Field | ❌ Missing | ❌ Missing — direct gRPC only; no schema-validated bus / identity leak detector |
| **Contract Registry** | §4.3 + §8 | **L9** Unified | ❌ Design-time matrix | ❌ Hardcoded `policy.rs::Policy::local()`; no runtime registration/versioning |
| **Module Lifecycle** | §4.4 | **L7** Runtime | ❌ Missing | ❌ Not implemented; `Governor` lifecycle is implicit |
| **Kill Switch** | §6 | **L7** Runtime | ⚠️ Exists; unwired | ⚠️ **CompensationService** exists; returns `failed_precondition`; no kill switch |
| **Identity Leak Detector** | §4.2 | **L8** Field | ❌ Missing | ❌ Not implemented as continuous background process |
| **Drift 4-Vector** | §3 Drift | **L8** Field | ⚠️ PDEs; no estimator | ⚠️ Not explicit; risk scoring in `policy.rs` + evidence risk levels |
| **Δ-Op (Recovery)** | §4 Δ-Op | **L7** Runtime | ❌ Lyapunov ≠ Δ-Op | ❌ CompensationService returns `failed_precondition`; no signed Δ-Op |
| **ARIS Cycle Operator** | §5 ARIS-OP-Λ | **Missing** | ❌ Missing | ❌ Not present |
| **Δ as Only Recovery** | §4 Δ-Op | **L7** | ❌ Lyapunov ≠ Δ-Op | ❌ No Δ-Op; `Governor` evaluates → approves/denies |
| **Conformance Objects** | §6 | **L9** | ⚠️ Design-time matrix | ⚠️ `merkle-audit` = audit chain worker; no conformance object |

**Key Architectural Gaps (Both Sides):**

| Gap | Stack Repo | Swarm Law 7.2 |
|-----|------------|---------------|
| **Λ.1–Λ.7 bijection** | 7 CIEMS ≠ Λ.1–Λ.7 | `policy.rs` enforces laws but no published bijection |
| **Singleton GRE** | Pipeline stages; no singleton | `Governor::connect()` = singleton; `law_gate()` is the enforcer |
| **Circuit Breaker** | System-level only | `ReplayGuard` (Redis SET NX/PX) + Scylla LWT = dual-layer |
| **Message Bus** | ❌ Missing | ❌ Missing — direct gRPC only |
| **Contract Registry** | Design-time matrix | Hardcoded `policy.rs::Policy::local()`; no runtime registration |
| **Module Lifecycle** | ❌ Missing | Not implemented |
| **Kill Switch** | Exists; unwired | ❌ CompensationService only; returns `failed_precondition` |
| **Identity Leak Detector** | ❌ Missing | ❌ Not implemented |
| **Drift 4-Vector** | PDEs; no estimator | Risk scoring in `policy.rs` + evidence risk levels |
| **Δ-Op** | Lyapunov ≠ Δ-Op | CompensationService returns `failed_precondition` |
| **ARIS Cycle Operator** | ❌ Missing | Not present |
| **Conformance Objects** | Design-time matrix | `merkle-audit` = audit chain worker |

---

## Status Line

**Constitution: ratified. Enactment in this repo: partial. Enactment in Swarm Law 7.2: further along the plane. Physical/field claims: open.**

---

## Priority Work Order (If the Map Is the Work Order)

Do not start with Message Bus or Field estimators.

1. **Published Λ ↔ CIEMS bijection** (one page — L6 ↔ §2)
2. **Singleton GRE**: no `execute()` except through it (L7 → §4.1)
3. **Runtime Contract Registry** (even dict + version) — L9 → §4.3 + §8
4. **Kill Switch wired into that GRE** (L7 → §6)
5. **Δ-Op = signed Operator record**, or it does not unlock (swarm recovery lesson) — L7 → §4 Δ-Op
6. **Then**: Message Bus / Identity Leak Detector / Cycle Operator

---

## Project Structure

```
constitutional_stack/
├── __init__.py
├── .gitignore
├── schemas/
│   ├── __init__.py
│   └── trace_schema_v1.py          # 7-field TraceSchema v1
├── layers/
│   ├── __init__.py
│   ├── layer1_wave_math.py         # ψ_{t+1} = J(ψ_t, R(ψ_t,E_t))
│   ├── layer2_cft.py               # x_{n+1} = T(x_n, η_n), MI fidelity
│   ├── layer3_reconstruction.py    # y=A(x)+η, R* with error bound ε
│   ├── layer4_duality.py           # D²=I, P±, decomposition, universal property
│   ├── layer5_duality_geometry.py  # Corrected C=Relational, O=Structural, H₅
│   ├── layer6_audit.py             # 7 CIEMS hard constraints, V(x), feedback
│   ├── layer7_runtime.py           # Audit→Evidence→R→J→ψ' loop, Lyapunov
│   ├── layer7_voss_runtime.py      # GRE, Breakers, Registry, Lifecycle, KillSwitch
│   ├── layer8_field_ecology.py     # ρ(x,t), h(x,t) PDEs, agent fields
│   ├── layer8_message_bus.py       # Schema-validated Message Bus, Leak Detector
│   ├── layer9_unified.py           # Conformance matrix, φ_i maps, Γ closure
│   └── layer9_voss_deployment.py   # Contract Registry v2, Deployment Checklist
└── tests/
    ├── test_layers_1_3.py          # H1, H2, H3
    ├── test_layers_4_7.py          # H4, H5, H6, H7
    ├── test_layers_8_9.py          # H8, H9
    └── adversarial/
        ├── adversarial_inputs/
        │   ├── trace_corruption.py
        │   ├── evidence_poisoning.py
        │   ├── audit_gaming.py
        │   └── byzantine_agents.py
        ├── parameter_sweeps/
        │   ├── layer1_sweep.py
        │   └── __init__.py (param spaces)
        ├── red_team/
        │   ├── test_layer1_adversarial.py
        │   ├── test_layer6_adversarial.py
        │   └── test_runtime_voss_binding.py
        ├── alternative_models/
        ├── stress_scenarios/
        ├── independent_reproduction/
        └── formal_verification/
```

---

## Running the Checks

```bash
# Install dependencies (numpy only)
pip install numpy

# Phase A/B: Layers 1-3 (H1-H3) — Numeric
python -m constitutional_stack.tests.test_layers_1_3

# Phase C/D: Layers 4-7 (H4-H7) — Numeric + Architectural
python -m constitutional_stack.tests.test_layers_4_7

# Phase E/F: Layers 8-9 (H8-H9) — Numeric + Architectural
python -m constitutional_stack.tests.test_layers_8_9

# Adversarial / Red Team (requires full stack wired)
# python -m constitutional_stack.adversarial.red_team.test_layer1_adversarial
# python -m constitutional_stack.adversarial.red_team.test_layer6_adversarial
# python -m constitutional_stack.adversarial.red_team.test_runtime_voss_binding
```

**Expected output:** `ALL HYPOTHESES PASSED: True` (for numeric checks that exist).

---

## Key Files

| File | Description |
|------|-------------|
| `schemas/trace_schema_v1.py` | 7-field JSON schema (necessary & sufficient for R*) |
| `layers/layer1_wave_math.py` | Wave Math engines + measurable corrigibility |
| `layers/layer2_cft.py` | CFT transmission + information-theoretic fidelity |
| `layers/layer3_reconstruction.py` | Inverse problem `y=A(x)+η`, reconstruction operator R* |
| `layers/layer4_duality.py` | Involution `D²=I`, projectors `P±`, orbit separation |
| `layers/layer5_duality_geometry.py` | **Corrected** Chaos=Relational, Order=Structural, `φ_boundary ± δφ` |
| `layers/layer6_audit.py` | 7 CIEMS hard constraints `c_j(x)=1`, verdict `V(x)` |
| `layers/layer7_runtime.py` | Reflexive loop `Audit→Evidence→R→J→ψ'`, Lyapunov monitor |
| `layers/layer7_voss_runtime.py` | **GRE, Breakers, Registry, Lifecycle, KillSwitch** (Voss §4) |
| `layers/layer8_field_ecology.py` | Continuum PDEs `ρ(x,t)`, `h(x,t)` with coherence diffusion |
| `layers/layer8_message_bus.py` | **Schema-validated Message Bus, Identity Leak Detector** (Voss §4.2) |
| `layers/layer9_unified.py` | Conformance matrix, φ_i maps, Γ closure |
| `layers/layer9_voss_deployment.py` | **Contract Registry v2, Deployment Checklist (CHK-01–10)** |

---

## The Triadic Backbone (C→O→H)

Every layer implements the same role-triad with typed observables:

```
C_i = admissible change / generative dynamics
O_i = constraint / structure / invariant
H_i = measurable coherence H_i: C_i × O_i → [0,1]
```

**Candidate Harmonization Functional:**
```
r(x) = F_C(x) − Π_{T_x M_O} F_C(x)
H(x) = exp(− ‖r(x)‖² / σ²)  ∈ (0,1]
```

---

## Closure

The prototype stack folds back on itself:
```
L1 → L2 → L3 → L4 → L5 → L6 → L7 → L8 → L9
                      ↓
                      Γ: L9 → L1
                      (correction cycle with memory)
```

---

## License

Apache 2.0

## Authors

- Jon Halstead (Project Infinity — AAIS / Mythar Root Systems)
- Steven Pritchard (Co-creator)

## Status

**Preprint — For Review** — Computational prototype complete, 9/9 numeric checks pass.  
**Not:** Voss Binding implemented. Not ARIS Cycle Operator integrated.  
**Physical claims** (Layer 5 helical geometry, Layer 8 field quantization, Layer 9 unified physics) **remain open research questions** per the paper's claim-class discipline.