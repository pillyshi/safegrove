import pytest

import safegrove as sg


def test_adds_people_individually_and_in_batches():
    community = sg.Community()

    community.add_person("A")
    community.add_people(["B", "C"])

    assert community.people == frozenset({"A", "B", "C"})


def test_records_directed_dislike_relationships():
    community = sg.Community()
    community.add_people(["A", "B"])

    community.dislike("A", "B")

    assert community.dislikes("A", "B") is True
    assert community.dislikes("B", "A") is False


def test_dislike_requires_registered_people():
    community = sg.Community()
    community.add_person("A")

    with pytest.raises(ValueError, match="Unknown person"):
        community.dislike("A", "B")

    with pytest.raises(ValueError, match="Unknown person"):
        community.dislike("B", "A")


def test_records_directed_like_relationships():
    community = sg.Community()
    community.add_people(["A", "B"])

    community.like("A", "B")

    assert community.likes("A", "B") is True
    assert community.likes("B", "A") is False


def test_like_requires_registered_people():
    community = sg.Community()
    community.add_person("A")

    with pytest.raises(ValueError, match="Unknown person"):
        community.like("A", "B")

    with pytest.raises(ValueError, match="Unknown person"):
        community.like("B", "A")


def test_bridge_load_counts_conflicts_among_liked_people():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    community.like("C", "A")
    community.like("C", "B")

    assert community.bridge_load("C") == 1


def test_bridge_load_is_zero_without_bridged_conflicts():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.like("C", "A")
    community.like("C", "B")

    assert community.bridge_load("C") == 0
    assert community.bridge_load("A") == 0


def test_bridge_load_counts_directed_conflict_edges():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    community.dislike("B", "A")
    community.like("C", "A")
    community.like("C", "B")

    assert community.bridge_load("C") == 2


def test_bridge_load_requires_registered_person():
    community = sg.Community()

    with pytest.raises(ValueError, match="Unknown person"):
        community.bridge_load("C")
