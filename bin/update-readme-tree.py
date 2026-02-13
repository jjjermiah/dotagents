#!/usr/bin/env -S pixi exec --spec python=3.12 -- python
"""Update the README agents/skills tree section between markers."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_tree_output(src_path: Path) -> str:
    """Run list-agents-skills.py and return plain tree output."""
    script = Path(__file__).parent / "list-agents-skills.py"
    result = subprocess.run(
        [
            str(script),
            "--format",
            "tree",
            "--show-descriptions",
            "--no-color",
            "--src",
            str(src_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def update_readme(readme_path: Path, tree_content: str) -> bool:
    """Update the README section between markers. Returns True if changed."""
    readme_content = readme_path.read_text(encoding="utf-8")

    # Pattern to match content between markers
    pattern = r"(<!-- AGENTS-SKILLS-TREE:START -->\n```console\n)(.*?)(```\n<!-- AGENTS-SKILLS-TREE:END -->)"

    match = re.search(pattern, readme_content, re.DOTALL)
    if not match:
        print(
            "Error: Could not find AGENTS-SKILLS-TREE markers in README",
            file=sys.stderr,
        )
        return False

    # Build new content
    new_section = f"<!-- AGENTS-SKILLS-TREE:START -->\n```console\n{tree_content}\n```\n<!-- AGENTS-SKILLS-TREE:END -->"

    if match.group(0) == new_section:
        print("README is already up to date")
        return False

    # Replace the section
    new_content = (
        readme_content[: match.start()] + new_section + readme_content[match.end() :]
    )
    readme_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {readme_path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update README agents/skills tree section.",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="Path to README file (default: ./README.md)",
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("src"),
        help="Path to src directory (default: ./src)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if README is up to date (exit 1 if not)",
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent.parent
    readme_path = args.readme if args.readme.is_absolute() else script_dir / args.readme
    src_path = args.src if args.src.is_absolute() else script_dir / args.src

    if not readme_path.exists():
        print(f"Error: README not found: {readme_path}", file=sys.stderr)
        return 1

    if not src_path.exists():
        print(f"Error: Source path not found: {src_path}", file=sys.stderr)
        return 1

    try:
        tree_content = get_tree_output(src_path)
    except subprocess.CalledProcessError as e:
        print(f"Error running list-agents-skills.py: {e}", file=sys.stderr)
        return 1

    if args.check:
        readme_content = readme_path.read_text(encoding="utf-8")
        pattern = r"<!-- AGENTS-SKILLS-TREE:START -->\n```console\n(.*?)```\n<!-- AGENTS-SKILLS-TREE:END -->"
        match = re.search(pattern, readme_content, re.DOTALL)
        if not match:
            print("Error: Could not find markers in README", file=sys.stderr)
            return 1

        current_content = match.group(1).strip()
        if current_content != tree_content:
            print(
                "README is out of date. Run: python bin/update-readme-tree.py",
                file=sys.stderr,
            )
            return 1
        print("README is up to date")
        return 0

    if update_readme(readme_path, tree_content):
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
