# GroundPatrol architecture diagram

```mermaid
flowchart LR
    U[Coastal operator] --> UI[Operator UI / CLI / API]
    UI -->|Patrol request| A[Strands Agent]
    A --> O[get_patrol_snapshot]
    O --> F{Evidence feed}
    F -->|Default| FX[Deterministic fixtures]
    F -->|Optional| OM[Open-Meteo live weather]
    O --> S[(Frozen PatrolSnapshot\ncontent-addressed snapshot_id)]
    S --> A
    A --> P[Bounded action proposal]
    P --> G[PatrolGate\ndeterministic execution boundary]
    G --> C1[Freshness]
    G --> C2[Access / habitat / people]
    G --> C3[Wind / visibility]
    G --> C4[Action allowlist / mass limit]
    G --> D{Decision}
    D -->|APPROVE| R[Tamper-evident SHA-256 receipt]
    D -->|CONDITIONAL| R
    D -->|DEFER| R
    D -->|DENY| R
    R --> V[Deterministic Finalizer\nreceipt integrity + next-action consistency]
    V -->|VERIFIED + APPROVE| X[Idempotent work-order dispatch]
    V -->|VERIFIED + non-APPROVE| H[Refresh / human review / stop]
    V -->|REJECTED| B[Correct inconsistency / stop]
    X --> Q[(Field-work queue adapter)]
    Q --> T[Execution trace]
    H --> T
    R --> UI
    Q --> UI
```

## AWS deployment view

```mermaid
flowchart TB
    UI[Operator UI / CLI / API] --> AC[Amazon Bedrock AgentCore Runtime]
    AC --> SA[GroundPatrol Strands Agent]
    SA --> BR[Amazon Bedrock model]
    SA --> TOOLS[GroundPatrol tools]
    TOOLS --> GATE[Deterministic PatrolGate + Finalizer]
    TOOLS --> FEEDS[Fixture feed / Open-Meteo]
    GATE --> REC[Decision receipt]
    GATE --> DISPATCH[Approval-gated work-order adapter]
```

The architecture deliberately separates probabilistic interpretation from deterministic execution authority. The model can propose; the gate decides whether the proposal is cleared; the finalizer checks that the agent's intended next action is consistent with that recorded decision; the side-effect adapter re-checks approval before dispatch.
