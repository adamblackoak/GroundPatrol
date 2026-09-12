from groundpatrol.evaluator import verify_output_contract


def test_approve_allows_execute():
    result = verify_output_contract(
        receipt_decision="APPROVE",
        claimed_decision="APPROVE",
        next_action="execute",
    )
    assert result.verified is True


def test_defer_blocks_execute():
    result = verify_output_contract(
        receipt_decision="DEFER",
        claimed_decision="DEFER",
        next_action="execute",
    )
    assert result.verified is False
    assert result.reason == "next_action_not_permitted_for_decision"


def test_claimed_decision_must_match_receipt():
    result = verify_output_contract(
        receipt_decision="DENY",
        claimed_decision="APPROVE",
        next_action="execute",
    )
    assert result.verified is False
    assert result.reason == "claimed_decision_mismatch"
