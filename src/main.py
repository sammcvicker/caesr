import click
from pathlib import Path
from supermemo2 import first_review, review
from src.deck import Deck
from src.config import Config

def as_csv_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.suffix != '.csv':
        raise click.ClickException("Deck must be a .csv file")
    return path

@click.group(name="srs")
def cli():
    pass

@cli.command()
@click.pass_context
@click.argument('deck', type=click.Path(exists=True, dir_okay=False))
def use(context: click.Context, deck: str):
    """Use a deck to practice"""

    Deck(as_csv_path(deck)).use()
    return

@cli.command()
@click.pass_context
@click.argument('deck', type=click.Path(exists=True, dir_okay=False))
@click.argument('content', type=str)
def add(context: click.Context, deck: str, content: str):
    """Add a card to a deck"""

    Deck(as_csv_path(deck)).add(content)
    return

@cli.command()
@click.pass_context
@click.argument('deck', type=click.Path(exists=True, dir_okay=False))
def list(context: click.Context, deck: str):
    """Add a card to a deck"""

    config: Config = Config()
    
    Deck(as_csv_path(deck)).list()
    return

@cli.command()
@click.pass_context
def config(context: click.Context):
    """Configure the srs tool"""

    config: Config = Config()
    config.configure()

    return

if __name__ == '__main__':
    cli()