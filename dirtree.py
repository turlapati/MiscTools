import os
import fnmatch
import sys
import argparse
import re
import time
from pathlib import Path
from typing import List, Set, Optional

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

def parse_time_expression(time_expr: str) -> Optional[float]:
    """
    Parse time expressions like '2h', '30m', '7d' and return seconds.
    Returns None if the expression is invalid.
    """
    if not time_expr:
        return None
    
    match = re.match(r'^(\d+)([mhd])$', time_expr.lower())
    if not match:
        return None
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'm':  # minutes
        return value * 60
    elif unit == 'h':  # hours
        return value * 3600
    elif unit == 'd':  # days
        return value * 86400
    
    return None

def should_include_by_time(path: Path, newer_than: Optional[float], older_than: Optional[float]) -> bool:
    """
    Check if a file/directory should be included based on time filters.
    """
    if newer_than is None and older_than is None:
        return True
    
    try:
        mtime = path.stat().st_mtime
        current_time = time.time()
        
        if newer_than is not None:
            if current_time - mtime > newer_than:
                return False
        
        if older_than is not None:
            if current_time - mtime < older_than:
                return False
        
        return True
    except (OSError, PermissionError):
        return True  # Include if we can't get stats

def _has_matching_content(directory: Path, ignore_patterns: Set[str], 
                         max_depth: Optional[int] = None, current_depth: int = 0,
                         dirs_only: bool = False, newer_than: Optional[float] = None, 
                         older_than: Optional[float] = None, prune_empty: bool = False) -> bool:
    """
    Check if a directory has any content that would match the current filters.
    Returns True if the directory should be included, False if it should be pruned.
    """
    if max_depth is not None and current_depth >= max_depth:
        return False
        
    try:
        # Filter entries based on ignore patterns
        entries = [e for e in directory.iterdir() if not any(fnmatch.fnmatch(e.name, p) for p in ignore_patterns)]
        
        # Filter by time if specified
        if newer_than is not None or older_than is not None:
            entries = [e for e in entries if should_include_by_time(e, newer_than, older_than)]
        
        # Filter by dirs_only if specified
        if dirs_only:
            entries = [e for e in entries if e.is_dir()]
        
        # Check if we have any files that would be shown
        if not dirs_only:
            files = [e for e in entries if not e.is_dir()]
            if files:
                return True
        
        # Check if any subdirectories would have content
        for entry in entries:
            if entry.is_dir():
                if _has_matching_content(entry, ignore_patterns, max_depth, current_depth + 1,
                                       dirs_only, newer_than, older_than, prune_empty):
                    return True
        
        return False
    except (OSError, PermissionError):
        return True  # Include if we can't check

# --- Text Tree Generation ---

def _generate_text_tree(directory: Path, prefix: str, ignore_patterns: Set[str], 
                       max_depth: Optional[int] = None, current_depth: int = 0,
                       dirs_only: bool = False, newer_than: Optional[float] = None, 
                       older_than: Optional[float] = None, prune_empty: bool = False):
    """Recursive helper to generate and print the text directory tree."""
    if max_depth is not None and current_depth >= max_depth:
        return
        
    try:
        # Filter entries based on ignore patterns
        entries = [e for e in directory.iterdir() if not any(fnmatch.fnmatch(e.name, p) for p in ignore_patterns)]
        
        # Filter by time if specified
        if newer_than is not None or older_than is not None:
            entries = [e for e in entries if should_include_by_time(e, newer_than, older_than)]
        
        # Filter by dirs_only if specified
        if dirs_only:
            entries = [e for e in entries if e.is_dir()]
        
        # Sort entries by name
        entries.sort(key=lambda e: e.name)
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
        return

    # If prune_empty is enabled, filter out directories that would be empty after filtering
    if prune_empty:
        filtered_entries = []
        for entry in entries:
            if entry.is_dir():
                # Check if directory would have any content after filtering
                if _has_matching_content(entry, ignore_patterns, max_depth, current_depth + 1, 
                                       dirs_only, newer_than, older_than, prune_empty):
                    filtered_entries.append(entry)
            else:
                filtered_entries.append(entry)
        entries = filtered_entries

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        if entry.is_dir():
            print(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            _generate_text_tree(entry, prefix + extension, ignore_patterns, 
                              max_depth, current_depth + 1, dirs_only, newer_than, older_than, prune_empty)
        else:
            if not dirs_only:  # Only print files if not dirs_only mode
                print(f"{prefix}{connector}{entry.name}")

def list_project_structure(root_dir_str: str, max_depth: Optional[int] = None, 
                          dirs_only: bool = False, newer_than: Optional[float] = None, 
                          older_than: Optional[float] = None, prune_empty: bool = False):
    """Prints a text tree view of a project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return
    
    ignore_patterns = get_ignore_patterns(root_dir)
    print(f"{root_dir.name}/")
    _generate_text_tree(root_dir, "", ignore_patterns, max_depth, 0, dirs_only, newer_than, older_than, prune_empty)

# --- Markdown Tree Generation ---

def _generate_markdown_tree(directory: Path, prefix: str, ignore_patterns: Set[str], lines: List[str],
                           max_depth: Optional[int] = None, current_depth: int = 0,
                           dirs_only: bool = False, newer_than: Optional[float] = None, 
                           older_than: Optional[float] = None, prune_empty: bool = False):
    """Recursive helper to build the Markdown directory tree."""
    if max_depth is not None and current_depth >= max_depth:
        return
        
    try:
        entries = [e for e in directory.iterdir() if not any(fnmatch.fnmatch(e.name, p) for p in ignore_patterns)]
        
        # Filter by time if specified
        if newer_than is not None or older_than is not None:
            entries = [e for e in entries if should_include_by_time(e, newer_than, older_than)]
        
        # Filter by dirs_only if specified
        if dirs_only:
            entries = [e for e in entries if e.is_dir()]
            
        entries.sort(key=lambda e: e.name)
    except PermissionError:
        lines.append(f"{prefix}- [Permission Denied]")
        return

    # Separate directories and files to process files first
    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if not e.is_dir()]

    # If prune_empty is enabled, filter out directories that would be empty
    if prune_empty:
        filtered_dirs = []
        for dir_entry in dirs:
            if _has_matching_content(dir_entry, ignore_patterns, max_depth, current_depth + 1,
                                   dirs_only, newer_than, older_than, prune_empty):
                filtered_dirs.append(dir_entry)
        dirs = filtered_dirs

    if not dirs_only:  # Only show files if not in dirs-only mode
        for file_entry in files:
            lines.append(f"{prefix}- 📄 {file_entry.name}")

    for dir_entry in dirs:
        # The <details> block is at the current prefix level
        lines.append(f'{prefix}<details>')
        lines.append(f'{prefix}  <summary>📁 {dir_entry.name}/</summary>')
        lines.append('') # Blank line is essential for the Markdown parser
        
        # The recursive call gets a deeper indentation
        _generate_markdown_tree(dir_entry, prefix + '  ', ignore_patterns, lines,
                              max_depth, current_depth + 1, dirs_only, newer_than, older_than, prune_empty)
        
        lines.append(f'{prefix}</details>')


def build_tree(current_dir: Path, ignore_patterns: Set[str], max_depth: Optional[int] = None, 
               current_depth: int = 0, dirs_only: bool = False, 
               newer_than: Optional[float] = None, older_than: Optional[float] = None, 
               prune_empty: bool = False) -> dict:
    """Recursively builds a nested dictionary representing the directory structure."""
    if max_depth is not None and current_depth >= max_depth:
        return {}
        
    tree = {}
    # Sort entries, directories first, then alphabetically
    entries = sorted(list(current_dir.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
    for entry in entries:
        if any(fnmatch.fnmatch(entry.name, pattern) for pattern in ignore_patterns) or \
           any(fnmatch.fnmatch(str(entry.relative_to(current_dir.parent)), pattern) for pattern in ignore_patterns):
            continue
            
        # Filter by time if specified
        if not should_include_by_time(entry, newer_than, older_than):
            continue
            
        # Filter by dirs_only if specified
        if dirs_only and not entry.is_dir():
            continue
            
        if entry.is_dir():
            subtree = build_tree(entry, ignore_patterns, max_depth, current_depth + 1, 
                               dirs_only, newer_than, older_than, prune_empty)
            # If prune_empty is enabled, only include directory if it has content
            if not prune_empty or subtree:
                tree[entry.name] = subtree
        else:
            tree[entry.name] = None
    return tree

# --- HTML Generation ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Notes</title>
    <style>
        {css}
    </style>
</head>
<body>
    <div class="instructions">
        <h2>Directory Tree Notes</h2>
        <p>Click on a directory to expand/collapse it. Click on the text to the right of any item to add or edit notes.</p>
        <p><strong>To save your notes, use your browser's "Save Page As..." feature (Ctrl+S or Cmd+S) and overwrite this file.</strong></p>
    </div>
    <ul class="tree">
        {tree}
    </ul>
    <script>
        {js}
    </script>
</body>
</html>"""

CSS_STYLES = """body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
}
ul.tree, ul.tree ul {
    list-style-type: none;
    padding-left: 20px;
    border-left: 1px solid #ddd;
}
.tree li {
    margin: 5px 0;
    position: relative;
}
.tree li::before {
    content: "";
    position: absolute;
    top: 10px;
    left: -10px;
    border-top: 1px solid #ddd;
    width: 10px;
    height: 0;
}
.name {
    cursor: pointer;
    padding: 2px 5px;
    border-radius: 3px;
    display: inline-block;
}
.name:hover {
    background-color: #eee;
}
.directory > .name::before {
    content: '📁';
    margin-right: 5px;
}
.file > .name::before {
    content: '📄';
    margin-right: 5px;
}
.directory.collapsed > ul {
    display: none;
}
.directory.collapsed > .name::before {
    content: '📂';
}
.notes {
    display: inline-block;
    margin-left: 15px;
    padding: 2px 5px;
    width: 60%;
    min-height: 1em;
    border-bottom: 1px dashed #ccc;
}
.notes:focus {
    outline: 1px solid #007bff;
    background-color: #fff;
}
.instructions {
    background-color: #eef;
    border: 1px solid #cce;
    border-radius: 5px;
    padding: 10px 20px;
    margin-bottom: 20px;
}
"""

JS_LOGIC = """document.addEventListener('click', function (event) {
    if (event.target.classList.contains('name')) {
        const parentLi = event.target.parentElement;
        if (parentLi.classList.contains('directory')) {
            parentLi.classList.toggle('collapsed');
        }
    }
});"""

def build_html_tree(tree_dict, is_root=True):
    """Recursively builds an HTML unordered list from a nested dictionary."""
    html = ''
    for name, content in tree_dict.items():
        if content is None:  # It's a file
            html += '<li class="file">'
            html += f'<span class="name">{name}</span>'
            html += '<div class="notes" contenteditable="true"></div>'
            html += '</li>\n'
        else:  # It's a directory
            html += '<li class="directory collapsed">'
            html += f'<span class="name">{name}</span>'
            html += '<div class="notes" contenteditable="true"></div>'
            html += '<ul>\n'
            html += build_html_tree(content, is_root=False)
            html += '</ul>\n'
            html += '</li>\n'
    return html

def generate_html_output(tree_dict, output_filename):
    """Generates the full HTML file and writes it to disk."""
    tree_html = build_html_tree(tree_dict)
    html_content = HTML_TEMPLATE.format(css=CSS_STYLES, js=JS_LOGIC, tree=tree_html)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Successfully generated '{output_filename}'. Open it in a browser to see the result.")

def generate_markdown_file(root_dir_str: str, output_file: str, max_depth: Optional[int] = None,
                          dirs_only: bool = False, newer_than: Optional[float] = None, 
                          older_than: Optional[float] = None, prune_empty: bool = False):
    """Generates an interactive Markdown file of the project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return

    ignore_patterns = get_ignore_patterns(root_dir)
    lines = [f"# Directory Tree for {root_dir.name}\n"]
    
    _generate_markdown_tree(root_dir, "", ignore_patterns, lines, max_depth, 0, dirs_only, newer_than, older_than, prune_empty)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Successfully generated interactive tree at '{output_file}'")

def _generate_text_from_tree(tree: dict, prefix=""):
    """Helper to generate plain text tree from dictionary."""
    lines = []
    entries = list(tree.keys())
    for i, name in enumerate(entries):
        connector = "├── " if i < len(entries) - 1 else "└── "
        lines.append(f"{prefix}{connector}{name}")
        if tree[name] is not None:
            new_prefix = prefix + ("│   " if i < len(entries) - 1 else "    ")
            lines.extend(_generate_text_from_tree(tree[name], new_prefix))
    return lines

def generate_text_output(root_dir_str: str, max_depth: Optional[int] = None,
                        dirs_only: bool = False, newer_than: Optional[float] = None, 
                        older_than: Optional[float] = None, prune_empty: bool = False):
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return
    ignore_patterns = get_ignore_patterns(root_dir)
    tree = build_tree(root_dir, ignore_patterns, max_depth, 0, dirs_only, newer_than, older_than, prune_empty)
    print(root_dir.name)
    lines = _generate_text_from_tree(tree)
    for line in lines:
        print(line)

def _generate_markdown_from_tree(tree: dict, lines: list, prefix=""):
    """Helper to generate markdown from dictionary."""
    entries = list(tree.keys())
    for name in entries:
        if tree[name] is None:
            lines.append(f'{prefix}- 📄 {name}')
        else:
            lines.append(f'{prefix}<details>')
            lines.append(f'{prefix}  <summary>📁 {name}</summary>')
            _generate_markdown_from_tree(tree[name], lines, prefix + "  ")
            lines.append(f'{prefix}</details>')

def generate_markdown_output(root_dir_str: str, output_file: str, max_depth: Optional[int] = None,
                            dirs_only: bool = False, newer_than: Optional[float] = None, 
                            older_than: Optional[float] = None, prune_empty: bool = False):
    """Generates an interactive Markdown file of the project directory."""
    root_dir = Path(root_dir_str).resolve()
    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{root_dir_str}'")
        return
    ignore_patterns = get_ignore_patterns(root_dir)
    tree = build_tree(root_dir, ignore_patterns, max_depth, 0, dirs_only, newer_than, older_than, prune_empty)
    lines = [f"# Directory Tree for {root_dir.name}\n"]
    _generate_markdown_from_tree({root_dir.name: tree}, lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Successfully generated interactive tree at '{output_file}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a directory tree as text, interactive Markdown, or a self-contained HTML file.",
        epilog="Example: python dirtree.py . --format html"
    )
    parser.add_argument(
        "root_dir", nargs='?', default='.', help="The root directory to scan (defaults to current directory)."
    )
    parser.add_argument(
        "--format", choices=['text', 'markdown', 'html'], default='text', help="Output format."
    )
    parser.add_argument(
        "--output", default=None, help="Output file for Markdown format. Defaults to <root_dir_name>.md."
    )
    parser.add_argument(
        '--html-output', default=None, help="Output file for HTML format. Defaults to <root_dir_name>.html."
    )
    parser.add_argument(
        '--max-depth', '-L', type=int, default=None, 
        help="Limit directory traversal to specified depth (e.g., --max-depth 2)"
    )
    parser.add_argument(
        '--dirs-only', '-d', action='store_true', 
        help="Show only directories, skip files"
    )
    parser.add_argument(
        '--newer-than', type=str, default=None,
        help="Show only files/dirs modified within specified time (e.g., '2h', '30m', '7d')"
    )
    parser.add_argument(
        '--older-than', type=str, default=None,
        help="Show only files/dirs older than specified time (e.g., '2h', '30m', '7d')"
    )
    parser.add_argument(
        '--prune-empty', action='store_true',
        help="Exclude directories from output if all their contents are filtered out"
    )
    
    args = parser.parse_args()
    root_dir = Path(args.root_dir).resolve()

    # Set default output filenames if not provided
    if args.output is None:
        args.output = f"{root_dir.name}.md"
    if args.html_output is None:
        args.html_output = f"{root_dir.name}.html"

    if not root_dir.is_dir():
        print(f"Error: Directory not found at '{args.root_dir}'")
        sys.exit(1)

    # Parse time expressions
    newer_than_seconds = None
    older_than_seconds = None
    
    if args.newer_than:
        newer_than_seconds = parse_time_expression(args.newer_than)
        if newer_than_seconds is None:
            print(f"Error: Invalid time expression '{args.newer_than}'. Use format like '2h', '30m', '7d'")
            sys.exit(1)
    
    if args.older_than:
        older_than_seconds = parse_time_expression(args.older_than)
        if older_than_seconds is None:
            print(f"Error: Invalid time expression '{args.older_than}'. Use format like '2h', '30m', '7d'")
            sys.exit(1)

    ignore_patterns = get_ignore_patterns(root_dir)
    
    if args.format == 'markdown':
        generate_markdown_output(args.root_dir, args.output, args.max_depth, args.dirs_only, 
                                newer_than_seconds, older_than_seconds, args.prune_empty)
    elif args.format == 'html':
        tree = {root_dir.name: build_tree(root_dir, ignore_patterns, args.max_depth, 0, 
                                         args.dirs_only, newer_than_seconds, older_than_seconds, args.prune_empty)}
        generate_html_output(tree, args.html_output)
    else: # 'text' format
        list_project_structure(args.root_dir, args.max_depth, args.dirs_only, 
                              newer_than_seconds, older_than_seconds, args.prune_empty)