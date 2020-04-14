"""Console script for bulkdata. (Currently does nothing)"""
import sys
import click


@click.command()
def main(args=None):
    """Console script for bulkdata."""
    click.echo("CLI not available yet...")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
