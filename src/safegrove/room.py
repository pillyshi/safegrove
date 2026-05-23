"""Room model for safegrove."""


class Room:
    """A room whose visibility is derived from community relationships."""

    _VISIBILITIES = {"private", "public"}

    def __init__(self, community, participants, visibility="private"):
        if visibility not in self._VISIBILITIES:
            raise ValueError(f"Unknown visibility: {visibility!r}")
        self._community = community
        self._participants = frozenset(participants)
        self.visibility = visibility

    @property
    def participants(self):
        """Return the room participants."""
        return self._participants

    def can_see(self, user):
        """Return whether user can see this room."""
        self._community._require_person(user)
        if self.visibility == "public":
            return True
        return all(
            not self._community.dislikes(participant, user)
            for participant in self._participants
        )
