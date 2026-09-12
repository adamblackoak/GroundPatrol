from groundpatrol.agent import SYSTEM_PROMPT


def test_autonomous_request_cannot_be_silently_downgraded_to_manual():
    assert "autonomous=true" in SYSTEM_PROMPT
    assert "Do not silently" in SYSTEM_PROMPT
    assert "manual" in SYSTEM_PROMPT
