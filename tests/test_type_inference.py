from yatla.lexer import Scanner
from yatla.parser import parse_from_scanner
from yatla.types import SlotType
from yatla.validation import Constraint


def test_multiple_slots_of_same_name():
    template = "{{ factor }} * 2 = {{ factor * 2 }}"
    parsed_template = parse_from_scanner(Scanner(template))
    parameters = parsed_template.get_parameters()

    assert parameters == [Constraint("factor", SlotType.Num)]
    