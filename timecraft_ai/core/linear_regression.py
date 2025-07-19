"""
Linear Regression Analysis Module
================================
This module provides functionality for performing linear regression analysis on a dataset.
"""

import logging
from datetime import datetime

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from ..shared.notify_webhook import Notifier

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class LinearRegressionAnalysis:
    """
    Class for performing linear regression analysis on a dataset.
    """

    def __init__(self, data_path):
        """
        Initialize the LinearRegressionAnalysis class.
        :param data_path: Path to the CSV data file.
        """
        self.data_path = data_path
        self.data = None
        self.model = None

    def load_data(self):
        """
        Load and preprocess the data from the CSV file.
        """
        self.data = pd.read_csv(self.data_path)
        self.data = self.data.rename(
            columns={"purchaseValue": "y", "saleValue": "yhat", "dt": "ds"}
        ).dropna()
        logger.info(
            f"Data loaded for regression analysis. Shape: {self.data.shape if self.data is not None else None}"
        )

    def analyze_correlation(self):
        """
        Analyze and print the correlation between purchase and sale values.
        """
        if self.data is not None:
            correlation = self.data["y"].corr(self.data["yhat"])
            logger.info(
                f"Correlation between purchaseValue and saleValue: {correlation}"
            )
            print(
                f"Correlation between purchaseValue and saleValue: {correlation}")
        else:
            logger.warning("Data is None. Cannot analyze correlation.")

    def prepare_data(self):
        """
        Prepare the data for training and testing the regression model.
        :return: Split data (X_train, X_test, y_train, y_test).
        """
        if self.data is not None:
            X = self.data[["yhat"]]
            y = self.data["y"]
            return train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            logger.warning("Data is None. Cannot prepare data.")
            return None, None, None, None

    def train_model(self, X_train, y_train):
        """
        Train the linear regression model using the training data.
        :param X_train: Training features.
        :param y_train: Training target values.
        """
        if X_train is not None and y_train is not None:
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            logger.info("Linear regression model trained.")
        else:
            logger.warning("Training data is None. Cannot train model.")

    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the trained model and print metrics.
        :param X_test: Test features.
        :param y_test: Test target values.
        """
        if self.model is not None and X_test is not None and y_test is not None:
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"Mean Squared Error: {mse}")
            logger.info(
                f"Model Coefficients: {getattr(self.model, 'coef_', None)}")
            logger.info(
                f"Model Intercept: {getattr(self.model, 'intercept_', None)}")
            print(f"Mean Squared Error: {mse}")
            print(f"Model Coefficients: {getattr(self.model, 'coef_', None)}")
            print(
                f"Model Intercept: {getattr(self.model, 'intercept_', None)}")
        else:
            logger.warning(
                "Model or test data is None. Cannot evaluate model.")

    def run_analysis(self, webhook_url=None, webhook_payload_extra=None):
        """
        Run the full analysis: load data, analyze correlation, train and evaluate the model.
        Optionally notify a webhook on completion.
        :param webhook_url: Optional webhook URL to notify after run.
        :param webhook_payload_extra: Optional dict to merge into the webhook payload.
        """
        self.load_data()
        self.analyze_correlation()
        X_train, X_test, y_train, y_test = self.prepare_data()
        self.train_model(X_train, y_train)
        self.evaluate_model(X_test, y_test)
        if webhook_url:
            payload = {
                "event": "linear_regression_analysis",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "data_path": self.data_path,
                "data_shape": self.data.shape if self.data is not None else None,
            }
            if webhook_payload_extra:
                payload.update(webhook_payload_extra)
            Notifier.notify_webhook(webhook_url, payload)
