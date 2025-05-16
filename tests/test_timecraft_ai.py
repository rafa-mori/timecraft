import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.timecraft_ai.timecraft_ai import TimeCraftModel, ClassifierModel, LinearRegressionAnalysis, DatabaseConnector

class TestTimeCraftModel(unittest.TestCase):
    def setUp(self):
        # Minimal DataFrame for Prophet
        self.df = pd.DataFrame({
            'ds': pd.date_range('2024-01-01', periods=10, freq='D'),
            'y': range(10)
        })
        self.model = TimeCraftModel(data=self.df, date_column='ds', value_columns=['y'], is_csv=False)
        self.model.df = self.df

    def test_fit_and_predict(self):
        self.model.fit_model()
        forecast = self.model.make_predictions(periods=2)
        self.assertIn('yhat', forecast.columns)

    def test_get_mse(self):
        self.model.fit_model()
        self.model.make_predictions(periods=2)
        mse = self.model.get_mse()
        self.assertIsInstance(mse, float)

class TestClassifierModel(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'data_compra': pd.date_range('2024-01-01', periods=10, freq='D'),
            'feature1': range(10),
            'target': [0, 1]*5
        })
        self.model = ClassifierModel(data=self.df, target_column='target')
        self.model.data = self.df

    def test_preprocess_and_split(self):
        self.model.preprocess_data()
        self.model.split_data()
        self.assertIsNotNone(self.model.X_train)
        self.assertIsNotNone(self.model.X_test)

    def test_train_and_predict(self):
        self.model.preprocess_data()
        self.model.split_data()
        self.model.train_model()
        self.model.make_predictions()
        self.assertIsNotNone(self.model.y_pred)

class TestLinearRegressionAnalysis(unittest.TestCase):
    @patch('pandas.read_csv')
    def test_run_analysis(self, mock_read_csv):
        df = pd.DataFrame({
            'purchaseValue': [1, 2, 3, 4],
            'saleValue': [2, 3, 4, 5],
            'dt': pd.date_range('2024-01-01', periods=4, freq='D')
        })
        mock_read_csv.return_value = df
        analysis = LinearRegressionAnalysis(data_path='fake.csv')
        analysis.run_analysis()  # Should not raise

class TestDatabaseConnector(unittest.TestCase):
    def test_init(self):
        db = DatabaseConnector(db_type='sqlite', db_path=':memory:')
        self.assertEqual(db.db_type, 'sqlite')

if __name__ == '__main__':
    unittest.main()
