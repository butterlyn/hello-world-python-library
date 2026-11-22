"""A tiny example library that ships a ``hello-world`` command-line tool."""

__all__ = ["GREETING", "greet"]

GREETING = "Hello World."


def greet() -> str:
    """Return the greeting that the ``hello-world`` command prints."""
    return GREETING
