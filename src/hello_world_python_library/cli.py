"""Command-line interface behind the ``hello-world`` command."""

import argparse
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version

from hello_world_python_library import greet

DISTRIBUTION_NAME = "hello-world-python-library"


def installed_version() -> str:
    """Return the installed version of the package, or ``"unknown"`` without metadata."""
    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``hello-world`` command."""
    parser = argparse.ArgumentParser(
        prog="hello-world",
        description="Print a friendly greeting.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="show the installed version and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``hello-world`` command and return its exit code."""
    args = build_parser().parse_args(argv)
    # Package metadata is looked up only for --version, so the greeting also works
    # when the package is imported from a source tree that was never installed.
    if args.version:
        print(f"hello-world {installed_version()}")
    else:
        print(greet())
    return 0
