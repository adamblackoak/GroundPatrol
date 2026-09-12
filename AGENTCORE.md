# AgentCore deployment notes

GroundPatrol includes `agentcore_app.py`, a minimal `BedrockAgentCoreApp` wrapper around the existing Strands agent.

## Local preparation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[deploy]"
python agentcore_app.py
```

The AgentCore Runtime SDK serves the entrypoint on the runtime-compatible HTTP interface.

## CLI route

Current Strands/AWS guidance recommends the AgentCore CLI for quick prototyping:

```powershell
npm install -g @aws/agentcore
agentcore create
```

Choose Python, Strands Agents and Bedrock. Integrate `groundpatrol/` plus `agentcore_app.py` into the generated project, then:

```powershell
agentcore dev
agentcore deploy
agentcore invoke
```

We deliberately do not commit guessed account, role, region or deployment-target configuration. Those files should be generated against the AWS account actually used for the competition.

## Runtime assumptions

- Bedrock model access is configured in the target AWS account.
- The default fixture mode requires no outbound network access.
- `GROUNDPATROL_FEED=live` requires outbound HTTPS to Open-Meteo.
- Runtime receipts are local ephemeral files in v0.2. A production version should move receipt custody to durable storage such as S3/DynamoDB or an equivalent evidence store.
