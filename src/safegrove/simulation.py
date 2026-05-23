"""Simulation API for safegrove."""

import random


class Simulation:
    """Run simulations against a community model."""

    _POLICIES = {"auto", "private", "public"}

    def __init__(self, community):
        self.community = community

    def run(self, steps, room_size, private_room_policy="auto", seed=None):
        """Run a random private-room simulation."""
        if steps < 0:
            raise ValueError("steps must be non-negative")
        if room_size < 1:
            raise ValueError("room_size must be at least 1")
        if private_room_policy not in self._POLICIES:
            raise ValueError(f"Unknown private_room_policy: {private_room_policy!r}")
        people = sorted(self.community.people, key=repr)
        if steps > 0 and not people:
            raise ValueError("simulation requires at least one person")
        if room_size > len(people) and steps > 0:
            raise ValueError("room_size cannot exceed community size")

        rng = random.Random(seed)
        visible_counts = {person: 0 for person in people}
        hidden_counts = {person: 0 for person in people}
        unwanted_encounter_count = 0
        private_room_count = 0
        public_room_count = 0

        for _ in range(steps):
            participants = rng.sample(people, room_size)
            visibility = self._visibility_for_policy(private_room_policy, participants)
            if visibility == "private":
                private_room_count += 1
            else:
                public_room_count += 1
            room = self.community.create_room(participants, visibility=visibility)
            if visibility == "public":
                unwanted_encounter_count += self._unwanted_encounters(participants)
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
            unwanted_encounter_count=unwanted_encounter_count,
            private_room_count=private_room_count,
            public_room_count=public_room_count,
        )

    def _visibility_for_policy(self, private_room_policy, participants):
        if private_room_policy == "public":
            return "public"
        if private_room_policy == "auto" and not self._has_conflict(participants):
            return "public"
        return "private"

    def _has_conflict(self, participants):
        return self._unwanted_encounters(participants) > 0

    def _unwanted_encounters(self, participants):
        return sum(
            1
            for source in participants
            for target in participants
            if source != target and self.community.dislikes(source, target)
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
        unwanted_encounter_count,
        private_room_count,
        public_room_count,
    ):
        self.community = community
        self.steps = steps
        self.room_size = room_size
        self.private_room_policy = private_room_policy
        self.seed = seed
        self.visible_counts = dict(visible_counts)
        self.hidden_counts = dict(hidden_counts)
        self._unwanted_encounter_count = unwanted_encounter_count
        self.private_room_count = private_room_count
        self.public_room_count = public_room_count

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
        """Return the directed unwanted encounter count."""
        return self._unwanted_encounter_count
