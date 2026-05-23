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
