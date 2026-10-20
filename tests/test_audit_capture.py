import json

from groundpatrol.hooks import PatrolAuditPlugin


def test_audit_extracts_structured_tool_results_only():
    nested = {'content': [{'text': json.dumps({'receipt_id': 'current-1', 'decision': 'APPROVE'})}]}
    assert PatrolAuditPlugin._documents(nested) == [{'receipt_id': 'current-1', 'decision': 'APPROVE'}]
    assert PatrolAuditPlugin._documents({'content': [{'text': 'The receipt is current-1'}]}) == []


def test_audit_keeps_run_scoped_receipt_ids():
    class Event:
        tool_use = {'name': 'request_action_clearance'}
        result = {'content': [{'text': json.dumps({'receipt_id': 'from-this-invocation'})}]}
        duration = 0.01

    first = PatrolAuditPlugin()
    second = PatrolAuditPlugin()
    first.after_tool(Event())
    assert first.receipt_ids == ['from-this-invocation']
    assert second.receipt_ids == []


def test_audit_does_not_treat_failed_dispatch_as_work_order():
    class Event:
        tool_use = {'name': 'dispatch_collection_work_order'}
        result = {'content': [{'text': json.dumps({'status': 'DISPATCH_REJECTED', 'work_order_id': 'old'})}]}
        duration = 0.01

    audit = PatrolAuditPlugin()
    audit.after_tool(Event())
    assert audit.work_orders == []
