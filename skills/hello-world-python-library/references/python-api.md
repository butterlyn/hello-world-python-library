# The Python API

```python
from hello_world_python_library import GREETING, greet
```

The public API is the two names in `hello_world_python_library.__all__`:

| Name | Type | What it is |
| --- | --- | --- |
| `GREETING` | `str` | The greeting text, `"Hello World."` |
| `greet` | `() -> str` | Returns `GREETING`. It takes no arguments, prints nothing and has no side effects. |

`greet()` returns the text that the `hello-world` command prints, without the trailing newline.

The package ships type hints, with a `py.typed` marker, so type checkers such as mypy and pyright check calls against these types.

Everything else, including the `hello_world_python_library.cli` module behind the command, is internal and can change in any release.

## Examples

Print the greeting:

```python
from hello_world_python_library import greet

print(greet())  # Hello World.
```

Build on it:

```python
from hello_world_python_library import greet


def welcome(name: str) -> str:
    return f"{greet()} Welcome, {name}!"
```

Test such code against `GREETING` rather than a copy of the text, so the test still passes if the greeting changes:

```python
from hello_world_python_library import GREETING


def test_welcome() -> None:
    assert welcome("Ada") == f"{GREETING} Welcome, Ada!"
```
