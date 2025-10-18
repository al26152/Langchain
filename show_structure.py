#!/usr/bin/env python3
"""
show_structure.py

Recursively prints a tree-style view of your project directory and saves it to a Markdown file.
"""

import os
import sys

def print_tree(root_path: str, output_file, prefix: str = ""):
    """
    Recursively print the directory tree starting from root_path to the specified file.
    """
    try:
        entries = sorted(os.listdir(root_path))
    except PermissionError:
        # If permission is denied for a directory, just skip it.
        return
    except FileNotFoundError:
        # If the root_path itself doesn't exist, handle gracefully.
        print(f"Error: Directory not found at '{root_path}'", file=sys.stderr)
        return

    for index, entry in enumerate(entries):
        path = os.path.join(root_path, entry)
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        output_file.write(prefix + connector + entry + "\n")

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, output_file, prefix + extension)

def main():
    # Allow passing a custom path, default to current directory
    # Allow passing a custom output filename, default to 'directory_structure.md'
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "directory_structure.md"

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"# Directory Structure for '{root}'\n\n")
            f.write("```\n") # Start a Markdown code block for better formatting
            f.write(root + "\n") # Print the root path at the top
            print_tree(root, f)
            f.write("```\n") # End the Markdown code block
        print(f"Directory structure successfully saved to '{output_filename}'")
    except IOError as e:
        print(f"Error: Could not write to file '{output_filename}'. {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()