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


def test_template_evaluation():
    template = (
        "This is the {{ factor }} times table:\n"
        "{{ foreach num in num_list }}\n"
        "{{ factor }} * {{ num }} = {{ factor * num }}\n"
        "{{ endforeach }}"
    )
    print(template)

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