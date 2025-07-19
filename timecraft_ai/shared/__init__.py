"""
Shared utilities and constants for the project.
This module contains shared functions, constants, and utilities that can be used across different parts of the project.
"""

from .chainnable_exceptions import (ChainableWrapperError,
                                    ChainableWrapperTypeError,
                                    ChainableWrapperValueError)
from .chainnable_runner import (ChainableBase, ChainableMeta, ChainableWrapper,
                                add_five, chainable_behavior, main, run,
                                square)
from .run_scheduled import SchedulerService

from .notify_webhook import Notifier

__all__ = [
    "ChainableWrapperError",
    "ChainableWrapperTypeError",
    "ChainableWrapperValueError",
    "ChainableBase",
    "ChainableMeta",
    "ChainableWrapper",
    "Notifier",
    "SchedulerService",
    "add_five",
    "square",
    "chainable_behavior",
    "run",
    "main",
]

# Ensure the module is importable from the root package
if __name__ == "__main__":
    print("This is the TimeCraft AI shared module. Import it in your scripts.")
    print(f"Available functions: {', '.join(__all__)}")
else:
    print("TimeCraft AI shared module imported successfully.")
    print(f"Available functions: {', '.join(__all__)}")

import sys
if sys.version_info < (3, 7):
    raise ImportError("TimeCraft AI requires Python 3.7 or higher.")
