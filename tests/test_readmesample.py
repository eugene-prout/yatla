from yatla.ast_nodes import (
    BinOpASTNode,
    BuiltinFunctionType,
    DocumentASTNode,
    ExpressionASTNode,
    ExpressionBlockASTNode,
    ForEachBlockASTNode,
    IndentiferASTNode,
    LineASTNode,
    NumberASTNode,
    TextASTNode,
)
from yatla.lexer import Scanner
from yatla.parser import parse_from_scanner
from yatla.types import SlotType
from yatla.validation import Constraint, compute_parameters


def test_parsing():
    template = (
        "This is the starter template.\n"
        "\n"
        "This line contains a {{ slot }}.\n"
        "\n"
        "Slots can also contain mathematical expressions: {{ 3 + factor * 7 }}.\n"
        "With full support for operator precedence: {{ (3 + factor) * 7 }}.\n"
        "\n"
        "Foreach loops are also valid. For example:\n"
        "\n"
        "This is the {{ factor }} times table:\n"
        "{{ foreach num in num_list }}\n"
        "    {{ factor }} * {{ num }} = {{ factor * num }}\n"
        "{{ endforeach }}"
    )  # fmt: skip

    ast = parse_from_scanner(Scanner(template))

    expected = DocumentASTNode(
        lines=[
            LineASTNode(content=[TextASTNode(value="This is the starter template.")]),
            LineASTNode(content=[]),
            LineASTNode(
                content=[
                    TextASTNode(value="This line contains a "),
                    ExpressionBlockASTNode(value=IndentiferASTNode(value="slot")),
                    TextASTNode(value="."),
                ]
            ),
            LineASTNode(content=[]),
            LineASTNode(
                content=[
                    TextASTNode(
                        value="Slots can also contain mathematical expressions: "
                    ),
                    ExpressionBlockASTNode(
                        value=BinOpASTNode(
                            lhs=NumberASTNode(value=3),
                            rhs=BinOpASTNode(
                                lhs=IndentiferASTNode(value="factor"),
                                rhs=NumberASTNode(value=7),
                                operator_type=BuiltinFunctionType.MULTIPLY,
                            ),
                            operator_type=BuiltinFunctionType.ADD,
                        )
                    ),
                    TextASTNode(value="."),
                ]
            ),
            LineASTNode(
                content=[
                    TextASTNode(value="With full support for operator precedence: "),
                    ExpressionBlockASTNode(
                        value=BinOpASTNode(
                            lhs=ExpressionASTNode(
                                value=BinOpASTNode(
                                    lhs=NumberASTNode(value=3),
                                    rhs=IndentiferASTNode(value="factor"),
                                    operator_type=BuiltinFunctionType.ADD,
                                )
                            ),
                            rhs=NumberASTNode(value=7),
                            operator_type=BuiltinFunctionType.MULTIPLY,
                        )
                    ),
                    TextASTNode(value="."),
                ]
            ),
            LineASTNode(content=[]),
            LineASTNode(
                content=[
                    TextASTNode(value="Foreach loops are also valid. For example:")
                ]
            ),
            LineASTNode(content=[]),
            LineASTNode(
                content=[
                    TextASTNode(value="This is the "),
                    ExpressionBlockASTNode(value=IndentiferASTNode(value="factor")),
                    TextASTNode(value=" times table:"),
                ]
            ),
            LineASTNode(
                content=[
                    ForEachBlockASTNode(
                        iterand="num",
                        iterator="num_list",
                        body=[
                            LineASTNode(
                                content=[
                                    TextASTNode(value="    "),
                                    ExpressionBlockASTNode(
                                        value=IndentiferASTNode(value="factor")
                                    ),
                                    TextASTNode(value=" * "),
                                    ExpressionBlockASTNode(
                                        value=IndentiferASTNode(value="num")
                                    ),
                                    TextASTNode(value=" = "),
                                    ExpressionBlockASTNode(
                                        value=BinOpASTNode(
                                            lhs=IndentiferASTNode(value="factor"),
                                            rhs=IndentiferASTNode(value="num"),
                                            operator_type=BuiltinFunctionType.MULTIPLY,
                                        )
                                    ),
                                ]
                            )
                        ],
                    )
                ]
            ),
        ]
    )

    assert ast == expected


def test_typing():
    template = (
        "This is the starter template.\n"
        "\n"
        "This line contains a {{ slot }}.\n"
        "\n"
        "Slots can also contain mathematical expressions: {{ 3 + factor * 7 }}.\n"
        "With full support for operator precedence: {{ (3 + factor) * 7 }}.\n"
        "\n"
        "Foreach loops are also valid. For example:\n"
        "\n"
        "This is the {{ factor }} times table:\n"
        "{{ foreach num in num_list }}\n"
        "    {{ factor }} * {{ num }} = {{ factor * num }}\n"
        "{{ endforeach }}"
    )  # fmt: skip

    ast = parse_from_scanner(Scanner(template))

    slots = ast.get_parameters()

    expected = [
        Constraint(identifier="factor", type=SlotType.Num),
        Constraint(identifier="num_list", type=SlotType.NumArray),
        Constraint(identifier="slot", type=SlotType.Any),
    ]

    assert slots == expected


def test_eval():
    template = (
        "This is the starter template.\n"
        "\n"
        "This line contains a {{ slot }}.\n"
        "\n"
        "Slots can also contain mathematical expressions: {{ 3 + factor * 7 }}.\n"
        "With full support for operator precedence: {{ (3 + factor) * 7 }}.\n"
        "\n"
        "Foreach loops are also valid. For example:\n"
        "\n"
        "This is the {{ factor }} times table:\n"
        "{{ foreach num in num_list }}\n"
        "    {{ factor }} * {{ num }} = {{ factor * num }}\n"
        "{{ endforeach }}"
    )  # fmt: skip

    ast = parse_from_scanner(Scanner(template))

    context = {"slot": "filled slot", "factor": 2, "num_list": [1, 2, 3, 4, 5]}

    evaluated_template = ast.eval(context)

    expected = (
        "This is the starter template.\n"
        "\n"
        "This line contains a filled slot.\n"
        "\n"
        "Slots can also contain mathematical expressions: 17.\n"
        "With full support for operator precedence: 35.\n"
        "\n"
        "Foreach loops are also valid. For example:\n"
        "\n"
        "This is the 2 times table:\n"
        "    2 * 1 = 2\n"
        "    2 * 2 = 4\n"
        "    2 * 3 = 6\n"
        "    2 * 4 = 8\n"
        "    2 * 5 = 10"
    )  # fmt: skip

    assert evaluated_template == expected
