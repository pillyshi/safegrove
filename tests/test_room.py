import pytest

import safegrove as sg


def test_private_room_visibility_follows_readme_basic_usage():
    community = sg.Community()
    community.add_people(["A", "B", "C", "D"])
    community.dislike("A", "B")

    room = community.create_room(["A", "C"])

    assert room.can_see("A") is True
    assert room.can_see("C") is True
    assert room.can_see("B") is False
    assert room.can_see("D") is True


def test_create_room_requires_registered_participants():
    community = sg.Community()
    community.add_person("A")

    with pytest.raises(ValueError, match="Unknown person"):
        community.create_room(["A", "B"])


def test_can_see_requires_registered_user():
    community = sg.Community()
    community.add_person("A")
    room = community.create_room(["A"])

    with pytest.raises(ValueError, match="Unknown person"):
        room.can_see("B")


def test_public_room_is_visible_without_private_safety_filtering():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")

    room = community.create_room(["A"], visibility="public")

    assert room.can_see("B") is True


def test_rejects_unknown_room_visibility():
    community = sg.Community()
    community.add_person("A")

    with pytest.raises(ValueError, match="Unknown visibility"):
        community.create_room(["A"], visibility="hidden")


def test_can_join_uses_the_same_policy_as_can_see():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    room = community.create_room(["A", "C"])

    assert room.can_join("C") is True
    assert room.can_join("B") is False


def test_participant_cannot_invite_user_blocked_by_room_policy():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    room = community.create_room(["A", "C"])

    assert room.can_invite("C", "B") is False


def test_participant_can_invite_user_allowed_by_room_policy():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    room = community.create_room(["A"])

    assert room.can_invite("A", "B") is True
    assert room.can_invite("A", "C") is True


def test_non_participant_cannot_invite_into_room():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    room = community.create_room(["A"])

    assert room.can_invite("B", "C") is False


def test_invite_requires_registered_people():
    community = sg.Community()
    community.add_person("A")
    room = community.create_room(["A"])

    with pytest.raises(ValueError, match="Unknown person"):
        room.can_invite("A", "B")

    with pytest.raises(ValueError, match="Unknown person"):
        room.can_invite("B", "A")


def test_suggest_room_returns_private_room_for_requested_participants():
    community = sg.Community()
    community.add_people(["B", "C"])

    room = community.suggest_room(["C", "B"])

    assert room.participants == frozenset({"B", "C"})
    assert room.visibility == "private"


def test_suggested_room_uses_normal_private_visibility_rules():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("C", "A")

    room = community.suggest_room(["C", "B"])

    assert room.can_see("B") is True
    assert room.can_see("A") is False


def test_suggest_room_requires_registered_participants():
    community = sg.Community()
    community.add_person("C")

    with pytest.raises(ValueError, match="Unknown person"):
        community.suggest_room(["C", "B"])
