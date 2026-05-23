"""Simulation API for safegrove."""


class Simulation:
    """Run simulations against a community model."""

    def __init__(self, community):
        self.community = community

    def run(self, steps, room_size, private_room_policy="auto", seed=None):
        """Run a deterministic placeholder simulation."""
        if steps < 0:
            raise ValueError("steps must be non-negative")
        if room_size < 1:
            raise ValueError("room_size must be at least 1")
        return SimulationResult(
            self.community,
            steps=steps,
            room_size=room_size,
            private_room_policy=private_room_policy,
            seed=seed,
        )


class SimulationResult:
    """Result metrics from a simulation run."""

    def __init__(self, community, steps, room_size, private_room_policy, seed):
        self.community = community
        self.steps = steps
        self.room_size = room_size
        self.private_room_policy = private_room_policy
        self.seed = seed

    def isolation_score(self, user):
        """Return the current placeholder isolation score for a user."""
        self.community._require_person(user)
        return 0

    def bridge_load(self, user):
        """Return the bridge load metric from the underlying community."""
        return self.community.bridge_load(user)

    def unwanted_encounters(self):
        """Return the current placeholder unwanted encounter count."""
        return 0
