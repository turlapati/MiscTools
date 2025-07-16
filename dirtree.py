import fnmatch
import sys
import argparse
from pathlib import Path
from typing import List, Set

def get_ignore_patterns(root_dir: Path) -> Set[str]:
    """
    Gathers ignore patterns from a default list and all '.*ignore' files in the root directory.
    """
    patterns = {
        # Default patterns
        '.git', '.github', '.vscode', '.idea', '.project', '.pydevproject',
        '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.env', 'venv', 
        'env', '.venv', '*.egg-info', '.DS_Store',
        '.pytest_cache', '.mypy_cache', '.coverage', '.coverage.*', 'htmlcov',
        'build', 'dist', 'node_modules', 'yarn-error.log', 'yarn.lock', 'package-lock.json',
    }

    # Find and process all '.*ignore' files
    for ignore_file in root_dir.glob('.*ignore'):
        if ignore_file.is_file():
            with open(ignore_file, 'r', encoding='utf-8') as f:
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

def list_project_structure(root_dir_str: str):
    """Prints a text tree view of a project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return
    ignore_patterns = get_ignore_patterns(root_dir)
    print(f"{root_dir.name}/")
    _generate_text_tree(root_dir, "", ignore_patterns)

# --- Markdown Tree Generation ---

def _generate_markdown_tree(directory: Path, prefix: str, ignore_patterns: Set[str], lines: List[str]):
    """Recursive helper to build the Markdown directory tree."""
    try:
        entries = [e for e in directory.iterdir() if not any(fnmatch.fnmatch(e.name, p) for p in ignore_patterns)]
        entries.sort(key=lambda e: e.name)
    except PermissionError:
        lines.append(f"{prefix}- [Permission Denied]")
        return

    for entry in entries:
        if entry.is_dir():
            lines.append(f'{prefix}<details>')
            lines.append(f'{prefix}  <summary>📁 {entry.name}/</summary>\n')
            _generate_markdown_tree(entry, prefix + '  ', ignore_patterns, lines)
            lines.append(f'{prefix}</details>')
        else:
            lines.append(f"{prefix}- 📄 {entry.name}")

def generate_markdown_file(root_dir_str: str, output_file: str):
    """Generates an interactive Markdown file of the project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return

    ignore_patterns = get_ignore_patterns(root_dir)
    lines = [f"# Directory Tree for {root_dir.name}\n"]
    
    _generate_markdown_tree(root_dir, "", ignore_patterns, lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Successfully generated interactive tree at '{output_file}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a directory tree as text or interactive Markdown.",
        epilog="Example: python dirtree.py ./my_project --format markdown --output tree.md"
    )
    parser.add_argument(
        "root_dir",
        nargs='?',
        default='.',
        help="The root directory to scan (defaults to current directory)."
    )
    parser.add_argument(
        "--format",
        choices=['text', 'markdown'],
        default='text',
        help="Output format (defaults to 'text')."
    )
    parser.add_argument(
        "--output",
        default='directory_tree.md',
        help="Output file name for Markdown format (defaults to 'directory_tree.md')."
    )
    
    args = parser.parse_args()
    
    if args.format == 'markdown':
        generate_markdown_file(args.root_dir, args.output)
    else:
        list_project_structure(args.root_dir)