import pytest

import safegrove as sg


def test_top_level_package_exports_simulation():
    community = sg.Community()

    assert isinstance(sg.Simulation(community), sg.Simulation)


def test_readme_simulation_api_shape_can_be_called():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    community.like("C", "A")
    community.like("C", "B")

    sim = sg.Simulation(community)
    result = sim.run(steps=1000, room_size=3, private_room_policy="auto")

    assert result.isolation_score("B") == 0
    assert result.bridge_load("C") == 1
    assert result.unwanted_encounters() == 0


def test_simulation_result_records_run_parameters():
    community = sg.Community()
    sim = sg.Simulation(community)

    result = sim.run(steps=10, room_size=2, private_room_policy="private", seed=42)

    assert result.steps == 10
    assert result.room_size == 2
    assert result.private_room_policy == "private"
    assert result.seed == 42


def test_simulation_rejects_invalid_run_parameters():
    community = sg.Community()
    sim = sg.Simulation(community)

    with pytest.raises(ValueError, match="steps"):
        sim.run(steps=-1, room_size=2)

    with pytest.raises(ValueError, match="room_size"):
        sim.run(steps=1, room_size=0)


def test_isolation_score_requires_registered_user():
    community = sg.Community()
    sim = sg.Simulation(community)
    result = sim.run(steps=1, room_size=1)

    with pytest.raises(ValueError, match="Unknown person"):
        result.isolation_score("A")
