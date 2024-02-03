import pyparsing as pp


"""
document = ZeroOrMore(line)
	 
line = ZeroOrMore(Optional(text) Optional(expr_block))\n
	 | {{ KeyWord(for) str_var Keyword(in) str_var }}\n ZeroOrMore(line) {{ endfor }}\n

expr_block = {{ sum }}

str_var = STR_IDENT
 
sum = product +|- product
	 | product
	 
product = atom *|/ atom
		| atom

atom = NUMBER
	 | - atom 
	 | NUM_IDENT
	 | ( sum )

"""


class UnaryOpNode:
    def __init__(self, tokens):
        tokens = tokens[0]
        if not len(tokens) == 2:
            raise ValueError(tokens)
        
        self.op, self.symbol = tokens

    def __repr__(self):
        return f"UnaryOp([[{self.op}, {self.symbol}]])"

class BinOpNode:
    def __init__(self, tokens):
        tokens = tokens[0]
        if not len(tokens) == 3:
            raise ValueError(tokens)
        
        self.lhs, self.op, self.rhs = tokens

    def __repr__(self):
        return f"BinaryOp([[{self.lhs}, {self.op}, {self.rhs}]])"

class PlainText:
    def __init__(self, tokens):
        tokens = tokens
        self.value = tokens

    def __repr__(self):
        return f"PlainText([[{self.value}]])"

class Expression:
    def __init__(self, tokens):
        tokens = tokens[0]
        self.value = tokens

    def __repr__(self):
        return f"Expression([[{self.value}]])"
    
class Identifier:
    def __init__(self, tokens):
        tokens = tokens[0]
        self.value = tokens

    def __repr__(self):
        return f"Indentifier([[{self.value}]])"
    
class Line:
    def __init__(self, tokens):
        self.contents = tokens

    def __repr__(self):
        return f"Line([{self.contents}])"
    
def generate_grammar():

    pp.ParserElement.set_default_whitespace_chars(" \t")
    
    identifier = pp.common.identifier
    identifier.set_parse_action(Identifier)
    
    atom = pp.common.signed_integer | identifier


    num_expression = pp.infix_notation(atom,
    [
        (pp.one_of("+ -"), 1, pp.opAssoc.RIGHT, UnaryOpNode), # sign
        (pp.one_of("* /"), 2, pp.opAssoc.LEFT, BinOpNode), # multiply
        (pp.one_of("+ -"), 2, pp.opAssoc.LEFT, BinOpNode), # add
    ]
    )
    expr_block = pp.Literal("{{").suppress() + (identifier | num_expression) + pp.Literal("}}").suppress()
    expr_block.set_parse_action(Expression)

    pp.ParserElement.set_default_whitespace_chars('') 

    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ascii_letters = ascii_lowercase + ascii_uppercase
    digits = '0123456789'
    
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`|~"""
    characters =  digits + ascii_letters + "," + ' \t' 

    text = pp.Word(characters)
    text.set_parse_action(PlainText)
    
    line = pp.ZeroOrMore(text | expr_block)
    line.set_parse_action(Line)

    body_line = line + pp.White("\r\n", min=1, max=1)
    ending_line = line + pp.Opt(pp.White("\r\n"))
    return pp.ZeroOrMore(body_line) + pp.Opt(ending_line)

g = generate_grammar()

file = open("mixed.txt").read()
# print(file)
tree = g.parse_string(file, parse_all=True)
print(tree)