"""
TimeCraft Core - Time Series Analysis and Forecasting
====================================================

This module contains the core functionality for time series analysis,
database connections, and forecasting models.
"""
from .timecraft_model import TimeCraftModel
from .classifier_model import ClassifierModel
from .linear_regression import LinearRegressionAnalysis
from .database_connection import DatabaseConnector
from .wrapper import TimeCraftAI, main
# from ..shared.notify_webhook import Notifier
# from ..shared.run_scheduled import SchedulerService


__all__ = [
    "TimeCraftModel",
    "ClassifierModel",
    "LinearRegressionAnalysis",
    "DatabaseConnector",
    "TimeCraftAI",
    "main",
    # "Notifier",
    # "SchedulerService",
]

# Ensure the module is importable from the root package
if __name__ == "__main__":
    print("This is the TimeCraft AI core module. Import it in your scripts.")
    print(f"Available modules: {', '.join(__all__)}")
else:
    print("TimeCraft AI core module imported successfully.")
    print(f"Available modules: {', '.join(__all__)}")

import sys
if sys.version_info < (3, 7):
    raise ImportError("TimeCraft AI requires Python 3.7 or higher.")
