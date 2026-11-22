# Installing hello-world-python-library

The package is not on PyPI yet, so install it from its GitHub repository. Its distribution name is `hello-world-python-library`. It needs Python 3.11 or newer, and its only dependency is [click](https://click.palletsprojects.com/).

| To | Run |
| --- | --- |
| Add it to a uv project | `uv add "hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library"` |
| Install it with pip | `pip install "hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library"` |
| Install only the command | `uv tool install git+https://github.com/butterlyn/hello-world-python-library` |
| Run the command once without installing it | `uvx --from git+https://github.com/butterlyn/hello-world-python-library hello-world` |

In a `requirements.txt` file or a `dependencies` list, write the same requirement: `hello-world-python-library @ git+https://github.com/butterlyn/hello-world-python-library`.

If the shell cannot find `hello-world` after `uv tool install`, run `uv tool update-shell` and open a new terminal.
