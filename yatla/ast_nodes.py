from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class Type(Enum):
    String = 1
    Num = 2
    Any = 3

@dataclass(frozen=True)
class Constraint:
    identifier: str
    type: Type


class ASTNode:
    def eval(self, context):
        raise NotImplementedError

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        raise NotImplementedError


@dataclass
class IndentiferASTNode(ASTNode):
    value: str

    def eval(self, context):
        return context[self.value]

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        if type is None:
            return [Constraint(self.value, Type.Any)]
        else:
            return [Constraint(self.value, type)]


@dataclass
class NumberASTNode(ASTNode):
    value: int | float

    def eval(self, context):
        return self.value

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        return [None]


@dataclass
class ExpressionASTNode(ASTNode):
    value: NumberASTNode | IndentiferASTNode | BinOpASTNode

    def eval(self, context):
        return self.value.eval(context)

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        return self.value.get_parameters(type)


@dataclass
class BinOpASTNode(ASTNode):
    lhs: BinOpASTNode | NumberASTNode
    rhs: BinOpASTNode | NumberASTNode
    operator: Callable[[int, int], int]

    def eval(self, context):
        return self.operator(self.lhs.eval(context), self.rhs.eval(context))

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        all_parameters = []
        arguments = [self.lhs, self.rhs]
        parameter_types = [Type.Num, Type.Num]

        for parameter, required_type in zip(arguments, parameter_types):
            if val := parameter.get_parameters(required_type):
                all_parameters.extend(val)

        return all_parameters


@dataclass
class ExpressionBlockASTNode(ASTNode):
    value: IndentiferASTNode | BinOpASTNode

    def eval(self, context):
        return str(self.value.eval(context))

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        return self.value.get_parameters()


@dataclass
class TextASTNode(ASTNode):
    value: str

    def eval(self, context):
        return self.value

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        return [None]


@dataclass
class LineASTNode(ASTNode):
    content: list[TextASTNode | ExpressionBlockASTNode]

    def eval(self, context):
        return "".join(node.eval(context) for node in self.content)

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        all_params = []
        for node in self.content:
            if val := node.get_parameters():
                all_params.extend(val)
        return [p for p in all_params if p is not None]


@dataclass
class DocumentASTNode(ASTNode):
    lines: list[LineASTNode]

    def eval(self, context):
        return "\n".join(l.eval(context) for l in self.lines)

    def get_parameters(self, type: Type = None) -> list[Constraint]:
        params = []
        for line in self.lines:
            params.extend(line.get_parameters())
        return params
