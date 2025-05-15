import sys

sys.path.append('../')
sys.path.append('../../src')

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class ClassifierModel:
    def __init__(self, data=None, target_column=None, test_size=0.2, random_state=42, db_connector=None, query=None):
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
        if self.db_connector and self.query:
            self.db_connector.connect()
            self.data = self.db_connector.execute_query(self.query)
            self.db_connector.close()
        elif filepath:
            self.data = pd.read_csv(filepath)

    def preprocess_data(self):
        self.data['data_compra'] = pd.to_datetime(self.data['data_compra'])
        self.data['mes'] = self.data['data_compra'].dt.month
        self.data['ano'] = self.data['data_compra'].dt.year

    def split_data(self):
        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=self.test_size, random_state=self.random_state)

    def train_model(self):
        self.model.fit(self.X_train, self.y_train)

    def make_predictions(self):
        self.y_pred = self.model.predict(self.X_test)

    def evaluate_model(self):
        self.accuracy = accuracy_score(self.y_test, self.y_pred)
        print(f"Acurácia do modelo: {self.accuracy}")

    def predict_proba(self, new_data):
        return self.model.predict_proba(new_data)

    def run(self, filepath=None):
        self.load_data(filepath)
        self.preprocess_data()
        self.split_data()
        self.train_model()
        self.make_predictions()
        self.evaluate_model()
