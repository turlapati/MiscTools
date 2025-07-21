import os
import argparse
from pathlib import Path

def create_project_scaffold(tree_structure: str, target_dir: str):
    """
    Parses a string representation of a directory tree and creates the
    corresponding directories and empty files in a specified target directory.

    Args:
        tree_structure: A multi-line string representing the project structure.
        target_dir: The path to the parent directory where the scaffold
                    should be created.
    """
    lines = [line for line in tree_structure.strip().split('\n') if line.strip()]
    if not lines:
        print("Error: The provided tree structure is empty or invalid.")
        return

    target_path = Path(target_dir)

    # --- 1. Determine the base path and processing scope ---
    first_line = lines[0].strip()
    # A "rootless" structure starts immediately with tree branch characters.
    is_rootless = '├──' in first_line or '└──' in first_line

    # path_context is a stack of Path objects to keep track of the current directory at each level.
    path_context = []
    lines_to_process = []

    if is_rootless:
        print(f"Scaffolding a rootless project in: '{target_path}'")
        # Ensure the base target directory exists.
        target_path.mkdir(parents=True, exist_ok=True)
        path_context.append(target_path)
        lines_to_process = lines
    else:
        # The first line defines the project's own root directory.
        root_name = first_line.replace('/', '')

        # --- Intelligent Root Handling ---
        # If the target directory name is the same as the project root name,
        # use the target directory as the project root to avoid redundant nesting
        # (e.g., target '/path/to/app' and root 'app/').
        if target_path.name == root_name:
            project_root = target_path
            print(f"Target directory matches project root. Scaffolding directly in: '{project_root}'")
        else:
            project_root = target_path / root_name
            print(f"Creating project root directory: '{project_root}'")

        project_root.mkdir(parents=True, exist_ok=True)
        path_context.append(project_root)
        lines_to_process = lines[1:]

    # --- 2. Process each line to create files and directories ---
    for line in lines_to_process:
        # Determine the level/depth by counting the vertical bars.
        # This works for most standard `tree` command outputs.
        level = line.count('│') + line.count('    ')

        # Extract the name of the file or directory.
        try:
            name_part = line.split('──')[-1].strip()
        except IndexError:
            print(f"Warning: Skipping malformed line: {line}")
            continue

        is_dir = name_part.endswith('/')
        clean_name = name_part.replace('/', '')

        # Adjust the path context stack to the correct parent level.
        # The parent's level is `level - 1`. The context stack size should
        # be `level + 1` to hold the parent Path object.
        while len(path_context) > level + 1:
            path_context.pop()

        # The parent directory is the last Path object on our context stack.
        parent_dir = path_context[-1]
        current_path = parent_dir / clean_name

        # --- 3. Create the file or directory ---
        if is_dir:
            print(f"  Creating directory: {current_path}")
            current_path.mkdir(exist_ok=True)
            # Add the new directory to the context stack for its children.
            path_context.append(current_path)
        else:
            print(f"    Creating file:      {current_path}")
            # Ensure the parent directory exists before creating the file.
            current_path.parent.mkdir(parents=True, exist_ok=True)
            # Create an empty file.
            current_path.touch()

    print("\nProject structure created successfully!")


if __name__ == "__main__":
    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Create a project scaffold from a directory tree structure file.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:

1. Create scaffold from 'structure.txt' in the current directory:
   python %(prog)s structure.txt

2. Create scaffold in a specific target directory '~/projects':
   python %(prog)s structure.txt -d ~/projects

3. Avoid redundant directory creation:
   python %(prog)s structure.txt -d /path/to/my_enterprise_app
   (If structure.txt starts with 'my_enterprise_app/', it won't create a nested folder)

---
A sample 'structure.txt' file with a root directory:
my_enterprise_app/
├── app/
│   └── main.py
└── tests/
    └── test_main.py

---
A sample 'rootless_structure.txt' file:
├── src/
│   └── component.js
├── public/
│   └── index.html
└── package.json
"""
    )
    parser.add_argument(
        "structure_file",
        help="Path to a text file containing the directory tree structure."
    )
    parser.add_argument(
        "-d", "--target-dir",
        default=".",
        help="The target directory where the scaffold will be created.\nDefaults to the current directory."
    )
    args = parser.parse_args()

    # --- Input Validation and Execution ---
    structure_file_path = Path(args.structure_file)
    # os.path.expanduser is used to handle '~' in paths.
    target_dir_path = Path(os.path.expanduser(args.target_dir))

    if not structure_file_path.is_file():
        print(f"Error: Structure file not found at '{structure_file_path}'")
        exit(1)

    if target_dir_path.exists() and not target_dir_path.is_dir():
        print(f"Error: Target path '{target_dir_path}' exists but is not a directory.")
        exit(1)

    try:
        tree_data = structure_file_path.read_text()
        create_project_scaffold(tree_data, str(target_dir_path))
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        exit(1)
