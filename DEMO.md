# GroundPatrol judge demo

The cleanest demo is deliberately small: run the same collection objective under two externally selected operating states in the operator UI.

## Start the UI

```powershell
pip install -e ".[ui]"
streamlit run operator_ui.py
```

Keep **Evidence mode** on `Deterministic fixture` so both runs are reproducible.

## Scenario A: clear operating envelope

Select **Clear operating envelope** and run the default patrol objective.

Expected decision path:

`observe -> propose -> APPROVE -> finalizer VERIFIED -> work order QUEUED_FOR_COLLECTION`

Point out the three UI columns: agent outcome, decision receipt, work order. The side-effect adapter independently verifies the approved receipt. Calling it twice with the same receipt produces the same work-order ID rather than duplicate work.

## Scenario B: person enters operating envelope

Change only **Operating state** to **Person enters operating envelope** and run again.

Expected decision path:

`observe -> same proposal class -> DEFER -> human_review/stop -> no new work order`

Even a direct attempt to call the dispatch boundary with the DEFER receipt is rejected.

## What to show on video

Aim for roughly two minutes of actual product demonstration. Show:

1. the patrol objective and externally selected operating state
2. `snapshot_id`
3. gate decision and concise reason
4. SHA-256 receipt ID
5. finalizer status
6. work-order ID on the clear run
7. refusal to dispatch on the changed-world run

Then spend the remaining pitch time on the problem, user and architecture rather than adding more scenarios.

The visible product claim is not "the model is clever". It is that changing runtime conditions change what the system is allowed to do, and that the action boundary enforces the decision rather than merely logging it.
