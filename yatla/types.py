from enum import Enum


class SlotType(Enum):
    """
    An enumeration of all supported parameter types by the templating engine.
    """
    String = 1
    Num = 2
    Any = 3
    StringArray = 4
    NumArray = 5
    AnyArray = 6
