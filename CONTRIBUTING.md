# Contributing

How to maintain this library. Written for both humans and AI agents: every step is a command you can run as-is from the repository root.

## Tooling

| Tool | Job | Configured in |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Python versions, virtual environment, dependencies, lockfile, builds | `pyproject.toml`, `uv.lock`, `.python-version` |
| [tox](https://tox.wiki/) + [tox-uv](https://github.com/tox-dev/tox-uv) | Runs the tests on every supported Python version, plus lint | `tox.toml` |
| [pytest](https://docs.pytest.org/) | Unit tests | `[tool.pytest]` in `pyproject.toml` |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting | `[tool.ruff]` in `pyproject.toml` |
| [prek](https://prek.j178.dev/) | Git pre-commit hooks: Ruff, file hygiene, lockfile sync | `prek.toml` |
| GitHub Actions | Runs the full check on Linux, macOS and Windows for pushes to `main` and pull requests | `.github/workflows/ci.yml` |

## Setup

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/). It downloads every Python version the project needs, so you don't need to install Python yourself.
2. From the repository root:

   ```console
   uv sync               # create .venv with the project and all development tools
   uv run prek install   # install the Git pre-commit hook
   ```

The development environment runs on the lowest supported Python (pinned in `.python-version`), so code that only works on newer versions fails locally first.

## Key commands

| Command | What it does |
| --- | --- |
| `uv run --locked tox` | **Full check**: tests on every supported Python, then lint. Must pass before every commit. CI runs exactly this. |
| `uv run --locked tox p` | The full check with environments in parallel. |
| `uv run --locked tox -e py313` | Tests on a single Python version (`py311` to `py315`). |
| `uv run --locked tox -e lint` | Checks Ruff lint and format, file hygiene and `uv.lock` on every tracked file. Never modifies files. |
| `uv run --locked tox -e py311 -- -k cli -x` | Arguments after `--` are passed straight to pytest. |
| `uv run --locked tox list` | List the tox environments and what each does. |
| `uv run prek run --all-files` | **Fix** what the hooks can fix (Ruff fixes and formatting, whitespace, `uv lock`), the same as the commit hook. |
| `uv run pytest` | Quick test loop on the development Python only. |
| `uv run hello-world` | Run the command from your checkout. |

Things to know:

- **Always pass `--locked` when verifying.** Plain `uv run` quietly updates `uv.lock` to match `pyproject.toml` before running anything, which would hide a stale lockfile. With `--locked`, a stale `uv.lock` fails instead. Run `uv lock` to fix it, then commit `uv.lock`.
- **tox tests the built wheel**, not your source folder. Each run rebuilds and installs the wheel, so the tests also catch packaging mistakes. `uv run pytest` uses an editable install, for speed.
- **Lint has two modes.** `tox -e lint` runs the check-only hooks (the `manual` stage in `prek.toml`). The commit hook and `prek run` run the fixing hooks (the `pre-commit` stage). Change both variants of a hook together.
- **prek only sees files Git tracks.** `git add` new files before running `tox -e lint` or `prek run --all-files`.

## Making a change

1. Add or update a test in `tests/` that describes the new behaviour.
2. Change the code in `src/hello_world_python_library/`.
3. Run `uv run --locked tox`. Every environment must end in `OK`.
4. Commit with a [Conventional Commits](#commit-messages) message. The pre-commit hook then runs the fixing hooks. If one rewrote a file, review the change, `git add` it, and commit again.

Code map:

| Path | Contents |
| --- | --- |
| `src/hello_world_python_library/__init__.py` | Public API: `GREETING` and `greet()` |
| `src/hello_world_python_library/cli.py` | The `hello-world` command (argparse); entry point `main()` |
| `src/hello_world_python_library/__main__.py` | Makes `python -m hello_world_python_library` work |
| `src/hello_world_python_library/py.typed` | Tells type checkers the package ships type hints |
| `tests/` | The pytest suite, including end-to-end runs of the installed `hello-world` launcher |

The `hello-world` command is registered under `[project.scripts]` in `pyproject.toml`.

## Commit messages

Every commit message follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **type** is one of:
  - `feat`: a new feature for users
  - `fix`: a bug fix
  - `docs`: documentation only
  - `test`: adding or fixing tests
  - `refactor`: a code change that neither fixes a bug nor adds a feature
  - `perf`: a performance improvement
  - `style`: formatting only
  - `build`: packaging, dependencies, `uv.lock`
  - `ci`: the GitHub Actions workflow
  - `chore`: other maintenance, such as tooling and hook versions
  - `revert`: undoes an earlier commit

  `feat` and `fix` are defined by the spec. The rest follow the widely used [`@commitlint/config-conventional`](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional) list.
- **scope** is optional and names the part of the codebase, in parentheses: `feat(cli): …`.
- **description** is a short, imperative, lower-case summary with no trailing full stop: `fix: handle missing package metadata`.
- **Breaking changes** add `!` before the colon (`feat(cli)!: rename --version to -V`), or a `BREAKING CHANGE: <what breaks>` footer, or both.

Examples:

```text
feat(cli): add --name option to greet someone specific
fix: print the greeting when package metadata is missing
build: bump pytest to 9.3
chore: update prek hook revisions
docs: explain the two lint modes in CONTRIBUTING
```

Keep each commit to one logical change, so its type and description stay accurate.

## Maintenance checklists

### Dependencies

Change dependencies with the uv CLI, not by editing `pyproject.toml` or `uv.lock` by hand. The CLI keeps the two in sync.

| Kind | Add | Remove |
| --- | --- | --- |
| Runtime (installed for users) | `uv add <pkg>` | `uv remove <pkg>` |
| Test-only | `uv add --group test <pkg>` | `uv remove --group test <pkg>` |
| Lint-only | `uv add --group lint <pkg>` | `uv remove --group lint <pkg>` |
| Other development tools | `uv add --dev <pkg>` | `uv remove --dev <pkg>` |

To upgrade every locked version, run `uv lock --upgrade` and then `uv run --locked tox`. Always commit `uv.lock`, using the `build:` type.

The `dev` group includes the `test` and `lint` groups, so `uv sync` installs everything. Each tox environment installs only the group it needs.

### Hook versions

`uv run prek update --freeze` moves every hook repository in `prek.toml` to its latest release, pinned to the exact commit with the tag name in a `# frozen:` comment. Always pass `--freeze`, so the pins stay reproducible. Then run `uv run --locked tox -e lint` and commit with `chore: update prek hook revisions`.

Keep the `uv-pre-commit` revision on the same uv version that you develop with.

### GitHub Actions versions

The actions in `.github/workflows/ci.yml` are pinned to full commit SHAs, with the tag in a trailing comment. To update one, look up the new tag's commit with `git ls-remote --tags https://github.com/<owner>/<action>`. Then replace both the SHA and the comment, and commit with the `ci:` type.

### The build backend

`uv init` set the `uv_build` range in `[build-system]`. Widen that range only when the project needs a newer build-backend feature. If your uv version falls outside the range, builds still work: uv downloads a matching `uv_build` instead of using its built-in copy.

### Supported Python versions

The policy is to support every CPython version in `bugfix` or `security` status on the [Python devguide status page](https://devguide.python.org/versions/). A new version is released every October, and the oldest one reaches end of life around the same time.

Adding a new version (3.16 as the example):

1. Add `py316` to `env_list` in `tox.toml`.
2. Add the `Programming Language :: Python :: 3.16` classifier in `pyproject.toml`.
3. Run `uv run --locked tox`.
4. Add the version to the list in `README.md`.

Dropping an end-of-life version (3.11 as the example):

1. Set `requires-python = ">=3.12"` in `pyproject.toml`. Ruff takes its target Python version from this setting.
2. Remove `py311` from `env_list` in `tox.toml` and remove the 3.11 classifier.
3. Run `uv python pin 3.12` so development uses the new lowest version.
4. Run `uv lock`, then `uv run --locked tox`.
5. Update the versions in `README.md`.

### Releasing

1. `uv version --bump patch` (or `minor`, `major`) updates the version in `pyproject.toml` and `uv.lock`. Use `minor` for a release with `feat` commits, and `major` for one with breaking changes.
2. `uv run --locked tox`.
3. Commit with `chore(release): <new version>`.
4. `uv build` writes the source distribution and wheel to `dist/`.

Publishing to PyPI is not set up yet. Before the first upload, change the README's icon to an absolute URL, because PyPI cannot display images referenced by a relative path. Then publish with `uv publish`.
