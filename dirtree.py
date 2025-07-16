import fnmatch
import sys
import argparse
from pathlib import Path
from typing import List, Set

def get_ignore_patterns(root_dir: Path, additional_ignores: List[str]) -> Set[str]:
    """
    Gathers ignore patterns from a default list, an additional list, and a .gitignore file.
    """
    patterns = {
        '.git', '.github', '.vscode', '.idea', '.project', '.pydevproject',
        '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.env', 'venv', 
        'env', '.venv', '*.egg-info', '.DS_Store',
        '.pytest_cache', '.mypy_cache', '.coverage', '.coverage.*', 'htmlcov',
        'build', 'dist', 'node_modules', 'yarn-error.log', 'yarn.lock', 'package-lock.json',
    }
    if additional_ignores:
        patterns.update(additional_ignores)

    gitignore_path = root_dir / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    patterns.add(stripped_line.strip('/'))
    return patterns

# --- Text Tree Generation ---

def _generate_text_tree(directory: Path, prefix: str, ignore_patterns: Set[str]):
    """Recursive helper to generate and print the text directory tree."""
    try:
        # Filter entries based on ignore patterns
        entries = [e for e in directory.iterdir() if not any(fnmatch.fnmatch(e.name, p) for p in ignore_patterns)]
        # Sort entries by name
        entries.sort(key=lambda e: e.name)
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
        return

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        if entry.is_dir():
            print(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            _generate_text_tree(entry, prefix + extension, ignore_patterns)
        else:
            print(f"{prefix}{connector}{entry.name}")

def list_project_structure(root_dir_str: str, additional_ignores: List[str] = None):
    """Prints a text tree view of a project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return
    ignore_patterns = get_ignore_patterns(root_dir, additional_ignores or [])
    print(f"{root_dir.name}/")
    _generate_text_tree(root_dir, "", ignore_patterns)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a directory tree as text.",
        epilog="Example: python dirtree.py ./my_project"
    )
    parser.add_argument(
        "root_dir",
        nargs='?',
        default='.',
        help="The root directory of the project to scan (defaults to current directory)."
    )
    
    args = parser.parse_args()

    # Common IDE-specific folders to ignore
    ide_ignores = ['.vscode', '.idea', '.project', '.pydevproject']
    
    list_project_structure(args.root_dir, additional_ignores=ide_ignores)