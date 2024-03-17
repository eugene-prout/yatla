from __future__ import annotations
from yatla.ast_nodes import (
    BinOpASTNode,
    BuiltinFunctionType,
    DocumentASTNode,
    ExpressionASTNode,
    ExpressionBlockASTNode,
    ForEachBlockASTNode,
    FunctionCallASTNode,
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

    def parse_argument_list(self) -> list[ExpressionBlockASTNode]:
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )
        args = []
        while True:
            args.append(self.parse_add_expression())

            if self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.RIGHT_PAREN:
                    raise ValueError(
                        "Unexpected end of argument list. Expected term after comma."
                    )
            if self.current_token.type == TokenType.RIGHT_PAREN:
                break
        return args

    # <expression> ::= <add-expr>
    #   string, number or (
    # <add-expr> ::= <mul-expr> (['+' | '-'] <mul-expr>)*
    #   string, number or (
    # <mul-expr> ::= <atomic> (['*' | '/'] <atomic>)*
    #   string, number or (
    # <atomic> ::= [<literal> | <variable> | '(' <expression> ')'
    #     string, number or (
    def parse_atom(self) -> IndentiferASTNode | NumberASTNode | ExpressionASTNode:
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )
        if self.current_token.type == TokenType.STRING:
            val = self.current_token.literal
            self.advance()
            if self.current_token.type == TokenType.LEFT_PAREN:
                if val == "RoundUp":
                    val = BuiltinFunctionType.ROUNDUP
                elif val == "RoundDown":
                    val = BuiltinFunctionType.ROUNDDOWN
                elif val == "Minimum":
                    val = BuiltinFunctionType.MINIMUM
                elif val == "Maximum":
                    val = BuiltinFunctionType.MAXIMUM
                else:
                    raise ValueError(f"Unknown function: {val}.")
                self.advance()
                args = self.parse_argument_list()

                self.assert_current_token_in_set([TokenType.RIGHT_PAREN])
                self.advance()

                return FunctionCallASTNode(val, args)
            else:
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
                TokenType.MULTIPLY: BuiltinFunctionType.MULTIPLY,
                TokenType.DIVIDE: BuiltinFunctionType.DIVIDE,
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
                        TokenType.COMMA,
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
                TokenType.PLUS: BuiltinFunctionType.ADD,
                TokenType.MINUS: BuiltinFunctionType.SUBTRACT,
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
                        TokenType.COMMA,
                    ]
                )
                break
        return term

    def parse_foreach_line(self) -> LineASTNode:
        self.assert_current_token_in_set(
            [TokenType.LEFT_DOUBLE_CURLY_PAREN, TokenType.STRING, TokenType.NEWLINE]
        )

        content = []

        while self.current_token.type not in [TokenType.NEWLINE, TokenType.EOF]:
            if self.current_token.type == TokenType.LEFT_DOUBLE_CURLY_PAREN:
                content.append(self.parse_template_expression())
            elif self.current_token.type == TokenType.STRING:
                content.append(self.parse_text())
        return LineASTNode(content)

    def parse_foreach_block(self) -> ForEachBlockASTNode:
        self.assert_current_token_in_set([TokenType.LEFT_DOUBLE_CURLY_PAREN])
        self.advance()

        self.assert_current_token_in_set([TokenType.FOREACH])
        self.advance()

        self.assert_current_token_in_set([TokenType.STRING])
        iterand = self.current_token.literal
        self.advance()

        self.assert_current_token_in_set([TokenType.IN])
        self.advance()

        self.assert_current_token_in_set([TokenType.STRING])
        iterator = self.current_token.literal
        self.advance()

        self.assert_current_token_in_set([TokenType.RIGHT_DOUBLE_CURLY_PAREN])
        self.tokens.lexer.keep_whitespace()
        self.advance()

        message = "Expected newline after foreach block."
        self.assert_current_token_in_set([TokenType.NEWLINE], message)
        self.advance()

        message = "Expected endforeach after foreach block."
        body = []
        while True:
            line_start_token = self.current_token
            if line_start_token.type == TokenType.LEFT_DOUBLE_CURLY_PAREN:
                self.tokens.lexer.trim_whitespace()
                self.advance()
                next_token = self.current_token
                if next_token.type == TokenType.FOREACH:
                    raise ValueError("Cannot nest foreach loops.")
                elif next_token.type == TokenType.ENDFOREACH:
                    self.advance()

                    self.assert_current_token_in_set(
                        [TokenType.RIGHT_DOUBLE_CURLY_PAREN]
                    )
                    self.tokens.lexer.keep_whitespace()
                    self.advance()
                    line_ending_tok = self.current_token
                    if line_ending_tok.type == TokenType.EOF:
                        break
                    self.assert_current_token_in_set(
                        [TokenType.NEWLINE], "Expected newline after endforeach block."
                    )
                    break
                else:
                    self.tokens.push_back_token(next_token)
                    self.current_token = line_start_token
                    self.tokens.lexer.keep_whitespace()

            parsed_line = self.parse_foreach_line()

            body.append(parsed_line)
            line_ending_tok = self.current_token
            if line_ending_tok.type == TokenType.EOF:
                raise ValueError(message)

            # Consume the newline
            self.advance()
            if (line_ending_tok.type == TokenType.NEWLINE) and (
                self.current_token.type == TokenType.EOF
            ):
                raise ValueError(message)

        return ForEachBlockASTNode(iterand, iterator, body)

    def parse_template_expression(self) -> ExpressionBlockASTNode:
        self.assert_current_token_in_set([TokenType.LEFT_DOUBLE_CURLY_PAREN])
        self.tokens.lexer.trim_whitespace()
        self.advance()

        if self.current_token.type == TokenType.FOREACH:
            raise ValueError(
                "Foreach loop declarations must be the first expression on a line."
            )
        self.assert_current_token_in_set(
            [TokenType.STRING, TokenType.NUMBER, TokenType.LEFT_PAREN]
        )
        if self.current_token.type in [
            TokenType.STRING,
            TokenType.NUMBER,
            TokenType.LEFT_PAREN,
        ]:
            node = ExpressionBlockASTNode(self.parse_add_expression())

        self.assert_current_token_in_set([TokenType.RIGHT_DOUBLE_CURLY_PAREN])
        self.tokens.lexer.keep_whitespace()
        self.advance()

        return node

    def parse_template_block(self) -> ExpressionBlockASTNode | ForEachBlockASTNode:
        self.assert_current_token_in_set([TokenType.LEFT_DOUBLE_CURLY_PAREN])

        line_start_token = self.current_token
        self.tokens.lexer.trim_whitespace()
        self.advance()

        next_token = self.current_token
        node = None

        if self.current_token.type == TokenType.ENDFOREACH:
            raise ValueError("Unexpected endforeach block.")

        self.assert_current_token_in_set(
            [
                TokenType.STRING,
                TokenType.NUMBER,
                TokenType.LEFT_PAREN,
                TokenType.FOREACH,
            ]
        )

        if next_token.type in [
            TokenType.STRING,
            TokenType.NUMBER,
            TokenType.LEFT_PAREN,
        ]:
            self.tokens.push_back_token(next_token)
            self.current_token = line_start_token
            node = self.parse_template_expression()

        elif next_token.type in [TokenType.FOREACH]:
            self.tokens.push_back_token(next_token)
            self.current_token = line_start_token
            node = self.parse_foreach_block()

        self.tokens.lexer.keep_whitespace()
        return node

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
                content.append(self.parse_template_block())
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

    def assert_current_token_in_set(self, expected: list[TokenType], message=None):
        if self.current_token.type not in expected:
            if not message:
                message = f"Parser error. Current token: {self.current_token} but expected {expected}."
            raise ValueError(message)


def parse(l: Scanner):
    token_buffer = TokenSource(l)
    parser = Parser(token_buffer)
    return parser.parse_document()
