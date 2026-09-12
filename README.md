# GroundPatrol

**A governed coastal-operations agent for Agents for Humans.**

GroundPatrol helps professional coastal teams turn field observations into bounded operational work. The Strands agent can interpret and propose; deterministic runtime controls decide whether a consequential action is cleared, and only an approved decision can become a collection work order.

## The point

The interesting question is not whether an LLM can tell a robot to pick up litter. It is whether an agent stays useful when evidence is stale, people enter the operating envelope, access closes, habitat rules apply, or weather degrades.

GroundPatrol therefore separates:

`OBSERVE -> FREEZE SNAPSHOT -> PROPOSE -> AUTHORISE -> VERIFY -> DISPATCH/ESCALATE -> RECEIPT`

The model is deliberately **not** the execution authority.

## Reliability spine

Current v0.4 implements:

- a real Strands agent with explicit tool boundaries
- an operator-facing Streamlit demo for a coherent patrol workflow
- evidence objects with timestamps and freshness checks
- a content-addressed `snapshot_id` binding clearance to the exact observed state
- fixture and optional live-weather feeds
- bounded allowlisted actions and deterministic operating-envelope checks
- discrete `APPROVE / CONDITIONAL / DEFER / DENY` outcomes
- human escalation for consequential ambiguity
- a deterministic second-pass finalizer that rejects decision/action contradictions
- tamper-evident SHA-256 decision receipts
- an approval-gated, idempotent collection work-order dispatch adapter
- Strands before/after tool hooks for the visible execution ledger
- deterministic tests covering safe, degraded and side-effect-boundary behaviour

The doctrine is simple: **model proposes; governed control decides; evaluator checks; trace records.**

## Architecture

See the [submission architecture diagrams](docs/architecture.md) and the longer [architecture note](ARCHITECTURE.md).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python main.py
```

Strands defaults to Amazon Bedrock, so configure AWS credentials and model access before running the live agent.

## Operator UI

For the judge/demo experience:

```powershell
pip install -e ".[ui]"
streamlit run operator_ui.py
```

The UI lets the operator select the evidence mode and an externally controlled operating state, run the patrol, and inspect the agent outcome, latest decision receipt and latest work order side by side. This keeps the product experience legible without hiding the governance boundary behind a chat transcript.

## Reproducible demo scenarios

The default feed is deterministic. Set the scenario outside the agent so the model cannot simply choose favourable conditions.

```powershell
$env:GROUNDPATROL_FEED="fixture"
$env:GROUNDPATROL_SCENARIO="clear"
python main.py

$env:GROUNDPATROL_SCENARIO="people_nearby"
python main.py
```

The first run should clear the bounded collection and create one idempotent `QUEUED_FOR_COLLECTION` work order. The second should defer the same class of collection request and refuse dispatch.

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
6. `dispatch_collection_work_order` independently re-verifies the receipt and creates an idempotent field work item only for `APPROVE`.
7. Non-approved outcomes stop, refresh evidence or hand off to a human.

The local JSON work-order queue is the hackathon adapter. A production deployment would replace that small adapter with the coastal team's work-management or robotics dispatch API while keeping the same action boundary.

## AgentCore deployment path

The intended competition deployment is a **code-based Strands agent on Amazon Bedrock AgentCore Runtime**. `agentcore_app.py` supplies the runtime entrypoint; see [AGENTCORE.md](AGENTCORE.md) for the deployment runbook.

## Hackathon provenance

This repository is MIT licensed. See [DISCLOSURE.md](DISCLOSURE.md) for project provenance, AI-assistance disclosure and the boundary between synthetic and live data.

## Competition track

Professional Agents.
