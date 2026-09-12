# Operator UI result binding

The operator UI deliberately displays only the receipt/work-order pair produced by the current browser session. Historical receipts remain on disk for audit, but are not silently surfaced as though they belong to the currently selected controls.

If the operator changes evidence mode or operating state after a run, the UI labels the displayed result as stale relative to the current controls until a new patrol is executed.
