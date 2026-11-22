# The `hello-world` command

```text
hello-world [OPTIONS]
```

The command takes no arguments, and reads no input, environment variables or configuration files.

| Option | Prints to standard output | Exit code |
| --- | --- | --- |
| none | `Hello World.` | 0 |
| `--version` | `hello-world <version>`, such as `hello-world 0.1.0` | 0 |
| `-h`, `--help` | The help text below | 0 |

Every output ends with a newline. `--version` prints `hello-world unknown` when the package metadata is missing, for example when the code runs from a source folder that was never installed.

```console
$ hello-world --help
Usage: hello-world [OPTIONS]

  Print a friendly greeting.

Options:
  --version   Show the installed version and exit.
  -h, --help  Show this message and exit.
```

## Errors

An unknown option or any argument is a usage error. The command prints the usage line and an error message to standard error, prints nothing to standard output, and exits with code 2:

```console
$ hello-world --unknown
Usage: hello-world [OPTIONS]

Error: No such option '--unknown'.
```

click writes the error message, and its wording can change between click versions. Check the exit code, not the message.

## Running it as a Python module

`python -m hello_world_python_library` is the same command, with the same options and output, run by that Python interpreter. Use it when the `hello-world` launcher is not on `PATH`, or to choose the environment explicitly. The usage line still says `hello-world`.

## Calling it from a script

From Python code, call `greet()` instead (see [python-api.md](python-api.md)). It returns the same text without starting a process. When a test or script needs the real command, run it through the current interpreter, so it uses the environment the library is installed in:

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "hello_world_python_library"],
    capture_output=True,
    text=True,
    check=True,
)
assert result.stdout == "Hello World.\n"
```
