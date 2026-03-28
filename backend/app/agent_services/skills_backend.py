"""
skills_backend.py — Filesystem-backed skills for LangChain core agents.

This module provides a lightweight skill-management layer on top of LangChain
agents. Skills are plain Markdown files stored on disk; this module discovers
them at startup, exposes them to the agent via a system-prompt injection, and
lets the model fetch full instructions on demand through a dedicated tool.

Directory layout expected on disk::

    skills_dir/
        my_skill/
            SKILL.md            # frontmatter: name, description; body: instructions
        another_skill/
            SKILL.md

Markdown file format::

    ---
    name: my_skill
    description: Short summary of what this skill does.
    ---

    Full instructions go here as the Markdown body.
    Everything after the closing ``---`` is treated as the instructions field.

Typical usage::

    registry   = SkillsRegistry("/path/to/skills")
    middleware = SkillMiddleware(registry)
    agent      = MyLangChainAgent(middleware=middleware)

The middleware injects a human-readable skill catalogue into every system
prompt.  When the model decides it needs a skill it calls the ``load_skill``
tool, which returns the full instructions body from the matching Markdown file.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.messages import SystemMessage
from langchain.tools import tool
from pydantic import BaseModel

# Accepted filenames for skill definitions, in lookup priority order.
_MD_NAMES = ("SKILL.md", "skill.md")


def _parse_md_skill(text: str) -> tuple[dict, str]:
    """Parse a Markdown file with YAML frontmatter into metadata and body.

    Expects the file to open with a ``---`` delimiter, followed by valid YAML,
    closed by a second ``---`` line.  Everything after the closing delimiter is
    treated as the instructions body.

    Args:
        text (str): Raw file contents.

    Returns:
        tuple[dict, str]: A ``(frontmatter, body)`` pair where ``frontmatter``
            is the parsed YAML mapping and ``body`` is the stripped Markdown
            body text.

    Raises:
        ValueError: If the file does not begin with ``---`` or the frontmatter
            block is not properly closed.
    """
    if not text.startswith("---"):
        raise ValueError("File does not begin with a '---' frontmatter delimiter.")
    # Strip the opening ---
    rest = text[3:]
    try:
        close = rest.index("---")
    except ValueError:
        raise ValueError("Frontmatter block is never closed with '---'.")
    frontmatter_text = rest[:close]
    body = rest[close + 3:].strip()
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    return frontmatter, body


class SkillDefinition(BaseModel):
    """Immutable, validated representation of a single skill loaded from disk.

    Each instance corresponds to one SKILL.md file found inside the skills
    directory.  Instances are created by :class:`SkillsRegistry` and are never
    mutated after construction.

    Attributes:
        name (str): Unique, human-readable identifier for the skill.  Used as
            the lookup key inside :class:`SkillsRegistry` and referenced by
            the ``load_skill`` tool.  Sourced from the file's YAML frontmatter.
        description (str): Short, one-to-two sentence summary injected into the
            agent system prompt so the model can decide *whether* to call the
            skill without fetching the full instructions.  Sourced from the
            file's YAML frontmatter.
        instructions (str): The full, detailed guidance the model should follow
            when executing the skill.  This is the Markdown body that follows
            the closing ``---`` frontmatter delimiter.  Returned verbatim by
            ``load_skill``.
        source_path (str): Absolute filesystem path of the Markdown file from
            which this skill was loaded.  Useful for debugging and hot-reload
            scenarios.  Defaults to an empty string if not set.
    """

    name: str
    description: str
    instructions: str
    source_path: str = ""


class SkillsRegistry:
    """Scans a directory for SKILL.md files and maintains an in-memory cache.

    On construction the registry performs an eager directory walk, parsing
    every recognised Markdown file it finds.  The result is stored in a private
    dict keyed by skill name.  If a file cannot be parsed a warning is printed
    and that skill is skipped — the rest of the registry is unaffected.

    Markdown files must contain a YAML frontmatter block with at least ``name``
    and ``description`` keys.  The body (everything after the closing ``---``)
    is used as the ``instructions`` field.

    The registry can be refreshed at any time by calling :meth:`reload`, which
    clears and repopulates the cache without creating a new instance.

    Args:
        skills_dir (str | Path): Path to the root directory that contains one
            sub-directory per skill.  The path is resolved to an absolute path
            at construction time.

    Raises:
        FileNotFoundError: If ``skills_dir`` does not exist on the filesystem
            at the time :meth:`reload` is called.

    Example::

        registry = SkillsRegistry("/app/skills")
        for skill in registry.list_skills():
            print(skill.name, "—", skill.description)
    """

    def __init__(self, skills_dir: str | Path):
        self.skills_dir = Path(skills_dir).resolve()
        self._cache: dict[str, SkillDefinition] = {}
        self.reload()

    def reload(self) -> None:
        """Clear the cache and re-scan the skills directory from scratch.

        Iterates over every immediate sub-directory of :attr:`skills_dir`,
        looks for a Markdown file whose name matches one of the entries in
        ``_MD_NAMES`` (checked in order), parses its frontmatter and body,
        and stores the result as a :class:`SkillDefinition`.

        Skills are processed in alphabetical directory order so that the
        catalogue presented to the model is deterministic across runs.

        Invalid files (missing required frontmatter keys, parse errors, I/O
        errors) are logged to stdout and skipped silently so that a single bad
        file cannot block the entire registry from loading.

        Raises:
            FileNotFoundError: If :attr:`skills_dir` does not exist.
        """
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")
        self._cache.clear()
        for entry in sorted(self.skills_dir.iterdir()):
            if not entry.is_dir():
                continue
            md_path = next(
                (entry / f for f in _MD_NAMES if (entry / f).exists()), None
            )
            if not md_path:
                continue
            try:
                raw_text = md_path.read_text(encoding="utf-8")
                frontmatter, body = _parse_md_skill(raw_text)
                missing = [k for k in ("name", "description") if k not in frontmatter]
                if missing:
                    raise ValueError(f"Missing frontmatter keys: {missing}")
                if not body:
                    raise ValueError("Skill body (instructions) must not be empty.")
                self._cache[frontmatter["name"]] = SkillDefinition(
                    name=frontmatter["name"],
                    description=str(frontmatter["description"]).strip(),
                    instructions=body,
                    source_path=str(md_path),
                )
            except Exception as exc:
                print(f"[SkillsRegistry] Warning: could not load {md_path}: {exc}")

    def list_skills(self) -> list[SkillDefinition]:
        """Return all successfully loaded skills as an ordered list.

        Returns:
            list[SkillDefinition]: A snapshot of all currently cached skills.
                The order matches the alphabetical directory order used during
                the last :meth:`reload` call.
        """
        return list(self._cache.values())

    def get(self, name: str) -> SkillDefinition | None:
        """Look up a single skill by its exact name.

        Args:
            name (str): The skill name to look up (case-sensitive, must match
                the ``name`` field in the frontmatter exactly).

        Returns:
            SkillDefinition | None: The matching skill, or ``None`` if no skill
                with that name exists in the cache.
        """
        return self._cache.get(name)

    def names(self) -> list[str]:
        """Return the names of all currently cached skills.

        Returns:
            list[str]: Skill names in the same order as :meth:`list_skills`.
        """
        return list(self._cache.keys())


def make_load_skill_tool(registry: SkillsRegistry) -> tool:
    """Build and return a LangChain ``tool`` that fetches skill instructions.

    The returned tool is intended to be registered with a LangChain agent.
    When the model invokes it, it receives the full ``instructions`` text for
    the requested skill, formatted with a Markdown heading and a trailing
    reminder to follow the instructions.

    If the requested skill name is not found in the registry the tool returns a
    plain-text error message listing the available skill names, which allows
    the model to self-correct without raising a hard exception.

    Args:
        registry (SkillsRegistry): The registry instance to query.  The tool
            captures a reference to this object, so any subsequent
            :meth:`SkillsRegistry.reload` calls are reflected immediately.

    Returns:
        tool: A LangChain tool named ``"load_skill"`` that accepts a
            single ``skill_name`` string argument.

    Tool contract:
        - **Name**: ``load_skill``
        - **Input**: ``{ "skill_name": "<exact name>" }``
        - **Output (success)**: Markdown string with the skill's instructions.
        - **Output (failure)**: Plain-text message listing available skill names.

    Example (agent perspective)::

        # The model calls:
        load_skill(skill_name="summarise_pdf")
        # Returns:
        # # summarise_pdf
        # <full instructions body from SKILL.md>
        # ---
        # _Follow these instructions._
    """

    @tool
    def load_skill(skill_name: str) -> str:
        """Retrieve and format the instructions for *skill_name*.

        Args:
            skill_name (str): The exact name of the skill to load, as listed
                in the agent system prompt.

        Returns:
            str: Formatted Markdown string containing the skill instructions,
                or an error message if the skill was not found.
        """
        skill = registry.get(skill_name)
        if not skill:
            return (
                f"Skill '{skill_name}' not found. "
                f"Available: {', '.join(registry.names()) or '(none)'}."
            )
        return f"# {skill.name}\n\n{skill.instructions}\n\n---\n_Follow these instructions._"

    return load_skill


class SkillMiddleware(AgentMiddleware):
    """LangChain middleware that auto-injects the skills catalogue into every model call.

    On each invocation the middleware appends a formatted block listing all
    currently registered skills (name + description) to the system message,
    and ensures the ``load_skill`` tool is available to the model.

    This means neither the caller nor the agent definition need to know about
    specific skills — the catalogue is always up to date with whatever the
    :class:`SkillsRegistry` currently holds.

    Args:
        registry (SkillsRegistry): The registry whose skills should be
            advertised to the model.
        header (str): Markdown heading prepended to the skills block in the
            system prompt.  Defaults to ``"## Available Skills"``.

    Attributes:
        tools (list[Any]): List of LangChain tools exposed by this middleware.
            Always contains at least the ``load_skill`` tool built from the
            provided registry.

    Example::

        registry   = SkillsRegistry("/app/skills")
        middleware = SkillMiddleware(registry)
        agent      = MyAgent(middleware=middleware)
        # Every call to `agent.run(...)` will have the skills catalogue
        # appended to its system prompt automatically.
    """

    tools: list[Any] = []

    def __init__(self, registry: SkillsRegistry, header: str = "## Available Skills"):
        self.registry = registry
        self.header = header
        _load_skills = make_load_skill_tool(registry)
        self.tools = [_load_skills]

    def _skills_block(self) -> str:
        """Render the skills catalogue as a Markdown string.

        Builds a bulleted list of ``**name**: description`` entries, each on
        its own line, preceded by :attr:`header` and followed by a reminder
        instructing the model to call ``load_skill`` before executing any
        listed skill.

        Returns:
            str: The formatted Markdown block, or an empty string if the
                registry contains no skills (so that callers can short-circuit
                without appending meaningless content to the system prompt).
        """
        skills = self.registry.list_skills()
        if not skills:
            return ""
        lines = [self.header, ""] + [f"- **{s.name}**: {s.description}" for s in skills]
        lines += ["", "Use `load_skill` **before** attempting any listed skill."]
        return "\n".join(lines)

    def _build_request(self, request: ModelRequest) -> ModelRequest:
        """Shared logic for both sync and async paths."""
        block = self._skills_block()
        if not block:
            return request
        system_text = ""
        if len(request.system_message.content_blocks) > 0:
            system_text = request.system_message.content_blocks[0]["text"]
            
        
        new_blocks =  [
            {"type": "text", "text": f"{system_text}\n\n{block}"}
        ]
        return request.override(system_message=SystemMessage(content=new_blocks))

    def wrap_model_call(self, request: ModelRequest, handler):
        return handler(self._build_request(request))

    async def awrap_model_call(self, request: ModelRequest, handler):
        return await handler(self._build_request(request))
