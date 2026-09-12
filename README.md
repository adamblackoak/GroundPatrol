# GroundPatrol

**A governed coastal-operations agent for Agents for Humans.**

GroundPatrol helps coastal teams turn field observations into bounded operational decisions. The Strands agent can interpret and propose; a deterministic runtime boundary decides whether the proposed physical action is actually cleared.

## The point

The interesting question is not whether an LLM can tell a robot to pick up litter. It is whether an agent stays useful when evidence is stale, people enter the operating envelope, access closes, habitat rules apply, or weather degrades.

GroundPatrol therefore separates:

`OBSERVE -> FREEZE SNAPSHOT -> PROPOSE -> AUTHORISE -> VERIFY -> EXECUTE/ESCALATE -> RECEIPT`

The model is deliberately **not** the execution authority.

## Reliability spine

Current v0.2 implements:

- a real Strands agent with explicit tool boundaries
- evidence objects with timestamps and freshness checks
- a content-addressed `snapshot_id` binding clearance to the exact observed state
- fixture and optional live-weather feeds
- bounded allowlisted actions and deterministic operating-envelope checks
- discrete `APPROVE / CONDITIONAL / DEFER / DENY` outcomes
- human escalation for consequential ambiguity
- a deterministic second-pass finalizer that rejects decision/action contradictions
- tamper-evident SHA-256 decision receipts
- Strands before/after tool hooks for the visible execution ledger
- 14 deterministic tests covering safe and degraded-state behaviour

The doctrine is simple: **model proposes; governed control decides; evaluator checks; trace records.**

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python main.py
```

Strands defaults to Amazon Bedrock, so configure AWS credentials and model access before running the live agent.

## Reproducible demo scenarios

The default feed is deterministic. Set the scenario outside the agent so the model cannot simply choose favourable conditions.

```powershell
$env:GROUNDPATROL_FEED="fixture"
$env:GROUNDPATROL_SCENARIO="clear"
python main.py

$env:GROUNDPATROL_SCENARIO="people_nearby"
python main.py
```

The first run should clear a bounded collection. The second should defer the same type of autonomous collection and route to human review.

Other fixture states: `protected_habitat`, `access_closed`, `high_wind`, `low_visibility`, `stale`.

## Optional live weather

```powershell
$env:GROUNDPATROL_FEED="live"
$env:GROUNDPATROL_SCENARIO="clear"
python main.py
```

Live mode overlays Open-Meteo wind and visibility on explicitly labelled fixture operational facts. GroundPatrol does not pretend that access, habitat, people or debris data came from sensors that do not exist.

## Governed tool path

1. `get_patrol_snapshot` observes state and returns a `snapshot_id`.
2. The model proposes a bounded action.
3. `request_action_clearance` evaluates that exact snapshot, not a silently regenerated one.
4. A SHA-256 receipt binds evidence, proposal and gate decision.
5. `finalize_patrol_decision` verifies receipt integrity and checks that the claimed decision and next action are consistent.
6. Only then does the agent report the operational next step.

## AgentCore deployment path

The intended competition deployment is a **code-based Strands agent on Amazon Bedrock AgentCore Runtime**.

```bash
npm install -g @aws/agentcore
agentcore create
```

Choose Python, Strands Agents and Bedrock in the wizard, then place this package in the generated application and deploy with the AgentCore CLI. We keep the runtime scaffold out of this repository until AWS account/region choices are known rather than committing guessed infrastructure config.

## Competition track

Professional Agents.
