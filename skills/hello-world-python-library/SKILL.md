---
name: hello-world-python-library
description: Install and use hello-world-python-library, whose `hello-world` command prints the greeting "Hello World." and whose Python package `hello_world_python_library` returns it from `greet()` and `GREETING`. Use when code imports hello_world_python_library, when running or scripting the hello-world command, or when adding the library to a project.
---

# hello-world-python-library

A deliberately tiny library whose whole job is the greeting `Hello World.`:

- The `hello-world` command prints it.
- The Python package `hello_world_python_library` returns it from `greet()` and holds it in `GREETING`.

Install it as `hello-world-python-library`, import it as `hello_world_python_library`. It needs Python 3.11 or newer, and its only dependency is [click](https://click.palletsprojects.com/).

## Install from GitHub

The package is not on PyPI yet, so install it from its GitHub repository:

| To | Run |
| --- | --- |
| Add it to a uv project | `uv add "hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library"` |
| Install it with pip | `pip install "hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library"` |
| Install only the command | `uv tool install git+https://github.com/butterlyn/hello-world-python-library` |
| Run the command once without installing it | `uvx --from git+https://github.com/butterlyn/hello-world-python-library hello-world` |

In a `requirements.txt` file or a `dependencies` list, write the same requirement: `hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library`.

If the shell cannot find `hello-world` after `uv tool install`, run `uv tool update-shell` and open a new terminal.

## Use it

```console
$ hello-world
Hello World.
```

```python
from hello_world_python_library import greet

message = greet()  # "Hello World."
```

## Details

- Read [references/command.md](references/command.md) before scripting the command or relying on its options, output or exit codes.
- Read [references/python-api.md](references/python-api.md) before writing code or tests against `greet()` or `GREETING`.
