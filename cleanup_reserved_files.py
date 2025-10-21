#!/usr/bin/env python3
"""
cleanup_reserved_files.py

PURPOSE:
  Removes Windows reserved device names (like 'nul') that sometimes get created
  by the pipeline and prevent git from working properly.

USAGE:
  python cleanup_reserved_files.py

ISSUE:
  On Windows, certain reserved device names ('nul', 'PRN', 'COM1', etc.) can
  sometimes be created as files when output redirection goes wrong. Git will
  refuse to add these files, causing "error: invalid path 'nul'" messages.

SOLUTION:
  This script safely removes these problematic files.
"""

import os
import sys
from pathlib import Path

# Enable UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')


def cleanup_reserved_files():
    """Remove Windows reserved device filenames from the project root."""
    reserved_names = [
        "nul", "NUL",
        "prn", "PRN",
        "con", "CON",
        "aux", "AUX",
        "com1", "COM1", "com2", "COM2", "com3", "COM3", "com4", "COM4",
        "lpt1", "LPT1", "lpt2", "LPT2", "lpt3", "LPT3"
    ]

    base_dir = Path(__file__).parent
    cleaned_count = 0
    failed_count = 0

    print(f"Checking for reserved device files in: {base_dir}\n")

    for name in reserved_names:
        file_path = base_dir / name

        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"✓ Deleted reserved file: {name}")
                    cleaned_count += 1
                elif file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"✓ Deleted reserved directory: {name}")
                    cleaned_count += 1
            except PermissionError:
                print(f"✗ Permission denied - cannot delete: {name}")
                print(f"  (File may be locked by another process)")
                failed_count += 1
            except Exception as e:
                print(f"✗ Error deleting {name}: {e}")
                failed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Cleaned: {cleaned_count} file(s)")
    if failed_count > 0:
        print(f"  Failed:  {failed_count} file(s)")
        print(f"\n  Note: If 'nul' is locked, try closing any open terminals")
        print(f"        or running: git clean -fdx nul")
    print(f"{'='*60}\n")

    if cleaned_count > 0:
        print("✓ Cleanup complete!")
        print("\nYou can now run: git add -A")
        return True
    elif failed_count == 0:
        print("✓ No reserved files found - repository is clean!")
        return True
    else:
        print("✗ Some files could not be deleted. Try closing other applications.")
        return False


if __name__ == "__main__":
    success = cleanup_reserved_files()
    sys.exit(0 if success else 1)
