import sys

sys.path.append('../')
sys.path.append('../../src')

import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import pandas as pd
import plotly.express as px  # Import Plotly
from matplotlib import pyplot as plt
from prophet import Prophet


# noinspection PyUnusedFunction
class TimeCraftModel:
    """
    Class for time series modeling using Prophet.
    """

    def __init__(self, data=None, date_column=None, value_columns=None, is_csv=True, db_connector=None, query=None, periods=60):
        """
        Initializes the TimeCraftModel class.

        :param data: Input data (can be a path to a CSV file or a list of data).
        :param date_column: Name of the date column.
        :param value_columns: List of value columns.
        :param is_csv: Indicates if the data is from a CSV file.
        :param db_connector: Database connector.
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
        Returns a string representation of the class.
        """
        return f"TimeCraftModel(data={self.data}, date_column={self.date_column}, value_columns={self.value_columns}, is_csv={self.is_csv}, db_connector={self.db_connector}, query={self.query})"

    def __repr__(self) -> str:
        """
        Returns an official representation of the class.
        """
        return f"TimeCraftModel(data={self.data}, date_column={self.date_column}, value_columns={self.value_columns}, is_csv={self.is_csv}, db_connector={self.db_connector}, query={self.query})"

    def __len__(self) -> int:
        """
        Returns the number of rows in the DataFrame.
        """
        return len(self.df) if self.df is not None else 0

    def __getitem__(self, key):
        """
        Allows access to DataFrame columns as if it were a dictionary.
        """
        return self.df[key] if self.df is not None else None

    def __iter__(self):
        """
        Allows iteration over the DataFrame.
        """
        return iter(self.df) if self.df is not None else iter([])

    def __next__(self):
        """
        Returns the next row of the DataFrame.
        """
        return next(iter(self.df)) if self.df is not None else None

    def __contains__(self, item) -> bool:
        """
        Checks if an item is in the DataFrame.
        """
        return item in self.df

    def __eq__(self, other) -> bool:
        """
        Compares two TimeCraftModel objects.
        """
        return self.data == other.data and self.date_column == other.date_column and self.value_columns == other.value_columns and self.is_csv == other.is_csv and self.db_connector == other.db_connector and self.query == other.query

    def dropna(self):
        """
        Removes rows with null values.
        """
        if self.df is not None:
            self.df = self.df.dropna()
        else:
            print("DataFrame is None, cannot drop NaN values.")
        return self.df

    def load_and_prepare_data(self):
        """
        Loads and prepares the data for modeling.
        """
        if self.db_connector and self.query:
            # Fetch data from the database
            try:
                self.db_connector.connect()
                df = self.db_connector.execute_query(self.query)
            except Exception as e:
                print(f"TimeCraftModel: Error fetching data from the database: {e}")
                return
            finally:
                if hasattr(self.db_connector, 'close'):
                    self.db_connector.close()
                else:
                    print("The engine does not have a 'close' method.")
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

    def fit_model(self) -> None:
        """
        Fits the Prophet model to the data.
        """
        self.model.fit(self.df[['ds', 'y']]) # type: ignore

    def make_predictions(self, periods=None) -> pd.DataFrame:
        """
        Makes predictions using the fitted model.

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
        Saves the forecasts to a CSV file.

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
            raise ValueError("Forecast is empty. Please run the model before saving the forecast.")
        if self.forecast is None:
            raise ValueError("Forecast is None. Please run the model before saving the forecast.")
        self.forecast.to_csv(output_file, index=False) # type: ignore
        return output_file

    def set_last_run_duration(self, start_time):
        """
        Sets the duration of the last run.

        :param start_time: Start time of the run.
        """
        self.last_run_duration.append(datetime.now() - start_time)

    def save_plots(self, output_dir:str, plot_types:list, formats:list) -> str:
        """
        Saves forecast plots in different formats.

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
                    print("The engine does not have a 'close' method.")
            except Exception as e:
                print(f"Error closing the figure: {e}")

        return output_dir

    def run_and_plot(self) -> None:
        """
        Runs the model and plots the forecasts.
        """
        self.run()
        self.plot_forecast()

    def run_and_plot_plotly(self) -> None:
        """
        Runs the model and plots the forecasts using Plotly.
        """
        self.run()
        self.plot_forecast_plotly()

    def run_and_save_forecast(self, output_file) -> None:
        """
        Runs the model and saves the forecasts to a file.

        :param output_file: Output file path.
        """
        self.run()
        self.save_forecast(output_file)

    def clear(self) -> None:
        """
        Clears the model's data and forecasts.
        """
        self.df = None
        self.forecast = None
        self.last_run_duration = list()

    def run_parallel(self, n_jobs=2) -> None:
        """
        Runs the model in parallel.

        :param n_jobs: Number of parallel jobs.
        """
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            executor.map(self.run, range(n_jobs))

    def run(self) -> None:
        """
        Runs the complete pipeline: data loading, model fitting, and forecasting.
        """
        start_time = datetime.now()
        self.load_and_prepare_data()
        self.fit_model()
        self.make_predictions()
        self.set_last_run_duration(start_time)

    def info(self) -> None:
        """
        Displays information about the model, data, and forecasts.
        """
        print(self.model)
        print(self.df)
        print(self.forecast)

    def get_model(self) -> Prophet:
        """
        Returns the Prophet model.
        """
        return self.model

    def get_data(self) -> pd.DataFrame:
        """
        Returns the loaded data.
        """
        return self.df # type: ignore

    def get_forecast(self) -> pd.DataFrame:
        """
        Returns the forecasts.
        """
        return self.forecast

    def get_data_columns(self) -> list:
        """
        Returns the data columns.
        """
        return self.df.columns.tolist()

    def get_last_run_duration(self) -> datetime:
        """
        Returns the duration of the last run.
        :rtype: str
        """
        return self.last_run_duration.pop()

    def get_duration_history(self) -> list:
        """
        Returns the history of run durations.
        :rtype: list of str
        """
        return self.last_run_duration

    def get_mse(self) -> float:
        """
        Calculates the mean squared error of the forecasts.

        :return: Mean squared error.
        """
        return ((self.forecast['yhat'] - self.df['y']) ** 2).mean()

    def get_correlation(self) -> float:
        """
        Calculates the correlation between the forecasts and the actual values.

        :return: Correlation.
        """
        return self.forecast['yhat'].corr(self.df['y'])

    def get_coefficients(self) -> float:
        """
        Returns the coefficients of the Prophet model.

        :return: Coefficients.
        """
        return self.model.params['k']

    def get_intercept(self) -> float:
        """
        Returns the intercept of the Prophet model.

        :return: Intercept.
        """
        return self.model.params['m']

    def plot_forecast(self) -> None:
        """
        Plots the forecasts using Matplotlib.
        """
        fig = self.model.plot(self.forecast)
        fig.show()

    def plot_forecast_plotly(self):
        """
        Plots the forecasts using Plotly.
        """
        plty = px.line(self.forecast, x='ds', y='yhat', title='Forecast')
        plty.show()