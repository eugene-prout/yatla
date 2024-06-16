from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from yatla.types import SlotType


@dataclass(frozen=True)
class Constraint:
    identifier: str
    type: SlotType


def check_validity(constraints: list[Constraint]):
    return True


def make_unique(constraints: list[Constraint]):
    return list(dict.fromkeys(constraints))


def group_constraints_by_identifier(
    constraints: list[Constraint],
) -> dict[str, list[SlotType]]:
    sorted_constraints = sorted(constraints, key=attrgetter("identifier"))

    grouped_constraints = {}
    for identifier, group in groupby(sorted_constraints, key=attrgetter("identifier")):
        grouped_constraints[identifier] = [c.type for c in group]

    return grouped_constraints


def convert_to_shared_subtype(constraints: list[Constraint]):
    grouped = group_constraints_by_identifier(constraints)
    new_constraints = []
    for identifier, c in grouped.items():
        new_type = None
        if len(c) == 1:
            new_type = c[0]
        else:
            if set(c) == set([SlotType.Any, SlotType.Num]):
                new_type = SlotType.Num

        new_constraints.append(Constraint(identifier, new_type))

    return new_constraints


def compute_parameters(constraints: list[Constraint]) -> list[Constraint]:
    constraints = make_unique(constraints)
    if not check_validity(constraints):
        raise ValueError("Invalid constraints")

    constraints = convert_to_shared_subtype(constraints)
    return constraints
