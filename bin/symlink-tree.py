#!/usr/bin/env -S pixi exec --spec python=3.12 --spec rich -- python
"""Tree view of symlinked files managed by stow.

Finds all symbolic links in a target directory (default: $HOME) and displays
them in a rich tree structure with their full paths and link targets.

Usage:
    symlink-tree.py [PATH] [--depth N]

Examples:
    symlink-tree.py ~                    # Show all symlinks in home
    symlink-tree.py ~/.config --depth 2  # Show symlinks, limit depth
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

console = Console()


def has_symlinks_recursive(
    path: Path, current_depth: int, max_depth: int | None
) -> bool:
    """Fast check if directory or subdirectories contain any symlinks.

    Args:
        path: Directory to check
        current_depth: Current recursion depth
        max_depth: Maximum depth to search (None for unlimited)

    Returns:
        True if any symlinks exist in this tree within depth limit
    """
    if max_depth is not None and current_depth > max_depth:
        return False

    try:
        for entry in path.iterdir():
            if entry.is_symlink():
                # Only count if within depth limit
                if max_depth is None or current_depth <= max_depth:
                    return True
            if entry.is_dir() and not entry.is_symlink():
                if has_symlinks_recursive(entry, current_depth + 1, max_depth):
                    return True
    except (PermissionError, OSError):
        pass

    return False


def build_symlink_tree(
    root_dir: Path,
    current_dir: Path,
    parent_tree: Tree,
    current_depth: int = 0,
    max_depth: int | None = None,
) -> bool:
    """Recursively build rich tree structure of symlinks.

    Args:
        root_dir: Root directory being scanned
        current_dir: Current directory to process
        parent_tree: Parent rich Tree node to attach children to
        current_depth: Current recursion depth
        max_depth: Maximum depth limit (None for unlimited)

    Returns:
        True if any symlinks were found in this branch
    """
    if max_depth is not None and current_depth > max_depth:
        return False

    found_symlinks = False

    try:
        entries = sorted(
            current_dir.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())
        )
    except PermissionError:
        parent_tree.add(Text("[Permission denied]", style="red"))
        return False
    except OSError as e:
        parent_tree.add(Text(f"[Error: {e}]", style="red"))
        return False

    for entry in entries:
        if entry.is_symlink():
            # Check depth: symlinks at current depth
            entry_depth = len(entry.relative_to(root_dir).parts)
            if max_depth is not None and entry_depth > max_depth:
                continue

            found_symlinks = True
            try:
                target = entry.readlink()
                if target.is_absolute():
                    target_display = str(target)
                else:
                    resolved = entry.parent / target
                    # Use absolute() to avoid following symlinks, with try/except for circular links
                    try:
                        target_display = str(resolved.resolve())
                    except (OSError, RuntimeError):
                        # Circular symlink or can't resolve
                        target_display = str(resolved.absolute())

                # Build styled text for the symlink
                label = Text()
                label.append(entry.name, style="cyan")
                label.append(" -> ")
                label.append(target_display, style="dim")

                # Check if symlink target exists (follows symlinks - that's what we want)
                is_broken = False
                try:
                    if not target.exists():
                        is_broken = True
                except (OSError, RuntimeError):
                    is_broken = True

                if is_broken:
                    label.append(" [broken]", style="red")

                parent_tree.add(label)
            except OSError as e:
                label = Text()
                label.append(entry.name, style="cyan")
                label.append(f" -> [broken: {e}]", style="red")
                parent_tree.add(label)
        elif entry.is_dir() and not entry.is_symlink():
            # Only create directory node if it has symlinks (or subdirs with symlinks)
            if has_symlinks_recursive(entry, current_depth + 1, max_depth):
                dir_node = parent_tree.add(Text(f"{entry.name}/", style="blue"))
                sub_found = build_symlink_tree(
                    root_dir, entry, dir_node, current_depth + 1, max_depth
                )
                if not sub_found:
                    parent_tree.children.remove(dir_node)
                else:
                    found_symlinks = True

    return found_symlinks


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 on success, 1 on error
    """
    parser = argparse.ArgumentParser(
        description="Display symlinks in a tree structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="~",
        help="Directory to scan (default: ~)",
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=int,
        default=None,
        help="Maximum depth to scan (default: unlimited)",
    )

    args = parser.parse_args()

    target = Path(args.path).expanduser()
    # Use absolute() not resolve() to avoid following symlinks
    target = target.absolute()

    if not target.exists():
        console.print(f"[red]Error: Path does not exist: {target}[/red]")
        return 1

    if not target.is_dir():
        console.print(f"[red]Error: Not a directory: {target}[/red]")
        return 1

    # Create root tree
    depth_info = f" (depth: {args.depth})" if args.depth else ""
    root_label = Text()
    root_label.append(str(target), style="bold green")
    root_label.append("/", style="bold green")
    root_label.append(depth_info, style="dim")
    root_tree = Tree(root_label)

    # Build tree
    found = build_symlink_tree(target, target, root_tree, max_depth=args.depth)

    if not found:
        console.print(f"[yellow]No symlinks found in {target}[/yellow]")
        return 0

    # Print tree
    console.print(root_tree)

    # Print summary
    symlink_count = sum(
        1
        for p in target.rglob("*")
        if p.is_symlink()
        and (args.depth is None or len(p.relative_to(target).parts) <= args.depth)
    )
    console.print(f"\n[dim]Symlinks shown: {symlink_count}[/dim]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
