# TimeCraft Linear Regression Example
# This example demonstrates how to use the TimeCraft library to perform time series analysis
# and linear regression on a dataset containing purchase and sale values.
# Ensure you have the required libraries installed:
# pip install timecraft_ai pandas scikit-learn


import sys

sys.path.append('../')
sys.path.append('../src')

from timecraft_ai import TimeCraftModel
from timecraft_ai import LinearRegression
from timecraft_ai import LinearRegressionAnalysis

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import pandas as pd

model = TimeCraftModel(
    data='./data/hist_cambio_float.csv',
    date_column='dt',
    value_columns=['purchaseValue', 'saleValue'],
    is_csv=True,
    periods=30
)
model.run()
mse_prophet = model.get_mse()
print(f'Correlation between purchaseValue and saleValue (Prophet): {model.get_correlation()}')
print(f'Mean Squared Error (Prophet): {mse_prophet}')
print(f'Model Coefficients (Prophet): {model.get_coefficients()}')
print(f'Model Intercept (Prophet): {model.get_intercept()}')
# Output:
# Correlation between purchaseValue and saleValue (Prophet): 0.9999999999999999
# Mean Squared Error (Prophet): 0.0
# Model Coefficients (Prophet): [1.0]
# Model Intercept (Prophet): 0.0
# ----------------------------------------------------------------------------------------------- #
# Using Linear Regression

data = pd.read_csv('./data/hist_cambio_float.csv')
data = pd.DataFrame(data, columns=['purchaseValue', 'saleValue', 'dt'])
data = data.rename(columns={'purchaseValue': 'y', 'saleValue': 'yhat', 'dt': 'ds'})
data = data.dropna()
correlation = data['y'].corr(data['yhat'])
X = data[['yhat']]  # Fix: Use 'yhat' as the feature
y = data['y']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
analyze = LinearRegressionAnalysis(data_path='./data/hist_cambio_float.csv')
analyze.run_analysis()
print(f'Correlation between purchaseValue and saleValue (Linear Regression): {correlation}')
print(f'Mean Squared Error (Linear Regression): {mse}')
print(f'Model Coefficients (Linear Regression): {model.coef_}')
print(f'Model Intercept (Linear Regression): {model.intercept_}')
# Output:
# Correlation between purchaseValue and saleValue (Linear Regression): 0.9999999999999999
# Mean Squared Error (Linear Regression): 0.0
# Model Coefficients (Linear Regression): [1.]
# Model Intercept (Linear Regression): 0.0
# ----------------------------------------------------------------------------------------------- #

