import sys

sys.path.append('../')
sys.path.append('../src')

from statistics import LinearRegression

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import pandas as pd

from src.timeseries.model import TimeSeriesModel

model = TimeSeriesModel(
    dzata='./data/hist_cambio_float.csv',
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
# Usando Regressão Linear

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
print(f'Correlation between purchaseValue and saleValue (Simple Regression): {correlation}')
print(f'Mean Squared Error: {mse}')
print(f'Model Coefficients: {model.coef_}')
print(f'Model Intercept: {model.intercept_}')
# Output:
# Correlation between purchaseValue and saleValue (Simple Regression): 0.9999999999999999
# Mean Squared Error: 0.0
# Model Coefficients: [1.0]
# Model Intercept: 0.0
# ----------------------------------------------------------------------------------------------- #
