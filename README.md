# Miscellaneous Tools

A collection of handy Python scripts for various tasks.

## Index

1.  [Directory Tree Generator (`dirtree.py`)](#directory-tree-generator-dirtreepy)
2.  [Multi-level Pie Chart Generator (`multilevel_pie.py`)](#multi-level-pie-chart-generator-multilevel_piepy)

---

## Directory Tree Generator (`dirtree.py`)

A script to generate a text-based representation of a directory structure. It's useful for quickly visualizing a project's layout.

### Usage

```bash
python dirtree.py [path_to_directory]
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
