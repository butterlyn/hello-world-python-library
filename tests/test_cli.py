import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path

import pytest
from click.testing import CliRunner, Result

from hello_world_python_library import cli

# The published distribution name, spelled out here rather than imported from the
# code under test, so a wrong name in the package cannot make these tests agree.
DISTRIBUTION = "hello-world-python-library"
SUBPROCESS_TIMEOUT_SECONDS = 60


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command to completion with colour output disabled."""
    env = {**os.environ, "PYTHON_COLORS": "0", "NO_COLOR": "1"}
    env.pop("FORCE_COLOR", None)
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=SUBPROCESS_TIMEOUT_SECONDS,
        env=env,
    )


def installed_console_script() -> Path:
    """Return the absolute path of the ``hello-world`` launcher of this install.

    The path comes from the distribution's RECORD file, so the test runs the
    launcher that was installed with the package under test, wherever the
    installer put it, and never an unrelated ``hello-world`` found on PATH.
    """
    dist = distribution(DISTRIBUTION)
    launchers = [
        dist.locate_file(file)
        for file in dist.files or []
        if file.stem == "hello-world" and file.parent.name in {"bin", "Scripts"}
    ]
    assert len(launchers) == 1, f"expected one hello-world launcher, got {launchers}"
    return Path(launchers[0]).resolve()


def invoke(args: list[str]) -> Result:
    """Run the click command in-process, letting unexpected exceptions propagate."""
    return CliRunner().invoke(cli.hello_world, args, catch_exceptions=False)


def missing_metadata(name: str) -> str:
    raise PackageNotFoundError(name)


def test_command_prints_greeting() -> None:
    result = invoke([])
    assert result.exit_code == 0
    assert result.stdout == "Hello World.\n"
    assert result.stderr == ""


def test_version_flag_prints_installed_version() -> None:
    result = invoke(["--version"])
    assert result.exit_code == 0
    assert result.stdout == f"hello-world {version(DISTRIBUTION)}\n"


def test_greeting_does_not_need_package_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "version", missing_metadata)
    result = invoke([])
    assert result.exit_code == 0
    assert result.stdout == "Hello World.\n"


def test_version_is_unknown_without_package_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "version", missing_metadata)
    result = invoke(["--version"])
    assert result.exit_code == 0
    assert result.stdout == "hello-world unknown\n"


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_flags_describe_the_command(flag: str) -> None:
    result = invoke([flag])
    assert result.exit_code == 0
    assert result.stdout.startswith("Usage: hello-world [OPTIONS]\n")
    assert "Print a friendly greeting." in result.stdout
    assert "--version" in result.stdout


def test_unknown_option_exits_with_usage_error() -> None:
    result = invoke(["--unknown"])
    assert result.exit_code == 2
    assert result.stdout == ""
    # Click's exact error wording can change between releases, so check only
    # that the usage line is shown and the bad option is named.
    assert result.stderr.startswith("Usage: hello-world [OPTIONS]\n")
    assert "--unknown" in result.stderr


def test_installed_console_script_prints_greeting() -> None:
    result = run([str(installed_console_script())])
    assert result.stdout == "Hello World.\n"
    assert result.stderr == ""


def test_installed_console_script_shows_help() -> None:
    result = run([str(installed_console_script()), "--help"])
    # Click would otherwise name the program after the launcher file, such as
    # hello-world.exe on Windows; the usage line must always say hello-world.
    assert result.stdout.startswith("Usage: hello-world [OPTIONS]\n")
    assert "--version" in result.stdout
    assert result.stderr == ""


def test_module_is_runnable_with_python_dash_m() -> None:
    result = run([sys.executable, "-m", "hello_world_python_library"])
    assert result.stdout == "Hello World.\n"
    assert result.stderr == ""


def test_module_help_names_the_command() -> None:
    # Without an explicit program name, click would print
    # "Usage: python -m hello_world_python_library".
    result = run([sys.executable, "-m", "hello_world_python_library", "--help"])
    assert result.stdout.startswith("Usage: hello-world [OPTIONS]\n")
    assert result.stderr == ""
