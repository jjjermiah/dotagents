#!/usr/bin/env -S pixi exec --spec python=3.12 --spec pyyaml --spec rich -- python
"""List agents and skills from the dot-agents repository."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
from rich.console import Console
from rich.table import Table
from rich.tree import Tree


@dataclass
class Skill:
    name: str
    description: str
    path: Path


@dataclass
class Agent:
    name: str
    description: str
    mode: str | None
    path: Path


def parse_yaml_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None

    # Find the end of frontmatter
    match = re.search(r"^---\s*$(.+?)^---\s*$", content, re.MULTILINE | re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def collect_skills(src_path: Path) -> List[Skill]:
    """Collect all skills from the skills directory."""
    skills_dir = src_path / "dot-agents" / "skills"
    if not skills_dir.exists():
        return []

    skills = []
    for skill_path in skills_dir.rglob("SKILL.md"):
        # Skip the AGENTS.md in skills root
        if skill_path.parent == skills_dir:
            continue

        content = skill_path.read_text(encoding="utf-8")
        frontmatter = parse_yaml_frontmatter(content)

        if frontmatter and "name" in frontmatter:
            skills.append(
                Skill(
                    name=frontmatter.get("name", ""),
                    description=frontmatter.get("description", "")
                    .replace("\n", " ")
                    .strip(),
                    path=skill_path,
                )
            )

    return sorted(skills, key=lambda s: s.name)


def collect_agents(src_path: Path) -> List[Agent]:
    """Collect all agents from the agents directory."""
    agents_dir = src_path / "dot-config" / "opencode" / "agents"
    if not agents_dir.exists():
        return []

    agents = []
    for agent_path in agents_dir.glob("*.md"):
        content = agent_path.read_text(encoding="utf-8")
        frontmatter = parse_yaml_frontmatter(content)

        if frontmatter and "description" in frontmatter:
            name = agent_path.stem
            agents.append(
                Agent(
                    name=name,
                    description=frontmatter.get("description", "").strip(),
                    mode=frontmatter.get("mode"),
                    path=agent_path,
                )
            )

    return sorted(agents, key=lambda a: a.name)


def format_description(description: str, max_len: int | None = None) -> str:
    """Clean description for display, optionally truncating."""
    # Replace multiple spaces and newlines with single space
    desc = " ".join(description.split())
    if max_len and len(desc) > max_len:
        # Find the last space before max_len to break at word boundary
        trunc = desc[: max_len - 3]
        last_space = trunc.rfind(" ")
        if last_space > 0:
            trunc = trunc[:last_space]
        return trunc + "..."
    return desc


def extract_use_when(description: str, max_len: int = 100) -> str:
    """Extract the 'Use when' sentence and truncate to max_len chars at word boundary."""
    # Clean the description first
    desc = " ".join(description.split())

    # Find the "Use when" clause
    match = re.search(r"Use when[^.]*\.", desc, re.IGNORECASE)
    if match:
        use_when = match.group(0)
    else:
        # Fallback: if no "Use when" found, use the whole description
        use_when = desc

    # Truncate at max_len to end of word
    if len(use_when) > max_len:
        trunc = use_when[:max_len]
        last_space = trunc.rfind(" ")
        if last_space > 0:
            trunc = trunc[:last_space]
        return trunc + "..."

    return use_when


def output_table(skills: List[Skill], agents: List[Agent], console: Console) -> None:
    """Output results in a formatted table."""
    # Agents table
    if agents:
        console.print("\n[bold cyan]Agents[/bold cyan]")
        agent_table = Table(show_header=True, header_style="bold")
        agent_table.add_column("Name", style="green", min_width=15)
        agent_table.add_column("Mode", style="yellow", width=12)
        agent_table.add_column("Description")

        for agent in agents:
            agent_table.add_row(
                agent.name,
                agent.mode or "—",
                extract_use_when(agent.description),
            )
        console.print(agent_table)

    # Skills table
    if skills:
        console.print("\n[bold cyan]Skills[/bold cyan]")
        skill_table = Table(show_header=True, header_style="bold")
        skill_table.add_column("Name", style="green", min_width=20)
        skill_table.add_column("Description")

        for skill in skills:
            skill_table.add_row(skill.name, extract_use_when(skill.description))
        console.print(skill_table)


def build_tree_content(
    skills: List[Skill],
    agents: List[Agent],
    show_descriptions: bool = False,
    use_color: bool = True,
) -> str:
    """Build tree content as string, optionally with color codes."""
    # Plain text tree without color codes
    lines = ["dot-agents"]

    if agents:
        lines.append("├── Agents")
        for i, agent in enumerate(agents):
            is_last_agent = i == len(agents) - 1 and not skills
            prefix = "│   └── " if is_last_agent else "│   ├── "
            mode_str = f" ({agent.mode})" if agent.mode else ""
            lines.append(f"{prefix}{agent.name}{mode_str}")
            if show_descriptions:
                desc = extract_use_when(agent.description)
                # Indent description under agent
                desc_prefix = "│       " if is_last_agent else "│   │   "
                for line in _wrap_text(desc, 60):
                    lines.append(f"{desc_prefix}{line}")

    if skills:
        lines.append("└── Skills")
        for i, skill in enumerate(skills):
            is_last = i == len(skills) - 1
            prefix = "    └── " if is_last else "    ├── "
            lines.append(f"{prefix}{skill.name}")
            if show_descriptions:
                desc = extract_use_when(skill.description)
                desc_prefix = "        " if is_last else "    │   "
                for line in _wrap_text(desc, 60):
                    lines.append(f"{desc_prefix}{line}")

    return "\n".join(lines)


def _wrap_text(text: str, width: int) -> List[str]:
    """Wrap text into lines of max width, breaking at word boundaries."""
    if len(text) <= width:
        return [text]

    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_len += len(word) + (1 if current_len > 0 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [text]


def output_tree(
    skills: List[Skill],
    agents: List[Agent],
    console: Console,
    show_descriptions: bool = False,
    use_color: bool = True,
) -> None:
    """Output results in a tree structure."""
    if use_color:
        root = Tree("[bold cyan]dot-agents[/bold cyan]")

        if agents:
            agents_branch = root.add("[bold]Agents[/bold]")
            for agent in agents:
                mode_str = f" ([yellow]{agent.mode}[/yellow])" if agent.mode else ""
                if show_descriptions:
                    desc = extract_use_when(agent.description)
                    agents_branch.add(
                        f"[green]{agent.name}[/green]{mode_str}\n  [dim]{desc}[/dim]"
                    )
                else:
                    agents_branch.add(f"[green]{agent.name}[/green]{mode_str}")

        if skills:
            skills_branch = root.add("[bold]Skills[/bold]")
            for skill in skills:
                if show_descriptions:
                    desc = extract_use_when(skill.description)
                    skills_branch.add(
                        f"[green]{skill.name}[/green]\n  [dim]{desc}[/dim]"
                    )
                else:
                    skills_branch.add(f"[green]{skill.name}[/green]")

        console.print()
        console.print(root)
        console.print()
    else:
        content = build_tree_content(skills, agents, show_descriptions, use_color)
        console.print(content)


def output_compact(
    skills: List[Skill],
    agents: List[Agent],
    console: Console,
    show_descriptions: bool = False,
) -> None:
    """Output compact list view."""
    if agents:
        console.print("\n[bold cyan]Agents[/bold cyan]")
        for agent in agents:
            if agent.mode:
                console.print(
                    f"  [green]{agent.name}[/green] [dim]({agent.mode})[/dim]"
                )
            else:
                console.print(f"  [green]{agent.name}[/green]")
            if show_descriptions:
                desc = extract_use_when(agent.description)
                console.print(f"      [dim]{desc}[/dim]")

    if skills:
        console.print("\n[bold cyan]Skills[/bold cyan]")
        for skill in skills:
            console.print(f"  [green]{skill.name}[/green]")
            if show_descriptions:
                desc = extract_use_when(skill.description)
                console.print(f"      [dim]{desc}[/dim]")


def output_json(skills: List[Skill], agents: List[Agent]) -> None:
    """Output as JSON for programmatic use."""
    import json

    data = {
        "agents": [
            {
                "name": a.name,
                "description": a.description,
                "mode": a.mode,
                "path": str(a.path),
            }
            for a in agents
        ],
        "skills": [
            {"name": s.name, "description": s.description, "path": str(s.path)}
            for s in skills
        ],
    }

    console = Console(file=sys.stdout)
    console.print(json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List agents and skills from the dot-agents repository.",
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("src"),
        help="Path to the src directory (default: ./src)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "tree", "compact", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--agents-only",
        action="store_true",
        help="Show only agents",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="Show only skills",
    )
    parser.add_argument(
        "--show-descriptions",
        action="store_true",
        help="Show descriptions in tree and compact formats",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Output plain text without ANSI color codes",
    )

    args = parser.parse_args()

    # Resolve path relative to script location or cwd
    src_path = args.src
    if not src_path.is_absolute():
        # First try relative to script's parent (repo root)
        script_dir = Path(__file__).parent.parent
        alt_path = script_dir / src_path
        if alt_path.exists():
            src_path = alt_path
        else:
            src_path = src_path.resolve()

    if not src_path.exists():
        print(f"Error: Source path does not exist: {src_path}", file=sys.stderr)
        return 1

    agents = []
    skills = []

    if not args.skills_only:
        agents = collect_agents(src_path)

    if not args.agents_only:
        skills = collect_skills(src_path)

    console = Console(file=sys.stdout)

    if args.format == "json":
        output_json(skills, agents)
    elif args.format == "tree":
        output_tree(skills, agents, console, args.show_descriptions, not args.no_color)
    elif args.format == "compact":
        output_compact(skills, agents, console, args.show_descriptions)
    else:
        output_table(skills, agents, console)

    # Summary
    if not args.format == "json":
        console.print(f"\n[dim]Total: {len(agents)} agents, {len(skills)} skills[/dim]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
