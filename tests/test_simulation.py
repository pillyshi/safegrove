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

    assert result.isolation_score("B") >= 0
    assert result.bridge_load("C") == 1000
    assert community.bridge_load("C") == 1
    assert result.unwanted_encounters() == 0


def test_simulation_result_records_run_parameters():
    community = sg.Community()
    community.add_people(["A", "B"])
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

    with pytest.raises(ValueError, match="private_room_policy"):
        sim.run(steps=1, room_size=1, private_room_policy="hidden")


def test_simulation_rejects_impossible_room_sampling():
    community = sg.Community()
    sim = sg.Simulation(community)

    with pytest.raises(ValueError, match="at least one person"):
        sim.run(steps=1, room_size=1)

    community.add_person("A")

    with pytest.raises(ValueError, match="community size"):
        sim.run(steps=1, room_size=2)


def test_isolation_score_requires_registered_user():
    community = sg.Community()
    sim = sg.Simulation(community)
    result = sim.run(steps=0, room_size=1)

    with pytest.raises(ValueError, match="Unknown person"):
        result.isolation_score("A")


def test_random_private_room_simulation_is_repeatable_with_seed():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    first = sim.run(steps=20, room_size=2, seed=7)
    second = sim.run(steps=20, room_size=2, seed=7)

    assert first.visible_counts == second.visible_counts
    assert first.hidden_counts == second.hidden_counts
    assert first.isolation_score("B") == second.isolation_score("B")


def test_isolation_score_tracks_hidden_private_rooms():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=30, room_size=1, private_room_policy="private", seed=3)

    assert result.hidden_counts["B"] > 0
    assert result.hidden_counts["A"] == 0
    assert result.isolation_score("B") == result.hidden_counts["B"] / 30
    assert result.isolation_score("B") > result.isolation_score("A")


def test_zero_step_simulation_has_zero_isolation_score():
    community = sg.Community()
    community.add_person("A")
    sim = sg.Simulation(community)

    result = sim.run(steps=0, room_size=1)

    assert result.visible_counts == {"A": 0}
    assert result.hidden_counts == {"A": 0}
    assert result.isolation_score("A") == 0


def test_public_room_simulation_counts_directed_unwanted_encounters():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="public", seed=1)

    assert result.unwanted_encounters() == 5


def test_public_room_simulation_counts_mutual_dislikes_separately():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    community.dislike("B", "A")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="public", seed=1)

    assert result.unwanted_encounters() == 10


def test_private_room_simulation_does_not_count_public_unwanted_encounters():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="private", seed=1)

    assert result.unwanted_encounters() == 0


def test_auto_policy_uses_private_rooms_for_conflict_groups():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="auto", seed=1)

    assert result.private_room_count == 5
    assert result.public_room_count == 0
    assert result.unwanted_encounters() == 0


def test_auto_policy_uses_public_rooms_for_non_conflict_groups():
    community = sg.Community()
    community.add_people(["A", "B"])
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="auto", seed=1)

    assert result.private_room_count == 0
    assert result.public_room_count == 5
    assert result.unwanted_encounters() == 0


def test_auto_policy_reduces_public_unwanted_encounters_for_conflict_groups():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    public_result = sim.run(steps=5, room_size=2, private_room_policy="public", seed=1)
    auto_result = sim.run(steps=5, room_size=2, private_room_policy="auto", seed=1)

    assert public_result.unwanted_encounters() == 5
    assert auto_result.unwanted_encounters() == 0


def test_policy_room_counts_are_recorded_for_always_public_and_private():
    community = sg.Community()
    community.add_people(["A", "B"])
    sim = sg.Simulation(community)

    public_result = sim.run(steps=3, room_size=2, private_room_policy="public")
    private_result = sim.run(steps=3, room_size=2, private_room_policy="private")

    assert public_result.public_room_count == 3
    assert public_result.private_room_count == 0
    assert private_result.public_room_count == 0
    assert private_result.private_room_count == 3


def test_simulation_tracks_dynamic_bridge_load_over_time():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=3, private_room_policy="private", seed=1)

    assert result.bridge_load("C") == 5
    assert result.bridge_load("A") == 0
    assert result.bridge_load("B") == 0


def test_dynamic_bridge_load_counts_directed_conflicts_among_other_participants():
    community = sg.Community()
    community.add_people(["A", "B", "C"])
    community.dislike("A", "B")
    community.dislike("B", "A")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=3, private_room_policy="private", seed=1)

    assert result.bridge_load("C") == 10


def test_dynamic_bridge_load_is_zero_when_no_user_bridges_a_conflict():
    community = sg.Community()
    community.add_people(["A", "B"])
    community.dislike("A", "B")
    sim = sg.Simulation(community)

    result = sim.run(steps=5, room_size=2, private_room_policy="private", seed=1)

    assert result.bridge_load("A") == 0
    assert result.bridge_load("B") == 0
    assert community.bridge_load("A") == 0
