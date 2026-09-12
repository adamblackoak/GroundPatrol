# GroundPatrol architecture note

## Core claim

A field agent should not move directly from language-model interpretation to physical consequence.

```text
external observations
       |
       v
 evidence-backed PatrolSnapshot
       |
       +--> content-addressed snapshot_id
       |
       v
 Strands agent proposes action
       |
       v
 deterministic PatrolGate
 freshness / access / habitat / people / weather / allowlist
       |
       +---- APPROVE
       +---- CONDITIONAL
       +---- DEFER
       +---- DENY
       |
       v
 tamper-evident receipt
       |
       v
 deterministic Finalizer
 decision claim + next-action consistency
       |
       +---- VERIFIED ---> bounded action or handoff
       +---- REJECTED ---> correct / stop
```

## Research-to-implementation choices

### 1. Interpose control, do not merely log
Observability after a bad action is too late. GroundPatrol's gate sits before a consequential action can be represented as cleared.

### 2. Bind the decision to the evidence actually observed
The first scaffold regenerated a fresh demo snapshot at clearance time. v0.2 fixes that. Observation now returns a content-addressed `snapshot_id`; clearance must reference that exact immutable state.

### 3. Discrete outcomes beat eloquent ambiguity
The control plane emits four explicit states. The language model can explain them but cannot silently soften them.

### 4. Use a narrow generator/evaluator pair
The Strands agent generates the proposal. The gate decides policy. A second deterministic finalizer checks whether the intended next action is compatible with the recorded decision. No extra free-running agent is needed for a rule that can be expressed directly.

### 5. Degraded state is first-class
Stale evidence, people in the envelope, protected habitat, closed access, poor visibility and high wind all have defined behaviour.

### 6. Preserve proof
Every gate event produces a canonical SHA-256 receipt containing snapshot identity, observations, proposal, decision and reasons. Finalization verifies the receipt before relying on it.

### 7. Make source boundaries legible
The default fixture feed is deterministic for evaluation. Optional live mode uses a real weather source while leaving synthetic/fixture facts explicitly labelled. The system does not launder mock inputs into "live sensor" claims.

## Evaluation targets

- interception effectiveness: every consequential action request hits the gate
- state binding: clearance references the exact previously observed snapshot
- bypass resistance: execution is not a valid next action for DEFER/DENY/CONDITIONAL
- false-positive/escalation rate: safe scenarios should not be needlessly blocked
- degraded-state behaviour: uncertainty reduces autonomy
- accountability completeness: proposal, evidence, decision and final next action can be reconstructed
