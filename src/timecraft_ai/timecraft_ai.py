import logging

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("timecraft_ai")

#__init__.py
# noinspection PyUnusedFunction

import os
import json
try:
    import requests
except ImportError:
    requests = None

from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import pandas as pd
import plotly.express as px  # Import Plotly

from matplotlib import pyplot as plt
from prophet import Prophet

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from sqlalchemy import create_engine
import threading
import time
from typing import Optional


def notify_webhook(webhook_url, payload):
    """
    Send a JSON payload to a webhook URL via HTTP POST.
    :param webhook_url: The webhook endpoint URL.
    :param payload: Dictionary to send as JSON.
    :return: Response object or None if requests is not available.
    """
    if not requests:
        logger.warning("[Webhook] 'requests' library not installed. Cannot send webhook notification.")
        return None
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        logger.info(f"[Webhook] Notification sent. Status code: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"[Webhook] Error sending notification: {e}")
        return None


class TimeCraftModel:
    """
    Class for time series modeling using Prophet.
    """

    def __init__(self, data=None, date_column=None, value_columns=None, is_csv=True, db_connector=None, query=None, periods=60):
        """
        Initialize the TimeCraftModel class.

        :param data: Input data (CSV path or list of data).
        :param date_column: Name of the date column.
        :param value_columns: List of value columns.
        :param is_csv: Whether the data is from a CSV file.
        :param db_connector: Database connector instance.
        :param query: Query to fetch data from the database.
        :param periods: Number of periods for forecasting.
        """
        self.data = data
        self.date_column = date_column
        self.value_columns = value_columns
        self.is_csv = is_csv
        self.periods = periods
        self.db_connector = db_connector  # Adds the database connector
        self.query = query  # Adds the query to fetch data
        self.model = Prophet()
        self.df = None
        self.forecast = None
        self.last_run_duration = list()

    def __str__(self) -> str:
        """
        Return a string representation of the TimeCraftModel instance.
        """
        return f"TimeCraftModel(data={self.data}, date_column={self.date_column}, value_columns={self.value_columns}, is_csv={self.is_csv}, db_connector={self.db_connector}, query={self.query})"

    def __repr__(self) -> str:
        """
        Return an official string representation of the TimeCraftModel instance.
        """
        return f"TimeCraftModel(data={self.data}, date_column={self.date_column}, value_columns={self.value_columns}, is_csv={self.is_csv}, db_connector={self.db_connector}, query={self.query})"

    def __len__(self) -> int:
        """
        Return the number of rows in the DataFrame.
        """
        return len(self.df) if self.df is not None else 0

    def __getitem__(self, key):
        """
        Allow access to DataFrame columns as if the object were a dictionary.
        """
        return self.df[key] if self.df is not None else None

    def __iter__(self):
        """
        Allow iteration over the DataFrame rows.
        """
        return iter(self.df) if self.df is not None else iter([])

    def __next__(self):
        """
        Return the next row of the DataFrame.
        """
        return next(iter(self.df)) if self.df is not None else None

    def __contains__(self, item) -> bool:
        """
        Check if an item is in the DataFrame columns.
        """
        return item in self.df

    def __eq__(self, other) -> bool:
        """
        Compare two TimeCraftModel objects for equality.
        """
        return self.data == other.data and self.date_column == other.date_column and self.value_columns == other.value_columns and self.is_csv == other.is_csv and self.db_connector == other.db_connector and self.query == other.query

    def dropna(self):
        """
        Remove rows with null values from the DataFrame.
        :return: DataFrame without null values.
        """
        if self.df is not None:
            self.df = self.df.dropna()
        else:
            logger.warning("DataFrame is None, cannot drop NaN values.")
        return self.df

    def load_and_prepare_data(self):
        """
        Load and prepare the data for modeling, from CSV or database.
        """
        if self.db_connector and self.query:
            # Fetch data from the database
            try:
                self.db_connector.connect()
                df = self.db_connector.execute_query(self.query)
            except Exception as e:
                logger.error(f"TimeCraftModel: Error fetching data from the database: {e}")
                return
            finally:
                if hasattr(self.db_connector, 'close'):
                    self.db_connector.close()
                else:
                    logger.warning("The engine does not have a 'close' method.")
        elif self.is_csv:
            chunks = pd.read_csv(self.data, chunksize=10000) # type: ignore
            df = pd.concat(chunks)
        else:
            # Converts the data list to a DataFrame
            df = pd.DataFrame(self.data, columns=[self.date_column] + self.value_columns) # type: ignore

        # Rename columns
        df = df.rename(columns={self.date_column: "ds", self.value_columns[0]: "y"}) # type: ignore

        # Remove rows with null values
        df = df.dropna()

        # Convert the date column to datetime format
        df["ds"] = pd.to_datetime(df["ds"])

        self.df = df
        logger.info(f"Data loaded and prepared. Shape: {self.df.shape if self.df is not None else None}")

    def fit_model(self) -> None:
        """
        Fit the Prophet model to the data.
        """
        self.model.fit(self.df[['ds', 'y']]) # type: ignore
        logger.info("Prophet model fitted.")

    def make_predictions(self, periods=None) -> pd.DataFrame:
        """
        Make predictions using the fitted model.

        :param periods: Number of periods for forecasting.
        :return: DataFrame with the forecasts.
        """
        if periods is None:
            periods = self.periods
        future = self.model.make_future_dataframe(periods=periods)
        self.forecast = self.model.predict(future)
        return self.forecast

    def save_forecast(self, output_file) -> str:
        """
        Save the forecasts to a CSV file.

        :param output_file: Output file path.
        :return: Output file path.
        """
        output_dir = os.path.dirname(output_file)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if not output_file.endswith('.csv'):
            output_file += '.csv'
        if os.path.exists(output_file):
            os.remove(output_file)
        if not os.path.exists(output_file):
            os.makedirs(output_file, exist_ok=True)
        if len(self.forecast.value_counts()) == 0: # type: ignore
            logger.error("Forecast is empty. Please run the model before saving the forecast.")
            raise ValueError("Forecast is empty. Please run the model before saving the forecast.")
        if self.forecast is None:
            logger.error("Forecast is None. Please run the model before saving the forecast.")
            raise ValueError("Forecast is None. Please run the model before saving the forecast.")
        self.forecast.to_csv(output_file, index=False) # type: ignore
        logger.info(f"Forecast saved to {output_file}")
        return output_file

    def set_last_run_duration(self, start_time):
        """
        Set the duration of the last run.

        :param start_time: Start time of the run.
        """
        duration = datetime.now() - start_time
        self.last_run_duration.append(duration)
        logger.info(f"Run duration: {duration}")

    def save_plots(self, output_dir: str, plot_types: list, formats: list) -> str:
        """
        Save forecast plots in different formats (HTML, PNG, etc).

        :param output_dir: Output directory.
        :param plot_types: Types of plots (line, scatter, bar).
        :param formats: File formats (html, png).
        :return: Output directory.
        """
        if output_dir is None:
            raise ValueError("Output directory not provided")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        for plot_type in plot_types:
            if plot_type == 'line':
                fig = px.line(self.forecast, x='ds', y='yhat', title='Forecast')
            elif plot_type == 'scatter':
                fig = px.scatter(self.forecast, x='ds', y='yhat', title='Forecast')
            elif plot_type == 'bar':
                fig = px.bar(self.forecast, x='ds', y='yhat', title='Forecast')
            else:
                continue

            for fmt in formats:
                if fmt == 'html':
                    fig.write_html(os.path.join(output_dir, f'plot_charts_forecast_{plot_type}.html'))
                elif fmt == 'png':
                    fig.write_image(os.path.join(output_dir, f'plot_charts_forecast_{plot_type}.png'), scale=3)
                else:
                    continue

        # Matplotlib plots
        for plot_type in plot_types:
            plt.figure()
            if plot_type == 'line':
                plt.plot(self.forecast['ds'], self.forecast['yhat']) # type: ignore
            elif plot_type == 'scatter':
                plt.scatter(self.forecast['ds'], self.forecast['yhat']) # type: ignore
            elif plot_type == 'bar':
                plt.bar(self.forecast['ds'], self.forecast['yhat']) # type: ignore
            else:
                continue

            plt.title('Forecast')
            for fmt in formats:
                if fmt == 'png':
                    plt.savefig(os.path.join(output_dir, f'plot_charts_forecast_{plot_type}.png'), transparent=True, dpi=300)
                else:
                    continue

            try:
                if hasattr(plt, 'close'):
                    plt.close()
                else:
                    logger.warning("The engine does not have a 'close' method.")
            except Exception as e:
                logger.error(f"Error closing the figure: {e}")

        return output_dir

    def run_and_plot(self) -> None:
        """
        Run the model and plot the forecasts using Matplotlib.
        """
        self.run()
        self.plot_forecast()

    def run_and_plot_plotly(self) -> None:
        """
        Run the model and plot the forecasts using Plotly.
        """
        self.run()
        self.plot_forecast_plotly()

    def run_and_save_forecast(self, output_file) -> None:
        """
        Run the model and save the forecasts to a file.

        :param output_file: Output file path.
        """
        self.run()
        self.save_forecast(output_file)

    def clear(self) -> None:
        """
        Clear the model's data and forecasts.
        """
        self.df = None
        self.forecast = None
        self.last_run_duration = list()
        logger.info("Model state cleared.")

    def run_parallel(self, n_jobs=2) -> None:
        """
        Run the model in parallel using multiple processes.

        :param n_jobs: Number of parallel jobs.
        """
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            executor.map(self.run, range(n_jobs))

    def run(self, webhook_url=None, webhook_payload_extra=None) -> None:
        """
        Run the complete pipeline: data loading, model fitting, and forecasting.
        Optionally notify a webhook on completion.
        :param webhook_url: Optional webhook URL to notify after run.
        :param webhook_payload_extra: Optional dict to merge into the webhook payload.
        """
        start_time = datetime.now()
        self.load_and_prepare_data()
        self.fit_model()
        self.make_predictions()
        self.set_last_run_duration(start_time)
        if webhook_url:
            payload = {
                "event": "timecraft_model_run",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "model_type": "Prophet",
                "data_shape": self.df.shape if self.df is not None else None,
                "forecast_shape": self.forecast.shape if self.forecast is not None else None,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }
            if webhook_payload_extra:
                payload.update(webhook_payload_extra)
            notify_webhook(webhook_url, payload)

    def info(self) -> None:
        """
        Display information about the model, data, and forecasts.
        """
        print(self.model)
        print(self.df)
        print(self.forecast)

    def get_model(self) -> Prophet:
        """
        Get the Prophet model instance.
        :return: Prophet model.
        """
        return self.model

    def get_data(self) -> pd.DataFrame:
        """
        Get the loaded data as a DataFrame.
        :return: DataFrame with loaded data.
        """
        return self.df # type: ignore

    def get_forecast(self) -> pd.DataFrame:
        """
        Get the forecasted values as a DataFrame.
        :return: DataFrame with forecasts.
        """
        return self.forecast # type: ignore

    def get_data_columns(self) -> list:
        """
        Get the list of data columns in the DataFrame.
        :return: List of column names.
        """
        if self.df is not None:
            return self.df.columns.tolist()
        return []

    def get_last_run_duration(self) -> datetime | None:
        """
        Get the duration of the last run.
        :return: Duration as datetime or None.
        """
        if self.last_run_duration:
            return self.last_run_duration.pop()
        return None

    def get_duration_history(self) -> list:
        """
        Get the history of run durations.
        :return: List of durations.
        """
        return self.last_run_duration

    def get_mse(self) -> float:
        """
        Calculate the mean squared error of the forecasts.
        :return: Mean squared error.
        """
        if self.forecast is not None and self.df is not None:
            return ((self.forecast['yhat'] - self.df['y']) ** 2).mean()
        return float('nan')

    def get_correlation(self) -> float:
        """
        Calculate the correlation between the forecasts and the actual values.
        :return: Correlation value.
        """
        if self.forecast is not None and self.df is not None:
            return self.forecast['yhat'].corr(self.df['y'])
        return float('nan')

    def get_coefficients(self) -> float:
        """
        Get the coefficients of the Prophet model.
        :return: Coefficient value.
        """
        if hasattr(self.model, 'params') and 'k' in self.model.params:
            return self.model.params['k']
        return float('nan')

    def get_intercept(self) -> float:
        """
        Get the intercept of the Prophet model.
        :return: Intercept value.
        """
        if hasattr(self.model, 'params') and 'm' in self.model.params:
            return self.model.params['m']
        return float('nan')

    def plot_forecast(self) -> None:
        """
        Plot the forecasts using Matplotlib.
        """
        fig = self.model.plot(self.forecast)
        fig.show()

    def plot_forecast_plotly(self):
        """
        Plot the forecasts using Plotly.
        """
        plty = px.line(self.forecast, x='ds', y='yhat', title='Forecast')
        plty.show()


class DatabaseConnector:
    """
    Class for managing database connections and executing queries for various database types.
    """
    def __init__(self, db_type, **kwargs):
        """
        Initialize the DatabaseConnector.
        :param db_type: Type of the database (oracle, sqlite, mssql, postgres, mysql, mongodb).
        :param kwargs: Database connection parameters.
        """
        self.db_type = db_type.lower()
        self.connection = None
        self.credentials = kwargs

    def connect(self):
        """
        Establish a connection to the database.
        """
        try:
            if self.db_type == "oracle":
                import cx_Oracle

                self.connection = cx_Oracle.connect(
                    user=self.credentials.get("username") or os.getenv("ORACLE_USERNAME"),
                    password=self.credentials.get("password") or os.getenv("ORACLE_PASSWORD"),
                    dsn=self.credentials.get("dsn") or os.getenv("ORACLE_DSN")
                )
            elif self.db_type == "sqlite":
                import sqlite3
                db_path = self.credentials.get("db_path") or os.getenv("SQLITE_DB_PATH")
                if db_path is None:
                    raise ValueError("Database path for SQLite cannot be None.")
                self.connection = sqlite3.connect(db_path)
            elif self.db_type == "mssql":
                conn_string = (
                    "mssql+pyodbc://"
                    f'{self.credentials.get("username") or os.getenv("MSSQL_USERNAME")}:'
                    f'{self.credentials.get("password") or os.getenv("MSSQL_PASSWORD")}@'
                    f'{self.credentials.get("host") or os.getenv("MSSQL_HOST", "127.0.0.1")}:'
                    f'{self.credentials.get("port") or os.getenv("MSSQL_PORT", 1433)}/'
                    f'{self.credentials.get("database") or os.getenv("MSSQL_DATABASE")}?'
                    "driver=ODBC+Driver+17+for+SQL+Server"
                )
                self.connection = create_engine(conn_string)
            elif self.db_type == "postgres":
                import psycopg2
                self.connection = psycopg2.connect(
                    host=self.credentials.get("host") or os.getenv("POSTGRES_HOST"),
                    database=self.credentials.get("database") or os.getenv("POSTGRES_DATABASE"),
                    user=self.credentials.get("user") or os.getenv("POSTGRES_USER"),
                    password=self.credentials.get("password") or os.getenv("POSTGRES_PASSWORD"),
                    port=self.credentials.get("port") or os.getenv("POSTGRES_PORT", 5432)
                )
            elif self.db_type == "mysql":
                import mysql.connector
                self.connection = mysql.connector.connect(
                    host=self.credentials.get("host") or os.getenv("MYSQL_HOST"),
                    user=self.credentials.get("user") or os.getenv("MYSQL_USER"),
                    password=self.credentials.get("password") or os.getenv("MYSQL_PASSWORD"),
                    database=self.credentials.get("database") or os.getenv("MYSQL_DATABASE"),
                    port=self.credentials.get("port") or os.getenv("MYSQL_PORT", 3306)
                )
            elif self.db_type == "mongodb":
                from pymongo import MongoClient
                self.connection = MongoClient(
                    self.credentials.get("uri") or os.getenv("MONGODB_URI")
                )
            else:
                raise ValueError("Unsupported database type")
            logger.info(f"Connected to {self.db_type.upper()} database.")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados {self.db_type}: {e}")
            self.connection = None

    def close(self):
        """
        Close the database connection if it exists.
        """
        if self.connection:
            from sqlalchemy.engine.base import Engine
            if self.db_type == "mssql" and isinstance(self.connection, Engine):
                self.connection.dispose()
            elif not isinstance(self.connection, Engine) and hasattr(self.connection, "close"):
                self.connection.close()
            logger.info(f"Connection to {self.db_type.upper()} closed.")

    def execute_query(self, query):
        """
        Execute a SQL query and return the result as a DataFrame (or None for MongoDB).
        :param query: SQL query string.
        :return: DataFrame with query results or None.
        """
        if self.connection and self.db_type == "mssql":
            try:
                from sqlalchemy.engine.base import Engine
                if isinstance(self.connection, Engine):
                    logger.info(f"Executing query on MSSQL: {query}")
                    return pd.read_sql(query, self.connection)
                else:
                    logger.warning("Conexão mssql não é um Engine do SQLAlchemy.")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        if self.connection and self.db_type == "oracle":
            try:
                from sqlalchemy.engine.base import Engine
                if not isinstance(self.connection, Engine) and hasattr(self.connection, "cursor"):
                    cursor_method = getattr(self.connection, "cursor", None)
                    if callable(cursor_method):
                        cursor = cursor_method()
                        execute = getattr(cursor, "execute", None)
                        description = getattr(cursor, "description", None)
                        fetchall = getattr(cursor, "fetchall", None)
                        close = getattr(cursor, "close", None)
                        if callable(execute) and callable(fetchall) and callable(close):
                            logger.info(f"Executing query on Oracle: {query}")
                            execute(query)
                            columns = [col[0] for col in description] if description else []
                            rows = list(fetchall()) # type: ignore
                            if hasattr(rows, '__iter__'):
                                rows = list(rows)
                                close()
                                return pd.DataFrame(rows, columns=columns)
                            else:
                                logger.warning("fetchall() não retornou um iterável.")
                                close()
                                return pd.DataFrame()
                        else:
                            logger.warning("Métodos do cursor não são chamáveis.")
                            return pd.DataFrame()
                    else:
                        logger.warning("Atributo cursor existe mas não é chamável.")
                        return pd.DataFrame()
                else:
                    logger.warning("Conexão Oracle não possui método cursor() ou é um Engine.")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        elif self.db_type == "mongodb":
            logger.warning("Use métodos específicos para MongoDB como find() ou insert_one().")
            return None
        else:
            logger.warning("Nenhuma conexão ativa.")
            return pd.DataFrame()


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
        self.data = self.data.rename(columns={
            "purchaseValue": "y",
            "saleValue": "yhat",
            "dt": "ds"
        }).dropna()
        logger.info(f"Data loaded for regression analysis. Shape: {self.data.shape if self.data is not None else None}")

    def analyze_correlation(self):
        """
        Analyze and print the correlation between purchase and sale values.
        """
        if self.data is not None:
            correlation = self.data["y"].corr(self.data["yhat"])
            logger.info(f"Correlation between purchaseValue and saleValue: {correlation}")
            print(f"Correlation between purchaseValue and saleValue: {correlation}")
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
            logger.info(f"Model Coefficients: {getattr(self.model, 'coef_', None)}")
            logger.info(f"Model Intercept: {getattr(self.model, 'intercept_', None)}")
            print(f"Mean Squared Error: {mse}")
            print(f"Model Coefficients: {getattr(self.model, 'coef_', None)}")
            print(f"Model Intercept: {getattr(self.model, 'intercept_', None)}")
        else:
            logger.warning("Model or test data is None. Cannot evaluate model.")

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
            notify_webhook(webhook_url, payload)


class ClassifierModel:
    """
    Class for training and evaluating a RandomForest classifier on tabular data.
    """
    def __init__(self, data=None, target_column=None, test_size=0.2, random_state=42, db_connector=None, query=None):
        """
        Initialize the ClassifierModel.
        :param data: Input data (DataFrame or None).
        :param target_column: Name of the target column.
        :param test_size: Fraction of data to use for testing.
        :param random_state: Random seed for reproducibility.
        :param db_connector: Database connector instance.
        :param query: Query to fetch data from the database.
        """
        self.data = data
        self.target_column = target_column
        self.test_size = test_size
        self.random_state = random_state
        self.db_connector = db_connector
        self.query = query
        self.model = RandomForestClassifier(n_estimators=100, random_state=random_state)
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.accuracy = None

    def load_data(self, filepath=None):
        """
        Load data from a database or CSV file.
        :param filepath: Path to the CSV file (optional).
        """
        if self.db_connector and self.query:
            self.db_connector.connect()
            self.data = self.db_connector.execute_query(self.query)
            self.db_connector.close()
        elif filepath:
            self.data = pd.read_csv(filepath)
        logger.info(f"Data loaded for classification. Shape: {self.data.shape if self.data is not None else None}")

    def preprocess_data(self):
        """
        Preprocess the data by converting date columns and extracting features.
        """
        if self.data is not None:
            self.data['data_compra'] = pd.to_datetime(self.data['data_compra'])
            self.data['mes'] = self.data['data_compra'].dt.month
            self.data['ano'] = self.data['data_compra'].dt.year
        else:
            logger.warning("Data is None. Cannot preprocess data.")

    def split_data(self):
        """
        Split the data into training and testing sets.
        """
        if self.data is not None and self.target_column in self.data.columns:
            X = self.data.drop(columns=[self.target_column])
            y = self.data[self.target_column]
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=self.test_size, random_state=self.random_state)
        else:
            logger.warning("Data is None or target column missing. Cannot split data.")
            self.X_train = self.X_test = self.y_train = self.y_test = None

    def train_model(self):
        """
        Train the RandomForest classifier on the training data.
        """
        if self.X_train is not None and self.y_train is not None:
            self.model.fit(self.X_train, self.y_train)
            logger.info("RandomForestClassifier trained.")
        else:
            logger.warning("Training data is None. Cannot train model.")

    def make_predictions(self):
        """
        Make predictions on the test set using the trained model.
        """
        if self.X_test is not None:
            self.y_pred = self.model.predict(self.X_test)
        else:
            logger.warning("Test data is None. Cannot make predictions.")
            self.y_pred = None

    def evaluate_model(self):
        """
        Evaluate the classifier and print the accuracy score.
        """
        if self.y_test is not None and self.y_pred is not None:
            self.accuracy = accuracy_score(self.y_test, self.y_pred)
            logger.info(f"Model accuracy: {self.accuracy}")
            print(f"Acurácia do modelo: {self.accuracy}")
        else:
            logger.warning("Test or prediction data is None. Cannot evaluate model.")
            self.accuracy = None

    def predict_proba(self, new_data):
        """
        Predict class probabilities for new data.
        :param new_data: DataFrame with new samples.
        :return: Array of probabilities or None.
        """
        if new_data is not None:
            return self.model.predict_proba(new_data)
        else:
            logger.warning("New data is None. Cannot predict probabilities.")
            return None

    def run(self, filepath=None, webhook_url=None, webhook_payload_extra=None):
        """
        Run the full classification pipeline: load, preprocess, split, train, predict, and evaluate.
        Optionally notify a webhook on completion.
        :param filepath: Path to the CSV file (optional).
        :param webhook_url: Optional webhook URL to notify after run.
        :param webhook_payload_extra: Optional dict to merge into the webhook payload.
        """
        self.load_data(filepath)
        self.preprocess_data()
        self.split_data()
        self.train_model()
        self.make_predictions()
        self.evaluate_model()
        if webhook_url:
            payload = {
                "event": "classifier_model_run",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "model_type": "RandomForestClassifier",
                "data_shape": self.data.shape if self.data is not None else None,
                "accuracy": self.accuracy,
            }
            if webhook_payload_extra:
                payload.update(webhook_payload_extra)
            notify_webhook(webhook_url, payload)


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
        self.timecraft_model = TimeCraftModel(db_connector=self.db_connector, **kwargs)
        return self.timecraft_model

    def create_classifier_model(self, **kwargs):
        """
        Create and store a ClassifierModel instance.
        :param kwargs: Arguments for ClassifierModel.
        :return: ClassifierModel instance.
        """
        self.classifier_model = ClassifierModel(db_connector=self.db_connector, **kwargs)
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


def run_scheduled(target_func, interval_seconds: int = 60, max_runs: Optional[int] = None, *args, **kwargs):
    """
    Run a target function periodically in a background thread.
    :param target_func: Function to execute.
    :param interval_seconds: Interval between executions in seconds.
    :param max_runs: Maximum number of executions (None for infinite).
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    """
    def _runner():
        run_count = 0
        while max_runs is None or run_count < max_runs:
            logger.info(f"[Scheduler] Running scheduled task: {target_func.__name__} (run {run_count+1})")
            try:
                target_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[Scheduler] Error in scheduled task: {e}")
            run_count += 1
            time.sleep(interval_seconds)
    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    return thread


def main():
    """
    Main entry point for command-line usage. Provides basic commands: help, status, version.
    """
    import sys
    VERSION = "1.0.0"
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
            model = ai.create_timecraft_model(data="example/data/hist_cambio_float.csv", date_column="dt", value_columns=["purchaseValue", "saleValue"], is_csv=True)
            run_scheduled(model.run, interval_seconds=interval)
        elif model_type == "classifier":
            model = ai.create_classifier_model(data="example/data/hist_cambio_float.csv", target_column="purchaseValue")
            run_scheduled(model.run, interval_seconds=interval)
        elif model_type == "regression":
            model = ai.create_linear_regression_analysis("example/data/hist_cambio_float.csv")
            run_scheduled(model.run_analysis, interval_seconds=interval)
        else:
            print(f"Unknown model type: {model_type}")
            sys.exit(1)
        print(f"Scheduled {model_type} model to run every {interval} seconds. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
    else:
        main()
