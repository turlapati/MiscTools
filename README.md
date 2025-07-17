# Miscellaneous Tools

A collection of handy Python scripts for various tasks.

## Index

1.  [Directory Tree Generator (`dirtree.py`)](#directory-tree-generator-dirtreepy)
2.  [Multi-level Pie Chart Generator (`multilevel_pie.py`)](#multi-level-pie-chart-generator-multilevel_piepy)

---

## Directory Tree Generator (`dirtree.py`)

A versatile command-line tool to generate a visual representation of a directory structure in various formats. It's designed to be simple to use, yet powerful enough to create clean text trees, interactive Markdown files, or even self-contained HTML files for note-taking.

### Features

*   **Multiple Output Formats**: Generate the directory tree in `text`, `markdown`, or `html` format.
*   **Interactive HTML**: The `html` format creates a single, self-contained file with a collapsible tree and inline note-taking capabilities. Save your notes simply by saving the page (`Ctrl+S`).
*   **Interactive Markdown**: The `markdown` format uses `<details>` and `<summary>` tags to create a collapsible tree that works on platforms like GitHub.
*   **Smart Ignoring**: Automatically respects patterns from all `.*ignore` files (e.g., `.gitignore`, `.codeiumignore`) in the root directory, in addition to a comprehensive list of default patterns.
*   **Dynamic Filenames**: Default output filenames are intelligently derived from the root directory's name (e.g., `my_project` -> `my_project.html`).

### Usage

The script can be run from the command line.

```bash
python3 dirtree.py [root_directory] [options]
```

**Arguments:**

*   `root_directory`: The path to the directory you want to scan. Defaults to the current directory (`.`).

**Options:**

*   `--format [text|markdown|html]`: Specify the output format. Defaults to `text`.
*   `--output [FILENAME]`: Set the output filename for the Markdown format. Defaults to `<root_directory_name>.md`.
*   `--html-output [FILENAME]`: Set the output filename for the HTML format. Defaults to `<root_directory_name>.html`.

### Examples

1.  **Generate a simple text tree of the current directory:**
    ```bash
    python3 dirtree.py
    ```

2.  **Generate an interactive Markdown file for a specific project:**
    ```bash
    python3 dirtree.py /path/to/my_project --format markdown
    ```

3.  **Generate a self-contained HTML file with a custom name:**
    ```bash
    python3 dirtree.py . --format html --html-output project_notes.html
    ```

---

## Multi-level Pie Chart Generator (`multilevel_pie.py`)

A script that creates a multi-level pie chart from a CSV file using `matplotlib` and `pandas`.

### Usage

1.  Modify the script to point to your CSV file (currently hardcoded as `your_file.csv`).
2.  Ensure your CSV has at least three columns for the hierarchical levels.
3.  Run the script:

```bash
python multilevel_pie.py
```
