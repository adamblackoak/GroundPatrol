# GroundPatrol judge demo

The cleanest demo is deliberately small: run the same collection request under two external states.

## Scenario A: clear operating envelope

```powershell
$env:GROUNDPATROL_FEED="fixture"
$env:GROUNDPATROL_SCENARIO="clear"
python main.py
```

Expected decision path: observe -> propose -> `APPROVE` -> finalizer `VERIFIED` -> `execute`.

## Scenario B: person enters operating envelope

```powershell
$env:GROUNDPATROL_SCENARIO="people_nearby"
python main.py
```

Expected decision path: observe -> same proposal class -> `DEFER` -> finalizer rejects `execute` and permits `human_review`/`stop`.

## What to show on video

Show the `snapshot_id`, gate decision, reason, finalizer status and receipt id. The visible product claim is not "the model is clever". It is that consequence remains bounded when runtime conditions change.
