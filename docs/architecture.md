# GroundPatrol architecture diagram

```mermaid
flowchart LR
    U[Coastal operator] -->|Patrol request| A[Strands Agent]
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
    V -->|VERIFIED + APPROVE| X[Bounded execution / dispatch]
    V -->|VERIFIED + non-APPROVE| H[Refresh / human review / stop]
    V -->|REJECTED| B[Correct inconsistency / stop]
    X --> T[Execution trace]
    H --> T
```

## AWS deployment view

```mermaid
flowchart TB
    UI[CLI / API / demo client] --> AC[Amazon Bedrock AgentCore Runtime]
    AC --> SA[GroundPatrol Strands Agent]
    SA --> BR[Amazon Bedrock model]
    SA --> TOOLS[GroundPatrol tools]
    TOOLS --> GATE[Deterministic PatrolGate + Finalizer]
    TOOLS --> FEEDS[Fixture feed / Open-Meteo]
    GATE --> REC[Decision receipt]
```

The architecture deliberately separates probabilistic interpretation from deterministic execution authority. The model can propose; the gate decides whether the proposal is cleared; the finalizer checks that the agent's intended next action is consistent with that recorded decision.
