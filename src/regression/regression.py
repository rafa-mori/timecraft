import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

class LinearRegressionAnalysis:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None
        self.model = None

    def load_data(self):
        self.data = pd.read_csv(self.data_path)
        self.data = self.data.rename(columns={
            "purchaseValue": "y",
            "saleValue": "yhat",
            "dt": "ds"
        }).dropna()

    def analyze_correlation(self):
        correlation = self.data["y"].corr(self.data["yhat"])
        print(f"Correlation between purchaseValue and saleValue: {correlation}")

    def prepare_data(self):
        X = self.data[["yhat"]]
        y = self.data["y"]
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train):
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

    def evaluate_model(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse}")
        print(f"Model Coefficients: {self.model.coef_}")
        print(f"Model Intercept: {self.model.intercept_}")

    def run_analysis(self):
        self.load_data()
        self.analyze_correlation()
        X_train, X_test, y_train, y_test = self.prepare_data()
        self.train_model(X_train, y_train)
        self.evaluate_model(X_test, y_test)