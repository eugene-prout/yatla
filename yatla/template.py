from dataclasses import dataclass
from typing import Iterable, List, Mapping
from yatla.ast_nodes import DocumentASTNode
from yatla.types import SlotType


@dataclass
class Slot:
    """
    Represents a slot in a template. Has a name which is derived from the placeholder in the template, and a type which is inferred from the
    use of the slot.
    """

    name: str
    type: SlotType


class Template:
    """
    Represents a parsed template. Can be filled using a mapping of slot names to values.
    """

    _ast: DocumentASTNode
    source: str
    slots: List[Slot]

    def __init__(self, _ast: DocumentASTNode, source: str, slots: List[Slot]):
        self._ast = _ast
        self.source = source
        self.slots = slots

    def fill(
        self,
        values: Mapping[
            str, int | float | str | Iterable[int] | Iterable[float] | Iterable[str]
        ],
    ) -> str:
        """
        Fill the slots in the template using the provided values.
        """
        return self._ast.eval(values)

    def __repr__(self) -> str:
        return f"Template(source='{self.source}', slots={self.slots})"
