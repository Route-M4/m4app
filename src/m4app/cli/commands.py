import click


@click.group()
def cli() -> None:
    """Main CLI group."""
    pass


@cli.group()
def run() -> None:
    """Run application components."""
    pass


@run.command()
def bot() -> None:
    """Run bot application."""
    click.echo("Running bot application...")
