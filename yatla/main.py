import re
import click
from yatla.lexer import Scanner
from yatla._parser import parse
from yatla.validation import compute_parameters


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def lexer(filepath):
    text = open(filepath).read()
    tokens = list(Scanner(text).scan())

    print("\n".join(map(str, tokens)))


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def ast(filepath):
    text = open(filepath).read()
    doc = parse(Scanner(text))

    print(doc)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.argument("data", nargs=-1)
def eval(filepath, data: tuple[str, ...]):
    text = open(filepath).read()
    doc = parse(Scanner(text))
    data: dict[str, str] = dict(arg.split(":") for arg in data)

    for k in data.keys():
        value = data[k]
        if re.match(r"^-?\d+", value):
            data[k] = int(value)
        elif re.match(r"^-?\d+\.\d+$", value):
            data[k] = float(value)

    print(doc.eval(data))


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def type(filepath):
    text = open(filepath).read()
    doc = parse(Scanner(text))

    paramters = compute_parameters(doc.get_parameters())

    print(paramters)

def main():
    cli()

if __name__ == "__main__":
    main()
