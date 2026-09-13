# Agents for Humans submission draft

## Project name

GroundPatrol

## Track

Professional Agents

## One-line pitch

GroundPatrol is a governed coastal-operations agent that turns live or simulated patrol evidence into an auditable collection decision and only dispatches work when deterministic runtime controls clear the action.

## Problem

Coastal teams do not just need another interface that describes debris. They need to turn incomplete, changing field observations into safe operational work. A collection that looked reasonable five minutes ago can become inappropriate when people enter the area, access closes, weather worsens, evidence goes stale or habitat constraints apply.

## Who it is for

Professional coastal operations teams, environmental contractors and local authorities coordinating shoreline inspection and debris collection.

## Why it matters

The hard part of agentic field operations is not generating a recommendation. It is controlling the boundary between recommendation and consequence. GroundPatrol keeps that boundary explicit: the model interprets and proposes, deterministic controls authorize, the finalizer checks consistency, and a tamper-evident receipt records what happened.

## Product experience

The operator UI exposes a patrol objective, evidence mode and operating state rather than presenting a bare chatbot. After each patrol it places the agent outcome, decision receipt and work-order state side by side, so an operator can see both what the agent recommends and what the governed runtime actually allowed.

## What it does end to end

1. A Strands agent receives a patrol objective.
2. `get_patrol_snapshot` observes the operating state and freezes it behind a content-addressed `snapshot_id`.
3. The agent proposes a bounded action.
4. `request_action_clearance` evaluates that exact snapshot against freshness, access, habitat, people-presence, weather and action limits.
5. The gate returns `APPROVE`, `CONDITIONAL`, `DEFER` or `DENY` and writes a SHA-256 decision receipt.
6. `finalize_patrol_decision` rejects any mismatch between the recorded decision and the agent's proposed next step.
7. Only an approved, verified collection can reach `dispatch_collection_work_order`, which independently re-checks the receipt and creates one idempotent work item.
8. All other outcomes refresh evidence, stop safely or hand off to a human.

## Technical implementation

- Strands Agents SDK for the agentic loop and tool use
- Streamlit operator UI for a coherent professional workflow
- Strands before/after tool hooks for execution tracing
- deterministic Python PatrolGate for runtime authority
- content-addressed immutable snapshot binding
- tamper-evident SHA-256 decision receipts
- deterministic second-pass output/action evaluator
- idempotent approval-gated side-effect adapter
- deterministic fixture scenarios for repeatable judging
- optional Open-Meteo live wind and visibility observations
- Amazon Bedrock for model inference
- Amazon Bedrock AgentCore Runtime for the deployed cloud agent
- automated tests in GitHub Actions

## Cloud proof

GroundPatrol has been deployed and invoked successfully on Amazon Bedrock AgentCore Runtime in `eu-west-2`. A remote invocation completed the full governed path:

`OBSERVE -> PROPOSE -> APPROVE -> RECEIPT -> VERIFIED -> QUEUED_FOR_COLLECTION`

The cloud run preserved the requested autonomous execution mode, used the constrained `collect_debris` action contract, passed the deterministic gate, issued a receipt and created an idempotent work order. See `CLOUD_PROOF.md` for the reproducible invocation and deployment-hardening notes.

## Demo narrative

### Scene 1: the happy path

Select the clear operating envelope in the UI and run the patrol. Show:

- observed state + `snapshot_id`
- autonomous collection proposal
- gate returns `APPROVE`
- receipt ID
- finalizer returns `VERIFIED`
- one `QUEUED_FOR_COLLECTION` work order appears

### Scene 2: the same intent, changed world

Change only the operating state to `people_nearby` and repeat the request. Show:

- new observed state
- same class of autonomous collection proposal
- gate returns `DEFER`
- finalizer will not permit `execute`
- no collection work order is created
- agent hands off or stops

The contrast is the product: changing runtime conditions reduce autonomy instead of being buried in model prose.

### Scene 3: cloud proof

Finish with a short terminal clip or screenshot showing `agentcore invoke` against `GroundPatrolAgent`, with the remote result reporting `APPROVE`, a receipt ID and a `QUEUED_FOR_COLLECTION` work order. This proves that the governed path is not only a localhost demo.

## Architecture diagram

See `docs/architecture.md`.

## Repository / licensing

MIT licensed. See `DISCLOSURE.md` for provenance and data-source disclosure.

## Final submission checklist

- [x] New Strands Agents implementation
- [x] Operator-facing product UI
- [x] README with install/run instructions
- [x] Architecture diagram
- [x] MIT license
- [x] Automated tests / CI
- [x] Demo script and reproducible scenarios
- [x] AgentCore Runtime application wrapper
- [x] Configure AWS credentials / Bedrock model access
- [x] Deploy to AgentCore Runtime
- [x] Successful remote AgentCore invocation with approved work-order dispatch
- [ ] Make repository public for judging
- [ ] Add repository About description and confirm GitHub detects MIT license
- [ ] Record <=5 minute demo + pitch video
- [ ] Supply AWS Builder ID
- [ ] Create Devpost submission draft and paste final text
- [ ] Optional: publish builder.aws build post before deadline
