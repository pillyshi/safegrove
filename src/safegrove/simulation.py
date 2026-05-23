"""Simulation API for safegrove."""

import random


class Simulation:
    """Run simulations against a community model."""

    def __init__(self, community):
        self.community = community

    def run(self, steps, room_size, private_room_policy="auto", seed=None):
        """Run a random private-room simulation."""
        if steps < 0:
            raise ValueError("steps must be non-negative")
        if room_size < 1:
            raise ValueError("room_size must be at least 1")
        people = sorted(self.community.people, key=repr)
        if steps > 0 and not people:
            raise ValueError("simulation requires at least one person")
        if room_size > len(people) and steps > 0:
            raise ValueError("room_size cannot exceed community size")

        rng = random.Random(seed)
        visible_counts = {person: 0 for person in people}
        hidden_counts = {person: 0 for person in people}

        for _ in range(steps):
            participants = rng.sample(people, room_size)
            room = self.community.create_room(participants, visibility="private")
            for person in people:
                if room.can_see(person):
                    visible_counts[person] += 1
                else:
                    hidden_counts[person] += 1

        return SimulationResult(
            self.community,
            steps=steps,
            room_size=room_size,
            private_room_policy=private_room_policy,
            seed=seed,
            visible_counts=visible_counts,
            hidden_counts=hidden_counts,
        )


class SimulationResult:
    """Result metrics from a simulation run."""

    def __init__(
        self,
        community,
        steps,
        room_size,
        private_room_policy,
        seed,
        visible_counts,
        hidden_counts,
    ):
        self.community = community
        self.steps = steps
        self.room_size = room_size
        self.private_room_policy = private_room_policy
        self.seed = seed
        self.visible_counts = dict(visible_counts)
        self.hidden_counts = dict(hidden_counts)

    def isolation_score(self, user):
        """Return hidden rooms divided by total simulated rooms for a user."""
        self.community._require_person(user)
        if self.steps == 0:
            return 0
        return self.hidden_counts[user] / self.steps

    def bridge_load(self, user):
        """Return the bridge load metric from the underlying community."""
        return self.community.bridge_load(user)

    def unwanted_encounters(self):
        """Return the current placeholder unwanted encounter count."""
        return 0
