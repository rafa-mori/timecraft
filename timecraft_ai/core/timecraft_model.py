"""
TimeCraftModel class for time series modeling using Prophet.

"""

import logging
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from prophet import Prophet

from ..shared.notify_webhook import Notifier

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class TimeCraftModel:
    """
    Class for time series modeling using Prophet.
    """

    def __init__(
        self,
        data=None,
        date_column=None,
        value_columns=None,
        is_csv=True,
        db_connector=None,
        query=None,
        periods=60,
    ):
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
        return (
            self.data == other.data
            and self.date_column == other.date_column
            and self.value_columns == other.value_columns
            and self.is_csv == other.is_csv
            and self.db_connector == other.db_connector
            and self.query == other.query
        )

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
                logger.error(
                    f"TimeCraftModel: Error fetching data from the database: {e}"
                )
                return
            finally:
                if hasattr(self.db_connector, "close"):
                    self.db_connector.close()
                else:
                    logger.warning(
                        "The engine does not have a 'close' method.")
        elif self.is_csv:
            chunks = pd.read_csv(self.data, chunksize=10000)  # type: ignore
            df = pd.concat(chunks)
        else:
            # Converts the data list to a DataFrame
            df = pd.DataFrame(self.data, columns=[
                              self.date_column] + self.value_columns)  # type: ignore

        # Rename columns
        df = df.rename(columns={self.date_column: "ds",
                       self.value_columns[0]: "y"})  # type: ignore

        # Remove rows with null values
        df = df.dropna()

        # Convert the date column to datetime format
        df["ds"] = pd.to_datetime(df["ds"])

        self.df = df
        logger.info(
            f"Data loaded and prepared. Shape: {self.df.shape if self.df is not None else None}"
        )

    def fit_model(self) -> None:
        """
        Fit the Prophet model to the data.
        """
        self.model.fit(self.df[["ds", "y"]])  # type: ignore
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

        if not output_file.endswith(".csv"):
            output_file += ".csv"
        if os.path.exists(output_file):
            os.remove(output_file)
        if not os.path.exists(output_file):
            os.makedirs(output_file, exist_ok=True)
        if len(self.forecast.value_counts()) == 0:  # type: ignore
            logger.error(
                "Forecast is empty. Please run the model before saving the forecast."
            )
            raise ValueError(
                "Forecast is empty. Please run the model before saving the forecast."
            )
        if self.forecast is None:
            logger.error(
                "Forecast is None. Please run the model before saving the forecast."
            )
            raise ValueError(
                "Forecast is None. Please run the model before saving the forecast."
            )
        self.forecast.to_csv(output_file, index=False)  # type: ignore
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
            if plot_type == "line":
                fig = px.line(self.forecast, x="ds",
                              y="yhat", title="Forecast")
            elif plot_type == "scatter":
                fig = px.scatter(self.forecast, x="ds",
                                 y="yhat", title="Forecast")
            elif plot_type == "bar":
                fig = px.bar(self.forecast, x="ds", y="yhat", title="Forecast")
            else:
                continue

            for fmt in formats:
                if fmt == "html":
                    fig.write_html(
                        os.path.join(
                            output_dir, f"plot_charts_forecast_{plot_type}.html"
                        )
                    )
                elif fmt == "png":
                    fig.write_image(
                        os.path.join(
                            output_dir, f"plot_charts_forecast_{plot_type}.png"
                        ),
                        scale=3,
                    )
                else:
                    continue

        # Matplotlib plots
        for plot_type in plot_types:
            plt.figure()
            if plot_type == "line":
                # type: ignore
                # type: ignore
                # type: ignore
                # type: ignore
                if self.forecast is not None:
                    plt.plot(self.forecast["ds"], self.forecast["yhat"])
                else:
                    logger.error("Forecast is None. Cannot plot.")
            elif plot_type == "scatter":
                # type: ignore
                # type: ignore
                # type: ignore
                # type: ignore
                if self.forecast is not None:
                    plt.scatter(self.forecast["ds"], self.forecast["yhat"])
                else:
                    logger.error("Forecast is None. Cannot plot scatter.")
            elif plot_type == "bar":
                # type: ignore
                # type: ignore
                # type: ignore
                # type: ignore
                if self.forecast is not None:
                    plt.bar(self.forecast["ds"], self.forecast["yhat"])
                else:
                    logger.error("Forecast is None. Cannot plot bar chart.")
            else:
                continue

            plt.title("Forecast")
            for fmt in formats:
                if fmt == "png":
                    plt.savefig(
                        os.path.join(
                            output_dir, f"plot_charts_forecast_{plot_type}.png"
                        ),
                        transparent=True,
                        dpi=300,
                    )
                else:
                    continue

            try:
                if hasattr(plt, "close"):
                    plt.close()
                else:
                    logger.warning(
                        "The engine does not have a 'close' method.")
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
                "forecast_shape": (
                    self.forecast.shape if self.forecast is not None else None
                ),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }
            if webhook_payload_extra:
                payload.update(webhook_payload_extra)
            Notifier.notify_webhook(webhook_url, payload)

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
        return self.df  # type: ignore

    def get_forecast(self) -> pd.DataFrame:
        """
        Get the forecasted values as a DataFrame.
        :return: DataFrame with forecasts.
        """
        return self.forecast  # type: ignore

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
            return ((self.forecast["yhat"] - self.df["y"]) ** 2).mean()
        return float("nan")

    def get_correlation(self) -> float:
        """
        Calculate the correlation between the forecasts and the actual values.
        :return: Correlation value.
        """
        if self.forecast is not None and self.df is not None:
            return self.forecast["yhat"].corr(self.df["y"])
        return float("nan")

    def get_coefficients(self) -> float:
        """
        Get the coefficients of the Prophet model.
        :return: Coefficient value.
        """
        if hasattr(self.model, "params") and "k" in self.model.params:
            return self.model.params["k"]
        return float("nan")

    def get_intercept(self) -> float:
        """
        Get the intercept of the Prophet model.
        :return: Intercept value.
        """
        if hasattr(self.model, "params") and "m" in self.model.params:
            return self.model.params["m"]
        return float("nan")

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
        plty = px.line(self.forecast, x="ds", y="yhat", title="Forecast")
        plty.show()
        plty.show()
        plty.show()
        plty.show()
