from yatla._parser import parse
from yatla.lexer import Scanner
def test_template_evaluation():
    template = ("This is the {{ factor }} times table:\n"
                "{{ foreach num in num_list }}\n"
                "{{ factor }} * {{ num }} = {{ factor * num }}\n"
                "{{ endforeach }}\n")
    
    ast = parse(Scanner(template))
    print(ast)

