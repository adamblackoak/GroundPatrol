# GroundPatrol judge demo

The cleanest demo is deliberately small: run the same collection request under two externally selected operating states.

## Scenario A: clear operating envelope

```powershell
$env:GROUNDPATROL_FEED="fixture"
$env:GROUNDPATROL_SCENARIO="clear"
python main.py
```

Expected decision path:

`observe -> propose -> APPROVE -> finalizer VERIFIED -> work order QUEUED_FOR_COLLECTION`

The side-effect adapter independently verifies the approved receipt. Calling it twice with the same receipt produces the same work-order ID rather than duplicate work.

## Scenario B: person enters operating envelope

```powershell
$env:GROUNDPATROL_SCENARIO="people_nearby"
python main.py
```

Expected decision path:

`observe -> same proposal class -> DEFER -> human_review/stop -> no work order`

Even a direct attempt to call the dispatch boundary with the DEFER receipt is rejected.

## What to show on video

Keep the screen on the tool trace and final output. Show:

1. `snapshot_id`
2. gate decision and concise reason
3. SHA-256 receipt ID
4. finalizer status
5. work-order ID on the clear run
6. absence/rejection of dispatch on the changed-world run

The visible product claim is not "the model is clever". It is that changing runtime conditions change what the system is allowed to do, and that the action boundary enforces the decision rather than merely logging it.
