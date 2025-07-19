"""
ClassifierModel
# ==========================================================
Class for training and evaluating a RandomForest classifier on tabular data.
"""

from sklearn.metrics import accuracy_score
import pandas as pd
import datetime
import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from ..shared.notify_webhook import Notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class ClassifierModel:
    """
    Class for training and evaluating a RandomForest classifier on tabular data.
    """

    def __init__(
        self,
        data=None,
        target_column=None,
        test_size=0.2,
        random_state=42,
        db_connector=None,
        query=None,
    ):
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
        self.model = RandomForestClassifier(
            n_estimators=100, random_state=random_state)
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
        logger.info(
            "Data loaded for classification. Shape: %s",
            self.data.shape if self.data is not None else None,
        )

    def preprocess_data(self):
        """
        Preprocess the data by converting date columns and extracting features.
        """
        if self.data is not None:
            self.data["data_compra"] = pd.to_datetime(self.data["data_compra"])
            self.data["mes"] = self.data["data_compra"].dt.month
            self.data["ano"] = self.data["data_compra"].dt.year
        else:
            logger.warning("Data is None. Cannot preprocess data.")

    def split_data(self):
        """
        Split the data into training and testing sets.
        """
        if self.data is not None and self.target_column in self.data.columns:
            X = self.data.drop(columns=[self.target_column])
            y = self.data[self.target_column]
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
        else:
            logger.warning(
                "Data is None or target column missing. Cannot split data.")
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
            logger.info("Model accuracy: %s", self.accuracy)
            print(f"Acurácia do modelo: {self.accuracy}")
        else:
            logger.warning(
                "Test or prediction data is None. Cannot evaluate model.")
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
                "timestamp": datetime.datetime.now().isoformat(),
                "model_type": "RandomForestClassifier",
                "data_shape": self.data.shape if self.data is not None else None,
                "accuracy": self.accuracy,
            }
            if webhook_payload_extra:
                payload.update(webhook_payload_extra)
            Notifier.notify_webhook(webhook_url, payload)
