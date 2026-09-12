from __future__ import annotations

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from groundpatrol.agent import build_agent


app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict):
    """AgentCore Runtime entrypoint for GroundPatrol."""
    prompt = payload.get(
        "prompt",
        "Patrol west-bay-01 and decide whether an autonomous debris collection pass may proceed.",
    )
    result = build_agent()(prompt)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
