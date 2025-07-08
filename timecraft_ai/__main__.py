"""
Allow TimeCraft AI to be executable as a module with `python -m timecraft_ai`

This enables running the CLI without installing the package:
    python -m timecraft_ai --help
    python -m timecraft_ai voice
    python -m timecraft_ai analyze data.csv
"""

from .cli import timecraft_ai as timecraft_ai_cli

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.insert(0, path.dirname(path.abspath(__file__)))

    # Ensure the package is correctly imported when run as a script
    # This allows the CLI to be executed directly

    timecraft_ai_cli.main(prog_name="timecraft_ai")
