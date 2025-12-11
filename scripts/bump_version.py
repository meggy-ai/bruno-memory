#!/usr/bin/env python3
"""Version bumping script for bruno-memory."""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

VersionPart = Literal["major", "minor", "patch"]


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    match = re.search(r'^version = "(\d+\.\d+\.\d+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def bump_version(current: str, part: VersionPart) -> str:
    """Bump the specified part of the version."""
    major, minor, patch = map(int, current.split("."))
    
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid version part: {part}")


def update_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    updated = re.sub(
        r'^version = "\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    pyproject.write_text(updated)
    print(f"✓ Updated pyproject.toml to version {new_version}")


def update_init(new_version: str) -> None:
    """Update version in __init__.py."""
    init_file = Path("bruno_memory/__init__.py")
    content = init_file.read_text()
    
    # Update __version__
    updated = re.sub(
        r'^__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    init_file.write_text(updated)
    print(f"✓ Updated bruno_memory/__init__.py to version {new_version}")


def create_git_tag(version: str, commit: bool = True) -> None:
    """Create git commit and tag for the version bump."""
    if commit:
        subprocess.run(["git", "add", "pyproject.toml", "bruno_memory/__init__.py"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Bump version to {version}"],
            check=True
        )
        print(f"✓ Created git commit for version {version}")
    
    subprocess.run(
        ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"],
        check=True
    )
    print(f"✓ Created git tag v{version}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bump bruno-memory version")
    parser.add_argument(
        "part",
        type=str,
        choices=["major", "minor", "patch"],
        help="Part of version to bump"
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Don't create git commit"
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Don't create git tag"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        new_version = bump_version(current_version, args.part)
        
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        
        if args.dry_run:
            print("\nDry run - no changes made")
            return 0
        
        # Update files
        update_pyproject(new_version)
        update_init(new_version)
        
        # Create git commit and tag
        if not args.no_tag:
            create_git_tag(new_version, commit=not args.no_commit)
        
        print(f"\n✓ Successfully bumped version to {new_version}")
        print("\nNext steps:")
        print(f"  git push origin main")
        print(f"  git push origin v{new_version}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
