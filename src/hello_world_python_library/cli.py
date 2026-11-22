"""Command-line interface behind the ``hello-world`` command."""

from importlib.metadata import PackageNotFoundError, version

import click

from hello_world_python_library import greet

DISTRIBUTION_NAME = "hello-world-python-library"
PROG_NAME = "hello-world"


def installed_version() -> str:
    """Return the installed version of the package, or ``"unknown"`` without metadata."""
    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "unknown"


def print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Print the installed version and exit, if ``--version`` was given."""
    if not value or ctx.resilient_parsing:
        return
    # Package metadata is looked up only for --version, so the greeting also works
    # when the package is imported from a source tree that was never installed.
    # click.version_option is not used because it fails without metadata.
    click.echo(f"{PROG_NAME} {installed_version()}")
    ctx.exit()


@click.command(name=PROG_NAME)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=print_version,
    help="Show the installed version and exit.",
)
# An explicit help option, rather than context_settings={"help_option_names": ...},
# because tools that render the help text themselves, such as the Great Docs CLI
# reference, build a bare click.Context that ignores the command's context_settings.
@click.help_option("-h", "--help")
def hello_world() -> None:
    """Print a friendly greeting."""
    click.echo(greet())


def main() -> None:
    """Run the ``hello-world`` command, then exit with its exit code."""
    # Click would otherwise name the program after sys.argv[0], which gives
    # "hello-world.exe" on Windows and "python -m hello_world_python_library"
    # for ``python -m``.
    hello_world(prog_name=PROG_NAME)
