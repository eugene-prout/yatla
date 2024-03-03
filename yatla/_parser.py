from __future__ import annotations
import operator
from yatla.ast_nodes import (
    BinOpASTNode,
    DocumentASTNode,
    ExpressionASTNode,
    ExpressionBlockASTNode,
    IndentiferASTNode,
    LineASTNode,
    NumberASTNode,
    TextASTNode,
)


from yatla.lexer import Token, TokenType, Scanner


class TokenSource:
    def __init__(self, lexer: Scanner):
        self.token_buffer: list[Token] = []
        self.lexer = lexer
        self.token_gen = lexer.scan()

    def get_next_token(self):
        if self.token_buffer:
            return self.token_buffer.pop(0)
        else:
            return next(self.token_gen)

    def push_back_token(self, token):
        self.token_buffer.append(token)


class Parser:
    def __init__(self, t: TokenSource) -> None:
        self.tokens = t
        self.current_token = t.get_next_token()

    def advance(self):
        self.current_token = self.tokens.get_next_token()

    def parse_identifier(self) -> IndentiferASTNode:
        self.assert_current_token_in_set([TokenType.STRING])
        print(self.current_token)
        value = self.current_token.literal
        self.advance()
        return IndentiferASTNode(value)

    # <expression> ::= <add-expr>
    #   string, number or (
    # <add-expr> ::= <mul-expr> (['+' | '-'] <mul-expr>)*
    #   string, number or (
    # <mul-expr> ::= <atomic> (['*' | '/'] <atomic>)*
    #   string, number or (
    # <atomic> ::= [<literal> | <variable> | '(' <expression> ')'
    #     string, number or (
    def parse_expression(self) -> ExpressionASTNode:
        pass

    def parse_atom(self) -> IndentiferASTNode | NumberASTNode | ExpressionASTNode:
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )
        if self.current_token.type == TokenType.STRING:
            val = self.current_token.literal
            self.advance()
            return IndentiferASTNode(val)
        elif self.current_token.type == TokenType.NUMBER:
            val = self.current_token.literal
            self.advance()
            return NumberASTNode(val)
        elif self.current_token.type == TokenType.LEFT_PAREN:
            # Consume (
            self.advance()

            value = self.parse_add_expression()

            self.assert_current_token_in_set([TokenType.RIGHT_PAREN])
            # Consume )
            self.advance()

            return ExpressionASTNode(value)

    def parse_mul_expression(self) -> BinOpASTNode:
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )

        term = self.parse_atom()

        while True:
            operator_map = {
                TokenType.MULTIPLY: operator.mul,
                TokenType.DIVIDE: operator.truediv,
            }

            if self.current_token.type in operator_map.keys():
                op = operator_map[self.current_token.type]
                self.advance()
                rhs = self.parse_atom()
                term = BinOpASTNode(term, rhs, op)
            else:
                self.assert_current_token_in_set(
                    [
                        TokenType.RIGHT_PAREN,
                        TokenType.PLUS,
                        TokenType.MINUS,
                        TokenType.RIGHT_DOUBLE_CURLY_PAREN,
                    ]
                )
                break
        return term

    def parse_add_expression(self) -> BinOpASTNode:
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )

        term = self.parse_mul_expression()

        while True:
            operator_map = {
                TokenType.PLUS: operator.add,
                TokenType.MINUS: operator.sub,
            }

            if self.current_token.type in operator_map.keys():
                op = operator_map[self.current_token.type]
                self.advance()
                rhs = self.parse_mul_expression()
                term = BinOpASTNode(term, rhs, op)
            else:
                self.assert_current_token_in_set(
                    [
                        TokenType.RIGHT_PAREN,
                        TokenType.MULTIPLY,
                        TokenType.DIVIDE,
                        TokenType.RIGHT_DOUBLE_CURLY_PAREN,
                    ]
                )
                break
        return term

    def parse_expression_block(self) -> ExpressionBlockASTNode:
        self.assert_current_token_in_set([TokenType.LEFT_DOUBLE_CURLY_PAREN])
        self.tokens.lexer.trim_whitespace()
        self.advance()

        content = None
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )

        content = self.parse_add_expression()

        self.assert_current_token_in_set([TokenType.RIGHT_DOUBLE_CURLY_PAREN])
        self.tokens.lexer.keep_whitespace()
        self.advance()
        return ExpressionBlockASTNode(content)

    def parse_text(self) -> TextASTNode:
        self.assert_current_token_in_set([TokenType.STRING])
        node = TextASTNode(self.current_token.literal)
        self.advance()
        return node

    def parse_line(self) -> LineASTNode:
        self.assert_current_token_in_set(
            [TokenType.LEFT_DOUBLE_CURLY_PAREN, TokenType.STRING, TokenType.NEWLINE]
        )

        content = []

        while self.current_token.type not in [TokenType.NEWLINE, TokenType.EOF]:
            if self.current_token.type == TokenType.LEFT_DOUBLE_CURLY_PAREN:
                content.append(self.parse_expression_block())
            elif self.current_token.type == TokenType.STRING:
                content.append(self.parse_text())

        return LineASTNode(content)

    def parse_document(self) -> DocumentASTNode:
        self.assert_current_token_in_set(
            [
                TokenType.LEFT_DOUBLE_CURLY_PAREN,
                TokenType.STRING,
                TokenType.NEWLINE,
                TokenType.EOF,
            ]
        )

        lines = []
        if self.current_token.type == TokenType.EOF:
            return DocumentASTNode(lines)

        while True:
            lines.append(self.parse_line())
            line_ending_tok = self.current_token
            if line_ending_tok.type == TokenType.EOF:
                break

            # Consume the newline
            self.advance()
            if (line_ending_tok.type == TokenType.NEWLINE) and (
                self.current_token.type == TokenType.EOF
            ):
                lines.append(LineASTNode([]))
                break

        return DocumentASTNode(lines)

    def assert_current_token_in_set(self, expected: list[TokenType]):
        if self.current_token.type not in expected:
            raise ValueError(
                f"Parser error. Current token: {self.current_token} but expected {expected}."
            )

    def assert_token_in_set(actual: Token, expected: list[Token], message: str):
        if actual in expected:
            return actual
        else:
            raise ValueError(message)


def parse(l: Scanner):
    token_buffer = TokenSource(l)
    parser = Parser(token_buffer)
    return parser.parse_document()
