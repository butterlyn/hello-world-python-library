"""The agent skill in skills/ ships inside the installed package.

library-skills finds a skill through an installed distribution's RECORD file, at
<package>/.agents/skills/<name>/SKILL.md, and installs the whole <name>/ folder.
These tests read that installed copy, so under tox they check the built wheel.
"""

import posixpath
import re
from importlib.metadata import distribution
from pathlib import Path, PurePosixPath

import pytest
import yaml

DISTRIBUTION = "hello-world-python-library"
SKILL_FOLDER = PurePosixPath(
    "hello_world_python_library", ".agents", "skills", "hello-world-python-library"
)
SKILL_MD = PurePosixPath("SKILL.md")
# Limits from the Agent Skills specification, https://agentskills.io/specification
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.DOTALL)
FENCED_CODE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
# The target of a Markdown link or image: [text](target) or ![alt](target).
LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")


@pytest.fixture(scope="module")
def skill_files() -> dict[PurePosixPath, Path]:
    """Map each installed file of the skill, relative to the skill folder, to its path."""
    dist = distribution(DISTRIBUTION)
    files = {
        PurePosixPath(file).relative_to(SKILL_FOLDER): Path(dist.locate_file(file))
        for file in dist.files or []
        if PurePosixPath(file).is_relative_to(SKILL_FOLDER)
    }
    assert files, f"the installed package has no files in {SKILL_FOLDER}"
    return files


def test_skill_ships_with_its_references(
    skill_files: dict[PurePosixPath, Path],
) -> None:
    assert SKILL_MD in skill_files
    assert any(path.parts[0] == "references" for path in skill_files)


def test_skill_frontmatter_follows_the_agent_skills_rules(
    skill_files: dict[PurePosixPath, Path],
) -> None:
    text = skill_files[SKILL_MD].read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    assert match, "SKILL.md must start with YAML frontmatter between --- lines"
    metadata = yaml.safe_load(match.group(1))

    # library-skills skips a skill whose name differs from its folder name.
    name = metadata["name"]
    assert name == SKILL_FOLDER.name
    assert SKILL_NAME.fullmatch(name)
    assert len(name) <= MAX_NAME_LENGTH

    description = metadata["description"]
    assert isinstance(description, str)
    assert 0 < len(description.strip()) <= MAX_DESCRIPTION_LENGTH


def test_skill_links_lead_to_files_in_the_skill(
    skill_files: dict[PurePosixPath, Path],
) -> None:
    broken = []
    for path, file in skill_files.items():
        if path.suffix != ".md":
            continue
        prose = FENCED_CODE.sub("", file.read_text(encoding="utf-8"))
        for target in LINK_TARGET.findall(prose):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            linked = posixpath.normpath(path.parent / target.partition("#")[0])
            if PurePosixPath(linked) not in skill_files:
                broken.append(f"{path} -> {target}")
    assert broken == []
