# Hackathon provenance and disclosure

GroundPatrol is a new implementation created during the Agents for Humans submission period.

## Pre-existing material

The author had explored the **GroundPatrol** problem concept before this repository was created, and had separately developed general architectural ideas around evidence provenance, deterministic runtime action gates, bounded authority and decision receipts.

No pre-existing GroundPatrol application code was incorporated into this repository. The submitted Strands agent, patrol models, action gate, snapshot binding, evaluator, feeds, receipt implementation, tests, AgentCore wrapper and demo materials were written anew for this hackathon.

## Development tools

Standard development tools, open-source libraries, documentation and AI coding assistance were used during implementation. The core agent uses the Strands Agents SDK. The optional live-weather path uses the public Open-Meteo API.

## Synthetic data

The reproducible judging scenarios use clearly labelled synthetic fixture data for debris, access, habitat and people-presence observations. Optional live mode replaces only weather observations with live Open-Meteo data. The project does not present synthetic operational observations as real sensor data.
