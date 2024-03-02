from dataclasses import dataclass
from enum import Enum
import re
import string
from typing import Optional


class TokenType(Enum):
    #   Single character tokens.
    LEFT_DOUBLE_CURLY_PAREN = 1
    RIGHT_DOUBLE_CURLY_PAREN = 2
    PLUS = 3
    MINUS = 4
    MULTIPLY = 5
    DIVIDE = 6
    LEFT_PAREN = 7
    RIGHT_PAREN = 8
    DOT = 9

    #   Literals.
    STRING = 10
    NUMBER = 11

    #   Keywords.
    FOREACH = 12
    IN = 13

    NEWLINE = 14
    EOF = 15


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[str | int | float]
    line: int


allowed_whitespace = " \t\v\f"
printable_characters = list(
    string.digits + string.ascii_letters + string.punctuation + string.whitespace
)
string_chars_without_nl = [c for c in printable_characters if c not in ["\n"]]
identifer_chars = [
    c
    for c in list(string.digits + string.ascii_letters + string.punctuation)
    if c not in ["(", ")"]
]


def normalise_newlines(source: str):
    return source.replace("\r\n", "\n")


class Scanner:
    def __init__(self, source):
        self.source = normalise_newlines(source)
        self.current = 0
        self.line = 1
        self.break_on_whitespace = False

    def add_token(self, type: TokenType, literal=None):
        return Token(type, None, literal, self.line)

    def char_in_list(self, character: str, symbols: list[str]):
        if character in symbols:
            return character

    def add_literal(self, value: str):
        if not self.break_on_whitespace:
            return self.add_token(TokenType.STRING, value)

        if value == "+":
            return self.add_token(TokenType.PLUS)
        elif value == "-":
            return self.add_token(TokenType.MINUS)
        elif value == "*":
            return self.add_token(TokenType.MULTIPLY)
        elif value == "/":
            return self.add_token(TokenType.DIVIDE)
        elif value == "(":
            return self.add_token(TokenType.LEFT_PAREN)
        elif value == ")":
            return self.add_token(TokenType.RIGHT_PAREN)
        elif value == ".":
            return self.add_token(TokenType.DOT)
        elif re.match(r"^-?\d+\.\d+$", value):
            return self.add_token(TokenType.NUMBER, float(value))
        elif value.isdigit():
            return self.add_token(TokenType.NUMBER, int(value))
        elif value == "foreach":
            return self.add_token(TokenType.FOREACH)
        elif value == "in":
            return self.add_token(TokenType.IN)
        else:
            return self.add_token(TokenType.STRING, value)

    def trim_whitespace(self):
        self.break_on_whitespace = True

    def keep_whitespace(self):
        self.break_on_whitespace = False

    def scan(self):
        while self.current < len(self.source):
            c = self.source[self.current]
            if self.break_on_whitespace and (c in allowed_whitespace):
                self.current += 1
            elif c == "\n":
                self.current += 1
                yield self.add_token(TokenType.NEWLINE)
                self.line += 1
            elif c == "{" and self.source[self.current + 1] == "{":
                self.current += 2
                yield self.add_token(TokenType.LEFT_DOUBLE_CURLY_PAREN)
            elif c == "}" and self.source[self.current + 1] == "}":
                self.current += 2
                yield self.add_token(TokenType.RIGHT_DOUBLE_CURLY_PAREN)
            elif c in string.printable:
                if self.break_on_whitespace:
                    # break on whitespace and emit string
                    allowed_chars = identifer_chars
                else:
                    # eat all the characters in printable stop on newline
                    allowed_chars = string_chars_without_nl

                literal_value = c
                self.current += 1
                while (self.current < len(self.source)) and (
                    s := self.char_in_list(self.source[self.current], allowed_chars)
                ):
                    self.current += 1

                    if s == "{" and self.source[self.current] == "{":
                        yield self.add_literal(literal_value)
                        self.current += 1
                        yield self.add_token(TokenType.LEFT_DOUBLE_CURLY_PAREN)
                        break
                    elif s == "}" and self.source[self.current] == "}":
                        self.current += 1
                        yield self.add_literal(literal_value)
                        yield self.add_token(TokenType.RIGHT_DOUBLE_CURLY_PAREN)
                        break
                    else:
                        literal_value += s
                else:
                    yield self.add_literal(literal_value)
            else:
                raise ValueError(f"Unknown token: {c} at {self.line}.")

        yield self.add_token(TokenType.EOF)
