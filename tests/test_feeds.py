from groundpatrol.feeds import FixtureFeed


def test_fixture_people_nearby(monkeypatch):
    monkeypatch.setenv("GROUNDPATROL_SCENARIO", "people_nearby")
    snapshot = FixtureFeed().snapshot("west-bay-01")
    assert snapshot.people_nearby is True


def test_fixture_clear(monkeypatch):
    monkeypatch.setenv("GROUNDPATROL_SCENARIO", "clear")
    snapshot = FixtureFeed().snapshot("west-bay-01")
    assert snapshot.people_nearby is False
    assert snapshot.access_open is True
