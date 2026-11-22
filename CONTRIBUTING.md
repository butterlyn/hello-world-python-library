# Contributing

How to maintain this library. Written for both humans and AI agents: every step is a command you can run as-is from the repository root.

## Tooling

| Tool | Job | Configured in |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Python versions, virtual environment, dependencies, lockfile, builds | `pyproject.toml`, `uv.lock`, `.python-version` |
| [Hatchling](https://hatch.pypa.io/latest/config/build/) | Build backend: turns the source into the wheel and the source distribution | `[build-system]` and `[tool.hatch.build]` in `pyproject.toml` |
| [tox](https://tox.wiki/) + [tox-uv](https://github.com/tox-dev/tox-uv) | Runs the tests on every supported Python version, plus lint | `tox.toml` |
| [pytest](https://docs.pytest.org/) | Unit tests | `[tool.pytest]` in `pyproject.toml` |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting | `[tool.ruff]` in `pyproject.toml` |
| [prek](https://prek.j178.dev/) | Git pre-commit hooks: Ruff, file hygiene, lockfile sync, documentation build | `prek.toml` |
| [Library Skills](https://library-skills.io/) | Installs the agent skills that dependencies bundle, for coding agents | the `dev` group in `pyproject.toml`; installs into `.agents/skills/` and `.claude/skills/` |
| [Great Docs](https://posit-dev.github.io/great-docs/) + [Quarto](https://quarto.org/) | Generate the documentation site from the README, `CONTRIBUTING.md`, `LICENSE`, the docstrings, the click command and the pages in `docs/` | `great-docs.yml`, `docs/`, the `docs` group in `pyproject.toml` |
| GitHub Actions | Runs the full check on Linux, macOS and Windows for pushes to `main` and pull requests; builds the documentation and publishes it to GitHub Pages | `.github/workflows/ci.yml`, `.github/workflows/docs.yml` |

## Setup

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/). It downloads every Python version the project needs, so you don't need to install Python yourself.
2. From the repository root:

   ```console
   uv sync               # create .venv with the project and all development tools
   uv run prek install   # install the Git pre-commit hook
   ```

3. If you work with a coding agent, install the agent skills that the dependencies bundle. See [Agent skills from dependencies](#agent-skills-from-dependencies).

The development environment runs on the lowest supported Python (pinned in `.python-version`), so code that only works on newer versions fails locally first.

`uv sync` leaves out the documentation tools, because they are large: Great Docs pulls in Jupyter, and Quarto is a few hundred MB. The docs commands below add them with `--group docs`. The first time, uv builds Quarto from its PyPI package, which takes about a minute. After that it comes from uv's cache.

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
| `uv run --locked --group docs great-docs build` | Build the documentation site into `great-docs/_site/`, the same as the docs hook and CI. |
| `uv run --locked --group docs great-docs preview` | Serve the built site on <http://localhost:3000> and open it in your browser. |

Things to know:

- **Always pass `--locked` when verifying.** Plain `uv run` quietly updates `uv.lock` to match `pyproject.toml` before running anything, which would hide a stale lockfile. With `--locked`, a stale `uv.lock` fails instead. Run `uv lock` to fix it, then commit `uv.lock`.
- **tox tests the built wheel**, not your source folder. Each run rebuilds and installs the wheel, so the tests also catch packaging mistakes. `uv run pytest` uses an editable install, for speed.
- **Lint has two modes.** `tox -e lint` runs the check-only hooks (the `manual` stage in `prek.toml`). The commit hook and `prek run` run the fixing hooks (the `pre-commit` stage). Change both variants of a hook together.
- **prek only sees files Git tracks.** `git add` new files before running `tox -e lint` or `prek run --all-files`.
- **Commits rebuild the documentation.** If a commit touches `src/`, `docs/`, `assets/`, `skills/`, the README, `CONTRIBUTING.md`, `LICENSE`, `great-docs.yml`, `pyproject.toml` or `uv.lock`, the `great-docs-build` hook builds the whole site (about 20 seconds). A broken page or a failing example stops the commit, and the error is printed above the hook result. The hook runs only at commit time, so `tox -e lint` doesn't need Quarto. CI builds the docs in the Docs workflow instead.

## Making a change

1. Add or update a test in `tests/` that describes the new behaviour.
2. Change the code in `src/hello_world_python_library/`.
3. Run `uv run --locked tox`. Every environment must end in `OK`.
4. Commit with a [Conventional Commits](#commit-messages) message. The pre-commit hook then runs the fixing hooks. If one rewrote a file, review the change, `git add` it, and commit again.

Code map:

| Path | Contents |
| --- | --- |
| `src/hello_world_python_library/__init__.py` | Public API: `GREETING` and `greet()` |
| `src/hello_world_python_library/cli.py` | The `hello-world` command, built with [click](https://click.palletsprojects.com/) as `hello_world`; entry point `main()` |
| `src/hello_world_python_library/__main__.py` | Makes `python -m hello_world_python_library` work |
| `src/hello_world_python_library/py.typed` | Tells type checkers the package ships type hints |
| `skills/hello-world-python-library/` | The agent skill for people who use the library: `SKILL.md` and `references/`. See [The agent skill](#the-agent-skill) |
| `tests/` | The pytest suite, including end-to-end runs of the installed `hello-world` launcher and checks of the skill inside the installed package |
| `docs/` | Hand-written documentation pages (Quarto `.qmd` files), shown under "User Guide" on the site |
| `great-docs.yml` | Great Docs settings. Every option is listed with its default; the uncommented lines are the ones this project changes |

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
| Documentation build | `uv add --group docs <pkg>` | `uv remove --group docs <pkg>` |
| Other development tools | `uv add --dev <pkg>` | `uv remove --dev <pkg>` |

To upgrade every locked version, run `uv lock --upgrade` and then `uv run --locked tox`. Always commit `uv.lock`, using the `build:` type.

The `dev` group includes the `test` and `lint` groups, so `uv sync` installs everything except the `docs` group (see [Setup](#setup)). Each tox environment installs only the group it needs.

### Agent skills from dependencies

Some libraries bundle an [agent skill](https://agentskills.io/) inside their package, at `<package>/.agents/skills/<name>/SKILL.md`. [Library Skills](https://library-skills.io/) finds the skills bundled by this project's direct dependencies, meaning the runtime dependencies and every dependency group. It installs them into `.agents/skills/`, which most coding agents read, and, with `--claude`, into `.claude/skills/`, which Claude Code reads. Both folders are gitignored, so run it once in each checkout, and again after adding or upgrading dependencies.

| Command | What it does |
| --- | --- |
| `uv run library-skills scan` | List the skills that direct dependencies bundle. `--all` adds indirect dependencies. |
| `uv run library-skills --claude` | Pick skills from a menu and install them. Needs an interactive terminal; without one it waits forever. |
| `uv run library-skills install --claude --yes --skill <name>` | Install one skill without prompts, for scripts and agents. `--yes` on its own installs nothing new, and `--all` also installs the skills of indirect dependencies. |
| `uv run library-skills list --installed --claude` | Show the installed skills and whether each is up to date. |

An empty `scan` is expected for now: none of the direct dependencies bundles a skill yet. `scan --all` does find one, for Typer, which is only there because library-skills depends on it.

Each installed skill is a symlink into `.venv`, so it follows upgrades on its own. On Windows, creating symlinks needs Developer Mode. Without it, add `--copy`. library-skills treats a copy as hand-written and never overwrites it, so after an upgrade, delete the copied folders from `.agents/skills/` and `.claude/skills/` and install again.

### The agent skill

The library's own skill, for people who use it, lives in `skills/hello-world-python-library/`. `SKILL.md` holds only what every use of the skill needs: a table that sends each kind of task to one file in `references/`. Everything else goes in those files, so an agent reads only what its task needs. Update the skill in the same commit as any change to the `hello-world` command, the public API or the install instructions.

Users get the skill from that one folder in three ways:

| Install route | How the skill gets there | Configured in |
| --- | --- | --- |
| Library Skills, from the installed package | The wheel ships the folder as `hello_world_python_library/.agents/skills/hello-world-python-library/`, where Library Skills looks in installed packages | `[tool.hatch.build.targets.wheel.force-include]` in `pyproject.toml` |
| `npx skills add <docs site URL>` | Great Docs copies the folder to `.well-known/agent-skills/hello-world-python-library/` on the site, lists its files in `.well-known/agent-skills/index.json`, and shows it on the Skills page | `skill.skills` in `great-docs.yml` |
| `npx skills add butterlyn/hello-world-python-library` | `npx skills` clones the repository and searches `skills/` | nothing: the folder's location is enough |

The README shows the install commands. Things to know:

- **`name` must equal the folder name**, in lowercase letters, digits and single hyphens. Library Skills skips a skill that breaks this rule. To rename the skill, rename the folder and update `great-docs.yml`, `tests/test_skill.py` and the README.
- **`description` is at most 1024 characters.** Agents read it to decide when to load the skill, so it names the cases the skill covers.
- **Keep the `skill.skills` list in `great-docs.yml`.** `skill.file`, and Great Docs' automatic detection of `skills/<package-name>/`, publish `SKILL.md` without `references/`.
- **`tests/test_skill.py` checks the installed copy**: that the package ships the skill where Library Skills looks, that the frontmatter follows the rules above, and that every relative link leads to a file in the skill. Under tox, that is the copy inside the built wheel.
- **`uv sync` installs a copy of the skill in `.venv`, not a link**, because the folder is outside the package. The `cache-keys` setting in `pyproject.toml` makes uv reinstall the project whenever a file in `skills/` changes, so `uv run pytest` always checks your current edits.
- **To see what the docs site publishes**, build the docs and look in `great-docs/_site/.well-known/agent-skills/`.

### Hook versions

`uv run prek update --freeze` moves every hook repository in `prek.toml` to its latest release, pinned to the exact commit with the tag name in a `# frozen:` comment. Always pass `--freeze`, so the pins stay reproducible. Then run `uv run --locked tox -e lint` and commit with `chore: update prek hook revisions`.

Keep the `uv-pre-commit` revision on the same uv version that you develop with.

### GitHub Actions versions

The actions in `.github/workflows/ci.yml` and `.github/workflows/docs.yml` are pinned to full commit SHAs, with the tag in a trailing comment. To update one, look up the new tag's commit with `git ls-remote --tags https://github.com/<owner>/<action>`. Then replace both the SHA and the comment, and commit with the `ci:` type.

### Documentation

The site is generated, so most changes need no docs work:

| Page on the site | Generated from |
| --- | --- |
| Home | `README.md` |
| User Guide | the `.qmd` and `.md` files in `docs/` |
| Reference: API | the names in `__all__` and their docstrings |
| Reference: CLI | the click command `hello_world` in `cli.py`, through its `--help` text |
| Skills, and the files under `.well-known/agent-skills/` | `skills/hello-world-python-library/` (see [The agent skill](#the-agent-skill)) |
| Contributing, License | `CONTRIBUTING.md`, `LICENSE` |

- **Adding a page:** add a Quarto `.qmd` file to `docs/`. Python code cells run during the build. `docs/examples.qmd` uses them to show what the command really prints, and sets `freeze: false` so the output is fresh on every build.
- **Links in the README:** use absolute GitHub URLs for other files in the repository, such as `CONTRIBUTING.md`. The README is also the site's homepage, where relative links to repository files lead nowhere.
- **Settings:** change `great-docs.yml`. `uv run --locked --group docs great-docs config --force` regenerates the file with every option at its default, which removes this project's settings, so copy them back afterwards.
- **Upgrading Great Docs or Quarto:** `uv lock --upgrade-package great-docs --upgrade-package quarto-cli`, then build the docs. Commit with the `build:` type.
- **Quarto on Windows:** `quarto-cli` is published only as a source distribution, which downloads Quarto and packs it into a wheel. The `[tool.uv.config-settings-package]` table in `pyproject.toml` shortens setuptools' build folder so Quarto's deepest files stay under Windows' 260-character path limit. Enabling Windows long paths also fixes this. If a build of `quarto-cli` failed before that, uv keeps the half-built folder: run `uv cache clean quarto-cli` and try again.

Publishing: on every push to `main`, the Docs workflow builds the site and deploys it to GitHub Pages at <https://butterlyn.github.io/hello-world-python-library/>. Pull requests only build it. To view a pull request's build, run `uv run --locked --group docs great-docs preview --pr <number> --use-gh`, which downloads the build through your `gh` login. One-time setup: in the repository's **Settings → Pages**, set **Source** to **GitHub Actions**. GitHub Free can publish Pages only from public repositories.

### The build backend

[Hatchling](https://hatch.pypa.io/latest/config/build/) builds the wheel and the source distribution. `uv build`, tox and `uv sync` all call it through `[build-system]` in `pyproject.toml`, and its settings are under `[tool.hatch.build]`:

- **The wheel** holds `src/hello_world_python_library/`, which Hatchling finds from the project name, and the skill, which `force-include` maps from `skills/` into the package (see [The agent skill](#the-agent-skill)).
- **The source distribution** holds only what `only-include` lists, `src/`, `skills/` and `assets/icon.svg`, plus the files Hatchling always adds: `pyproject.toml`, the README, the license and `.gitignore`. `uv build` builds the wheel from the source distribution, so everything the wheel needs must be in that list. The icon is there so the README renders when the archive is unpacked.

`[build-system]` asks for `hatchling>=1.33.0`, the latest release when the project switched to Hatchling. Each build installs the newest Hatchling that matches, so raise the minimum only when the project needs a newer Hatchling feature.

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

Publishing to PyPI is not set up yet. Before the first upload, change the README's icon to an absolute URL, because PyPI cannot display images referenced by a relative path. Then publish with `uv publish`, and delete `pypi: false` from `great-docs.yml` so the documentation links to the PyPI page.
