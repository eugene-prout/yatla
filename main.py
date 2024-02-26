from enum import Enum
from functools import reduce
from itertools import groupby
from multiprocessing import Value

import pyparsing as pp


class Type(Enum):
    string = 1
    numbers = 2
    any = 3

# end up with a bag of contraints
# and have something solve them
# when calling get_parameters yield the type and the name of the parameter


class UnaryOpNode:
    def __init__(self, tokens):
        tokens = tokens.as_list()[0]
        if not len(tokens) == 2:
            raise ValueError(tokens)
        
        self.op, self.symbol = tokens

    def __repr__(self):
        return f"UnaryOp([[{self.op}, {self.symbol}]])"
    
    def eval(self, context):
        res = self.symbol.eval(context)
        if self.op == "+":
            return res
        elif self.op == "-":
            return -1 * res
        else:
            raise ValueError(f"Unknown operator: {self.op}.")
        
    def get_parameters(self):
        return self.symbol.get_parameters()

class BinOpNode:
    def __init__(self, tokens):
        tokens = tokens.as_list()[0]
        if len(tokens) % 2 == 0:
            raise ValueError("Input list must have odd number of element s.")

        self.values = tokens
    
    def apply_operator(self, acc, chunk):
        op, num = chunk
        if op == '+':
            return acc + num
        elif op == '-':
            return acc - num
        elif op == '*':
            return acc * num
        elif op == '/':
            return acc / num
        else:
            raise ValueError(f"Unknown operator: {op}.")

    def __repr__(self):
        return f"BinaryOp([[{self.values}]])"
    
    def eval(self, context):
        initial_value = self.values[0].eval(context)
        pairs = ((self.values[i], self.values[i + 1].eval(context)) for i in range(1, len(self.values), 2))
        
        return reduce(self.apply_operator, pairs, initial_value)
    
    def get_parameters(self):
        params = []
        for value in self.values[::2]:
            if param := value.get_parameters():
                for p in param:
                    params.append((p[0], Type.numbers))
        return params

class PlainText:
    def __init__(self, tokens):
        tokens = tokens.as_list()
        self.value = tokens

    def __repr__(self):
        return f"PlainText([[{self.value}]])"
    
    def eval(self, context):
        return self.value
    
    def get_parameters(self):
        return None

class Expression:
    def __init__(self, tokens):
        tokens = tokens.as_list()[0]
        self.value = tokens

    def __repr__(self):
        return f"Expression([[{self.value}]])"
    
    def eval(self, context):
        return str(self.value.eval(context))
    
    def get_type(self):
        return self.value.get_type()
    
    def get_parameters(self):
        if param := self.value.get_parameters():
            return param


class Number:
    def __init__(self, tokens):
        tokens = float(tokens.as_list()[0])
        self.value = tokens

    def __repr__(self):
        return f"Number([[{self.value}]])"

    def eval(self, context):
        return self.value
    
    def get_parameters(self):
        return None

class StringIdentifier:
    def __init__(self, tokens):
        tokens = tokens.as_list()[0]
        self.value = tokens

    def __repr__(self):
        return f"StringIdentifier([[{self.value}]])"
    
    def eval(self, context):
        return context[self.value]
    
    def get_parameters(self):
        return [(self.value, Type.string)]
    
class NumIdentifier:
    def __init__(self, tokens):
        tokens = tokens.as_list()[0]
        self.value = tokens

    def __repr__(self):
        return f"NumIdentifier([[{self.value}]])"
    
    def eval(self, context):
        return context[self.value]
    
    def get_parameters(self):
        return [(self.value, Type.numbers)]

class ForLoopBlock:
    def __init__(self, tokens):
        self.iterand, self.iterator = tokens.as_list()    
        print(self.iterand, self.iterator)
    def __repr__(self):
        return f"ForLoopBlock([[{self.iterand}, {self.iterator}]])"
    
    def eval(self, context):
        return context[self.value]
    
    # need to encode, ΛT λx: array[T].next(x) : ∀T.array[T]->T 

    def get_parameters(self):
        return [(self.value, Type.numbers)]

class Line:
    def __init__(self, tokens):
        self.contents = tokens.as_list()

    def __repr__(self):
        return f"Line([{self.contents}])"
    
    def eval(self, context):
        return "".join(n.eval(context) for n in self.contents)
    
    def get_parameters(self):
        params = []
        for n in self.contents:
            if param := n.get_parameters():
                params += param
        return params
    
class Document:
    def __init__(self, tokens):
        self.contents = tokens.as_list()

    def __repr__(self):
        return f"Document([{self.contents}])"
    
    def eval(self, context):
        return "\n".join(n.eval(context) for n in self.contents)

    def get_parameters(self):
        params = []
        for n in self.contents:
            params += n.get_parameters()
        return params


def set_is_exactly(s: set, t: list):
    return all(e in t for e in s)

def unify_types(parameters: list[tuple[str, Type]]):
    typed_parameters = {}
    for parameter, named_constraints in groupby(sorted(parameters, key=lambda x: x[0]), key=lambda x: x[0]):
        constraints = list(c[1] for c in named_constraints)
        if len(set(constraints)) == 1:
            typed_parameters[parameter] = constraints[0]
        elif set_is_exactly(constraints, [Type.string, Type.numbers]):
            typed_parameters[parameter] = Type.numbers
        else:
            raise ValueError("Unable to unify types.")
    return typed_parameters

def generate_grammar():

    pp.ParserElement.set_default_whitespace_chars(" \t")
    
    num_identifier = pp.common.identifier
    num_identifier.set_parse_action(NumIdentifier)
    
    number = pp.common.fnumber
    number.set_parse_action(Number)

    atom = number | num_identifier
    
    string_identifer = pp.common.identifier
    string_identifer.set_parse_action(StringIdentifier)

    num_expression = pp.infix_notation(atom,
    [
        (pp.one_of("+ -"), 1, pp.opAssoc.RIGHT, UnaryOpNode), # sign
        (pp.one_of("* /"), 2, pp.opAssoc.LEFT, BinOpNode), # multiply
        (pp.one_of("+ -"), 2, pp.opAssoc.LEFT, BinOpNode), # add
    ]
    )
    
    body_line = pp.Forward()

    for_loop_block = (
        pp.Literal("{{").suppress()  + pp.Literal("foreach").suppress() + string_identifer 
            + pp.Literal("in").suppress() + string_identifer + pp.Literal("}}").suppress() + pp.White("\r\n")
        + pp.ZeroOrMore(body_line)
        + pp.Literal("{{").suppress() + pp.Literal("endfor") + pp.Literal("}}").suppress() )
    for_loop_block.set_parse_action(ForLoopBlock) 

    expr_block = pp.Literal("{{").suppress() + (string_identifer | num_expression) + pp.Literal("}}").suppress()
    expr_block.set_parse_action(Expression).set_whitespace_chars(" \t")

    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ascii_letters = ascii_lowercase + ascii_uppercase
    digits = '0123456789'
    
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`|~"""
    characters =  digits + ascii_letters + punctuation + ' \t' 

    text = pp.Word(characters)
    text.set_parse_action(PlainText)
    
    line = pp.ZeroOrMore(text | expr_block) | for_loop_block
    line.set_parse_action(Line)

    body_line <<= line + pp.White("\r\n", min=1, max=1).suppress()
    ending_line = line + pp.Opt(pp.White("\r\n").suppress())

    document = pp.ZeroOrMore(body_line) + pp.Opt(ending_line)
    document.add_parse_action(Document)

    return expr_block

g = generate_grammar()

file = open("stringvar.txt").read()
# print(file)
tree = g.parse_string(file, parse_all=True)
print(tree.dump())
# parsed_result = tree.as_list()[0]
# print(parsed_result)
context = {"test_message": "Hello, world!"}
# print(parsed_result.eval(context))
# print(parsed_result.get_parameters())
# print(unify_types(parsed_result.get_parameters()))