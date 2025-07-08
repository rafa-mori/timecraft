"""
TimeCraft AI Core Module
================================

This module includes classes for time series modeling using Prophet, linear regression analysis, and database connectivity.

"""
from __future__ import annotations


from typing import Optional
import time
import threading
import logging

import os
import sys

from .classifier_model import ClassifierModel
from .database_connection import DatabaseConnector
from .linear_regression import LinearRegressionAnalysis
from .timecraft_model import TimeCraftModel
from ..shared.run_scheduled import SchedulerService

# Adicionar src ao path para importações diretas
_root_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_root_dir, "timecraft_ai")

if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Import core classes from the timecraft_ai package

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


try:
    import requests
except ImportError:
    requests = None

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class TimeCraftAI:
    """
    Central class for integrating TimeCraftModel, ClassifierModel, LinearRegressionAnalysis, and DatabaseConnector.
    """

    def __init__(self, db_connector=None):
        """
        Initialize the TimeCraftAI class.
        :param db_connector: DatabaseConnector instance (optional).
        """
        self.db_connector = db_connector
        self.timecraft_model = None
        self.classifier_model = None
        self.linear_regression_analysis = None

    def create_timecraft_model(self, **kwargs):
        """
        Create and store a TimeCraftModel instance.
        :param kwargs: Arguments for TimeCraftModel.
        :return: TimeCraftModel instance.
        """
        self.timecraft_model = TimeCraftModel(
            db_connector=self.db_connector, **kwargs)
        return self.timecraft_model

    def create_classifier_model(self, **kwargs):
        """
        Create and store a ClassifierModel instance.
        :param kwargs: Arguments for ClassifierModel.
        :return: ClassifierModel instance.
        """
        self.classifier_model = ClassifierModel(
            db_connector=self.db_connector, **kwargs
        )
        return self.classifier_model

    def create_linear_regression_analysis(self, data_path):
        """
        Create and store a LinearRegressionAnalysis instance.
        :param data_path: Path to the CSV data file.
        :return: LinearRegressionAnalysis instance.
        """
        self.linear_regression_analysis = LinearRegressionAnalysis(data_path)
        return self.linear_regression_analysis

    def set_db_connector(self, db_connector):
        """
        Set the database connector and update it in all created models.
        :param db_connector: DatabaseConnector instance.
        """
        self.db_connector = db_connector
        # Atualiza o conector nos modelos já criados
        if self.timecraft_model:
            self.timecraft_model.db_connector = db_connector
        if self.classifier_model:
            self.classifier_model.db_connector = db_connector

    def get_timecraft_model(self):
        """
        Get the stored TimeCraftModel instance.
        :return: TimeCraftModel instance or None.
        """
        return self.timecraft_model

    def get_classifier_model(self):
        """
        Get the stored ClassifierModel instance.
        :return: ClassifierModel instance or None.
        """
        return self.classifier_model

    def get_linear_regression_analysis(self):
        """
        Get the stored LinearRegressionAnalysis instance.
        :return: LinearRegressionAnalysis instance or None.
        """
        return self.linear_regression_analysis

    def get_db_connector(self):
        """
        Get the stored DatabaseConnector instance.
        :return: DatabaseConnector instance or None.
        """
        return self.db_connector

    def run_all(self):
        """
        Run all created models, if they exist.
        """
        if self.timecraft_model:
            self.timecraft_model.run()
        if self.classifier_model:
            self.classifier_model.run()
        if self.linear_regression_analysis:
            self.linear_regression_analysis.run_analysis()


def main():
    """
    Main entry point for command-line usage. Provides basic commands: help, status, version.
    """
    import sys

    VERSION = "1.1.3"
    HELP = """
TimeCraftAI - Command Line Interface

Usage:
  python -m timecraft_ai [command]

Commands:
  help      Show this help message
  status    Show basic status of the TimeCraftAI module
  version   Show version information
"""
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print(HELP)
        return
    cmd = sys.argv[1].lower()
    if cmd == "version":
        print(f"TimeCraftAI version: {VERSION}")
    elif cmd == "status":
        print("TimeCraftAI is installed and ready to use.")
    elif cmd == "schedule":
        if len(sys.argv) < 4:
            print("Usage: python -m timecraft_ai schedule <interval_seconds> <model>")
            sys.exit(1)
        interval = int(sys.argv[2])
        model_type = sys.argv[3].lower()
        ai = TimeCraftAI()
        if model_type == "timecraft":
            model = ai.create_timecraft_model(
                data="example/data/hist_cambio_float.csv",
                date_column="dt",
                value_columns=["purchaseValue", "saleValue"],
                is_csv=True,
            )
            SchedulerService.scheduled_run(
                model.run, interval_seconds=interval)
        elif model_type == "classifier":
            model = ai.create_classifier_model(
                data="example/data/hist_cambio_float.csv", target_column="purchaseValue"
            )
            SchedulerService.scheduled_run(
                model.run, interval_seconds=interval)
        elif model_type == "regression":
            model = ai.create_linear_regression_analysis(
                "example/data/hist_cambio_float.csv"
            )
            SchedulerService.scheduled_run(
                model.run_analysis, interval_seconds=interval)
        else:
            print(f"Unknown model type: {model_type}")
            sys.exit(1)
        print(
            f"Scheduled {model_type} model to run every {interval} seconds. Press Ctrl+C to stop."
        )
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
    else:
        main()
        main()
