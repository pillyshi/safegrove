"""Community model for safegrove."""

from .room import Room


class Community:
    """A community of people and their directed relationship graph."""

    def __init__(self):
        self._people = set()
        self._dislikes = {}

    @property
    def people(self):
        """Return the people currently registered in the community."""
        return frozenset(self._people)

    def add_person(self, person):
        """Add one person to the community."""
        self._people.add(person)
        self._dislikes.setdefault(person, set())

    def add_people(self, people):
        """Add multiple people to the community."""
        for person in people:
            self.add_person(person)

    def dislike(self, source, target):
        """Record that source does not want to share rooms with target."""
        self._require_person(source)
        self._require_person(target)
        self._dislikes[source].add(target)

    def dislikes(self, source, target):
        """Return whether source dislikes target."""
        self._require_person(source)
        self._require_person(target)
        return target in self._dislikes[source]

    def create_room(self, participants, visibility="private"):
        """Create a room for registered participants."""
        participant_set = frozenset(participants)
        for participant in participant_set:
            self._require_person(participant)
        return Room(self, participant_set, visibility=visibility)

    def _require_person(self, person):
        if person not in self._people:
            raise ValueError(f"Unknown person: {person!r}")
