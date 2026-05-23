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
