# GroundPatrol

**A governed coastal-operations agent for Agents for Humans.**

GroundPatrol helps coastal teams turn messy field observations into a bounded
operational decision. The model can interpret and propose; a deterministic runtime
gate decides whether the proposed physical action is actually cleared.

## Why this build

The interesting problem is not "can an LLM tell a drone to collect litter?"
It is whether an agent can remain useful when evidence is stale, people are nearby,
access is closed, habitat rules apply, or operating conditions degrade.

GroundPatrol therefore separates:

`OBSERVE -> PROPOSE -> AUTHORISE -> EXECUTE/ESCALATE -> RECEIPT`

The model is deliberately **not** the execution authority.

## Reliability spine

The current v0 implements:

- explicit evidence objects with timestamps
- bounded allowlisted actions
- deterministic operating-envelope checks
- discrete `APPROVE / CONDITIONAL / DEFER / DENY` outcomes
- human escalation for consequential ambiguity
- a Strands tool-call audit hook
- tamper-evident SHA-256 decision receipts
- unit tests for failure and degraded-state cases

This follows a simple doctrine: **model proposes; governed control decides; trace records.**

## Strands Agents

`groundpatrol/agent.py` is a real Strands agent. The system prompt requires the agent
to retrieve a patrol snapshot and pass any consequential proposal through
`request_action_clearance` before it can claim an action may proceed.

The hook in `groundpatrol/hooks.py` records tool activity. More sophisticated steering
can be added after the deterministic v0 behaviour is stable.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python main.py
```

Strands defaults to Amazon Bedrock, so configure AWS credentials and model access before
running the live agent.

## AgentCore deployment path

The intended competition deployment is a **code-based Strands agent on Amazon Bedrock
AgentCore Runtime**.

Current AWS documentation supports scaffolding with:

```bash
npm install -g @aws/agentcore
agentcore create \
  --project-name GroundPatrol \
  --name GroundPatrolAgent \
  --language Python \
  --framework Strands \
  --model-provider Bedrock \
  --memory none \
  --build CodeZip
```

Then transplant the GroundPatrol package into the generated project, run locally, and
deploy with `agentcore deploy`.

## Demo story

**Good conditions:** confirmed debris + open access + no protected habitat + clear
operating envelope -> autonomous collection receives `APPROVE` and a receipt.

**Changed conditions:** a person enters the operating envelope or evidence goes stale
-> the same proposed collection becomes `DEFER`; no physical action is implied and the
agent hands the decision to a human.

That visible transition is the demo: intelligence is useful, but consequence is gated.

## Next implementation slice

1. Replace demo conditions with live/mockable external feeds.
2. Add a second-pass evaluator that checks response/gate consistency rather than adding
   another free-running agent loop.
3. Add controlled steering for repeated tool failures and evidence refresh.
4. Deploy to AgentCore Runtime and record a two-scenario demo.
5. Add a tiny operator UI only if it improves judging legibility.

## Competition track

Professional Agents.
