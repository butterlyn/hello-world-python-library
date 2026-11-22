import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path

import pytest

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


def missing_metadata(name: str) -> str:
    raise PackageNotFoundError(name)


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main([]) == 0
    captured = capsys.readouterr()
    assert captured.out == "Hello World.\n"
    assert captured.err == ""


def test_version_flag_prints_installed_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--version"]) == 0
    assert capsys.readouterr().out == f"hello-world {version(DISTRIBUTION)}\n"


def test_greeting_does_not_need_package_metadata(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "version", missing_metadata)
    assert cli.main([]) == 0
    assert capsys.readouterr().out == "Hello World.\n"


def test_version_is_unknown_without_package_metadata(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "version", missing_metadata)
    assert cli.main(["--version"]) == 0
    assert capsys.readouterr().out == "hello-world unknown\n"


def test_unknown_argument_exits_with_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--unknown"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments: --unknown" in capsys.readouterr().err


def test_installed_console_script_prints_greeting() -> None:
    result = run([str(installed_console_script())])
    assert result.stdout == "Hello World.\n"
    assert result.stderr == ""


def test_installed_console_script_shows_help() -> None:
    result = run([str(installed_console_script()), "--help"])
    assert result.stdout.startswith("usage: hello-world")
    assert "--version" in result.stdout
    assert result.stderr == ""


def test_module_is_runnable_with_python_dash_m() -> None:
    result = run([sys.executable, "-m", "hello_world_python_library"])
    assert result.stdout == "Hello World.\n"
    assert result.stderr == ""
