from yatla._parser import parse
from yatla.ast_nodes import (
    BinOpASTNode,
    BuiltinFunctionType,
    DocumentASTNode,
    ExpressionBlockASTNode,
    ForEachBlockASTNode,
    IndentiferASTNode,
    LineASTNode,
    TextASTNode,
)
from yatla.lexer import Scanner


def test_foreach_parsing():
    template = (
        "This is the {{ factor }} times table:\n"
        "{{ foreach num in num_list }}\n"
        "{{ factor }} * {{ num }} = {{ factor * num }}\n"
        "{{ endforeach }}"
    )  # fmt: skip

    ast = parse(Scanner(template))

    expected = DocumentASTNode(
        lines=[
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


def test_foreach_with_endforeach_being_last_token_in_file():
    template = (
        "{{ foreach x in y }}\n"
        "x\n" 
        "{{ endforeach }}"
    )  # fmt: skip

    ast = parse(Scanner(template))

    expected = DocumentASTNode(
        lines=[
            LineASTNode(
                content=[
                    ForEachBlockASTNode(
                        iterand="x",
                        iterator="y",
                        body=[LineASTNode(content=[TextASTNode(value="x")])],
                    )
                ]
            )
        ]
    )

    assert ast == expected
