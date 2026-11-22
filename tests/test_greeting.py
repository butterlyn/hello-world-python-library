from hello_world_python_library import GREETING, greet


def test_greeting_is_hello_world() -> None:
    assert GREETING == "Hello World."


def test_greet_returns_the_greeting() -> None:
    assert greet() == GREETING
