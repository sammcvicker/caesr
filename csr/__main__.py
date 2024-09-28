import click
from pathlib import Path
from csr.deck import Deck
from csr.config import load_config, configure
from csr.styles import styles
from csr.auto_aliasing import AliasedGroup


def ensure_csv(path_str: str) -> Path:
    """
    Gets a path to a CSV file from a string.

    Args:
        path_str (str): The string-path to check and convert.

    Returns:
        Path: A Path object to a CSV file.

    Raises:
        click.ClickException: If path_str is not to a CSV file.
    """
    path = Path(path_str)
    if path.suffix != ".csv":
        raise click.ClickException("Deck must be a .csv file")
    return path


# "cli" group is entrypoint for csr CLI
# Subcommands under @cli.command() decorator
@click.group(name="csr", cls=AliasedGroup)
def cli():
    pass


@cli.command()
@click.argument("deck", type=click.Path(exists=True, dir_okay=False))
def practice(deck: str):
    """Practice with a deck"""

    Deck(ensure_csv(deck)).practice()
    return


@cli.command()
@click.argument("deck", type=click.Path(exists=True, dir_okay=False))
@click.argument("content", type=str)
def add(deck: str, content: str):
    """Add a card to a deck"""
    deck_path = ensure_csv(deck)
    Deck(deck_path).add_card(content)
    click.secho(f'Added "{content}" to {deck}', **styles["good"])
    return


@cli.command()
@click.argument("deck", type=click.Path(exists=True, dir_okay=False))
def list(deck: str):
    """List cards in a deck"""
    deck_path = ensure_csv(deck)
    Deck(deck_path).list()
    return


@cli.command(name="configure")  # name describes how command appears in CLI
def config():
    """Configure the API, Model, and API key csr uses"""
    user_config = load_config()
    configure(config=user_config, force_reconfigure=True)
    return


cli()
