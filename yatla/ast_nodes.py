from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import operator
from typing import Any, Callable, Optional

from yatla.validation import Constraint, Type, convert_to_shared_subtype


class BuiltinFunctionType(Enum):
    # Arithmetic
    ADD = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4


FUNCTION_LOOKUP: dict[str, Callable[[Any, Any], Any]] = {
    BuiltinFunctionType.ADD: operator.__add__,
    BuiltinFunctionType.SUBTRACT: operator.__sub__,
    BuiltinFunctionType.MULTIPLY: operator.__mul__,
    BuiltinFunctionType.DIVIDE: operator.__truediv__,
}


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
    operator_type: BuiltinFunctionType

    def eval(self, context):
        function = FUNCTION_LOOKUP[self.operator_type]
        return function(self.lhs.eval(context), self.rhs.eval(context))

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
class ForEachBlockASTNode(ASTNode):
    iterand: str
    iterator: str
    body: list[LineASTNode]

    def eval(self, context):
        iterator = context[self.iterator]
        output = []
        for value in iterator:
            context_with_iterator = context | {self.iterand: value}
            output.append("\n".join(l.eval(context_with_iterator) for l in self.body))
        return "\n".join(output)

    def get_parameters(self, type: Type = None) -> list[Optional[Constraint]]:
        body_params: list[Constraint] = []
        for node in self.body:
            if val := node.get_parameters():
                body_params.extend(val)

        iterand_types = [p.type for p in body_params if p.identifier == self.iterand]

        iterand_type = None
        if len(iterand_types) == 1:
            iterand_type = iterand_types[0]
        elif set(iterand_types) == set([Type.Any, Type.Num]):
            iterand_type = Type.Num
        else:
            raise ValueError("Using array of mixed type")

        iterator_type = None
        if iterand_type == Type.Num:
            iterator_type = Type.NumArray
        elif iterand_type == Type.Any:
            iterator_type = Type.AnyArray
        else:
            raise ValueError("Created array with invalid type of iterator")

        body_params = [p for p in body_params if p.identifier != self.iterand]
        body_params.append(Constraint(self.iterator, iterator_type))
        return body_params


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
