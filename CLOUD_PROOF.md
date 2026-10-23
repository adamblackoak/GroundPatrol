# GroundPatrol AgentCore cloud proof

GroundPatrol has been deployed and invoked successfully on **Amazon Bedrock AgentCore Runtime** in `eu-west-2`.

## Proven cloud path

A remote AgentCore invocation completed the full governed collection path:

`OBSERVE -> PROPOSE -> APPROVE -> RECEIPT -> VERIFIED -> QUEUED_FOR_COLLECTION`

The successful run preserved the operator's requested autonomous execution mode. The model proposed `collect_debris` with `autonomous=true`; the deterministic PatrolGate returned `APPROVE`; the finalizer verified the decision/action pairing; and the dispatch boundary created an idempotent `QUEUED_FOR_COLLECTION` work order.

The deployed runtime uses:

- Strands Agents for the agent/tool loop
- Amazon Bedrock for model inference
- Amazon Bedrock AgentCore Runtime for cloud execution
- deterministic Python controls for action authority
- content-addressed snapshots and SHA-256 decision receipts
- an approval-gated work-order dispatch boundary

## Remote invocation

From the AgentCore project directory, the deployed agent can be invoked with:

```powershell
agentcore invoke `
  --runtime GroundPatrolAgent `
  --prompt "Patrol west-bay-01. Assess the debris situation and decide whether an autonomous collection pass may proceed. Preserve the requested autonomous execution mode."
```

Expected successful outcome under the deterministic clear fixture:

- observed debris evidence and operating conditions
- proposed autonomous `collect_debris` pass
- gate: `APPROVE`
- next action: `execute`
- receipt ID issued
- work order: `QUEUED_FOR_COLLECTION`

## Failure behaviour observed during deployment hardening

Two cloud integration faults were encountered and corrected before the successful run:

1. The packaged runtime initially could not persist receipt/work-order files in the application directory. GroundPatrol failed closed and refused to imply authorization without a receipt. Runtime state now falls back to a writable state root.
2. The model initially coined an unsupported autonomous-action label. The deterministic gate denied it as `action_not_allowlisted`. The tool schema now constrains action names, with autonomy represented separately by the `autonomous` boolean.

These failures are useful evidence of the core design claim: implementation faults did not turn into accidental execution authority.

## Demo recommendation

Use the Streamlit UI for the visually legible two-scenario demo, and show a short terminal clip or screenshot of the successful AgentCore invocation to prove that the same governed path runs remotely on AWS.
