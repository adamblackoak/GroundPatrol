# GroundPatrol architecture note

## Core claim

A field agent should not move directly from language-model interpretation to physical
consequence.

```text
runtime observations
      |
      v
 Strands agent
 interpretation + proposal
      |
      v
 execution request
      |
      v
 deterministic PatrolGate
 evidence freshness
 scope / access
 habitat authority
 people-clearance
 operating envelope
 action allowlist
      |
      +---- APPROVE ------> bounded action + receipt
      +---- CONDITIONAL --> unmet condition + human control
      +---- DEFER --------> refresh/escalate
      +---- DENY ---------> no action
```

## Research-to-implementation choices

### 1. Interpose control, do not merely log
Observability after a bad action is too late. GroundPatrol's gate sits before the
consequential claim that an action may proceed.

### 2. Discrete outcomes beat eloquent ambiguity
The control plane emits four explicit states. The language model can explain them but
cannot silently soften them.

### 3. Degraded state is first-class
Stale evidence, people in the envelope, protected habitat, poor visibility and high
wind all have defined behaviour.

### 4. Build the generator/evaluator pair narrowly
The generator is the Strands agent. The first evaluator is deterministic policy code.
A later shadow evaluator may inspect drift and faithfulness, but only after v0 creates
real traces to evaluate.

### 5. Preserve proof
Every gate event produces a canonicalised SHA-256 receipt containing observations,
proposal, decision and reasons.

### 6. Avoid agent-loop theatre
No committee of agents is required to decide whether 80 kph wind is outside an allowed
operating envelope. Deterministic controls own that class of decision.

## Evaluation targets

- interception effectiveness: every consequential action request hits the gate
- bypass resistance: the agent cannot legitimately claim execution without clearance
- false-positive/escalation rate: safe scenarios should not be needlessly blocked
- degraded-state behaviour: uncertainty reduces autonomy
- accountability completeness: proposal, evidence, decision and result can be replayed
