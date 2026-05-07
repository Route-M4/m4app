import logging

import click

from ..core import logging as logger
from ..core.settings import settings


@click.group()
def cli() -> None:
    """Main CLI group."""
    debug = settings.get("debug")
    if debug:
        logger.setup_logger(loglevel=logging.DEBUG)
    else:
        logger.setup_logger(loglevel=logging.INFO)


@cli.group()
def run() -> None:
    """Run application components."""
    pass


@run.command()
def bot() -> None:
    """Run bot application."""
    click.echo("Running bot application...")
