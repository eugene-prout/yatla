from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from click import Parameter
from yatla.ast_nodes import Constraint, Type


@dataclass
class Parameter:
    identfier: str
    type: Type


def check_validity(constraints: list[Constraint]):
    return True


def make_unique(constraints: list[Constraint]):
    return list(dict.fromkeys(constraints))


def group_constraints_by_identifier(constraints: list[Constraint]):
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
            new_type = c
        else:
            if set(c) == set([Type.Any, Type.Num]):
                new_type = Type.Num

        new_constraints.append(Constraint(identifier, new_type))

    return new_constraints


def convert_constraint_to_parameter(constraint: Constraint):
    return Parameter(constraint.identifier, constraint.type)


def compute_parameters(constraints: list[Constraint]) -> list[Parameter]:
    constraints = make_unique(constraints)
    if not check_validity(constraints):
        raise ValueError("Invalid constraints")

    constraints = convert_to_shared_subtype(constraints)
    return [convert_constraint_to_parameter(c) for c in constraints]
