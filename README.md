# safegrove

A Python library for modeling safe social spaces with directed affinity graphs.

`safegrove` helps simulate communities where people can like or dislike others, and where room visibility is derived from those directed relationships.

The core idea is simple:

> A room should be visible only to people who are acceptable to all current participants.

This makes it possible to protect people from unwanted social encounters without removing others from the community entirely.

## Concept

A community is represented as a directed graph.

- Nodes are people.
- Edges are relationships.
- A directed `dislike` edge means the source user does not want to share a room with the target user.

For example:

```python
A dislikes B
```

means:

```python
A -> B = dislike
```

If A and C are in a private room, B should not be able to see or join that room.

## Installation

```bash
pip install safegrove
```

## Basic Usage

```python
import safegrove as sg

community = sg.Community()

community.add_people(["A", "B", "C", "D"])

community.dislike("A", "B")

room = community.create_room(["A", "C"])

room.can_see("A")  # True
room.can_see("C")  # True
room.can_see("B")  # False
room.can_see("D")  # True
```

## Visibility Rule

A user can see a room if no participant in that room dislikes them.

Formally:

```text
x can see room R iff
  for every participant p in R:
    p does not dislike x
```

## Public and Private Rooms

`safegrove` distinguishes between public and private rooms.

```python
public_room = community.create_room(["A", "C"], visibility="public")
private_room = community.create_room(["A", "C"], visibility="private")
```

Public rooms are the default shared space of a community.

Private rooms apply safety constraints based on the directed dislike graph.

## Shareability

Room visibility, joinability, and shareability should follow the same safety policy.

If B cannot see a room, participants should not be able to invite B into that room.

```python
room.can_invite("C", "B")  # False
```

Instead, the system can suggest creating a separate room.

```python
community.suggest_room(["C", "B"])
```

## Bridge Load

`safegrove` can estimate the social load placed on neutral bridge users.

A bridge user is someone who is connected to multiple people who cannot safely share the same room.

For example:

```text
A dislikes B
C likes A
C likes B
```

C is bridging a conflict between A and B.

```python
community.bridge_load("C")
```

This can be used to detect users who may be forced into social coordination roles too often.

## Simulation

`safegrove` is designed for simulation.

Possible simulations include:

- How often users become isolated
- How often bridge users are placed under social load
- How room visibility changes as dislike edges increase
- Whether protected rooms reduce unwanted encounters
- How community structure changes over time

Example:

```python
sim = sg.Simulation(community)

result = sim.run(
    steps=1000,
    room_size=3,
    private_room_policy="auto"
)

result.isolation_score("B")
result.bridge_load("C")
result.unwanted_encounters()
```

## Design Goals

`safegrove` is not a blocklist library.

It is a model for safe shared spaces.

The goals are:

- Protect users from unwanted encounters
- Preserve public community spaces where possible
- Avoid forcing neutral users to manually manage conflicts
- Make social friction measurable
- Support simulations of community dynamics

## Status

Experimental.

The API is expected to change while the core model is refined.

## License

MIT

